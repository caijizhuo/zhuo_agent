"""`zhuo ping` 子命令：探测 core 守护进程是否在线。

以 JSON-RPC 方式向 daemon 发送 `core.ping`，解析 PongResult 并打印
服务端版本、uptime 与本地往返延迟；连接失败则报错退出。
"""

from __future__ import annotations

import asyncio
import json
import sys
import time

import zhuo_agent
from zhuo_agent.core.bus.commands import PongResult
from zhuo_agent.core.bus.envelope import JsonRpcError, JsonRpcSuccess
from zhuo_agent.core.config import ZhuoConfig


# 同步入口：运行 ping 协程，连接失败时打印错误并退出
def cmd_ping(config: ZhuoConfig) -> None:
    try:
        asyncio.run(_ping(config))
    except (ConnectionRefusedError, OSError):
        print(f"error: core not running ({config.host}:{config.port})", file=sys.stderr)
        sys.exit(1)


# 向 core 守护进程发送 ping 请求，打印 pong 响应及延迟
async def _ping(config: ZhuoConfig) -> None:
    t0 = time.monotonic()
    reader, writer = await asyncio.open_connection(config.host, config.port)

    req = {
        "jsonrpc": "2.0",
        "id": "cli-1",
        "method": "core.ping",
        "params": {"client": f"cli/{zhuo_agent.__version__}"},
    }
    writer.write((json.dumps(req) + "\n").encode())
    await writer.drain()

    line = await asyncio.wait_for(reader.readline(), timeout=10.0)
    latency_ms = int((time.monotonic() - t0) * 1000)

    writer.close()
    await writer.wait_closed()

    raw = json.loads(line)
    if "error" in raw:
        err = JsonRpcError.model_validate(raw)
        print(f"error: {err.error.code} {err.error.message}", file=sys.stderr)
        sys.exit(1)

    resp = JsonRpcSuccess.model_validate(raw)
    result = PongResult.model_validate(resp.result)
    print(f"pong server={result.server_version} uptime={result.uptime_ms}ms latency={latency_ms}ms")
