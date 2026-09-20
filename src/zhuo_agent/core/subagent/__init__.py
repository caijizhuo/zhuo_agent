"""subagent 子系统：子 agent 派生工具与后台任务注册表。"""

from zhuo_agent.core.subagent.registry import BackgroundTaskRegistry
from zhuo_agent.core.subagent.tool import AgentResultTool, SpawnAgentTool

__all__ = ["BackgroundTaskRegistry", "SpawnAgentTool", "AgentResultTool"]
