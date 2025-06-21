.PHONY: install run test lint format clean sync

UV := uv

install-uv:
	@command -v uv >/dev/null 2>&1 || { echo "Installing UV..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }

sync:
	$(UV) sync

install: install-uv
	$(UV) sync --all-extras

run:
	$(UV) run streamlit run app.py

run-api:
	$(UV) run uvicorn api:app --reload --port 8000

run-api-prod:
	$(UV) run uvicorn api:app --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm start

run-all:
	@echo "Starting backend API..."
	$(UV) run uvicorn api:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm start

test:
	$(UV) run pytest tests/ -v --cov=core --cov=services --cov=utils

lint:
	$(UV) run ruff check . --fix

format:
	$(UV) run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .ruff_cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

clean-all: clean
	rm -rf .venv
	$(UV) cache clean

dev: install
	cp .env.example .env
	@echo "Development environment ready! Edit .env file with your settings."

pre-commit: lint test
	@echo "All checks passed!"

update:
	$(UV) lock --upgrade

deps:
	$(UV) tree

lock:
	$(UV) lock