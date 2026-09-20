"""权限相关的异常定义。

目前仅包含 PermissionDeniedError，表示某次工具调用被权限管理器拒绝。
"""

from __future__ import annotations


class PermissionDeniedError(Exception):
    """Raised when a tool call is denied by the permission manager."""
