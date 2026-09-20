"""trace 的异步落盘。

TraceWriter 用 asyncio.Queue + 后台 drain 协程，把 emit() 进来的 TraceRecord
非阻塞地追加写入 daemon.jsonl（每条立即 flush）；stop() 会先等队列排空。
让 IPC/事件/LLM 等热点路径的 trace 记录不拖慢主流程。
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from zhuo_agent.core.trace.record import TraceRecord


class TraceWriter:
    # 初始化 TraceWriter；写入目标文件路径在 start() 前不会创建
    def __init__(self, path: Path) -> None:
        self._path = path
        self._queue: asyncio.Queue[TraceRecord] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

    # 创建目录、启动后台 drain task
    async def start(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._task = asyncio.create_task(self._drain())

    # 等待队列清空后取消 drain task
    async def stop(self) -> None:
        await self._queue.join()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # 非阻塞地将 record 放入写入队列
    def emit(self, record: TraceRecord) -> None:
        self._queue.put_nowait(record)

    # 持续从队列读取 record 并追加写入文件
    async def _drain(self) -> None:
        with open(self._path, "a") as f:
            while True:
                record = await self._queue.get()
                try:
                    f.write(record.model_dump_json() + "\n")
                    f.flush()
                finally:
                    self._queue.task_done()
