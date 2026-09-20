"""长期记忆的路径约定与读取。

定义全局记忆（~/.zhuo/context.md，跨项目共享）与项目记忆
（PROJECT_ROOT/context.md，与 config.toml 同级）两个文件位置，并提供把它们
读成字符串的工具函数。加载结果由 AgentRunner 注入 ExecutionContext，
最终拼进 system prompt 的 Global/Project Context 段落。
"""

from __future__ import annotations

from pathlib import Path

from zhuo_agent.core.config import PROJECT_ROOT

# 全局记忆：跨项目共享，放在家目录
GLOBAL_CONTEXT_PATH = Path("~/.zhuo/context.md").expanduser()
# 项目记忆：与 config.toml / policy.toml 同级，锚定在 PROJECT_ROOT 而非 cwd
PROJECT_CONTEXT_PATH = PROJECT_ROOT / "context.md"


# 读取指定路径的 context.md，路径不存在或内容为空时返回空字符串
def load_context_file(path: Path) -> str:
    p = path.expanduser()
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").strip()
