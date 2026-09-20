"""工具相关的异常定义。

目前仅包含 RateLimitedError，供工具在上游限流时抛出，
由 invoke_tool 识别为 rate_limited 错误类并触发重试。
"""

from __future__ import annotations


class RateLimitedError(Exception):
    """Raised by a tool when the upstream service is rate-limiting the request."""
