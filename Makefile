.PHONY: lint run ping

run:
	uv run zhuo-core

ping:
	uv run zhuo ping

lint:
	uv run ruff check src
	uv run mypy src

