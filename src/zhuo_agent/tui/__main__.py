"""zhuo-tui 可执行入口。

解析 `--replay` 参数、读取配置，并把日志初始化成只写文件（否则会干扰 Textual 渲染），
最后启动 ZhuoTuiApp。对应 pyproject 中 `zhuo-tui` 命令。
"""

from __future__ import annotations

import argparse
import logging
import logging.handlers
import os
from pathlib import Path

from zhuo_agent.core.config import PROJECT_ROOT, get_config
from zhuo_agent.tui.app import ZhuoTuiApp

# 与 core 的日志目录保持一致，都落在 PROJECT_ROOT/logs 下
_DEFAULT_TUI_LOG = str(PROJECT_ROOT / "logs" / "tui.log")


# TUI 文件日志初始化：不写 stderr（避免干扰 Textual 渲染），只写滚动文件
def _setup_logging(level: str) -> None:
    log_path = Path(os.environ.get("ZHUO_TUI_LOG_FILE", _DEFAULT_TUI_LOG)).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter(
            'level=%(levelname)s ts=%(asctime)s source=%(name)s msg="%(message)s"',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    root.handlers.clear()
    root.addHandler(handler)


# zhuo-tui 入口：解析 --replay 参数后启动 TUI 应用
def main() -> None:
    parser = argparse.ArgumentParser(prog="zhuo-tui", description="zhuo_agent TUI")
    parser.add_argument(
        "--replay",
        metavar="RUN_ID",
        help="Replay events from a past run on connect",
    )
    args = parser.parse_args()

    config = get_config()
    _setup_logging(config.logging.level)
    app = ZhuoTuiApp(config.host, config.port, replay_run_id=args.replay)
    app.run()


if __name__ == "__main__":
    main()
