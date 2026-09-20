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

## 运行时序

`zhuo-core` 是常驻守护进程，`zhuo`（CLI）与 `zhuo-tui`（TUI）作为前端，通过 loopback 上
换行分隔的 JSON-RPC 2.0（NDJSON）与它通信。下图只表达大模块之间的调用关系，不展开报文
内容与状态细节：启动 → 建会话 → 装配一轮 run → LLM 步进 → 工具调用与权限审批 →
子 agent → 上下文压缩 → 收尾与退出。

只画 10 个大模块；`Compactor`、`TraceWriter`、`SessionStore`、`memory loader` 等内部件
折叠进 `CORE` / `SESS` 的说明行里。


### 时序图（Mermaid）

```mermaid
sequenceDiagram
    autonumber
    participant TUI as ui/app
    participant CLIENT as SocketClient
    participant CORE as app+runner+loop
    participant BUS as EventBus+广播
    participant SESS as SessionManager
    participant LLM as LLM Provider
    participant TOOLS as tools+MCP
    participant PERM as PermissionManager
    participant TASK as TaskManager
    participant SUB as subagent

    Note over TUI,SUB: ═══ 1.  启动 ═══
    CLIENT->>CORE: 启动守护进程
    Note over TUI,SUB: [CORE] 加载配置，初始化 trace / 权限 / MCP，注册 RPC 方法后监听端口

    Note over TUI,SUB: ═══ 2.  连接与建会话 ═══
    TUI->>CLIENT: 建立连接
    CLIENT->>CORE: 订阅事件
    CORE->>BUS: 注册订阅者
    CORE-->>CLIENT: 订阅成功
    CLIENT-->>TUI: 连接就绪
    TUI->>CLIENT: 创建会话
    CLIENT->>CORE: 创建会话
    CORE->>SESS: 创建会话
    SESS-)BUS: 广播会话创建
    BUS-)TUI: 推送会话就绪
    SESS-->>CORE: 返回会话
    CORE-->>CLIENT: 返回会话
    CLIENT-->>TUI: 会话就绪

    Note over TUI,SUB: ═══ 3.  发送消息与装配 run ═══
    TUI->>CLIENT: 发送消息
    CLIENT->>CORE: 发送消息
    CORE->>SESS: 处理消息
    SESS-)BUS: 广播用户消息
    BUS-)TUI: 推送用户轮次
    SESS-)BUS: 广播 skill 调用
    BUS-)TUI: 推送 skill
    SESS->>CORE: 驱动 run
    CORE-)BUS: 广播 run 开始
    BUS-)TUI: 推送 run 开始

    Note over TUI,SUB: ═══ 4.  LLM 步进 ═══
    CORE-)BUS: 广播 step 开始
    CORE->>LLM: 调用 LLM
    LLM-)BUS: 广播模型选择
    LLM-)BUS: 流式输出 token
    BUS-)TUI: 流式渲染
    LLM-)BUS: 广播 token 用量
    BUS-)TUI: 显示用量与占用
    LLM-->>CORE: 返回响应

    Note over TUI,SUB: ═══ 5.  工具调用与权限审批 ═══
    CORE-)BUS: 广播工具开始
    BUS-)TUI: 显示工具卡片
    CORE->>PERM: 请求审批
    PERM-)BUS: 广播审批请求
    BUS-)TUI: 显示审批选择
    TUI->>CLIENT: 提交决策
    CLIENT->>CORE: 提交决策
    CORE->>PERM: 回复审批
    PERM-->>CORE: 返回决策
    CORE->>TOOLS: 执行工具
    TOOLS->>TASK: 读写任务
    TASK-->>TOOLS: 返回任务
    TOOLS-->>CORE: 返回工具结果
    CORE-)BUS: 广播工具结束
    BUS-)TUI: 更新工具卡片

    Note over TUI,SUB: ═══ 6.  子 agent ═══
    TOOLS->>SUB: 派生子 agent
    SUB-)BUS: 广播子 agent 开始
    BUS-)TUI: 显示子任务
    SUB->>PERM: 请求审批（共用）
    SUB-)BUS: 广播子 agent 结束
    BUS-)TUI: 更新子任务

    Note over TUI,SUB: ═══ 7.  上下文压缩 ═══
    Note over TUI,SUB: [CORE] 触发条件：context 占用超过阈值（默认关闭）
    CORE->>LLM: 生成对话摘要
    LLM-->>CORE: 返回摘要
    CORE-)BUS: 广播压缩完成
    BUS-)TUI: 提示压缩结果

    Note over TUI,SUB: ═══ 8.  run 收尾 ═══
    CORE-)BUS: 广播 step 结束
    CORE-)BUS: 广播 run 结束
    BUS-)TUI: 显示运行结果
    CORE->>SESS: 持久化历史
    SESS-)BUS: 广播会话状态
    BUS-)TUI: 更新会话状态
    CORE-->>CLIENT: 返回 run 结果
    CLIENT-->>TUI: 本轮结束

    Note over TUI,SUB: ═══ 9.  手动压缩与退出 ═══
    TUI->>CLIENT: 手动压缩
    CLIENT->>CORE: 手动压缩
    CORE->>SESS: 压缩会话
    SESS-->>CORE: 返回压缩结果
    CORE-->>CLIENT: 返回结果
    CLIENT->>CORE: 停止守护进程
```


## Skills / Subagents / MCP

TUI 里输入 `/` 会弹出 skill 补全框（↑↓ 选择、Tab/Enter 确认、Esc 收起）。内建 skill：
`/orchestrate`（planner→executor→reviewer 三阶段多 agent 工作流）、`/review`、`/summarize`、`/init`。

覆盖优先级：项目本地 `<PROJECT_ROOT>/.zhuo/skills/*.md` > 用户全局 `~/.zhuo/skills/*.md` > 内建。
Agent 角色配置同理（`<PROJECT_ROOT>/.zhuo/agents/*.toml` > `~/.zhuo/agents/*.toml` > 内建
planner / executor / reviewer）。

MCP server 在 `config.toml`（默认 `<PROJECT_ROOT>/config.toml`）中声明，工具以 `{server}__{tool}`
命名注册（首次调用会像其他工具一样请求审批）：

```toml
[[mcp.servers]]
name = "filesystem"
transport = "stdio"          # "stdio" | "tcp"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

[[mcp.servers]]
name = "remote"
transport = "tcp"
host = "127.0.0.1"
port = 4010
```

## 验证

```bash
uv run ruff check src    # 风格与 import 排序
uv run mypy src          # 严格类型检查
uv run zhuo-tui          # 手工验收：输入 / 看补全框，/orchestrate <目标> 看子 agent 树
```

前两条等价于 `make lint`；`make` 里还有 `run` / `ping` / `chat` / `test` / `tui` /
`trace` / `replay` / `clean` 等目标，`zhuo` 的完整子命令见 `uv run zhuo --help`。
