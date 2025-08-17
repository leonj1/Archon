# Archon Root Makefile
# Main commands for running Archon with different database backends

.PHONY: help
help: ## Show this help message
	@echo "Archon Main Commands"
	@echo "===================="
	@echo ""
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make start-with-mysql     # Start Archon with MySQL backend"
	@echo "  make start-with-supabase  # Start Archon with Supabase backend"
	@echo "  make stop                 # Stop all Archon services"

# Color codes for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Check for docker-compose vs docker compose
DOCKER_COMPOSE_CHECK := $(shell which docker-compose 2>/dev/null)
ifdef DOCKER_COMPOSE_CHECK
    DOCKER_COMPOSE = docker-compose
else
    DOCKER_COMPOSE = docker compose
endif

# Check for required environment variables
.PHONY: check-openai-key
check-openai-key:
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "$(RED)Error: OPENAI_API_KEY environment variable is not set$(NC)"; \
		echo "Please set it with: export OPENAI_API_KEY=your-api-key"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ OPENAI_API_KEY found$(NC)"

.PHONY: start-mysql-db
start-mysql-db: ## Start MySQL database container
	@echo "$(YELLOW)Starting MySQL database...$(NC)"
	@cd python && $(MAKE) start-mysql
	@echo "$(GREEN)✓ MySQL database ready$(NC)"

.PHONY: start-with-mysql
start-with-mysql: check-openai-key start-mysql-db ## Start Archon with MySQL backend
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     Starting Archon with MySQL         ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting Archon services with MySQL backend...$(NC)"
	@DATABASE_TYPE=mysql \
	MYSQL_HOST=archon-mysql \
	MYSQL_PORT=3306 \
	MYSQL_DATABASE=archon_db \
	MYSQL_USER=archon \
	MYSQL_PASSWORD=archon_secure_password \
	OPENAI_API_KEY=$$OPENAI_API_KEY \
	LOG_LEVEL=$${LOG_LEVEL:-INFO} \
	$(DOCKER_COMPOSE) up --build

.PHONY: start-with-mysql-detached
start-with-mysql-detached: check-openai-key start-mysql-db ## Start Archon with MySQL backend (detached)
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Starting Archon with MySQL (detached) ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting Archon services in background...$(NC)"
	@DATABASE_TYPE=mysql \
	MYSQL_HOST=archon-mysql \
	MYSQL_PORT=3306 \
	MYSQL_DATABASE=archon_db \
	MYSQL_USER=archon \
	MYSQL_PASSWORD=archon_secure_password \
	OPENAI_API_KEY=$$OPENAI_API_KEY \
	LOG_LEVEL=$${LOG_LEVEL:-INFO} \
	$(DOCKER_COMPOSE) up --build -d
	@echo ""
	@echo "$(GREEN)✓ Archon is running with MySQL backend$(NC)"
	@echo ""
	@echo "Access points:"
	@echo "  • UI: http://localhost:3737"
	@echo "  • API: http://localhost:8181"
	@echo "  • MCP: http://localhost:8051"
	@echo "  • MySQL Admin: http://localhost:8080"
	@echo ""
	@echo "View logs with: $(DOCKER_COMPOSE) logs -f"
	@echo "Stop with: make stop"

.PHONY: start-with-mysql-local
start-with-mysql-local: check-openai-key start-mysql-db ## Start Archon with MySQL (using localhost)
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║  Starting Archon with MySQL (localhost)║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting Archon services with MySQL on localhost...$(NC)"
	@DATABASE_TYPE=mysql \
	MYSQL_HOST=localhost \
	MYSQL_PORT=3306 \
	MYSQL_DATABASE=archon_db \
	MYSQL_USER=archon \
	MYSQL_PASSWORD=archon_secure_password \
	OPENAI_API_KEY=$$OPENAI_API_KEY \
	LOG_LEVEL=$${LOG_LEVEL:-INFO} \
	$(DOCKER_COMPOSE) up --build

.PHONY: start-with-supabase
start-with-supabase: check-openai-key ## Start Archon with Supabase backend
	@if [ -z "$$SUPABASE_URL" ] || [ -z "$$SUPABASE_SERVICE_KEY" ]; then \
		echo "$(RED)Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set$(NC)"; \
		echo "Please set them in your environment or .env file"; \
		exit 1; \
	fi
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║    Starting Archon with Supabase       ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting Archon services with Supabase backend...$(NC)"
	@DATABASE_TYPE=supabase \
	SUPABASE_URL=$$SUPABASE_URL \
	SUPABASE_SERVICE_KEY=$$SUPABASE_SERVICE_KEY \
	OPENAI_API_KEY=$$OPENAI_API_KEY \
	LOG_LEVEL=$${LOG_LEVEL:-INFO} \
	$(DOCKER_COMPOSE) up --build

