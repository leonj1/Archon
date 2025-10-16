"""
Status Badge Implementation Agent - Phase 2
Automates frontend TypeScript type definitions

This agent implements Phase 2 of the STATUS_BADGE_IMPLEMENTATION.md:
- Updates KnowledgeItemMetadata interface with crawl_status field
- Runs TypeScript compiler to verify no errors
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
        ],
        disallowed_tools=["WebSearch", "WebFetch", "Task"]
    )

    console.print(Panel.fit(
        "[bold cyan]Status Badge Implementation Agent - Phase 2[/bold cyan]\n\n"
        "This agent will:\n"
        "1. Update KnowledgeItemMetadata interface in knowledge.ts\n"
        "2. Add crawl_status field after status field\n"
        "3. Run TypeScript compiler to verify no errors\n\n"
        "[yellow]Model: sonnet[/yellow]",
        border_style="cyan"
    ))

    # Define the implementation prompt
    implementation_prompt = """
You are implementing Phase 2 of the Status Badge Implementation from @STATUS_BADGE_IMPLEMENTATION.md.

CRITICAL INSTRUCTIONS:
1. Read /home/jose/src/Archon/archon-ui-main/src/features/knowledge/types/knowledge.ts

2. Find the KnowledgeItemMetadata interface (around line 6-24)

3. Add the crawl_status field after the status field:
   ```typescript
   export interface KnowledgeItemMetadata {
     knowledge_type?: "technical" | "business";
     tags?: string[];
     source_type?: "url" | "file" | "group";
     status?: "active" | "processing" | "error";
     crawl_status?: "pending" | "completed" | "failed";  // NEW - Add this line
     description?: string;
     // ... rest of fields remain unchanged
   }
   ```

4. Make the edit using the Edit tool:
   - Find the exact string starting with `status?: "active" | "processing" | "error";`
   - Replace it with both the status line AND the new crawl_status line

5. After making the change:
   - Change to frontend directory: cd archon-ui-main
   - Run TypeScript compiler: npx tsc --noEmit
   - If errors appear, check they're not related to our change
   - Return to root: cd ..

IMPORTANT:
- Preserve exact indentation (2 spaces per level)
- Keep the optional ? operator on crawl_status
- Maintain alphabetical-ish ordering (after status makes sense)
- Don't modify any other fields

Start by reading the file to see the current interface structure.
"""

    async with ClaudeSDKClient(options=options) as client:
        console.print("\n[bold yellow]Starting implementation...[/bold yellow]\n")

        await client.query(implementation_prompt)

        # Receive and display responses
        async for message in client.receive_response():
            from cli_tools import parse_and_print_message
            parse_and_print_message(message, console, print_stats=True)

    console.print("\n[bold green]✓ Phase 2 implementation completed![/bold green]\n")
    console.print(Panel(
        "[cyan]Next steps:[/cyan]\n\n"
        "1. Verify TypeScript changes:\n"
        "   cat archon-ui-main/src/features/knowledge/types/knowledge.ts | grep -A 2 'crawl_status'\n\n"
        "2. Check TypeScript compilation passed with no new errors\n\n"
        "3. Proceed to Phase 3: Frontend Components\n"
        "   Run: uv run python agents/implement_status_badge_phase3.py",
        title="Implementation Complete",
        border_style="green"
    ))


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
