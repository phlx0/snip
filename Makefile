.PHONY: install dev test test-cov lint run clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=snip --cov-report=term-missing

lint:
	python -m py_compile snip/**/*.py && echo "Syntax OK"

run:
	python -m snip

clean:
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
