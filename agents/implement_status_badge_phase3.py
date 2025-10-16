"""
Status Badge Implementation Agent - Phase 3
Automates frontend component creation and integration

This agent implements Phase 3 of the STATUS_BADGE_IMPLEMENTATION.md:
- Creates KnowledgeCardStatus.tsx component
- Imports component in KnowledgeCard.tsx
- Adds status badge to card header
- Runs Biome formatter
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
            "Write",
            "Bash",
        ],
        disallowed_tools=["WebSearch", "WebFetch", "Task"]
    )

    console.print(Panel.fit(
        "[bold cyan]Status Badge Implementation Agent - Phase 3[/bold cyan]\n\n"
        "This agent will:\n"
        "1. Create KnowledgeCardStatus.tsx component\n"
        "2. Import component in KnowledgeCard.tsx\n"
        "3. Add status badge to card header\n"
        "4. Run Biome formatter on changes\n\n"
        "[yellow]Model: sonnet[/yellow]",
        border_style="cyan"
    ))

    # Define the implementation prompt
    implementation_prompt = """
You are implementing Phase 3 of the Status Badge Implementation from @STATUS_BADGE_IMPLEMENTATION.md.

CRITICAL INSTRUCTIONS:

STEP 1: Create KnowledgeCardStatus.tsx component
- File path: /home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx
- Use the Write tool to create this NEW file
- Copy the EXACT code from the checklist (lines 82-154 of STATUS_BADGE_IMPLEMENTATION.md):

```typescript
/**
 * Knowledge Card Status Badge
 * Displays crawl status with appropriate icon and color
 */

import { CheckCircle, Clock, XCircle } from "lucide-react";
import { cn } from "../../ui/primitives/styles";
import { SimpleTooltip } from "../../ui/primitives/tooltip";

interface KnowledgeCardStatusProps {
  status: "active" | "processing" | "error";
  crawlStatus?: "pending" | "completed" | "failed";
  className?: string;
}

export const KnowledgeCardStatus: React.FC<KnowledgeCardStatusProps> = ({
  status,
  crawlStatus,
  className,
}) => {
  const getStatusConfig = () => {
    switch (status) {
      case "error":
        return {
          label: "Failed",
          icon: <XCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-red-100 dark:bg-red-500/10",
          textColor: "text-red-700 dark:text-red-400",
          borderColor: "border-red-200 dark:border-red-500/20",
          tooltip: "Crawl failed - click refresh to retry",
        };
      case "processing":
        return {
          label: "Pending",
          icon: <Clock className="w-3.5 h-3.5" />,
          bgColor: "bg-yellow-100 dark:bg-yellow-500/10",
          textColor: "text-yellow-700 dark:text-yellow-400",
          borderColor: "border-yellow-200 dark:border-yellow-500/20",
          tooltip: "Crawl not yet completed",
        };
      case "active":
      default:
        return {
          label: "Completed",
          icon: <CheckCircle className="w-3.5 h-3.5" />,
          bgColor: "bg-green-100 dark:bg-green-500/10",
          textColor: "text-green-700 dark:text-green-400",
          borderColor: "border-green-200 dark:border-green-500/20",
          tooltip: "Successfully crawled and indexed",
        };
    }
  };

  const config = getStatusConfig();

  return (
    <SimpleTooltip content={config.tooltip}>
      <div
        className={cn(
          "inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium border",
          config.bgColor,
          config.textColor,
          config.borderColor,
          className,
        )}
      >
        {config.icon}
        <span>{config.label}</span>
      </div>
    </SimpleTooltip>
  );
};
```

STEP 2: Import the component in KnowledgeCard.tsx
- Read /home/jose/src/Archon/archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx
- Find the import section at the top (around line 25)
- Add the import AFTER line 25 using Edit tool:
  ```typescript
  import { KnowledgeCardStatus } from "./KnowledgeCardStatus";
  ```

STEP 3: Add status badge to card header
- In the same KnowledgeCard.tsx file
- Find the section with `<div className="flex items-center gap-2">` (around line 137)
- This is where KnowledgeCardType is rendered
- Update the div to include flex-wrap and add the KnowledgeCardStatus component
- The section should look like this after editing:

```typescript
<div className="flex items-center gap-2 flex-wrap">
  <SimpleTooltip content={isUrl ? "Content from a web page" : "Uploaded document"}>
    <div className={...}>
      {getSourceIcon()}
      <span>{isUrl ? "Web Page" : "Document"}</span>
    </div>
  </SimpleTooltip>
  <KnowledgeCardType sourceId={item.source_id} knowledgeType={item.knowledge_type} />
  <KnowledgeCardStatus
    status={item.status}
    crawlStatus={item.metadata?.crawl_status}
  />
</div>
```

STEP 4: Format with Biome
- Change to frontend directory: cd archon-ui-main
- Run Biome formatter: npm run biome:fix
- Return to root: cd ..

IMPORTANT:
- Use Write tool for creating NEW file (Step 1)
- Use Edit tool for modifying EXISTING files (Steps 2 & 3)
- Preserve all existing code structure
- Match indentation exactly (2 spaces)
- Don't modify unrelated code

Start by creating the KnowledgeCardStatus.tsx component.
"""

    async with ClaudeSDKClient(options=options) as client:
        console.print("\n[bold yellow]Starting implementation...[/bold yellow]\n")

        await client.query(implementation_prompt)

        # Receive and display responses
        async for message in client.receive_response():
            from cli_tools import parse_and_print_message
            parse_and_print_message(message, console, print_stats=True)

    console.print("\n[bold green]✓ Phase 3 implementation completed![/bold green]\n")
    console.print(Panel(
        "[cyan]Next steps:[/cyan]\n\n"
        "1. Verify component was created:\n"
        "   ls -la archon-ui-main/src/features/knowledge/components/KnowledgeCardStatus.tsx\n\n"
        "2. Check import was added:\n"
        "   grep 'KnowledgeCardStatus' archon-ui-main/src/features/knowledge/components/KnowledgeCard.tsx\n\n"
        "3. Verify no Biome errors\n\n"
        "4. Proceed to Phase 4: Testing\n"
        "   Run: uv run python agents/implement_status_badge_phase4.py",
        title="Implementation Complete",
        border_style="green"
    ))


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
