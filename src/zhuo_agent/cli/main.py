from __future__ import annotations

import argparse
import sys

from zhuo_agent.cli.commands.ping import cmd_ping
from zhuo_agent.cli.commands.run import cmd_run
from zhuo_agent.cli.commands.version import cmd_version
from zhuo_agent.core.config import get_config
from zhuo_agent.core.logging_setup import setup_logging


# CLI 主入口：解析命令行参数并分发到对应子命令
def main() -> None:
    parser = argparse.ArgumentParser(prog="zhuo", description="zhuo_agent CLI")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("ping", help="Ping the core daemon")

    run_parser = subparsers.add_parser("run", help="Run a task")
    run_parser.add_argument("--goal", required=True, help="Goal for the agent to do")

    args = parser.parse_args()

    if args.version:
        cmd_version()
        return

    config = get_config()
    setup_logging(config)

    if args.command == "ping":
        cmd_ping(config)
    elif args.command == "run":
        cmd_run(args.goal, config)
    else:
        parser.print_help()
        sys.exit(1)
