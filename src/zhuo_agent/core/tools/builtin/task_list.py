"""内建 task_list 工具：列出全部任务及其状态与依赖。

调用 TaskManager.format_list() 生成带 [ ]/[>]/[x] 标记的清单文本，
让 agent 在收尾前确认没有遗留的 pending / in_progress 任务。
"""

from __future__ import annotations

from zhuo_agent.core.task.manager import TaskManager
from zhuo_agent.core.tools.base import BaseTool, ToolResult


class TaskListTool(BaseTool):
    name = "task_list"
    description = (
        "List all tasks with their current status and blocking dependencies. "
        "Use this to check what work remains and what can be started next."
    )
    input_schema: dict[str, object] = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    # 持有 TaskManager 实例，供 invoke 调用
    def __init__(self, task_manager: TaskManager) -> None:
        self._manager = task_manager

    # 返回格式化的任务列表摘要
    async def invoke(self, params: dict[str, object]) -> ToolResult:
        return ToolResult(content=self._manager.format_list())
