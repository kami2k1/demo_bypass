PYTHON ?= python3
SOURCES = app tests wsgi.py

.PHONY: install run test lint format check clean

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(PYTHON) -m flask --app wsgi run --debug

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check $(SOURCES)
	$(PYTHON) -m ruff format --check $(SOURCES)

format:
	$(PYTHON) -m ruff format $(SOURCES)

check: lint test
	$(PYTHON) -c "from app import create_app; create_app()"
	@echo "OK: lint sach, test xanh, noi dung nap duoc"

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
