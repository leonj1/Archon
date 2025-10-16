#!/usr/bin/env python3
"""
Investigation script using Claude Code SDK agents to debug crawl_status update issue.

This script creates two specialized agents:
1. InvestigatorAgent - Investigates why metadata.crawl_status doesn't update to 'completed'
2. TestWriterAgent - Creates and modifies integration tests for the crawl flow

The tests will actually crawl 'https://go.dev/doc' and validate status updates.
Uses SQLite database and Qdrant vector DB as specified.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    tool,
    create_sdk_mcp_server,
)
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

console = Console()


def print_agent_message(agent_name: str, message: str, style: str = "bold cyan"):
    """Print formatted agent messages."""
    panel = Panel(
        Text(message, style=style),
        title=f"[bold]{agent_name}[/bold]",
        border_style=style.split()[1] if len(style.split()) > 1 else "cyan",
    )
    console.print(panel, end="\n\n")


# ==========================================
# Custom Tools for Agents
# ==========================================


@tool(
    "restart_backend",
    "Restart the Archon backend services using 'make restart'",
    {},
)
async def restart_backend(args: dict[str, Any]) -> dict[str, Any]:
    """Restart backend services."""
    import subprocess

    try:
        result = subprocess.run(
            ["make", "restart"],
            cwd="/home/jose/src/Archon",
            capture_output=True,
            text=True,
            timeout=120,
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Backend restart initiated.\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nReturn Code: {result.returncode}",
                }
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error restarting backend: {str(e)}"}]}


@tool(
    "curl_backend",
    "Execute curl commands against the running backend server",
    {
        "endpoint": str,
        "method": str,
        "data": str,
    },
)
async def curl_backend(args: dict[str, Any]) -> dict[str, Any]:
    """Execute curl commands to validate backend behavior."""
    import subprocess

    endpoint = args.get("endpoint", "/api/health")
    method = args.get("method", "GET")
    data = args.get("data", "")

    base_url = "http://localhost:8181"
    url = f"{base_url}{endpoint}"

    cmd = ["curl", "-X", method, "-s"]

    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", data])

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"CURL {method} {endpoint}\n\nResponse:\n{result.stdout}\n\nError (if any):\n{result.stderr}",
                }
            ]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error executing curl: {str(e)}"}]}


@tool(
    "check_database_status",
    "Check the SQLite database for source crawl_status values",
    {"source_id": str},
)
async def check_database_status(args: dict[str, Any]) -> dict[str, Any]:
    """Query SQLite database to check crawl_status."""
    import sqlite3
    import json

    source_id = args.get("source_id", "")

    try:
        # Connect to SQLite database
        db_path = os.getenv("SQLITE_PATH", "/app/data/archon.db")
        if not os.path.exists(db_path):
            db_path = "/home/jose/src/Archon/data/archon.db"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if source_id:
            # Query specific source
            cursor.execute(
                "SELECT source_id, title, metadata, created_at, updated_at FROM sources WHERE source_id = ?",
                (source_id,),
            )
        else:
            # Query all sources
            cursor.execute(
                "SELECT source_id, title, metadata, created_at, updated_at FROM sources"
            )

        rows = cursor.fetchall()
        conn.close()

        result_text = "Database Query Results:\n\n"
        for row in rows:
            metadata = json.loads(row[2]) if row[2] else {}
            crawl_status = metadata.get("crawl_status", "unknown")
            result_text += f"Source ID: {row[0]}\n"
            result_text += f"Title: {row[1]}\n"
            result_text += f"Crawl Status: {crawl_status}\n"
            result_text += f"Created: {row[3]}\n"
            result_text += f"Updated: {row[4]}\n"
            result_text += f"Full Metadata: {json.dumps(metadata, indent=2)}\n"
            result_text += "-" * 80 + "\n"

        return {"content": [{"type": "text", "text": result_text}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error querying database: {str(e)}"}]
        }


@tool(
    "check_qdrant_collections",
    "Check Qdrant vector database collections and points",
    {},
)
async def check_qdrant_collections(args: dict[str, Any]) -> dict[str, Any]:
    """Query Qdrant to check collections and points."""
    try:
        from qdrant_client import QdrantClient

        # Try to connect to local Qdrant
        client = QdrantClient(host="localhost", port=6333)

        # Get collections
        collections = client.get_collections()

        result_text = "Qdrant Collections:\n\n"
        for collection in collections.collections:
            result_text += f"Collection: {collection.name}\n"

            # Get collection info
            collection_info = client.get_collection(collection.name)
            result_text += f"  Points: {collection_info.points_count}\n"
            result_text += f"  Vector size: {collection_info.config.params.vectors.size}\n"
            result_text += "-" * 80 + "\n"

        return {"content": [{"type": "text", "text": result_text}]}
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error checking Qdrant (may not be running): {str(e)}",
                }
            ]
        }


# Create SDK MCP server with custom tools
investigation_tools_server = create_sdk_mcp_server(
    name="investigation_tools",
    version="1.0.0",
    tools=[
        restart_backend,
        curl_backend,
        check_database_status,
        check_qdrant_collections,
    ],
)


# ==========================================
# Main Investigation Flow
# ==========================================


async def main():
    """Main entry point for investigation."""

    print_agent_message(
        "System",
        "Initializing Crawl Status Investigation\n\n"
        "Goal: Investigate why metadata.crawl_status doesn't update to 'completed'\n"
        "Environment: SQLite + Qdrant + Live Backend\n"
        "Test URL: https://go.dev/doc\n",
        "bold yellow",
    )

    # Agent configuration
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        permission_mode="acceptEdits",
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "MultiEdit",
            "Grep",
            "Glob",
            "Bash",
            "Task",
            "TodoWrite",
            "mcp__investigation_tools__restart_backend",
            "mcp__investigation_tools__curl_backend",
            "mcp__investigation_tools__check_database_status",
            "mcp__investigation_tools__check_qdrant_collections",
        ],
        mcp_servers={"investigation_tools": investigation_tools_server},
        agents={
            "investigator": AgentDefinition(
                description="Expert at investigating backend code flows and identifying bugs in status update logic",
                prompt="""You are an expert backend developer investigating why crawl_status doesn't update to 'completed'.

