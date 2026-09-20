"""传输层：基于 TCP loopback 的 JSON-RPC 通信实现。

包含服务端（socket_server）、客户端（socket_client）与事件广播器（ipc_broadcaster），
三者共同支撑 core 守护进程与 CLI/TUI 之间的命令调用和事件推送。
"""