.PHONY: start-postgres-db
start-postgres-db: ## Start PostgreSQL database container
	@echo "$(YELLOW)Starting PostgreSQL database...$(NC)"
	@cd python && $(MAKE) start-postgres
	@echo "$(GREEN)✓ PostgreSQL database ready$(NC)"

.PHONY: start-with-postgres
start-with-postgres: check-openai-key start-postgres-db ## Start Archon with PostgreSQL backend
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║   Starting Archon with PostgreSQL      ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Starting Archon services with PostgreSQL backend...$(NC)"
	@DATABASE_TYPE=postgresql \
	POSTGRES_HOST=archon-postgres \
	POSTGRES_PORT=5432 \
	POSTGRES_DB=archon_db \
	POSTGRES_USER=archon \
	POSTGRES_PASSWORD=archon_secure_password \
	OPENAI_API_KEY=$$OPENAI_API_KEY \
	LOG_LEVEL=$${LOG_LEVEL:-INFO} \
	$(DOCKER_COMPOSE) up --build

.PHONY: stop
stop: ## Stop all Archon services and databases
	@echo "$(YELLOW)Stopping Archon services...$(NC)"
	@$(DOCKER_COMPOSE) down || true
	@echo "$(YELLOW)Stopping database containers...$(NC)"
	@cd python && $(MAKE) stop-databases || true
	@echo "$(GREEN)✓ All services stopped$(NC)"

.PHONY: clean
clean: ## Stop and remove all containers and volumes
	@echo "$(YELLOW)Cleaning up all Archon resources...$(NC)"
	@$(DOCKER_COMPOSE) down -v || true
	@cd python && $(MAKE) clean-databases || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: logs
logs: ## Show logs for all running services
	@$(DOCKER_COMPOSE) logs -f

.PHONY: logs-mysql
logs-mysql: ## Show MySQL container logs
	@cd python && $(MAKE) logs-mysql

.PHONY: status
status: ## Show status of all containers
	@echo "$(BLUE)Archon Services Status:$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)Database Containers Status:$(NC)"
	@cd python && $(MAKE) status

.PHONY: test-mysql
test-mysql: ## Run MySQL integration tests
	@cd python && $(MAKE) test-mysql

.PHONY: shell-mysql
shell-mysql: ## Open MySQL shell
	@cd python && $(MAKE) shell-mysql

.PHONY: create-env-mysql
create-env-mysql: ## Create .env file for MySQL configuration
	@echo "$(YELLOW)Creating .env file for MySQL configuration...$(NC)"
	@if [ -f .env ]; then \
		echo "$(YELLOW)Backing up existing .env to .env.backup$(NC)"; \
		cp .env .env.backup; \
	fi
	@echo "# Archon MySQL Configuration" > .env
	@echo "DATABASE_TYPE=mysql" >> .env
	@echo "MYSQL_HOST=archon-mysql" >> .env
	@echo "MYSQL_PORT=3306" >> .env
	@echo "MYSQL_DATABASE=archon_db" >> .env
	@echo "MYSQL_USER=archon" >> .env
	@echo "MYSQL_PASSWORD=archon_secure_password" >> .env
	@echo "" >> .env
	@echo "# API Keys (set these values)" >> .env
	@echo "OPENAI_API_KEY=$${OPENAI_API_KEY:-your-api-key-here}" >> .env
	@echo "" >> .env
	@echo "# Logging" >> .env
	@echo "LOG_LEVEL=INFO" >> .env
	@echo "" >> .env
	@echo "# Service Ports" >> .env
	@echo "ARCHON_SERVER_PORT=8181" >> .env
	@echo "ARCHON_MCP_PORT=8051" >> .env
	@echo "ARCHON_AGENTS_PORT=8052" >> .env
	@echo "ARCHON_UI_PORT=3737" >> .env
	@echo "" >> .env
	@echo "$(GREEN)✓ .env file created for MySQL configuration$(NC)"
	@echo "$(YELLOW)Note: Edit .env and set OPENAI_API_KEY if not already set in environment$(NC)"

.PHONY: quick-start-mysql
quick-start-mysql: create-env-mysql start-with-mysql-detached ## Quick start with MySQL (creates .env and starts services)

# Default target
.DEFAULT_GOAL := help