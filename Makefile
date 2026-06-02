# hexrag developer commands. Requires `uv` (https://docs.astral.sh/uv/).
# Run `make help` to list targets.

.DEFAULT_GOAL := help
.PHONY: help install run dev test lint format check ingest wipe docker-build docker-up clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies into a local venv
	uv sync

run: ## Run the API server (mock backend, no setup)
	uv run hexrag

dev: ## Run with autoreload on :8001
	uv run uvicorn hexrag.main:app --reload --port 8001

test: ## Run the test suite
	uv run pytest -q

lint: ## Lint with ruff
	uv run ruff check

format: ## Auto-format / fix with ruff
	uv run ruff check --fix
	uv run ruff format

check: lint test ## Lint then test

ingest: ## Ingest a file: make ingest FILE=path/to/doc.pdf
	uv run python scripts/ingest.py $(FILE)

wipe: ## Delete all ingested data (vector store + doc store)
	rm -rf local_data && echo "wiped local_data/"

docker-build: ## Build the Docker image
	docker build -t hexrag:latest .

docker-up: ## Run via docker compose
	docker compose up --build

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache dist build src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
