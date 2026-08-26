.PHONY: install test lint format check

install:
	python -m pip install -e .

test:
	python -m pytest -q

lint:
	python -m ruff check src tests

format:
	python -m ruff format src tests

check:
	python -m compileall -q src
	python -m pytest -q
