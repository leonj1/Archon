#!/usr/bin/env python3
"""
MCP Server for Archon - Stdio Transport Version

This version of the MCP server uses stdio transport for better compatibility
with Claude Code. It can be run directly from the command line or via
Claude Code's MCP configuration.

Transport: stdio (stdin/stdout)
"""

import json
import logging
import os
import sys
import threading
import time
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load environment variables from the project root .env file
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / ".env"
load_dotenv(dotenv_path, override=True)

# Configure logging to stderr so it doesn't interfere with stdio protocol
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),  # Use stderr for logs
        logging.FileHandler("/tmp/mcp_server_stdio.log", mode="a")
        if os.path.exists("/tmp")
        else logging.NullHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Try to import Logfire configuration if available
try:
    from src.server.config.logfire_config import mcp_logger, setup_logfire
except ImportError:
    logger.warning("Logfire not available - continuing without it")
    mcp_logger = logger
    def setup_logfire(service_name): pass

# Try to import service client for HTTP calls
try:
    from src.server.services.mcp_service_client import get_mcp_service_client
except ImportError:
    logger.warning("Service client not available - some features may be limited")
    def get_mcp_service_client(): return None

# Try to import session management
try:
    from src.server.services.mcp_session_manager import get_session_manager
except ImportError:
    logger.warning("Session manager not available - continuing without it")
    class DummySessionManager:
        def get_active_session_count(self): return 0
        timeout = 3600
    def get_session_manager(): return DummySessionManager()

# Global initialization lock and flag
_initialization_lock = threading.Lock()
_initialization_complete = False
_shared_context = None


@dataclass
class ArchonContext:
    """
    Context for MCP server.
    No heavy dependencies - just service client for HTTP calls.
    """

    service_client: Any
    health_status: dict = None
    startup_time: float = None

    def __post_init__(self):
        if self.health_status is None:
            self.health_status = {
                "status": "healthy",
                "api_service": False,
                "agents_service": False,
                "last_health_check": None,
            }
        if self.startup_time is None:
            self.startup_time = time.time()


