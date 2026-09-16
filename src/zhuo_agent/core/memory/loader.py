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
