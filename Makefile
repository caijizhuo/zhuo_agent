.PHONY: lint run ping test tui replay trace chat perm verify

run:
	uv run zhuo-core

clean:
	pkill -f "zhuo_agent.core" || true
	rm -rf runs/* logs/* traces/* sessions/*

ping:
	uv run zhuo ping

lint:
	uv run ruff check src
	uv run mypy src

# 验收 S7 移植（Skills / Subagents / MCP / 会话 skill / TUI），不需要真实 LLM
verify:
	uv run python scripts/verify_s7_port.py

test:
	uv run zhuo run --goal "用python写一个快速排序，放到当前文件夹的一个log文件中"

tui:
	uv run zhuo-tui

replay:
	uv run zhuo-tui --replay 20260905-173234-dc441b

trace:
	uv run zhuo trace 20260911-180948-4cf4fc --layer llm --raw

chat:
	uv run zhuo chat
