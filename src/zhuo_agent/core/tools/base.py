"""工具的统一抽象。

定义 BaseTool 抽象基类（name/description/input_schema/params_model 与 invoke 契约）
和 ToolResult 返回值数据类（内容、是否错误、错误类型）。
所有内建工具与 MCP 工具都实现该接口，从而能被 ToolRegistry 统一注册与调用。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from pydantic import BaseModel


@dataclass
class ToolResult:
    content: str
    is_error: bool = False
    # "runtime_error" | "timeout" | "schema_error" | "permission_denied"
    error_type: str | None = None


class BaseTool(ABC):
    name: str
    description: str
    input_schema: dict[str, object]
    params_model: ClassVar[type[BaseModel] | None] = None

    # 执行工具调用，返回结果或错误
    @abstractmethod
    async def invoke(self, params: dict[str, object]) -> ToolResult: ...
