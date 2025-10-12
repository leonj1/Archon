#!/bin/sh
# Flyway Migration Runner
# Detects database type and runs appropriate migrations

set -e

echo "🚀 Starting database migration process..."
echo "Database backend: ${ARCHON_DB_BACKEND:-supabase}"

# Check if we're using SQLite or Supabase
if [ "${ARCHON_DB_BACKEND}" = "sqlite" ]; then
    echo "📦 Detected SQLite backend"
    
    # Wait for SQLite file to be available (in case of volume mounting delays)
    SQLITE_PATH="${ARCHON_SQLITE_PATH:-/data/archon.db}"
    SQLITE_DIR=$(dirname "$SQLITE_PATH")
    
    # Create directory if it doesn't exist
    if [ ! -d "$SQLITE_DIR" ]; then
        echo "Creating SQLite directory: $SQLITE_DIR"
        mkdir -p "$SQLITE_DIR"
    fi
    
    # Initialize SQLite database if it doesn't exist
    if [ ! -f "$SQLITE_PATH" ]; then
        echo "Initializing new SQLite database at $SQLITE_PATH"
        sqlite3 "$SQLITE_PATH" "VACUUM;"
    fi
    
    # First, repair the schema history to fix checksum mismatches (development mode)
    echo "Running Flyway repair to fix any checksum mismatches..."
    flyway -url="jdbc:sqlite:$SQLITE_PATH" \
           -driver=org.sqlite.JDBC \
           -locations="filesystem:/flyway/sql/sqlite" \
           -baselineOnMigrate=true \
           -validateMigrationNaming=false \
           repair
    
    # Now run the actual migrations
    echo "Running Flyway migrations..."
    flyway -url="jdbc:sqlite:$SQLITE_PATH" \
           -driver=org.sqlite.JDBC \
           -locations="filesystem:/flyway/sql/sqlite" \
           -baselineOnMigrate=true \
           -validateMigrationNaming=false \
           migrate
           
    echo "✅ SQLite migrations completed"
    
else
    echo "☁️  Detected Supabase/PostgreSQL backend"
    
    # Check required environment variables
    if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
        echo "❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
        exit 1
    fi
    
    # Extract database connection details from Supabase URL
    # Format: https://xxxxx.supabase.co -> postgresql://postgres.[xxxxx]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
    
    # Parse Supabase project ID from URL
    PROJECT_ID=$(echo $SUPABASE_URL | sed -n 's|https://\([^.]*\)\.supabase\.co.*|\1|p')
    
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ Error: Could not parse project ID from SUPABASE_URL"
        exit 1
    fi
    
    # Get database URL from environment or construct it
    if [ -n "$SUPABASE_DB_URL" ]; then
        DB_URL="$SUPABASE_DB_URL"
    else
        # Try to use the direct database connection
        # Note: This requires the database password, not the service key
        DB_PASSWORD="${SUPABASE_DB_PASSWORD:-$SUPABASE_SERVICE_KEY}"
        DB_HOST="${SUPABASE_DB_HOST:-db.$PROJECT_ID.supabase.co}"
        DB_PORT="${SUPABASE_DB_PORT:-5432}"
        DB_NAME="${SUPABASE_DB_NAME:-postgres}"
        DB_USER="${SUPABASE_DB_USER:-postgres}"
        
        DB_URL="jdbc:postgresql://$DB_HOST:$DB_PORT/$DB_NAME"
        
        echo "Using database URL: $DB_URL (host: $DB_HOST)"
    fi
    
    # Run Flyway migrations for PostgreSQL/Supabase
    flyway -url="$DB_URL" \
           -user="$DB_USER" \
           -password="$DB_PASSWORD" \
           -schemas=public \
           -locations="filesystem:/flyway/sql/postgresql" \
           -baselineOnMigrate=true \
           -validateMigrationNaming=false \
           -connectRetries=3 \
           migrate
           
    echo "✅ Supabase/PostgreSQL migrations completed"
fi

echo "🎉 All database migrations applied successfully!"
echo "Container work complete - other services can now start"

# Keep container alive for a moment to ensure dependent services see it as healthy
sleep 2
