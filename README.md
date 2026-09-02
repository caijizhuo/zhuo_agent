# zhuo_agent

本地 AI Agent 系统。`zhuo-core` 作为常驻守护进程处理所有任务，`zhuo`（CLI）和 `zhuo-tui`（TUI）通过 TCP loopback 与之通信。

## 环境要求

| 依赖 | 版本 |
|------|------|
| 操作系统 | macOS / Linux |
| Python | 3.12.x |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 |

安装 uv（若尚未安装）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Python 3.12 由 uv 自动管理，无需手动安装。

## 快速开始

```bash
git clone <repo> && cd zhuo_agent
uv sync

uv run zhuo-core            # 启动守护进程
uv run zhuo ping            # 验证连通：应返回 pong
uv run zhuo --version       # 应输出 0.0.1
```