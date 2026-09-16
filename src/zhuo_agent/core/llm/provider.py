from __future__ import annotations

import asyncio
import importlib
import logging
import os
import sys
from datetime import UTC, datetime
from types import ModuleType
from typing import Any

import anthropic

from zhuo_agent.core.bus.events import LlmModelSelectedEvent, LlmTokenEvent, LlmUsageEvent
from zhuo_agent.core.events.bus import EventBus
from zhuo_agent.core.llm.types import LlmResponse, ToolCallBlock, UsageStats

_MODEL_CONTEXT_WINDOWS: dict[str, int] = {
    "claude-sonnet-4-6": 200_000,
    "claude-haiku-4-5-20251001": 200_000,
    "claude-opus-4-7": 200_000,
    "deepseek-v4-flash": 1_000_000,
}

_MAX_STREAM_RETRIES = 3
_RETRY_BACKOFF_S = (1.0, 2.0, 4.0)

log = logging.getLogger(__name__)


# anthropic SDK 的传输层可能是 httpx 或 httpx2（取决于解析到的 SDK 版本）。
# 流式中断抛出的原始传输异常不会被 SDK 包装，因此按 SDK 实际使用的模块解析异常类型，
# 否则 except 分支永远不会命中，重试形同虚设。
def _load_transport_module() -> ModuleType | None:
    # anthropic 在 import 时已把自己的传输层放进 sys.modules，优先复用同一实例
    for name in ("httpx2", "httpx"):
        module = sys.modules.get(name)
        if module is not None:
            return module
    for name in ("httpx", "httpx2"):
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            continue
    return None


def _stream_drop_errors() -> tuple[type[BaseException], ...]:
    module = _load_transport_module()
    if module is None:
        return ()
    errors = (
        getattr(module, "RemoteProtocolError", None),
        getattr(module, "ReadError", None),
        getattr(module, "ConnectError", None),
    )
    return tuple(e for e in errors if isinstance(e, type) and issubclass(e, BaseException))


# 流式响应意外中断时需要重试的异常集合
_STREAM_DROP_ERRORS: tuple[type[BaseException], ...] = _stream_drop_errors()


# 返回指定模型的最大 context window token 数
def _context_window(model: str) -> int:
    return _MODEL_CONTEXT_WINDOWS.get(model, 200_000)

# _SYSTEM_PROMPT = (
#     "You are a helpful AI assistant. "
#     "Use the available tools to complete the user's goal. "
#     "When the goal is fully achieved, respond with a final answer and do not call any more tools."
# )

_SYSTEM_PROMPT = (
    "You are a helpful AI assistant running inside an agent runtime that tracks work as tasks.\n"
    "\n"
    "TASK PROTOCOL (MANDATORY — follow it for EVERY goal, no exceptions):\n"
    "1. Your FIRST tool call of a run MUST be task_create. Break the goal into one or more\n"
    "   concrete tasks before doing any other work. Use several tasks for multi-step goals.\n"
    "2. Before starting work on a task, call task_update with status='in_progress'\n"
    "   for that task id.\n"
    "3. Immediately after finishing a task, call task_update with status='completed' for that id.\n"
    "4. Call task_list before you finish, to confirm no task is still pending or in_progress.\n"
    "5. Never skip step 1: a run that performs no task_create call is considered invalid.\n"
    "\n"
    "Use the other available tools (read_file, write_file, list_dir, bash) to actually carry out\n"
    "the work each task describes. When the goal is fully achieved and every task is completed,\n"
    "respond with a final answer and do not call any more tools."
)


# 返回当前 UTC 时间的 ISO 8601 字符串
def _now() -> str:
    return datetime.now(UTC).isoformat()


class AnthropicProvider:
    # 初始化 Anthropic 客户端；client 可在测试时注入以跳过 API key 检查
    def __init__(self, model: str, client: Any = None) -> None:
        if client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise SystemExit("ANTHROPIC_API_KEY not set")
            # 读取 base URL：优先项目自定义变量，其次 SDK 标准变量，最后默认官方端点
            base_url = os.environ.get("ANTHROPIC_API_BASE_URL") or os.environ.get(
                "ANTHROPIC_BASE_URL"
            )
            if base_url:
                self._client = anthropic.AsyncAnthropic(
                    api_key=api_key, base_url=base_url
                )
            else:
                self._client = anthropic.AsyncAnthropic(api_key=api_key)
        else:
            self._client = client
        self._model = model

    # 流式调用 Anthropic API，逐 token 发布事件并返回 LlmResponse；网络中断时自动重试
    async def chat(
        self,
        messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]],
        bus: EventBus,
        run_id: str,
        *,
        step: int = 0,
        system: str | None = None,
    ) -> LlmResponse:
        await bus.publish(
            LlmModelSelectedEvent(run_id=run_id, model=self._model, strategy="static", ts=_now())
        )

        system_blocks: list[dict[str, object]] = [
            {
                "type": "text",
                "text": system or _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
        ]

        tools: list[dict[str, object]] = list(tool_schemas)
        if tools:
            last = dict(tools[-1])
            last["cache_control"] = {"type": "ephemeral"}
            tools = tools[:-1] + [last]

        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": 8192,
            "system": system_blocks,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        text_parts: list[str] = []
        final_message: Any = None

        for attempt in range(1, _MAX_STREAM_RETRIES + 1):
            text_parts = []
            try:
                async with self._client.messages.stream(**kwargs) as stream:
                    async for text in stream.text_stream:
                        # Only publish token events on the first attempt to avoid TUI duplicates
                        if attempt == 1:
                            await bus.publish(LlmTokenEvent(run_id=run_id, token=text, ts=_now()))
                        text_parts.append(text)
                    final_message = await stream.get_final_message()
                break  # success
            except _STREAM_DROP_ERRORS as exc:
                if attempt == _MAX_STREAM_RETRIES:
                    log.error(
                        "stream failed after %d attempts run_id=%s step=%d: %s",
                        _MAX_STREAM_RETRIES, run_id, step, exc,
                    )
                    raise
                delay = _RETRY_BACKOFF_S[attempt - 1]
                log.warning(
                    "stream dropped (attempt %d/%d) run_id=%s step=%d: %s — retrying in %.0fs",
                    attempt, _MAX_STREAM_RETRIES, run_id, step, exc, delay,
                )
                await asyncio.sleep(delay)

        assert final_message is not None

        usage = final_message.usage
        cache_read: int = getattr(usage, "cache_read_input_tokens", 0) or 0
        cache_create: int = getattr(usage, "cache_creation_input_tokens", 0) or 0
        # 命中 prompt cache 的 token 不计入 input_tokens，必须单独累加，
        # 否则对话越长、缓存命中越多，context_pct 低估得越厉害。
        context_tokens = usage.input_tokens + cache_read + cache_create
        context_pct = context_tokens / _context_window(self._model)

        await bus.publish(
            LlmUsageEvent(
                run_id=run_id,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cache_read_input_tokens=cache_read,
                cache_creation_input_tokens=cache_create,
                context_pct=context_pct,
                ts=_now(),
            )
        )

        tool_calls: list[ToolCallBlock] = []
        for block in final_message.content:
            if block.type == "tool_use":
                tool_calls.append(
                    ToolCallBlock(id=block.id, name=block.name, input=dict(block.input))
                )

        return LlmResponse(
            stop_reason=final_message.stop_reason or "end_turn",
            tool_calls=tool_calls,
            text="".join(text_parts),
            usage=UsageStats(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cache_read_input_tokens=cache_read,
                cache_creation_input_tokens=cache_create,
                context_pct=context_pct,
            ),
        )
