"""core 与客户端之间的消息契约层（协议模型集合）。

汇总导出 commands（命令/结果）、events（事件）、envelope（JSON-RPC 封装与错误码）
三部分公共符号，方便其他模块从一处导入协议类型。
"""

from zhuo_agent.core.bus.commands import Command, PingCommand, PongResult
from zhuo_agent.core.bus.envelope import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    JsonRpcError,
    JsonRpcErrorObject,
    JsonRpcRequest,
    JsonRpcSuccess,
    make_error,
)
from zhuo_agent.core.bus.events import (
    CoreStartedEvent,
    Event,
    LlmModelSelectedEvent,
    LlmTokenEvent,
    LlmUsageEvent,
    LogLineEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StepFinishedEvent,
    StepStartedEvent,
    ToolCallFailedEvent,
    ToolCallFinishedEvent,
    ToolCallStartedEvent,
)

__all__ = [
    "Command",
    "CoreStartedEvent",
    "Event",
    "INTERNAL_ERROR",
    "INVALID_PARAMS",
    "INVALID_REQUEST",
    "JsonRpcError",
    "JsonRpcErrorObject",
    "JsonRpcRequest",
    "JsonRpcSuccess",
    "LlmModelSelectedEvent",
    "LlmTokenEvent",
    "LlmUsageEvent",
    "LogLineEvent",
    "METHOD_NOT_FOUND",
    "PARSE_ERROR",
    "PingCommand",
    "PongResult",
    "RunFinishedEvent",
    "RunStartedEvent",
    "StepFinishedEvent",
    "StepStartedEvent",
    "ToolCallFailedEvent",
    "ToolCallFinishedEvent",
    "ToolCallStartedEvent",
    "make_error",
]
