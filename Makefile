.PHONY: lint run ping test

run:
	uv run zhuo-core

ping:
	uv run zhuo ping

lint:
	uv run ruff check src
	uv run mypy src

test:
	uv run zhuo run --goal "用python写一个快速排序，放到当前文件夹的一个log文件中"

tui:
	uv run zhuo-tui

replay:
	uv run zhuo-tui --replay 20260905-173234-dc441b

trace:
	uv run zhuo trace 20260911-180948-4cf4fc --layer llm --raw