Your investigation should:
1. Read the crawling service code (src/server/services/crawling/crawling_service.py)
2. Identify where crawl_status SHOULD be updated to 'completed'
3. Check if the update code is being called
4. Use curl_backend tool to trigger a test crawl of https://go.dev/doc
5. Use check_database_status tool to verify if status updates
6. Use Grep to search for all places where 'crawl_status' is set
7. Create a detailed report in /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md

Focus on:
- The flow from crawl initiation to completion
- Where metadata.crawl_status should be updated
- Any error handling that might prevent the update
- Database persistence layer (repository methods)

You have access to Bash, Read, Write, Edit, Grep, Glob, and custom investigation tools.
""",
                model="claude-sonnet-4-5-20250929",
                tools=[
                    "Read",
                    "Write",
                    "Edit",
                    "MultiEdit",
                    "Grep",
                    "Glob",
                    "Bash",
                    "TodoWrite",
                    "mcp__investigation_tools__curl_backend",
                    "mcp__investigation_tools__check_database_status",
                    "mcp__investigation_tools__check_qdrant_collections",
                ],
            ),
            "test_writer": AgentDefinition(
                description="Expert at writing integration tests for backend APIs and crawling workflows",
                prompt="""You are an expert test engineer writing integration tests for the crawl status flow.

Your task:
1. Read the existing test patterns in tests/
2. Create integration tests in /home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py
3. Tests must actually crawl https://go.dev/doc (no mocking!)
4. Use SQLite database (as configured in .env)
5. Use Qdrant for vector storage
6. Verify crawl_status updates from 'pending' -> 'completed'
7. Use curl_backend and check_database_status tools to validate

