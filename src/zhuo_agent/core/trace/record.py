"""trace 记录的 schema。

定义 TraceRecord：时间戳、方向（CLIENT↔CORE、CORE、CORE↔LLM）、层次
（ipc/event/llm）、类型（command/response/event/api_call 等）、run_id/step
以及原始 data。是 daemon.jsonl 的单行格式，也是 `zhuo trace` 的解析对象。
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class TraceRecord(BaseModel):
    ts: str
    direction: Literal[
        "CLIENT→CORE",
        "CORE→CLIENT",
        "CORE",
        "CORE→LLM",
        "LLM→CORE",
    ]
    layer: Literal["ipc", "event", "llm"]
    kind: str  # command / response / error / push / event / api_call / api_response
    run_id: str | None = None
    step: int | None = None
    client_id: str | None = None
    data: dict[str, Any]
