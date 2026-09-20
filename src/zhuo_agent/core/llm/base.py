"""LLM provider 的抽象接口。

用 Protocol 描述 chat() 的签名：接收 messages、tool_schemas、事件总线与 run 信息，
流式产出事件并返回 LlmResponse。让 AgentLoop 只依赖此协议，
从而可以替换具体实现（如测试桩或 TracingProvider 包装）。
"""

from __future__ import annotations

from typing import Protocol

from zhuo_agent.core.events.bus import EventBus
from zhuo_agent.core.llm.types import LlmResponse


class LLMProvider(Protocol):
    # 流式调用 LLM 并发布进度事件，返回完整响应
    async def chat(
        self,
        messages: list[dict[str, object]],
        tool_schemas: list[dict[str, object]],
        bus: EventBus,
        run_id: str,
        *,
        step: int = 0,
        system: str | None = None,
    ) -> LlmResponse: ...
