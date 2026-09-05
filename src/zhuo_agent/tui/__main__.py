from __future__ import annotations

import argparse

from zhuo_agent.core.config import get_config
from zhuo_agent.tui.app import ZhuoTuiApp


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
    app = ZhuoTuiApp(config.host, config.port, replay_run_id=args.replay)
    app.run()


if __name__ == "__main__":
    main()
