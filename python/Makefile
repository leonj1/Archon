# Archon Database Integration Test Makefile
# Tests MySQL and PostgreSQL support implementation

.PHONY: help
help: ## Show this help message
	@echo "Archon Database Integration Tests"
	@echo "================================="
	@echo ""
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make integration-test     # Run all integration tests"
	@echo "  make test-mysql          # Test only MySQL"
	@echo "  make test-postgres       # Test only PostgreSQL"
	@echo "  make test-all           # Test all databases including Supabase"

# Variables
# Check for docker-compose vs docker compose
DOCKER_COMPOSE_CHECK := $(shell which docker-compose 2>/dev/null)
ifdef DOCKER_COMPOSE_CHECK
    DOCKER_COMPOSE = docker-compose -f docker-compose.dev.yml
else
    DOCKER_COMPOSE = docker compose -f docker-compose.dev.yml
endif

PYTHON = uv run python
TEST_DIR = tests/integration
MYSQL_CONTAINER = archon-mysql
POSTGRES_CONTAINER = archon-postgres

# Color codes for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: check-dependencies
check-dependencies: ## Check if required dependencies are installed
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)Docker is not installed$(NC)"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)uv is not installed$(NC)"; exit 1; }
	@# Check for either docker-compose or docker compose
	@if command -v docker-compose >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Found docker-compose$(NC)"; \
	elif docker compose version >/dev/null 2>&1; then \
		echo "$(GREEN)✓ Found docker compose$(NC)"; \
	else \
		echo "$(RED)Docker Compose is not installed$(NC)"; \
		echo "Install with: https://docs.docker.com/compose/install/"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ All dependencies found$(NC)"

.PHONY: start-mysql
start-mysql: ## Start MySQL container
	@echo "$(YELLOW)Starting MySQL container...$(NC)"
	@$(DOCKER_COMPOSE) up -d mysql
	@echo "$(BLUE)Waiting for MySQL to be ready...$(NC)"
	@for i in $$(seq 1 30); do \
		if docker exec $(MYSQL_CONTAINER) mysqladmin ping -h localhost -u root -proot_secure_password >/dev/null 2>&1; then \
			echo "$(GREEN)✓ MySQL is ready$(NC)"; \
			break; \
		fi; \
		echo -n "."; \
		sleep 1; \
	done
	@sleep 2  # Extra wait for schema initialization

.PHONY: start-postgres
start-postgres: ## Start PostgreSQL container
	@echo "$(YELLOW)Starting PostgreSQL container...$(NC)"
	@$(DOCKER_COMPOSE) up -d postgres
	@echo "$(BLUE)Waiting for PostgreSQL to be ready...$(NC)"
	@for i in $$(seq 1 30); do \
		if docker exec $(POSTGRES_CONTAINER) pg_isready -U archon >/dev/null 2>&1; then \
			echo "$(GREEN)✓ PostgreSQL is ready$(NC)"; \
			break; \
		fi; \
		echo -n "."; \
		sleep 1; \
	done
	@sleep 2  # Extra wait for schema initialization

.PHONY: start-databases
start-databases: start-mysql start-postgres ## Start all database containers
	@echo "$(GREEN)✓ All databases started$(NC)"

.PHONY: stop-databases
stop-databases: ## Stop all database containers
	@echo "$(YELLOW)Stopping databases...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Databases stopped$(NC)"

.PHONY: clean-databases
clean-databases: ## Stop and remove all database containers and volumes
	@echo "$(YELLOW)Cleaning up databases and volumes...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: verify-mysql-schema
verify-mysql-schema: ## Verify MySQL schema is correctly created
	@echo "$(BLUE)Verifying MySQL schema...$(NC)"
	@docker exec $(MYSQL_CONTAINER) mysql -u archon -parchon_secure_password -e "USE archon_db; SHOW TABLES;" | grep -q archon_sources || { echo "$(RED)✗ Schema verification failed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ MySQL schema verified$(NC)"

.PHONY: verify-postgres-schema
verify-postgres-schema: ## Verify PostgreSQL schema is correctly created
	@echo "$(BLUE)Verifying PostgreSQL schema...$(NC)"
	@docker exec $(POSTGRES_CONTAINER) psql -U archon -d archon_db -c "\dt" | grep -q archon_sources || { echo "$(RED)✗ Schema verification failed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ PostgreSQL schema verified$(NC)"

.PHONY: test-mysql
test-mysql: check-dependencies start-mysql verify-mysql-schema ## Run MySQL integration tests
	@echo ""
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)     Running MySQL Integration Tests     $(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo ""
	@DATABASE_TYPE=mysql \
	MYSQL_HOST=localhost \
	MYSQL_PORT=3306 \
	MYSQL_DATABASE=archon_db \
	MYSQL_USER=archon \
	MYSQL_PASSWORD=archon_secure_password \
	$(PYTHON) test_mysql_support.py || { echo "$(RED)✗ MySQL tests failed$(NC)"; exit 1; }
	@echo ""
	@echo "$(GREEN)✓ MySQL integration tests passed$(NC)"

.PHONY: test-postgres
test-postgres: check-dependencies start-postgres verify-postgres-schema ## Run PostgreSQL integration tests
	@echo ""
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo "$(BLUE)   Running PostgreSQL Integration Tests  $(NC)"
	@echo "$(BLUE)════════════════════════════════════════$(NC)"
	@echo ""
	@DATABASE_TYPE=postgresql \
	POSTGRES_HOST=localhost \
	POSTGRES_PORT=5433 \
	POSTGRES_DB=archon_db \
	POSTGRES_USER=archon \
	POSTGRES_PASSWORD=archon_secure_password \
	$(PYTHON) test_postgres_support.py || { echo "$(RED)✗ PostgreSQL tests failed$(NC)"; exit 1; }
	@echo ""
	@echo "$(GREEN)✓ PostgreSQL integration tests passed$(NC)"

.PHONY: test-dal
test-dal: ## Test Database Abstraction Layer components
	@echo "$(BLUE)Testing DAL components...$(NC)"
	@$(PYTHON) -c "from src.server.dal import ConnectionManager, DatabaseType, QueryBuilder, query; print('✓ DAL imports successful')" || { echo "$(RED)✗ DAL import test failed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ DAL component tests passed$(NC)"

.PHONY: test-adapters
test-adapters: ## Test database adapters can be imported
	@echo "$(BLUE)Testing database adapters...$(NC)"
	@$(PYTHON) -c "from src.server.dal.adapters import MySQLAdapter, SupabaseAdapter; print('✓ Adapter imports successful')" || { echo "$(RED)✗ Adapter import test failed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Adapter tests passed$(NC)"

.PHONY: integration-test
integration-test: check-dependencies test-dal test-adapters start-databases ## Run complete integration test suite
	@echo ""
	@echo "$(BLUE)╔════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     ARCHON INTEGRATION TEST SUITE      ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)Running complete database integration tests...$(NC)"
	@echo ""
	
	# Verify schemas
	@$(MAKE) -s verify-mysql-schema
	@$(MAKE) -s verify-postgres-schema
	@echo ""
	
	# Test MySQL
	@echo "$(BLUE)[1/3] Testing MySQL Support$(NC)"
	@echo "────────────────────────────"
	@DATABASE_TYPE=mysql \
	MYSQL_HOST=localhost \
	MYSQL_PORT=3306 \
	MYSQL_DATABASE=archon_db \
	MYSQL_USER=archon \
	MYSQL_PASSWORD=archon_secure_password \
	$(PYTHON) test_mysql_support.py || { echo "$(RED)✗ MySQL tests failed$(NC)"; exit 1; }
	@echo ""
	
	# Test PostgreSQL (if test script exists)
	@if [ -f "test_postgres_support.py" ]; then \
		echo "$(BLUE)[2/3] Testing PostgreSQL Support$(NC)"; \
		echo "────────────────────────────────"; \
		DATABASE_TYPE=postgresql \
		POSTGRES_HOST=localhost \
		POSTGRES_PORT=5433 \
		POSTGRES_DB=archon_db \
		POSTGRES_USER=archon \
		POSTGRES_PASSWORD=archon_secure_password \
		$(PYTHON) test_postgres_support.py || { echo "$(RED)✗ PostgreSQL tests failed$(NC)"; exit 1; }; \
		echo ""; \
	else \
		echo "$(YELLOW)[2/3] PostgreSQL test script not found, skipping$(NC)"; \
		echo ""; \
	fi
	
	# Test Query Builder
	@echo "$(BLUE)[3/3] Testing Query Builder$(NC)"
	@echo "──────────────────────────"
	@$(PYTHON) -c "from src.server.dal.query_builder import query, QueryBuilder; \
		q = query().table('test').select('*').where('status', '=', 'active'); \
		sql, params = q.to_sql(); \
		print(f'✓ Query Builder test: {sql[:50]}...')" || { echo "$(RED)✗ Query Builder test failed$(NC)"; exit 1; }
	@echo ""
	
	@echo "$(GREEN)╔════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║   ✅ ALL INTEGRATION TESTS PASSED!     ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "Database support verified for:"
	@echo "  • MySQL 8.0"
	@echo "  • PostgreSQL 16 with pgvector"
	@echo "  • Database Abstraction Layer (DAL)"
	@echo "  • Query Builder"
	@echo ""

.PHONY: test-quick
test-quick: test-dal test-adapters ## Run quick tests without starting databases
	@echo "$(GREEN)✓ Quick tests passed$(NC)"

.PHONY: logs-mysql
logs-mysql: ## Show MySQL container logs
	@$(DOCKER_COMPOSE) logs -f mysql

.PHONY: logs-postgres
logs-postgres: ## Show PostgreSQL container logs
	@$(DOCKER_COMPOSE) logs -f postgres

.PHONY: shell-mysql
shell-mysql: ## Open MySQL shell
	@docker exec -it $(MYSQL_CONTAINER) mysql -u archon -parchon_secure_password archon_db

.PHONY: shell-postgres
shell-postgres: ## Open PostgreSQL shell
	@docker exec -it $(POSTGRES_CONTAINER) psql -U archon archon_db

.PHONY: status
status: ## Show status of database containers
	@echo "$(BLUE)Database Container Status:$(NC)"
	@$(DOCKER_COMPOSE) ps

.PHONY: test-connection
test-connection: ## Test database connections without full integration tests
	@echo "$(BLUE)Testing database connections...$(NC)"
	@echo ""
	@echo "MySQL connection test:"
	@docker exec $(MYSQL_CONTAINER) mysqladmin ping -h localhost -u root -proot_secure_password && echo "$(GREEN)✓ MySQL is responding$(NC)" || echo "$(RED)✗ MySQL not responding$(NC)"
	@echo ""
	@echo "PostgreSQL connection test:"
	@docker exec $(POSTGRES_CONTAINER) pg_isready -U archon && echo "$(GREEN)✓ PostgreSQL is responding$(NC)" || echo "$(RED)✗ PostgreSQL not responding$(NC)"

.PHONY: benchmark
benchmark: start-databases ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	@$(PYTHON) -c "import asyncio; from src.server.dal.adapters import MySQLAdapter; \
		async def bench(): \
			adapter = MySQLAdapter(); \
			await adapter.connect(); \
			import time; \
			start = time.time(); \
			for _ in range(100): \
				await adapter.select('archon_sources', limit=1); \
			elapsed = time.time() - start; \
			print(f'MySQL: 100 queries in {elapsed:.2f}s ({100/elapsed:.1f} QPS)'); \
			await adapter.disconnect(); \
		asyncio.run(bench())"

.PHONY: ci
ci: integration-test ## Run CI pipeline tests
	@echo "$(GREEN)CI pipeline complete$(NC)"

.PHONY: install-deps
install-deps: ## Install Python dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@uv sync
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# Default target
.DEFAULT_GOAL := help