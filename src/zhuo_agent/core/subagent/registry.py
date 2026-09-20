"""后台 subagent 任务的注册表（BackgroundTaskRegistry）。

以 run_id 为键记录后台子 agent 的 asyncio.Task 与其 ExecutionContext，
提供注册、按 run_id 查询（供 agent_result 工具取结果）以及 daemon 退出时
批量取消全部未完成任务的 cancel_all()。daemon 内跨 run 共享同一实例。
"""

from __future__ import annotations

import asyncio

from zhuo_agent.core.context import ExecutionContext


# 管理后台 subagent 任务的生命周期：注册、查询、批量取消
class BackgroundTaskRegistry:
    def __init__(self) -> None:
        self._tasks: dict[str, tuple[asyncio.Task[None], ExecutionContext]] = {}

    # 注册一个后台任务及其执行上下文
    def register(
        self,
        run_id: str,
        task: asyncio.Task[None],
        context: ExecutionContext,
    ) -> None:
        self._tasks[run_id] = (task, context)

    # 查询后台任务及其上下文；不存在时返回 None
    def get(self, run_id: str) -> tuple[asyncio.Task[None], ExecutionContext] | None:
        return self._tasks.get(run_id)

    # 返回所有已注册的 (task, context) 对，用于 daemon 退出时批量清理
    def all(self) -> list[tuple[asyncio.Task[None], ExecutionContext]]:
        return list(self._tasks.values())

    # 取消所有仍在运行的后台任务，供 daemon 退出时批量清理
    async def cancel_all(self, wait: bool = True) -> None:
        running: list[asyncio.Task[None]] = []
        for task, _ctx in self._tasks.values():
            if not task.done():
                task.cancel()
                running.append(task)
        if running and wait:
            await asyncio.gather(*running, return_exceptions=True)
        self._tasks.clear()
