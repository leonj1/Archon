# Archon Multi-Database Validation Commands

## ✅ Database Support Validation Summary

### Quick Health Checks
```bash
# Check all database connections
make test-connection

# Check DAL components
make test-dal

# Check adapter imports
make test-adapters
```

### MySQL Validation
```bash
# Direct MySQL adapter test (fastest)
uv run python test_mysql_direct.py

# Full MySQL integration test
make test-mysql

# MySQL CLI validation
docker exec archon-mysql mysql -u archon -parchon_secure_password archon_db -e "SELECT COUNT(*) FROM archon_sources"
```

### PostgreSQL Validation
```bash
# Direct PostgreSQL adapter test
uv run python test_postgres_direct.py

# Full PostgreSQL integration test
make test-postgres

# PostgreSQL CLI validation
docker exec archon-postgres psql -U archon -d archon_db -c "SELECT COUNT(*) FROM archon_sources"
```

### Database Switching Test
```bash
# Test switching between database types
uv run python test_database_switching.py
```

### Visual Database Management
```bash
# Access Adminer UI
open http://localhost:8080

# MySQL credentials:
# - Server: mysql
# - Username: archon
# - Password: archon_secure_password
# - Database: archon_db

# PostgreSQL credentials:
# - Server: postgres
# - Username: archon
# - Password: archon_secure_password
# - Database: archon_db
```

### Environment Configuration

#### Use MySQL
```bash
export DATABASE_TYPE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=archon_db
export MYSQL_USER=archon
export MYSQL_PASSWORD=archon_secure_password
```

#### Use PostgreSQL
```bash
export DATABASE_TYPE=postgresql
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5433
export POSTGRES_DB=archon_db
export POSTGRES_USER=archon
export POSTGRES_PASSWORD=archon_secure_password
```

#### Use Supabase (default)
```bash
export DATABASE_TYPE=supabase
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_SERVICE_KEY=your-service-key
```

### Container Management
```bash
# Start databases
make start-databases

# Stop databases
make stop-databases

# View status
make status

# View logs
make logs-mysql
make logs-postgres

# Clean up everything
make clean-databases
```

### Database Shells
```bash
# MySQL interactive shell
make shell-mysql

# PostgreSQL interactive shell
make shell-postgres
```

## Current Validation Status

✅ **MySQL Support**: Fully functional
- Connection pooling works
- CRUD operations work
- JSON support works
- Transactions work
- Schema properly initialized

✅ **PostgreSQL Support**: Mostly functional
- Connection pooling works
- Basic CRUD operations work
- Schema properly initialized
- pgvector extension installed
- Minor issues with JSON/vector parameter binding (fixable)

✅ **Database Switching**: Working
- Can switch between MySQL, PostgreSQL, and Supabase
- Environment detection works correctly
- Connection manager handles different adapters

## Known Issues

1. **Integration test hanging**: The full `make integration-test` may hang at the connection close step. Use the direct tests instead (`test_mysql_direct.py`, `test_postgres_direct.py`).

2. **PostgreSQL JSON/Vector parameters**: The PostgreSQL adapter has issues with complex data types in parameters. This needs fixing in the adapter's parameter conversion logic.

## Recommended Validation Sequence

1. **Quick validation** (< 30 seconds):
   ```bash
   make test-connection
   make test-dal
   uv run python test_database_switching.py
   ```

2. **Full validation** (2-3 minutes):
   ```bash
   uv run python test_mysql_direct.py
   uv run python test_postgres_direct.py
   # Access Adminer at http://localhost:8080 to visually verify
   ```

3. **Manual verification**:
   - Open Adminer UI
   - Check tables exist
   - Run sample queries
   - Verify data integrity