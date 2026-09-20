"""任务的数据模型。

定义 TaskStatus（pending / in_progress / completed）与 Task 数据类，
并提供与 JSON 文件格式一致的 to_dict / from_dict 序列化方法，
供 TaskManager 落盘与读取任务时使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

TaskStatus = Literal["pending", "in_progress", "completed"]


@dataclass
class Task:
    id: int
    subject: str
    description: str
    status: TaskStatus
    blocked_by: list[int]
    created_at: str
    updated_at: str

    # 序列化为 dict，字段名与 JSON 文件格式一致
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "description": self.description,
            "status": self.status,
            "blocked_by": self.blocked_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # 从 dict 构造 Task
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            id=int(data["id"]),
            subject=str(data["subject"]),
            description=str(data.get("description", "")),
            status=data.get("status", "pending"),
            blocked_by=[int(x) for x in data.get("blocked_by", [])],
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )
