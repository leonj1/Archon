#!/usr/bin/env python3
"""
Agent Team Script to Fix Recrawl Status Bug

Bug Description:
When there is an existing knowledge base, a user invokes recrawl, waits for the crawl
to finish successfully, and the knowledge base status reads 'completed' instead of 'pending'
in the frontend. The problem is the status shows 'pending' after a successful crawl.

Team Architecture:
- Investigator Agent: Analyzes the bug and data flow
- Backend Agent: Examines backend status update logic
- Frontend Agent: Examines frontend status display logic
- Integration Test Agent: Creates and runs integration tests
- Orchestrator Agent: Coordinates fixes and validates solutions
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, ClaudeSDKClient
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv()

console = Console()

# Ensure we're in the project root
PROJECT_ROOT = Path(__file__).parent.absolute()
os.chdir(PROJECT_ROOT)


def log_section(title: str, message: str = ""):
    """Log a section header."""
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n{message}", expand=False))


def log_info(message: str):
    """Log an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str):
    """Log a success message."""
    console.print(f"[green]✓[/green] {message}")


def log_error(message: str):
    """Log an error message."""
    console.print(f"[red]✗[/red] {message}")


def restart_services():
    """Restart archon services to pick up code changes."""
    log_info("Restarting services with 'make restart'...")
    try:
        result = subprocess.run(
            ["make", "restart"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            log_success("Services restarted successfully")
            # Wait for services to be ready
            time.sleep(10)
            return True
        else:
            log_error(f"Failed to restart services: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log_error("Service restart timed out")
        return False
    except Exception as e:
        log_error(f"Error restarting services: {e}")
        return False


def run_all_tests():
    """Run 'make test' to validate all tests pass."""
    log_info("Running 'make test' to validate all tests...")
    try:
        result = subprocess.run(
            ["make", "test"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            log_success("All tests passed!")
            console.print(result.stdout)
            return True
        else:
            log_error("Some tests failed:")
            console.print(result.stdout)
            console.print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        log_error("Tests timed out after 10 minutes")
        return False
    except Exception as e:
        log_error(f"Error running tests: {e}")
        return False


async def main():
    """Main orchestration function."""
    log_section(
        "🤖 Recrawl Status Bug Fix - Agent Team",
        "Deploying specialized agents to fix the recrawl status bug"
    )

    # Define agent team
    options = ClaudeAgentOptions(
        model="sonnet",
        permission_mode="acceptEdits",
        setting_sources=["project"],
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
        ],
        agents={
            "investigator": AgentDefinition(
                description="Investigates the recrawl status bug by analyzing data flow from backend to frontend. Identifies where status gets lost or incorrectly set.",
                prompt="""You are a bug investigation specialist. Your task is to investigate why the recrawl status shows 'pending' instead of 'completed' after a successful recrawl.

Investigation Steps:
1. Examine the backend recrawl endpoint: python/src/server/api_routes/knowledge_api.py
   - Look at the refresh_knowledge_item function
   - Trace where crawl_status gets updated

2. Examine the crawling service: python/src/server/services/crawling/crawling_service.py
   - Look for where crawl_status is updated to "completed"
   - Verify the update_source_info call

3. Examine the frontend components:
   - archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx
   - archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx
   - See how status is mapped from backend data

4. Check the knowledge service: archon-ui-main/src/features/knowledge/services/knowledgeService.ts
   - Identify which endpoint is being called
   - Verify data transformation

5. Create a detailed report in INVESTIGATION_REPORT.md with:
   - Data flow diagram (backend → frontend)
   - Where status gets set/updated
   - Where the disconnect happens
   - Root cause hypothesis

Use Read, Grep, and Glob tools to examine code. Write your findings to INVESTIGATION_REPORT.md.
Do NOT make any code changes yet.""",
                model="sonnet",
                tools=["Read", "Write", "Grep", "Glob", "TodoWrite"],
            ),
            "backend-fixer": AgentDefinition(
                description="Backend specialist that fixes backend status update issues based on investigation findings.",
                prompt="""You are a backend Python specialist. Your task is to fix backend status update issues.

CRITICAL RULES:
1. Read INVESTIGATION_REPORT.md first to understand the root cause
2. Only fix issues identified in the report
3. Follow beta development guidelines - fail fast and loud
4. Update source crawl_status correctly after recrawl completion
5. Ensure metadata.crawl_status is preserved and updated properly

Common Issues to Check:
- Is crawl_status being updated in the source table?
- Is metadata being merged correctly (preserving existing data)?
- Are there any errors during status update that are silently caught?

After making changes:
- Document what you changed and why in BACKEND_CHANGES.md
- Do NOT restart services (orchestrator will do that)""",
                model="sonnet",
                tools=["Read", "Write", "Edit", "MultiEdit", "Grep", "Glob", "TodoWrite"],
            ),
            "frontend-fixer": AgentDefinition(
                description="Frontend specialist that fixes frontend status display issues based on investigation findings.",
                prompt="""You are a frontend TypeScript/React specialist. Your task is to fix frontend status display issues.

CRITICAL RULES:
1. Read INVESTIGATION_REPORT.md first to understand the root cause
2. Only fix issues identified in the report
3. Check the knowledge service endpoint being used
4. Verify status mapping in components
5. Ensure the correct status field is being read from API response

Common Issues to Check:
- Is the frontend calling the right endpoint (/api/knowledge-items/summary vs /api/knowledge-items)?
- Is the status field being correctly extracted from the response?
- Is item.status vs metadata.crawl_status being handled correctly?
- Are there any caching issues preventing fresh data?

After making changes:
- Document what you changed and why in FRONTEND_CHANGES.md
- Do NOT restart services (orchestrator will do that)""",
                model="sonnet",
                tools=["Read", "Write", "Edit", "MultiEdit", "Grep", "Glob", "TodoWrite"],
            ),
            "integration-tester": AgentDefinition(
                description="Creates and runs integration tests for the recrawl status bug. Uses real services, no mocks. Tests actual crawl behavior.",
                prompt="""You are an integration testing specialist. Your task is to create a comprehensive integration test for the recrawl status bug.

CRITICAL REQUIREMENTS:
1. Create integration test in python/tests/integration/test_recrawl_status.py
2. Use REAL services - NO MOCKS
3. Use environment variables from .env file
4. Test the ACTUAL recrawl flow:
   a. Create a new knowledge item by crawling a URL
   b. Wait for crawl to complete (poll /api/crawl-progress/{progress_id})
   c. Verify status is "completed" and crawl_status is "completed"
   d. Trigger a recrawl using /api/knowledge-items/{source_id}/refresh
   e. Wait for recrawl to complete (poll again)
   f. Verify status is STILL "completed" (not "pending")
   g. Verify crawl_status in metadata is "completed"

Test Structure:
```python
import asyncio
import os
import pytest
import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ARCHON_API_URL", "http://localhost:8181")
TEST_URL = "https://example.com"  # Simple, fast URL for testing

@pytest.mark.asyncio
async def test_recrawl_status_remains_completed():
    '''Test that status stays "completed" after successful recrawl.'''
    async with httpx.AsyncClient(timeout=600.0) as client:
        # 1. Start initial crawl
        # 2. Poll until completed
        # 3. Verify status
        # 4. Trigger recrawl
        # 5. Poll until completed
        # 6. Verify status is STILL completed (not pending)
        pass
```

IMPORTANT:
- Use httpx.AsyncClient for HTTP requests
- Use polling with timeout to wait for crawl completion
- Check BOTH item.status and metadata.crawl_status
- Test should take 5-15 minutes to run (real crawl time)
- Use pytest and async/await
- Clean up test data at the end

After creating the test:
- Document test strategy in INTEGRATION_TEST.md
- DO NOT run the test yet (orchestrator will do that)
""",
                model="sonnet",
                tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash", "TodoWrite"],
            ),
        },
    )

    log_section("Phase 1: Investigation", "Analyzing the bug and identifying root cause...")

    async with ClaudeSDKClient(options=options) as client:
        # Phase 1: Investigation
        await client.query(
            """Delegate to the 'investigator' agent to analyze the recrawl status bug.

The investigator should:
1. Examine backend code (API routes, services)
2. Examine frontend code (components, services)
3. Trace the data flow from recrawl trigger to status display
4. Identify the root cause
5. Create INVESTIGATION_REPORT.md with findings

This is a research task - no code changes yet!"""
        )

        async for message in client.receive_response():
            # Just let it complete - output is displayed automatically
            pass

        log_success("Investigation phase complete - check INVESTIGATION_REPORT.md")

        # Check if investigation report was created
        if not Path("INVESTIGATION_REPORT.md").exists():
            log_error("Investigation report not found! Cannot proceed.")
            return False

        # Phase 2: Create Integration Test
        log_section(
            "Phase 2: Integration Test Creation",
            "Creating integration test to reproduce and validate the bug fix..."
        )

        await client.query(
            """Delegate to the 'integration-tester' agent to create a comprehensive integration test.

The tester should:
1. Read INVESTIGATION_REPORT.md to understand the bug
2. Create python/tests/integration/test_recrawl_status.py
3. Test the complete recrawl flow with REAL services
4. Document the test strategy in INTEGRATION_TEST.md

NO MOCKS! Use real API endpoints and wait for actual crawl completion."""
        )

        async for message in client.receive_response():
            pass

        log_success("Integration test created")

        # Phase 3: Fix Backend Issues
        log_section("Phase 3: Backend Fixes", "Fixing backend status update issues...")

        await client.query(
            """Delegate to the 'backend-fixer' agent to fix backend issues.

The fixer should:
1. Read INVESTIGATION_REPORT.md
2. Fix status update issues in backend code
3. Ensure crawl_status is correctly set to "completed" after recrawl
4. Document changes in BACKEND_CHANGES.md"""
        )

        async for message in client.receive_response():
            pass

        log_success("Backend fixes applied")

        # Phase 4: Fix Frontend Issues
        log_section("Phase 4: Frontend Fixes", "Fixing frontend status display issues...")

        await client.query(
            """Delegate to the 'frontend-fixer' agent to fix frontend issues.

The fixer should:
1. Read INVESTIGATION_REPORT.md
2. Fix status display issues in frontend code
3. Ensure correct API endpoint and status field are used
4. Document changes in FRONTEND_CHANGES.md"""
        )

        async for message in client.receive_response():
            pass

        log_success("Frontend fixes applied")

        # Phase 5: Restart and Test
        log_section(
            "Phase 5: Integration Testing",
            "Restarting services and running integration test..."
        )

        if not restart_services():
            log_error("Failed to restart services")
            return False

        # Run integration test
        log_info("Running integration test (this may take 5-15 minutes)...")
        test_file = "python/tests/integration/test_recrawl_status.py"

        try:
            result = subprocess.run(
                ["pytest", test_file, "-v", "-s"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=1200,  # 20 minute timeout
            )

            console.print(result.stdout)
            console.print(result.stderr)

            if result.returncode == 0:
                log_success("Integration test passed!")
            else:
                log_error("Integration test failed - need to iterate")

                # Ask user if they want to retry
                console.print("\n[yellow]Integration test failed. Options:[/yellow]")
                console.print("1. Review logs and retry with agent fixes")
                console.print("2. Exit and fix manually")

                # For now, we'll iterate once more
                log_section(
                    "Phase 6: Iteration",
                    "Re-analyzing failures and applying additional fixes..."
                )

                await client.query(
                    f"""The integration test failed. Please analyze the failure and coordinate fixes.

Test output:
{result.stdout}
{result.stderr}

Delegate to backend-fixer and frontend-fixer as needed to address the failures.
Then we'll restart and test again."""
                )

                async for message in client.receive_response():
                    pass

                # Restart and test again
                if not restart_services():
                    return False

                result = subprocess.run(
                    ["pytest", test_file, "-v", "-s"],
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=1200,
                )

                console.print(result.stdout)
                console.print(result.stderr)

                if result.returncode != 0:
                    log_error("Integration test failed again")
                    return False

                log_success("Integration test passed after iteration!")

        except subprocess.TimeoutExpired:
            log_error("Integration test timed out")
            return False

        # Phase 6: Run Full Test Suite
        log_section(
            "Phase 6: Full Test Suite",
            "Running 'make test' to ensure no regressions..."
        )

        if not run_all_tests():
            log_error("Some tests failed - there may be regressions")
            return False

        # Success!
        log_section(
            "🎉 Success!",
            "All tests passed! The recrawl status bug has been fixed."
        )

        # Summary
        console.print("\n[bold green]Summary of Changes:[/bold green]")

        if Path("BACKEND_CHANGES.md").exists():
            with open("BACKEND_CHANGES.md") as f:
                console.print(Panel(f.read(), title="Backend Changes", expand=False))

        if Path("FRONTEND_CHANGES.md").exists():
            with open("FRONTEND_CHANGES.md") as f:
                console.print(Panel(f.read(), title="Frontend Changes", expand=False))

        return True


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
