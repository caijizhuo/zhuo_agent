"""进程日志初始化。

按配置决定日志级别与 text/json 两种格式，为 root logger 挂上输出到 stderr
的 handler 和按 10MB×5 轮转的文件 handler（目录自动创建）。
由 core 守护进程和 CLI 入口在启动时各调用一次。
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from zhuo_agent.core.config import ZhuoConfig

_TEXT_FMT = 'level=%(levelname)s ts=%(asctime)s source=%(name)s msg="%(message)s"'
_JSON_FMT = '{"level":"%(levelname)s","ts":"%(asctime)s","source":"%(name)s","msg":"%(message)s"}'


# 根据配置初始化 root logger：设置级别、格式，并挂载 stderr 和可选的滚动文件 handler
def setup_logging(config: ZhuoConfig) -> None:
    level = getattr(logging, config.logging.level.upper(), logging.INFO)
    fmt = _JSON_FMT if config.logging.format == "json" else _TEXT_FMT
    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S")

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)
    root.addHandler(stderr_handler)

    if config.logging.file:
        log_path = Path(config.logging.file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
