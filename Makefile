.PHONY: setup data test lint

setup:
	uv sync --extra dev

data:
	uv run python -m goalline.data.cli

test:
	uv run pytest

lint:
	uv run ruff check .
