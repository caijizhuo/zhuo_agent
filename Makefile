.PHONY: lint run ping test

run:
	uv run zhuo-core

ping:
	uv run zhuo ping

lint:
	uv run ruff check src
	uv run mypy src

test:
	uv run zhuo run --goal "总结下readme说了什么"

tui:
	uv run zhuo-tui

replay:
	uv run zhuo-tui --replay 20260905-173234-dc441b

trace:
	uv run zhuo trace