# Switch to SQLite Backend

To use SQLite instead of Supabase (avoids all schema migration issues):

## Option 1: Environment Variable

Add to your `.env` file or docker-compose.yml:
```bash
ARCHON_DB_BACKEND=sqlite
ARCHON_SQLITE_PATH=/data/archon.db  # Optional, defaults to archon.db
```

## Option 2: Modify docker-compose.yml

```yaml
archon-server:
  environment:
    - ARCHON_DB_BACKEND=sqlite
    - ARCHON_SQLITE_PATH=/data/archon.db
  volumes:
    - ./data:/data  # Persist SQLite database
```

## Then Restart:
```bash
docker compose down
docker compose up -d
```

## Benefits of SQLite:
- No schema migration issues
- Works immediately
- No cloud dependencies
- Automatic schema creation on startup
- Good for local development

## Limitations:
- No vector search (RAG features limited)
- Single-file database (not scalable)
- No real-time sync between instances
- Limited concurrent writes

## Current Setup:
You're currently using Supabase. The SQLite option is available if you want to switch.
