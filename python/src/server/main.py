"""
FastAPI Backend for Archon Knowledge Engine

This is the main entry point for the Archon backend API.
It uses a modular approach with separate API modules for different functionality.

Modules:
- settings_api: Settings and credentials management
- mcp_api: MCP server management and tool execution
- knowledge_api: Knowledge base, crawling, and RAG operations
- projects_api: Project and task management with streaming
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from .api_routes.agent_chat_api import router as agent_chat_router
from .api_routes.bug_report_api import router as bug_report_router
from .api_routes.internal_api import router as internal_router
from .api_routes.knowledge_api import router as knowledge_router
from .api_routes.mcp_api import router as mcp_router
from .api_routes.migration_api import router as migration_router
from .api_routes.ollama_api import router as ollama_router
from .api_routes.pages_api import router as pages_router
from .api_routes.progress_api import router as progress_router
from .api_routes.projects_api import router as projects_router
from .api_routes.providers_api import router as providers_router

# Import modular API routers
from .api_routes.settings_api import router as settings_router
from .api_routes.version_api import router as version_router

# Import Logfire configuration
from .config.logfire_config import api_logger, setup_logfire
from .services.crawler_manager import cleanup_crawler, initialize_crawler

# Import utilities and core classes
from .services.credential_service import initialize_credentials

# Import missing dependencies that the modular APIs need
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig
except ImportError:
    # These are optional dependencies for full functionality
    AsyncWebCrawler = None
    BrowserConfig = None

# Logger will be initialized after credentials are loaded
logger = logging.getLogger(__name__)

# Set up logging configuration to reduce noise

# Override uvicorn's access log format to be less verbose
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.setLevel(logging.WARNING)  # Only log warnings and errors, not every request

# CrawlingContext has been replaced by CrawlerManager in services/crawler_manager.py

# Global flag to track if initialization is complete
_initialization_complete = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    global _initialization_complete
    _initialization_complete = False

    # Startup
    logger.info("🚀 Starting Archon backend...")

    try:
        # Validate configuration FIRST - check for anon vs service key
        from .config.config import get_config

        get_config()  # This will raise ConfigurationError if anon key detected
        
        # Check if we're using SQLite backend
        db_backend = os.getenv("ARCHON_DB_BACKEND", "supabase").lower()
        
        if db_backend == "sqlite":
            # Check if we should skip DB initialization (e.g., when using Flyway)
            skip_db_init = os.getenv("ARCHON_SKIP_DB_INIT", "false").lower() == "true"
            
            if skip_db_init:
                logger.info("✅ Skipping SQLite initialization (handled by Flyway migration container)")
            else:
                # Initialize SQLite database if needed
                from .services.sqlite_migration_service import ensure_sqlite_database
                
                db_path = os.getenv("ARCHON_SQLITE_PATH", "archon.db")
                logger.info(f"Initializing SQLite database: {db_path}")
                
                if await ensure_sqlite_database(db_path):
                    logger.info("✅ SQLite database initialized successfully")
                else:
                    logger.error("❌ Failed to initialize SQLite database")
                    raise RuntimeError("SQLite database initialization failed")

        # Initialize credentials from database FIRST - this is the foundation for everything else
        await initialize_credentials()
        
        # Check for pending database migrations (Supabase)
        if db_backend != "sqlite":
            from .services.migration_service import migration_service
            from .services.auto_migration_service import ensure_database_schema
            
            try:
                # First, try to auto-apply critical migrations
                logger.info("Attempting to auto-apply critical database migrations...")
                schema_ready = await ensure_database_schema()
                
                if not schema_ready:
                    logger.warning("Auto-migration could not complete - manual action may be required")
                
                # Then check overall migration status
                status = await migration_service.get_migration_status()
                if status["bootstrap_required"] or status["has_pending"]:
                    # Critical migrations are missing - don't just warn, fail to start
                    error_msg = (
                        f"❌ CRITICAL: Database is missing required schema!\n"
                        f"   - {status['pending_count']} migrations need to be applied\n"
                        f"   - Bootstrap required: {status['bootstrap_required']}\n\n"
                        f"   SOLUTION:\n"
                        f"   1. Open Supabase Dashboard → SQL Editor\n"
                        f"   2. Run the complete setup: /migration/complete_setup.sql\n"
                        f"      OR apply individual migrations from /migration/0.1.0/\n\n"
                        f"   First missing migration: {status['pending_migrations'][0]['name'] if status['pending_migrations'] else 'unknown'}\n\n"
                        f"   The application CANNOT run without the proper database schema.\n"
                        f"   See /QUICK_FIX_DATABASE.md for detailed instructions."
                    )
                    
                    logger.error(error_msg)
                    
                    # Check if this is a critical migration (like source_url)
                    critical_migrations = ["001_add_source_url_display_name", "008_add_migration_tracking"]
                    has_critical = any(
                        m["name"] in critical_migrations 
                        for m in status["pending_migrations"]
                    )
                    
                    if has_critical or status["bootstrap_required"]:
                        # Log critical warning but allow startup (temporary fix)
                        logger.error(
                            "⚠️  RUNNING WITH INCOMPLETE SCHEMA - EXPECT ERRORS!\n"
                            "   Apply migrations ASAP to fix issues.\n"
                            "   Run /APPLY_MIGRATIONS_NOW.sql in Supabase"
                        )
                        # Uncomment the lines below to enforce schema (recommended)
                        # raise RuntimeError(
                        #     "Database schema is incomplete. Please apply migrations before starting. "
                        #     "See logs above for instructions."
                        # )
            except RuntimeError:
                # Re-raise RuntimeError to stop startup (if enforcement is enabled)
                raise
            except Exception as e:
                logger.warning(f"Could not check migration status: {e}")

        # Now that credentials are loaded, we can properly initialize logging
        # This must happen AFTER credentials so LOGFIRE_ENABLED is set from database
        setup_logfire(service_name="archon-backend")

        # Now we can safely use the logger
        logger.info("✅ Credentials initialized")
        api_logger.info("🔥 Logfire initialized for backend")

        # Initialize crawling context
        try:
            await initialize_crawler()
        except Exception as e:
            api_logger.warning(f"Could not fully initialize crawling context: {str(e)}")

        # Make crawling context available to modules
        # Crawler is now managed by CrawlerManager

        api_logger.info("✅ Using polling for real-time updates")

        # Initialize prompt service
        try:
            from .services.prompt_service import prompt_service

            await prompt_service.load_prompts()
            api_logger.info("✅ Prompt service initialized")
        except Exception as e:
            api_logger.warning(f"Could not initialize prompt service: {e}")

        # MCP Client functionality removed from architecture
        # Agents now use MCP tools directly

        # Mark initialization as complete
        _initialization_complete = True
        api_logger.info("🎉 Archon backend started successfully!")

    except Exception:
        api_logger.error("❌ Failed to start backend", exc_info=True)
        raise

    yield

    # Shutdown
    _initialization_complete = False
    api_logger.info("🛑 Shutting down Archon backend...")

    try:
        # MCP Client cleanup not needed

        # Cleanup crawling context
        try:
            await cleanup_crawler()
        except Exception as e:
            api_logger.warning("Could not cleanup crawling context: %s", e, exc_info=True)

        api_logger.info("✅ Cleanup completed")

    except Exception:
        api_logger.error("❌ Error during shutdown", exc_info=True)

# Create FastAPI application
app = FastAPI(
    title="Archon Knowledge Engine API",
    description="Backend API for the Archon knowledge management and project automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to skip logging for health checks
@app.middleware("http")
async def skip_health_check_logs(request, call_next):
    # Skip logging for health check endpoints
    if request.url.path in ["/health", "/api/health"]:
        # Temporarily suppress the log
        import logging

        logger = logging.getLogger("uvicorn.access")
        old_level = logger.level
        logger.setLevel(logging.ERROR)
        response = await call_next(request)
        logger.setLevel(old_level)
        return response
    return await call_next(request)

# Include API routers
app.include_router(settings_router)
app.include_router(mcp_router)
# app.include_router(mcp_client_router)  # Removed - not part of new architecture
app.include_router(knowledge_router)
app.include_router(pages_router)
app.include_router(ollama_router)
app.include_router(projects_router)
app.include_router(progress_router)
app.include_router(agent_chat_router)
app.include_router(internal_router)
app.include_router(bug_report_router)
app.include_router(providers_router)
app.include_router(version_router)
app.include_router(migration_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Archon Knowledge Engine API",
        "version": "1.0.0",
        "description": "Backend API for knowledge management and project automation",
        "status": "healthy",
        "modules": ["settings", "mcp", "mcp-clients", "knowledge", "projects"],
    }

# Health check endpoint
@app.get("/health")
async def health_check(response: Response):
    """Health check endpoint that indicates true readiness including credential loading."""
    from datetime import datetime

    # Check if initialization is complete
    if not _initialization_complete:
        response.status_code = 503  # Service Unavailable
        return {
            "status": "initializing",
            "service": "archon-backend",
            "timestamp": datetime.now().isoformat(),
            "message": "Backend is starting up, credentials loading...",
            "ready": False,
        }

    # Check for required database schema
    schema_status = await _check_database_schema()
    if not schema_status["valid"]:
        response.status_code = 503  # Service Unavailable
        migration_response = {
            "status": "migration_required",
            "service": "archon-backend",
            "timestamp": datetime.now().isoformat(),
            "ready": False,
            "migration_required": True,
            "message": schema_status["message"],
            "schema_valid": False
        }
        
        # Add specific instructions if available
        if "instructions" in schema_status:
            migration_response["instructions"] = schema_status["instructions"]
        else:
            migration_response["instructions"] = [
                "Apply complete schema: Run /migration/complete_setup.sql in Supabase SQL Editor",
                "Check pending migrations: GET /api/migrations/status"
            ]
        
        if "missing_columns" in schema_status:
            migration_response["missing_columns"] = schema_status["missing_columns"]
        
        return migration_response

    return {
        "status": "healthy",
        "service": "archon-backend",
        "timestamp": datetime.now().isoformat(),
        "ready": True,
        "credentials_loaded": True,
        "schema_valid": True,
    }

# API health check endpoint (alias for /health at /api/health)
@app.get("/api/health")
async def api_health_check(response: Response):
    """API health check endpoint - alias for /health."""
    return await health_check(response)

# Cache schema check result to avoid repeated database queries
_schema_check_cache = {"valid": None, "checked_at": 0}

async def _check_database_schema():
    """Check if required database schema exists - only for existing users who need migration."""
    import time

    # If we've already confirmed schema is valid, don't check again
    if _schema_check_cache["valid"] is True:
        return {"valid": True, "message": "Schema is up to date (cached)"}

    # If we recently failed, don't spam the database (wait at least 30 seconds)
    current_time = time.time()
    if (_schema_check_cache["valid"] is False and
        current_time - _schema_check_cache["checked_at"] < 30):
        return _schema_check_cache["result"]

    try:
        from .repositories.repository_factory import get_repository

        repository = get_repository()

        # Try to query sources table to verify schema exists
        # This will fail if table doesn't exist or required columns are missing
        await repository.list_sources()

        # Cache successful result permanently
        _schema_check_cache["valid"] = True
        _schema_check_cache["checked_at"] = current_time

        return {"valid": True, "message": "Schema is up to date"}

    except Exception as e:
        error_msg = str(e).lower()

        # Log schema check error for debugging
        api_logger.debug(f"Schema check error: {type(e).__name__}: {str(e)}")

        # Check for specific error types based on PostgreSQL error codes and messages

        # Check for missing columns first (more specific than table check)
        missing_source_url = 'source_url' in error_msg and ('column' in error_msg or 'does not exist' in error_msg)
        missing_source_display = 'source_display_name' in error_msg and ('column' in error_msg or 'does not exist' in error_msg)

        # Also check for PostgreSQL error code 42703 (undefined column)
        is_column_error = '42703' in error_msg or 'column' in error_msg

        if (missing_source_url or missing_source_display) and is_column_error:
            result = {
                "valid": False,
                "message": "Database schema outdated - missing source_url column. Please apply migrations.",
                "instructions": [
                    "Quick fix: Run /migration/complete_setup.sql in Supabase SQL Editor",
                    "Or apply individual migration: /migration/0.1.0/001_add_source_url_display_name.sql"
                ],
                "missing_columns": ["source_url", "source_display_name"] if missing_source_url else ["source_display_name"]
            }
            # Cache failed result with timestamp
            _schema_check_cache["valid"] = False
            _schema_check_cache["checked_at"] = current_time
            _schema_check_cache["result"] = result
            return result

        # Check for table doesn't exist (less specific, only if column check didn't match)
        # Look for relation/table errors specifically
        if ('relation' in error_msg and 'does not exist' in error_msg) or ('table' in error_msg and 'does not exist' in error_msg):
            # Table doesn't exist - this is a critical setup issue
            result = {
                "valid": False,
                "message": "Required table missing (archon_sources). Run initial migrations before starting."
            }
            # Cache failed result with timestamp
            _schema_check_cache["valid"] = False
            _schema_check_cache["checked_at"] = current_time
            _schema_check_cache["result"] = result
            return result

        # Other errors indicate a problem - fail fast principle
        result = {"valid": False, "message": f"Schema check error: {type(e).__name__}: {str(e)}"}
        # Don't cache inconclusive results - allow retry
        return result

# Export the app directly for uvicorn to use

def main():
    """Main entry point for running the server."""
    import uvicorn

    # Require ARCHON_SERVER_PORT to be set
    server_port = os.getenv("ARCHON_SERVER_PORT")
    if not server_port:
        raise ValueError(
            "ARCHON_SERVER_PORT environment variable is required. "
            "Please set it in your .env file or environment. "
            "Default value: 8181"
        )

    uvicorn.run(
        "src.server.main:app",
        host="0.0.0.0",
        port=int(server_port),
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    main()
