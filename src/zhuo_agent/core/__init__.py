"""core 包：agent 运行时与常驻守护进程 `zhuo-core` 的实现。

汇聚配置、LLM 接入、agent 循环、工具、权限、会话、记忆、压缩、MCP、trace
与 IPC 传输等子系统；对外暴露的唯一入口是 app.run()。
"""
