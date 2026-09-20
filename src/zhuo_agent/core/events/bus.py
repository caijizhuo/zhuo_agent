"""进程内事件总线（EventBus）。

提供极简的订阅/发布：publish 按注册顺序依次 await 所有 handler。
core 用它把 run/step/tool 等事件扇出到事件日志、IPC 广播器和 trace 等多个消费者。
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from pydantic import BaseModel

type EventHandler = Callable[[BaseModel], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[EventHandler] = []

    # 注册一个事件处理函数
    def subscribe(self, handler: EventHandler) -> None:
        self._subscribers.append(handler)

    # 按注册顺序依次调用所有订阅者
    async def publish(self, event: BaseModel) -> None:
        for handler in self._subscribers:
            await handler(event)
