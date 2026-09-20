"""工具注册表。

ToolRegistry 以名称为键保存 BaseTool（同名覆盖），提供按名查找，并把所有工具
转成 Anthropic 要求的 {name, description, input_schema} schema 列表交给 LLM。
每次 run 会按工具白名单与 MCP 可用性新建一个注册表实例。
"""

from __future__ import annotations

from zhuo_agent.core.tools.base import BaseTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    # 注册工具；同名覆盖
    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    # 按名称查找工具，不存在返回 None
    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    # 返回所有工具的 Anthropic 格式 schema 列表
    def tool_schemas(self) -> list[dict[str, object]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]
