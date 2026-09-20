"""支持 `python -m zhuo_agent.core` 启动守护进程。

仅作为薄封装，直接调用 app 模块的 run()；CLI 的 `zhuo core start` 正是以此方式拉起后台进程。
"""

from zhuo_agent.core.app import run

run()
