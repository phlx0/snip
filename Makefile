.PHONY: install dev test test-cov lint run clean

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

# ── setup ────────────────────────────────────────────────────────────

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet

dev: $(VENV)
	$(PIP) install -e ".[dev]" --quiet
	@echo ""
	@echo "  Dev install done."
	@echo "  To use the 'snip' command directly:"
	@echo "    source $(VENV)/bin/activate"
	@echo ""
	@echo "  Or just run without activating:"
	@echo "    make run"

install: $(VENV)
	$(PIP) install . --quiet

# ── run ──────────────────────────────────────────────────────────────

run: $(VENV)
	$(PYTHON) -m snip

# ── test ─────────────────────────────────────────────────────────────

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=snip --cov-report=term-missing

# ── misc ─────────────────────────────────────────────────────────────

lint:
	$(PYTHON) -m py_compile snip/**/*.py && echo "Syntax OK"

clean:
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/ .pytest_cache/ $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
