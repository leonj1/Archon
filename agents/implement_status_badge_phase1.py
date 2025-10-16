"""
Status Badge Implementation Agent - Phase 1
Automates backend API mapping for status badge feature

This agent implements Phase 1 of the STATUS_BADGE_IMPLEMENTATION.md:
- Updates knowledge_item_service.py with crawl_status to status mapping
- Restarts backend and verifies health
"""

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def main():
    console = Console()

    # Configure the agent with necessary tools
    options = ClaudeAgentOptions(
        model="sonnet",
        allowed_tools=[
            "Read",
            "Edit",
            "Bash",
            "Grep",
        ],
        # Disable tools we don't need for this task
        disallowed_tools=["WebSearch", "WebFetch", "Task"]
    )

    console.print(Panel.fit(
        "[bold cyan]Status Badge Implementation Agent - Phase 1[/bold cyan]\n\n"
        "This agent will:\n"
        "1. Update knowledge_item_service.py - list_items method\n"
        "2. Update knowledge_item_service.py - _transform_source_to_item method\n"
        "3. Restart backend and verify health\n\n"
        "[yellow]Model: sonnet[/yellow]",
        border_style="cyan"
    ))

    # Define the implementation prompt
    implementation_prompt = """
You are implementing Phase 1 of the Status Badge Implementation from @STATUS_BADGE_IMPLEMENTATION.md.

CRITICAL INSTRUCTIONS:
1. Read /home/jose/src/Archon/python/src/server/services/knowledge/knowledge_item_service.py
2. Update the `list_items` method (around lines 129-146):
   - Find where it sets "status": "active" in the metadata
   - Replace with this mapping logic:
   ```python
   # Map crawl_status to frontend-expected status
   crawl_status = source_metadata.get("crawl_status", "pending")
   frontend_status = {
       "completed": "active",    # Successful crawl = active
       "failed": "error",        # Failed crawl = error
       "pending": "processing"   # Pending/in-progress = processing
   }.get(crawl_status, "processing")
   ```
   - Update the metadata dictionary to include both status and crawl_status:
   ```python
   "metadata": {
       **source_metadata,
       "status": frontend_status,
       "crawl_status": crawl_status,  # Keep original for reference
       # ... rest of fields
   }
   ```

3. Update the `_transform_source_to_item` method (around lines 219-241):
   - Find where it sets "status": "active" in the metadata
   - Apply the EXACT SAME mapping logic as in step 2

4. After making changes:
   - Run: docker compose restart archon-server
   - Wait 15 seconds for restart
   - Verify health: curl http://localhost:8181/api/health

IMPORTANT:
- Make precise edits using the Edit tool
- Use exact string matching from the file
- Preserve all indentation and formatting
- Only modify the "status": "active" lines to use the mapping logic
- Add the crawl_status field to metadata in both methods

Start by reading the file to locate the exact lines to modify.
"""

    async with ClaudeSDKClient(options=options) as client:
        console.print("\n[bold yellow]Starting implementation...[/bold yellow]\n")

        await client.query(implementation_prompt)

        # Receive and display responses
        async for message in client.receive_response():
            # Print all messages for visibility
            from cli_tools import parse_and_print_message
            parse_and_print_message(message, console, print_stats=True)

    console.print("\n[bold green]✓ Phase 1 implementation completed![/bold green]\n")
    console.print(Panel(
        "[cyan]Next steps:[/cyan]\n\n"
        "1. Verify backend changes:\n"
        "   curl http://localhost:8181/api/knowledge-items | jq '.items[0].metadata'\n\n"
        "2. Check that response includes both 'status' and 'crawl_status'\n\n"
        "3. Proceed to Phase 2: Frontend Types\n"
        "   Run: python agents/implement_status_badge_phase2.py",
        title="Implementation Complete",
        border_style="green"
    ))


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
