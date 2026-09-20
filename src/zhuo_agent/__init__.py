"""zhuo_agent：本地 AI Agent 系统的主包。

采用 守护进程 + 前端 架构：zhuo-core 常驻处理任务，zhuo（CLI）与 zhuo-tui
通过 TCP loopback 与之通信。此处仅定义包级版本号，被 CLI ping 与 daemon 上报使用。
"""

__version__ = "0.0.1"
