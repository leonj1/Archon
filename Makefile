# Archon Makefile - Simple, Secure, Cross-Platform
SHELL := /bin/bash
.SHELLFLAGS := -ec

# Docker compose command - prefer newer 'docker compose' plugin over standalone 'docker-compose'
COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

.PHONY: help dev dev-docker stop restart restart-rebuild test test-fe test-be test-be-unit test-be-coverage test-be-build test-be-interactive test-integration-sqlite-qdrant lint lint-fe lint-be clean install check

help:
	@echo "Archon Development Commands"
	@echo "==========================="
	@echo "Development:"
	@echo "  make dev               - Backend in Docker, frontend local (recommended)"
	@echo "  make dev-docker        - Everything in Docker"
	@echo "  make stop              - Stop all services"
	@echo "  make restart           - Quick restart (no rebuild)"
	@echo "  make restart-rebuild   - Restart with full rebuild"
	@echo "  make clean             - Remove containers and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-fe           - Run frontend tests only"
	@echo "  make test-be           - Run backend tests in Docker"
	@echo "  make test-be-unit      - Run backend unit tests only"
	@echo "  make test-be-coverage  - Run backend tests with coverage report"
	@echo "  make test-be-build     - Build/rebuild test Docker image"
	@echo "  make test-be-interactive - Open shell in test container"
	@echo "  make test-integration-sqlite-qdrant - Run SQLite + Qdrant integration test"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              - Run all linters"
	@echo "  make lint-fe           - Run frontend linter only"
	@echo "  make lint-be           - Run backend linter only"
	@echo ""
	@echo "Setup:"
	@echo "  make install           - Install dependencies"
	@echo "  make check             - Check environment setup"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@cd archon-ui-main && npm install
	@cd python && uv sync --group all --group dev
	@echo "✓ Dependencies installed"

# Check environment
check:
	@echo "Checking environment..."
	@node -v >/dev/null 2>&1 || { echo "✗ Node.js not found (require Node 18+)."; exit 1; }
	@node check-env.js
	@echo "Checking Docker..."
	@docker --version > /dev/null 2>&1 || { echo "✗ Docker not found"; exit 1; }
	@$(COMPOSE) version > /dev/null 2>&1 || { echo "✗ Docker Compose not found"; exit 1; }
	@echo "✓ Environment OK"


# Hybrid development (recommended)
dev: check
	@echo "Starting hybrid development..."
	@echo "Backend: Docker | Frontend: Local with hot reload"
	@$(COMPOSE) --profile backend up -d --build
	@set -a; [ -f .env ] && . ./.env; set +a; \
	echo "Backend running at http://$${HOST:-localhost}:$${ARCHON_SERVER_PORT:-8181}"
	@echo "Starting frontend..."
	@cd archon-ui-main && \
	VITE_ARCHON_SERVER_PORT=$${ARCHON_SERVER_PORT:-8181} \
	VITE_ARCHON_SERVER_HOST=$${HOST:-} \
	npm run dev

# Full Docker development
start: check
	@echo "Starting full Docker environment..."
	@$(COMPOSE) --profile full up -d --build
	@echo "✓ All services running"
	@echo "Frontend: http://localhost:3737"
	@echo "API: http://localhost:8181"

# Stop all services
stop:
	@echo "Stopping all services..."
	@$(COMPOSE) --profile backend --profile frontend --profile full down
	@echo "✓ Services stopped"

# Quick restart without rebuild
restart: stop start

# Full restart with rebuild
restart-rebuild: stop start

# Run all tests
test: test-fe test-be

# Run frontend tests
test-fe:
	@echo "Running frontend tests..."
	@cd archon-ui-main && npm run test:run

# Run backend tests in Docker container
test-be:
	@echo "Running backend tests in Docker..."
	@cd python && \
	if [ -f ".env.test" ]; then \
		$(COMPOSE) -f docker-compose.test.yml --env-file .env.test run --rm test pytest -v --tb=short; \
	else \
		echo "⚠️  Warning: .env.test not found. Using default environment."; \
		$(COMPOSE) -f docker-compose.test.yml run --rm test pytest -v --tb=short; \
	fi

# Run only unit tests in Docker
test-be-unit:
	@echo "Running backend unit tests in Docker..."
	@cd python && $(COMPOSE) -f docker-compose.test.yml run --rm test pytest -m unit -v --tb=short

# Run tests with coverage report
test-be-coverage:
	@echo "Running backend tests with coverage..."
	@cd python && $(COMPOSE) -f docker-compose.test.yml run --rm test pytest --cov=src --cov-report=term-missing --cov-report=html

# Build/rebuild test Docker image
test-be-build:
	@echo "Building backend test Docker image..."
	@cd python && docker build -f Dockerfile.test -t archon-test .
	@echo "✓ Test image built"

# Open interactive shell in test container
test-be-interactive:
	@echo "Starting interactive shell in test container..."
	@cd python && $(COMPOSE) -f docker-compose.test.yml run --rm test bash

# Run full SQLite + Qdrant + Crawling integration test
test-integration-sqlite-qdrant:
	@echo "Running full SQLite + Qdrant + Crawling integration test..."
	@echo "Checking for OPENAI_API_KEY..."
	@test -n "$$OPENAI_API_KEY" || { echo "Error: OPENAI_API_KEY environment variable not set"; exit 1; }
	@echo "✓ OPENAI_API_KEY found"
	@echo ""
	@echo "⏱️  Note: This test will crawl https://github.com/The-Pocket/PocketFlow and may take 2-5 minutes"
	@echo ""
	@cd python && uv run --group all pytest tests/integration/test_sqlite_qdrant_crawl_mcp.py -v -s --timeout=300
	@echo "✓ Integration test complete"

# Run simplified SQLite + Qdrant test (no actual crawling)
test-integration-sqlite-qdrant-simple:
	@echo "Running simplified SQLite + Qdrant integration test..."
	@echo "Checking for OPENAI_API_KEY..."
	@test -n "$$OPENAI_API_KEY" || { echo "Error: OPENAI_API_KEY environment variable not set"; exit 1; }
	@echo "✓ OPENAI_API_KEY found"
	@cd python && uv run --group all pytest tests/integration/test_sqlite_qdrant_crawl_mcp_simple.py -v -s
	@echo "✓ Integration test complete"

# Run all linters
lint: lint-fe lint-be

# Run frontend linter
lint-fe:
	@echo "Linting frontend..."
	@cd archon-ui-main && npm run lint

# Run backend linter
lint-be:
	@echo "Linting backend..."
	@cd python && uv run ruff check --fix

# Clean everything (with confirmation)
clean:
	@echo "⚠️  This will remove all containers and volumes"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) down -v --remove-orphans; \
		echo "✓ Cleaned"; \
	else \
		echo "Cancelled"; \
	fi

.DEFAULT_GOAL := help