Test requirements:
- Test crawl initiation (POST /api/knowledge/crawl)
- Test crawl progress tracking
- Test crawl completion status update
- Test metadata.crawl_status value in database
- Test that source shows 'active' status in API response
- Use pytest with async support
- Real HTTP calls to running backend (localhost:8181)
- Real database queries to verify persistence

Follow pytest best practices and make tests reproducible.
Use the investigation report from the investigator agent to guide your tests.
""",
                model="claude-sonnet-4-5-20250929",
                tools=[
                    "Read",
                    "Write",
                    "Edit",
                    "MultiEdit",
                    "Grep",
                    "Glob",
                    "Bash",
                    "TodoWrite",
                    "mcp__investigation_tools__curl_backend",
                    "mcp__investigation_tools__check_database_status",
                    "mcp__investigation_tools__restart_backend",
                ],
            ),
        },
    )

    async with ClaudeSDKClient(options=options) as client:

        # Step 1: Run investigator agent
        print_agent_message(
            "Control Flow",
            "Step 1: Launching Investigator Agent\nTask: Analyze crawl status update flow",
            "bold blue",
        )

        await client.query(
            """Use the Task tool to launch the 'investigator' agent with this task:

Investigate why metadata.crawl_status doesn't update to 'completed' after crawling finishes.

Steps:
1. Read src/server/services/crawling/crawling_service.py - find where status should be updated
2. Read src/server/services/source_management_service.py - check update_source_info function
3. Use Grep to find all files that set crawl_status
4. Trigger a test crawl using curl: POST /api/knowledge/crawl with {"url": "https://go.dev/doc", "knowledge_type": "technical"}
5. Wait 30 seconds for crawl to complete
6. Check database status with check_database_status tool
7. Identify the root cause - why isn't the status updating?
8. Create detailed report at /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md

The report should include:
- Code flow diagram
- Where the bug is
- Why the update isn't happening
- Recommended fix
"""
        )

        async for message in client.receive_response():
            # Process investigator messages
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        print_agent_message("Investigator", block.text, "bold cyan")

        # Step 2: Run test writer agent
        print_agent_message(
            "Control Flow",
            "Step 2: Launching Test Writer Agent\nTask: Create integration tests",
            "bold blue",
        )

        await client.query(
            """Use the Task tool to launch the 'test_writer' agent with this task:

Create comprehensive integration tests for the crawl status flow.

Requirements:
1. Read the investigation report at /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md
2. Create tests at /home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py
3. Tests must:
   - Actually crawl https://go.dev/doc (no mocking!)
   - Use SQLite database from .env
   - Verify crawl_status transitions: pending -> completed
   - Check API response has status='active' for completed crawls
   - Query database directly to verify metadata.crawl_status
   - Use curl_backend tool to make real HTTP calls
   - Use check_database_status tool to verify database state
   - Clean up test data after each test

4. Create at least these test cases:
   - test_crawl_initiation_sets_pending_status
   - test_crawl_completion_updates_status_to_completed
   - test_completed_crawl_shows_active_in_api
   - test_source_metadata_persists_to_database

5. Include setup/teardown that:
   - Starts with clean database state
   - Creates unique test sources
   - Cleans up after tests complete

6. Add a README explaining how to run the tests
7. Run the tests and fix any failures
"""
        )

        async for message in client.receive_response():
            # Process test writer messages
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "text"):
                        print_agent_message("Test Writer", block.text, "bold green")

        print_agent_message(
            "System",
            "Investigation Complete!\n\n"
            "Check the following files:\n"
            "- /home/jose/src/Archon/CRAWL_STATUS_INVESTIGATION.md\n"
            "- /home/jose/src/Archon/python/tests/integration/test_crawl_status_integration.py\n\n"
            "Run tests with:\n"
            "cd /home/jose/src/Archon/python && uv run pytest tests/integration/test_crawl_status_integration.py -v",
            "bold yellow",
        )


if __name__ == "__main__":
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.run(main())
