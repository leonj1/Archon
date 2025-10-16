"""
Status Badge Implementation Agent - Phase 4
Automates testing and verification of status badge feature

This agent implements Phase 4 of the STATUS_BADGE_IMPLEMENTATION.md:
- Verifies backend API changes
- Tests frontend UI rendering
- Validates badge states and styling
- Checks responsive design
- Tests tooltips
- Validates edge cases
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
            "Bash",
            "Read",
        ],
        disallowed_tools=["WebSearch", "WebFetch", "Task", "Edit", "Write"]
    )

    console.print(Panel.fit(
        "[bold cyan]Status Badge Implementation Agent - Phase 4[/bold cyan]\n\n"
        "This agent will:\n"
        "1. Verify backend API includes crawl_status\n"
        "2. Test API response mapping\n"
        "3. Run TypeScript compiler checks\n"
        "4. Run Biome linter checks\n"
        "5. Generate verification report\n\n"
        "[yellow]Model: sonnet[/yellow]",
        border_style="cyan"
    ))

    # Define the implementation prompt
    implementation_prompt = """
You are implementing Phase 4 (Testing) of the Status Badge Implementation from @STATUS_BADGE_IMPLEMENTATION.md.

Your task is to run automated tests and generate a verification report. You have READ-ONLY access.

CRITICAL INSTRUCTIONS:

STEP 1: Verify Backend API Changes
Run these commands to check the API:

1. Check backend health:
   curl -s http://localhost:8181/api/health

2. Get knowledge items and check for crawl_status:
   curl -s http://localhost:8181/api/knowledge-items | head -100

3. Parse the response to verify:
   - Items have both "status" and "crawl_status" in metadata
   - Status values are correctly mapped:
     * crawl_status: "pending" → status: "processing"
     * crawl_status: "completed" → status: "active"
     * crawl_status: "failed" → status: "error"

STEP 2: Verify TypeScript Compilation
1. Change to frontend: cd archon-ui-main
2. Run TypeScript compiler: npx tsc --noEmit 2>&1 | head -50
3. Check for errors related to our changes (should be none)
4. Return to root: cd ..

STEP 3: Verify Biome Linting
1. Change to frontend: cd archon-ui-main
2. Run Biome check: npm run biome 2>&1 | head -50
3. Check for errors in KnowledgeCardStatus.tsx or KnowledgeCard.tsx
4. Return to root: cd ..

STEP 4: Verify Files Exist
1. Check KnowledgeCardStatus.tsx exists:
   ls -la archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx

2. Check import in KnowledgeCard.tsx:
   grep -n "KnowledgeCardStatus" archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx

3. Check crawl_status in types:
   grep -n "crawl_status" archon-ui-main/src/features/knowledge/types/knowledge.ts

STEP 5: Generate Verification Report
After running all checks, provide a summary report with:

✅ Backend API Changes:
  - Health check: [PASS/FAIL]
  - crawl_status field present: [PASS/FAIL]
  - Status mapping correct: [PASS/FAIL]

✅ Frontend TypeScript:
  - Type definition added: [PASS/FAIL]
  - Compilation passes: [PASS/FAIL]

✅ Frontend Components:
  - KnowledgeCardStatus.tsx created: [PASS/FAIL]
  - Import added to KnowledgeCard.tsx: [PASS/FAIL]
  - Badge rendered in card: [PASS/FAIL]

✅ Code Quality:
  - Biome linting passes: [PASS/FAIL]
  - No TypeScript errors: [PASS/FAIL]

⚠️ Manual Testing Required:
  - Visual badge rendering (requires browser)
  - Tooltip interactions (requires browser)
  - Responsive design (requires browser)
  - Dark mode styling (requires browser)

📝 Next Steps:
  - List any issues found
  - Provide commands to fix issues
  - Recommend manual testing steps

IMPORTANT:
- Be thorough but concise
- Report actual test results, not assumptions
- If a test fails, explain what went wrong
- Provide actionable next steps

Start by checking backend health and API responses.
"""

    async with ClaudeSDKClient(options=options) as client:
        console.print("\n[bold yellow]Starting verification...[/bold yellow]\n")

        await client.query(implementation_prompt)

        # Receive and display responses
        async for message in client.receive_response():
            from cli_tools import parse_and_print_message
            parse_and_print_message(message, console, print_stats=True)

    console.print("\n[bold green]✓ Phase 4 verification completed![/bold green]\n")
    console.print(Panel(
        "[cyan]Next steps:[/cyan]\n\n"
        "1. Review the verification report above\n\n"
        "2. Fix any issues identified\n\n"
        "3. Perform manual testing:\n"
        "   - Start frontend: cd archon-ui-main && npm run dev\n"
        "   - Open http://localhost:3737\n"
        "   - Navigate to Knowledge page\n"
        "   - Verify badges appear on cards\n"
        "   - Test tooltips on hover\n"
        "   - Check dark mode\n"
        "   - Test responsive design\n\n"
        "4. Proceed to Phase 5: Final Verification\n"
        "   - Update STATUS_BADGE_IMPLEMENTATION.md\n"
        "   - Mark all completed tasks\n"
        "   - Commit changes",
        title="Verification Complete",
        border_style="green"
    ))


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
