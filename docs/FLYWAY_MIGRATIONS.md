# Database Migration System with Flyway

## Overview

The project now includes an **automatic database migration system** using Flyway that ensures the database schema is always up-to-date before the application starts.

## How It Works

1. **Migration Container** (`archon-migrations`):
   - Runs before other containers start
   - Detects database backend (SQLite or Supabase)
   - Applies any pending migrations automatically
   - Exits after migrations complete

2. **Service Dependencies**:
   - `archon-server` waits for migrations to complete
   - Other services start only after database is ready
   - No manual SQL execution required

## Architecture

```
docker-compose up
    ↓
archon-migrations (Flyway)
    ├── Detects DB backend (SQLite/Supabase)
    ├── Runs migrations from /migration/flyway/
    └── Exits with success
    ↓
archon-server (depends on migrations)
    ├── Skips internal migration (ARCHON_SKIP_DB_INIT=true)
    └── Uses migrated database
    ↓
archon-mcp, archon-ui (depend on server)
```

## File Structure

```
/migration/
├── flyway/
│   ├── postgresql/          # Supabase/PostgreSQL migrations
│   │   ├── V001__add_source_url_columns.sql
│   │   └── V002__create_migrations_tracking.sql
│   └── sqlite/              # SQLite migrations
│       └── V001__initial_schema.sql
├── flyway.conf              # Flyway configuration
└── run-migrations.sh        # Migration runner script
```

## Migration Naming Convention

Flyway uses specific naming:
- Format: `V{version}__{description}.sql`
- Example: `V001__initial_schema.sql`
- Version: Sequential numbers (001, 002, 003...)
- Description: Use underscores for spaces

## Adding New Migrations

### For SQLite:
1. Create file: `/migration/flyway/sqlite/V00X__description.sql`
2. Add your SQL changes
3. Restart containers: `docker compose restart`

### For Supabase/PostgreSQL:
1. Create file: `/migration/flyway/postgresql/V00X__description.sql`
2. Add your SQL changes
3. Restart containers: `docker compose restart`

## Configuration

### Environment Variables

For **SQLite** (current):
```yaml
ARCHON_DB_BACKEND=sqlite
ARCHON_SQLITE_PATH=/data/archon.db
ARCHON_SKIP_DB_INIT=true  # Let Flyway handle migrations
```

For **Supabase** (optional):
```yaml
ARCHON_DB_BACKEND=supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx
SUPABASE_DB_URL=postgresql://...  # Direct DB connection
SUPABASE_DB_PASSWORD=xxx
```

## Benefits

1. **Automatic Schema Management**:
   - No manual SQL execution
   - Migrations run on every startup
   - Only unapplied migrations are executed

2. **Version Control**:
   - All schema changes tracked in Git
   - Rollback capability (with down migrations)
   - Clear migration history

3. **Multi-Database Support**:
   - Same system works for SQLite and Supabase
   - Easy to add support for other databases

4. **Container Dependencies**:
   - Services wait for database readiness
   - No startup race conditions
   - Clean separation of concerns

## Troubleshooting

### Check Migration Status:
```bash
docker logs archon-migrations
```

### Re-run Migrations:
```bash
docker compose restart archon-migrations
```

### View Migration History (SQLite):
```bash
docker exec archon-server sqlite3 /data/archon.db \
  "SELECT * FROM flyway_schema_history;"
```

### Reset Database (Development Only):
```bash
# Remove database file
rm ./data/archon.db

# Restart to recreate
docker compose restart
```

## Migration Container Details

- **Base Image**: `flyway/flyway:10-alpine`
- **Added Tools**: SQLite, bash
- **JDBC Drivers**: PostgreSQL (included), SQLite (downloaded)
- **Exit Behavior**: Exits after migrations complete (expected)

## Best Practices

1. **Test Migrations Locally**:
   - Run in development before production
   - Check rollback scripts work

2. **Keep Migrations Small**:
   - One logical change per migration
   - Easier to debug and rollback

3. **Never Edit Applied Migrations**:
   - Create new migration to fix issues
   - Maintains integrity of migration history

4. **Include Both Up and Down**:
   - Up migrations: Apply changes
   - Down migrations: Rollback changes (optional)

## Future Enhancements

- [ ] Add rollback/down migration support
- [ ] Add migration validation/dry-run mode  
- [ ] Support for seed data migrations
- [ ] Migration performance metrics
- [ ] Automatic backup before migrations
- [ ] Support for other databases (MySQL, etc.)

## Summary

The Flyway migration system ensures your database schema is always correct without manual intervention. Just add migration files and restart - Flyway handles the rest!
