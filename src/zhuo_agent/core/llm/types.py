"""LLM 调用的返回值类型。

定义 UsageStats（token 用量与 context 占用比例）、ToolCallBlock（模型请求的工具调用）
与 LlmResponse（stop_reason、工具调用、文本、用量）三个数据类，
是 provider 实现与 AgentLoop 之间的共同数据结构。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UsageStats:
    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    context_pct: float = 0.0


@dataclass
class ToolCallBlock:
    id: str
    name: str
    input: dict[str, object]


@dataclass
class LlmResponse:
    stop_reason: str  # "end_turn" | "tool_use"
    tool_calls: list[ToolCallBlock] = field(default_factory=list)
    text: str = ""
    usage: UsageStats | None = None