async def perform_health_checks(context: ArchonContext):
    """Perform health checks on dependent services via HTTP."""
    try:
        if context.service_client is None:
            logger.warning("Service client not available - skipping health checks")
            return

        # Check dependent services
        service_health = await context.service_client.health_check()

        context.health_status["api_service"] = service_health.get("api_service", False)
        context.health_status["agents_service"] = service_health.get("agents_service", False)

        # Overall status
        all_critical_ready = context.health_status["api_service"]

        context.health_status["status"] = "healthy" if all_critical_ready else "degraded"
        context.health_status["last_health_check"] = datetime.now().isoformat()

        if not all_critical_ready:
            logger.warning(f"Health check failed: {context.health_status}")
        else:
            logger.info("Health check passed - dependent services healthy")

    except Exception as e:
        logger.error(f"Health check error: {e}")
        context.health_status["status"] = "unhealthy"
        context.health_status["last_health_check"] = datetime.now().isoformat()


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[ArchonContext]:
    """
    Lifecycle manager - no heavy dependencies.
    """
    global _initialization_complete, _shared_context

    # Quick check without lock
    if _initialization_complete and _shared_context:
        logger.info("♻️ Reusing existing context for new stdio connection")
        yield _shared_context
        return

    # Acquire lock for initialization
    with _initialization_lock:
        # Double-check pattern
        if _initialization_complete and _shared_context:
            logger.info("♻️ Reusing existing context for new stdio connection")
            yield _shared_context
            return

        logger.info("🚀 Starting MCP server (stdio mode)...")

        try:
            # Initialize session manager
            logger.info("🔐 Initializing session manager...")
            session_manager = get_session_manager()
            logger.info("✓ Session manager initialized")

            # Initialize service client for HTTP calls
            logger.info("🌐 Initializing service client...")
            service_client = get_mcp_service_client()
            logger.info("✓ Service client initialized")

            # Create context
            context = ArchonContext(service_client=service_client)

            # Perform initial health check
            await perform_health_checks(context)

            logger.info("✓ MCP server ready (stdio mode)")

            # Store context globally
            _shared_context = context
            _initialization_complete = True

            yield context

        except Exception as e:
            logger.error(f"💥 Critical error in lifespan setup: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Clean up resources
            logger.info("🧹 Cleaning up MCP server...")
            logger.info("✅ MCP server shutdown complete")


# Define MCP instructions for Claude Code and other clients
MCP_INSTRUCTIONS = """
# Archon MCP Server Instructions

## 🚨 CRITICAL RULES (ALWAYS FOLLOW)
1. **Task Management**: ALWAYS use Archon MCP tools for task management.
   - Combine with your local TODO tools for granular tracking

2. **Research First**: Before implementing, use rag_search_knowledge_base and rag_search_code_examples
3. **Task-Driven Development**: Never code without checking current tasks first

## 🎯 Targeted Documentation Search

When searching specific documentation (very common!):
1. **Get available sources**: `rag_get_available_sources()` - Returns list with id, title, url
2. **Find source ID**: Match user's request to source title (e.g., "PydanticAI docs" -> find ID)
3. **Filter search**: `rag_search_knowledge_base(query="...", source_id="src_xxx", match_count=5)`

Examples:
- User: "Search the Supabase docs for vector functions"
  1. Call `rag_get_available_sources()`
  2. Find Supabase source ID from results (e.g., "src_abc123")
  3. Call `rag_search_knowledge_base(query="vector functions", source_id="src_abc123")`

- User: "Find authentication examples in the MCP documentation"
  1. Call `rag_get_available_sources()`
  2. Find MCP docs source ID
  3. Call `rag_search_code_examples(query="authentication", source_id="src_def456")`

IMPORTANT: Always use source_id (not URLs or domain names) for filtering!

## 📋 Core Workflow

### Task Management Cycle
1. **Get current task**: `list_tasks(task_id="...")`
2. **Search/List tasks**: `list_tasks(query="auth", filter_by="status", filter_value="todo")`
3. **Mark as doing**: `manage_task("update", task_id="...", status="doing")`
4. **Research phase**:
   - `rag_search_knowledge_base(query="...", match_count=5)`
   - `rag_search_code_examples(query="...", match_count=3)`
5. **Implementation**: Code based on research findings
6. **Mark for review**: `manage_task("update", task_id="...", status="review")`
7. **Get next task**: `list_tasks(filter_by="status", filter_value="todo")`

## 🏗️ Project Management

### Project Tools
- `list_projects(project_id=None, query=None, page=1, per_page=10)`
  - List all projects, search by query, or get specific project by ID
- `manage_project(action, project_id=None, title=None, description=None, github_repo=None)`
  - Actions: "create", "update", "delete"

### Document Tools
- `list_documents(project_id, document_id=None, query=None, document_type=None, page=1, per_page=10)`
  - List project documents, search, filter by type, or get specific document
- `manage_document(action, project_id, document_id=None, title=None, document_type=None, content=None, ...)`
  - Actions: "create", "update", "delete"

## 🔍 Research Patterns

### CRITICAL: Keep Queries Short and Focused!
Vector search works best with 2-5 keywords, NOT long sentences or keyword dumps.

✅ GOOD Queries (concise, focused):
- `rag_search_knowledge_base(query="vector search pgvector")`
- `rag_search_code_examples(query="React useState")`
- `rag_search_knowledge_base(query="authentication JWT")`
- `rag_search_code_examples(query="FastAPI middleware")`

❌ BAD Queries (too long, unfocused):
- `rag_search_knowledge_base(query="how to implement vector search with pgvector in PostgreSQL for semantic similarity matching with OpenAI embeddings")`
- `rag_search_code_examples(query="React hooks useState useEffect useContext useReducer useMemo useCallback")`
"""

# Initialize the main FastMCP server with stdio transport
try:
    logger.info("🏗️ MCP SERVER INITIALIZATION (STDIO):")
    logger.info("   Server Name: archon-mcp-server")
    logger.info("   Description: MCP server using stdio transport")
    logger.info("   Transport: stdio (stdin/stdout)")

    mcp = FastMCP(
        "archon-mcp-server",
        description="MCP server for Archon - uses HTTP calls to other services",
        instructions=MCP_INSTRUCTIONS,
        lifespan=lifespan,
    )
    logger.info("✓ FastMCP server instance created successfully (stdio mode)")

except Exception as e:
    logger.error(f"✗ Failed to create FastMCP server: {e}")
    logger.error(traceback.format_exc())
    raise


# Health check endpoint
@mcp.tool()
async def health_check(ctx: Context) -> str:
    """
    Check health status of MCP server and dependencies.

    Returns:
        JSON with health status, uptime, and service availability
    """
    try:
        # Try to get the lifespan context
        context = getattr(ctx.request_context, "lifespan_context", None)

        if context is None:
            # Server starting up
            return json.dumps({
                "success": True,
                "status": "starting",
                "message": "MCP server is initializing...",
                "timestamp": datetime.now().isoformat(),
            })

        # Server is ready - perform health checks
        if hasattr(context, "health_status") and context.health_status:
            await perform_health_checks(context)

            return json.dumps({
                "success": True,
                "health": context.health_status,
                "uptime_seconds": time.time() - context.startup_time,
                "timestamp": datetime.now().isoformat(),
            })
        else:
            return json.dumps({
                "success": True,
                "status": "ready",
                "message": "MCP server is running",
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        })


# Session management endpoint
@mcp.tool()
async def session_info(ctx: Context) -> str:
    """
    Get current and active session information.

    Returns:
        JSON with active sessions count and server uptime
    """
    try:
        session_manager = get_session_manager()

        # Build session info
        session_info_data = {
            "active_sessions": session_manager.get_active_session_count(),
            "session_timeout": session_manager.timeout,
        }

        # Add server uptime
        context = getattr(ctx.request_context, "lifespan_context", None)
        if context and hasattr(context, "startup_time"):
            session_info_data["server_uptime_seconds"] = time.time() - context.startup_time

        return json.dumps({
            "success": True,
            "session_management": session_info_data,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Session info failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to get session info: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        })


# Import and register modules
def register_modules():
    """Register all MCP tool modules."""
    logger.info("🔧 Registering MCP tool modules...")

    modules_registered = 0

    # Import and register RAG module (HTTP-based version)
    try:
        from src.mcp_server.features.rag import register_rag_tools

        register_rag_tools(mcp)
        modules_registered += 1
        logger.info("✓ RAG module registered (HTTP-based)")
    except ImportError as e:
        logger.warning(f"⚠ RAG module not available: {e}")
    except Exception as e:
        logger.error(f"✗ Error registering RAG module: {e}")
        logger.error(traceback.format_exc())

    # Import and register all feature tools - separated and focused

    # Project Management Tools
    try:
        from src.mcp_server.features.projects import register_project_tools

        register_project_tools(mcp)
        modules_registered += 1
        logger.info("✓ Project tools registered")
    except ImportError as e:
        # Module not found - this is acceptable in modular architecture
        logger.warning(f"⚠ Project tools module not available (optional): {e}")
    except (SyntaxError, NameError, AttributeError) as e:
        # Code errors that should not be ignored
        logger.error(f"✗ Code error in project tools - MUST FIX: {e}")
        logger.error(traceback.format_exc())
        raise  # Re-raise to prevent running with broken code
    except Exception as e:
        # Unexpected errors during registration
        logger.error(f"✗ Failed to register project tools: {e}")
        logger.error(traceback.format_exc())
        # Don't raise - allow other modules to register

    # Task Management Tools
    try:
        from src.mcp_server.features.tasks import register_task_tools

        register_task_tools(mcp)
        modules_registered += 1
        logger.info("✓ Task tools registered")
    except ImportError as e:
        logger.warning(f"⚠ Task tools module not available (optional): {e}")
    except (SyntaxError, NameError, AttributeError) as e:
        logger.error(f"✗ Code error in task tools - MUST FIX: {e}")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"✗ Failed to register task tools: {e}")
        logger.error(traceback.format_exc())

    # Document Management Tools
    try:
        from src.mcp_server.features.documents import register_document_tools

        register_document_tools(mcp)
        modules_registered += 1
        logger.info("✓ Document tools registered")
    except ImportError as e:
        logger.warning(f"⚠ Document tools module not available (optional): {e}")
    except (SyntaxError, NameError, AttributeError) as e:
        logger.error(f"✗ Code error in document tools - MUST FIX: {e}")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"✗ Failed to register document tools: {e}")
        logger.error(traceback.format_exc())

    # Version Management Tools
    try:
        from src.mcp_server.features.documents import register_version_tools

        register_version_tools(mcp)
        modules_registered += 1
        logger.info("✓ Version tools registered")
    except ImportError as e:
        logger.warning(f"⚠ Version tools module not available (optional): {e}")
    except (SyntaxError, NameError, AttributeError) as e:
        logger.error(f"✗ Code error in version tools - MUST FIX: {e}")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"✗ Failed to register version tools: {e}")
        logger.error(traceback.format_exc())

    # Feature Management Tools
    try:
        from src.mcp_server.features.feature_tools import register_feature_tools

        register_feature_tools(mcp)
        modules_registered += 1
        logger.info("✓ Feature tools registered")
    except ImportError as e:
        logger.warning(f"⚠ Feature tools module not available (optional): {e}")
    except (SyntaxError, NameError, AttributeError) as e:
        logger.error(f"✗ Code error in feature tools - MUST FIX: {e}")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"✗ Failed to register feature tools: {e}")
        logger.error(traceback.format_exc())

    logger.info(f"📦 Total modules registered: {modules_registered}")

    if modules_registered == 0:
        logger.error("💥 No modules were successfully registered!")
        raise RuntimeError("No MCP modules available")


# Register all modules when this file is imported
try:
    register_modules()
except Exception as e:
    logger.error(f"💥 Critical error during module registration: {e}")
    logger.error(traceback.format_exc())
    raise


def main():
    """Main entry point for the MCP server (stdio mode)."""
    try:
        # Initialize Logfire first if available
        setup_logfire(service_name="archon-mcp-server-stdio")

        logger.info("🚀 Starting Archon MCP Server (stdio mode)")
        logger.info("   Transport: stdio (stdin/stdout)")
        logger.info("   Reading from stdin, writing to stdout")
        logger.info("   Logs are written to stderr")

        mcp_logger.info("🔥 Logfire initialized for MCP server (stdio)")
        mcp_logger.info("🌟 Starting MCP server in stdio mode")

        # Run with stdio transport
        mcp.run(transport="stdio")

    except Exception as e:
        mcp_logger.error(f"💥 Fatal error in main - error={str(e)}, error_type={type(e).__name__}")
        logger.error(f"💥 Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 MCP server stopped by user")
    except Exception as e:
        logger.error(f"💥 Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)