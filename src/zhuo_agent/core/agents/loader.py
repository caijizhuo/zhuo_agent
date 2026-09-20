"""子 agent 角色配置（AgentProfile）的查找与解析。

定义角色数据类（名称、描述、system prompt、可用工具、模型）以及 project 本地
> 用户全局 > 内建 三级覆盖的加载器；配置为 TOML 文件。
SpawnAgentTool 通过 subagent_type 参数用它加载 planner/executor/reviewer 等角色，
决定子 agent 的人设与工具白名单。
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from zhuo_agent.core.config import PROJECT_ROOT

# 用户全局角色目录：与 ~/.zhuo 下其余状态（config.toml / policy.toml）同级
GLOBAL_AGENTS_DIR = Path("~/.zhuo/agents").expanduser()
# 项目本地角色目录：锚定 PROJECT_ROOT 而非 cwd，保证从任何目录启动都落在同一仓库根
PROJECT_AGENTS_DIR = PROJECT_ROOT / ".zhuo" / "agents"


@dataclass
class AgentProfile:
    name: str
    description: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=list)
    model: str = ""


# 按两级优先级（项目本地 > 用户全局 > 内建）查找并解析角色配置
class AgentProfileLoader:
    _BUILTIN_DIR = Path(__file__).parent / "builtin"

    # 查找指定角色配置；未找到返回 None
    def load(self, name: str) -> AgentProfile | None:
        for path in self._search_paths(name):
            if path.exists():
                try:
                    return self._parse(path, name)
                except Exception:
                    return None
        return None

    # 返回 [项目本地, 用户全局, 内建] 路径；load() 返回第一个存在的，项目本地优先级最高
    def _search_paths(self, name: str) -> list[Path]:
        builtin = self._BUILTIN_DIR / f"{name}.toml"
        global_ = GLOBAL_AGENTS_DIR / f"{name}.toml"
        local = PROJECT_AGENTS_DIR / f"{name}.toml"
        return [local, global_, builtin]

    # 解析 TOML 角色配置文件
    def _parse(self, path: Path, name: str) -> AgentProfile:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        agent = data.get("agent", {})
        return AgentProfile(
            name=name,
            description=agent.get("description", ""),
            system_prompt=agent.get("system_prompt", "").strip(),
            allowed_tools=agent.get("allowed_tools", []),
            model=agent.get("model", ""),
        )
