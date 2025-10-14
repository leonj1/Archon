"""
Vector DB Pipeline Builder - Single Orchestrated Workflow

This script creates a complete web crawling and vector database pipeline using
Claude Code Agent SDK with inter-agent communication and feedback loops.

The orchestrator coordinates 5 specialized agents in a workflow where each agent
can review and provide feedback on previous work.

Usage:
    python build_vectordb_pipeline.py --model sonnet
"""

import asyncio
import nest_asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ThinkingBlock,
    SystemMessage,
    UserMessage,
    ToolResultBlock,
    ResultMessage,
)
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
import argparse

load_dotenv()
nest_asyncio.apply()


def create_pipeline_options(model: str = "sonnet") -> ClaudeAgentOptions:
    """
    Configure the orchestrator and specialized agents.

    The main agent coordinates the workflow and can delegate to specialized agents.
    Each agent can review previous work and provide feedback.
    """

    # Core tools for file operations and coordination
    core_tools = [
        'Read',
        'Write',
        'Edit',
        'MultiEdit',
        'Grep',
        'Glob',
        'Task',  # REQUIRED for delegating to subagents
        'TodoWrite',
        'Bash',
    ]

    return ClaudeAgentOptions(
        model=model,
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=core_tools,
        agents={
            # Agent 1: Crawling Service Builder
            "crawling-service": AgentDefinition(
                description="Creates SimpleCrawlingService by analyzing existing crawling code patterns",
                prompt="""You are an expert Python developer creating a simplified web crawling service.

TASK: Create SimpleCrawlingService in python/src/server/services/simple_crawling_service.py

REQUIREMENTS:
1. Analyze existing patterns in python/src/server/services/crawling/crawling_service.py
2. Create a SIMPLIFIED async service with this API:
   ```python
   async def crawl(url: str, max_depth: int = 1) -> List[Dict[str, str]]
   ```
3. Each document dict should have: url, content, title
4. Support single pages, recursive crawling, and sitemaps
5. Reuse existing helpers where possible
6. Add proper error handling, logging (logfire), and type hints
7. Keep under 300 lines

IMPORTANT:
- Use existing code patterns - don't reinvent the wheel
- Follow repository pattern from the codebase
- Add comprehensive docstrings with usage examples

After creating the service, provide a summary of:
- What patterns you reused
- Key features implemented
- Any concerns or limitations
- Suggestions for the next agent (vectordb service)

You have: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite']
            ),

            # Agent 2: VectorDB Service Builder
            "vectordb-service": AgentDefinition(
                description="Creates SimpleVectorDBService for Qdrant vector storage with embeddings",
                prompt="""You are an expert Python developer creating a vector database storage service.

TASK: Create SimpleVectorDBService in python/src/server/services/simple_vectordb_service.py

REQUIREMENTS:
1. Review the SimpleCrawlingService created by the previous agent
2. Analyze existing patterns:
   - python/src/server/services/storage/qdrant_vector_service.py
   - python/src/server/services/storage/document_storage_service.py
   - python/src/server/services/embeddings/embedding_service.py
3. Create a service with this API:
   ```python
   async def store_documents(
       documents: List[Dict[str, str]],
       source_id: str,
       chunk_size: int = 5000
   ) -> Dict[str, int]
   ```
4. Chunk documents using smart_chunk_text_async pattern
5. Generate embeddings via OpenAI (reuse create_embeddings_batch)
6. Store in Qdrant (reuse QdrantVectorService)
7. Return: {"chunks_stored": int, "source_id": str}
8. Keep under 250 lines

CRITICAL FEEDBACK:
- Review the crawling service output format
- Ensure your input format matches crawling service output
- If there's a mismatch, explain it clearly and suggest fixes
- Add proper error handling for missing/malformed documents

After creating the service, provide:
- How it integrates with the crawling service
- Any concerns about data format compatibility
- Performance considerations
- Suggestions for the wrapper service

You have: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite']
            ),

            # Agent 3: Wrapper Service Builder
            "wrapper-service": AgentDefinition(
                description="Creates unified CrawlAndStoreService wrapper combining both services",
                prompt="""You are an expert Python developer creating a unified service wrapper.

TASK: Create CrawlAndStoreService in python/src/server/services/crawl_and_store_service.py

REQUIREMENTS:
1. **REVIEW PREVIOUS WORK:**
   - Read SimpleCrawlingService code
   - Read SimpleVectorDBService code
   - Check for any compatibility issues between them
   - Verify data format matches (crawl output → vectordb input)

2. Create a unified service with this API:
   ```python
   async def crawl_and_store(
       url: str,
       source_id: str | None = None,
       chunk_size: int = 5000,
       max_depth: int = 1
   ) -> Dict[str, Any]
   ```

3. Return format:
   ```python
   {
       "success": bool,
       "crawl": {"documents": [...], "total_pages": int},
       "storage": {"chunks_stored": int, "source_id": str},
       "error": str | None  # if failed
   }
   ```

4. Key features:
   - Initialize both services via dependency injection
   - Call crawling service first
   - If successful, pass results to vectordb service
   - Handle errors gracefully (don't store if crawl fails)
   - Add progress logging at each stage

5. Keep under 200 lines

CRITICAL REVIEW:
- **If you find data format mismatches, STOP and explain them**
- **Suggest fixes to previous services if needed**
- **Don't add hacky workarounds - proper integration is key**

After creating the service, provide:
- Integration assessment (does it work smoothly?)
- Any issues discovered with previous services
- Recommendations for fixes
- Suggestions for integration testing

You have: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite']
            ),

            # Agent 4: Integration Test Builder
            "integration-test": AgentDefinition(
                description="Creates comprehensive integration test with REAL external calls",
                prompt="""You are an expert test engineer creating integration tests.

TASK: Create test_crawl_and_store_real.py in python/tests/integration/

REQUIREMENTS:
1. **REVIEW ALL PREVIOUS WORK:**
   - Read all three service files
   - Check for any obvious bugs or issues
   - Verify APIs are consistent
   - Note any concerns for testing

2. Create a REAL integration test (NO MOCKS):
   ```python
   @pytest.mark.asyncio
   @pytest.mark.integration
   async def test_real_crawl_and_store():
       # Test with real URL: https://github.com/The-Pocket/PocketFlow
       # Real OpenAI API calls
       # Real Qdrant storage
       # Proper cleanup
   ```

3. Test structure:
   - Setup: Skip if OPENAI_API_KEY missing
   - Act: Call crawl_and_store with real URL
   - Assert: Verify all expected behaviors
   - Cleanup: Delete test data from Qdrant

4. Assertions:
   - result["success"] is True
   - Documents were crawled (count > 0)
   - Content is non-empty
   - Chunks were stored (count > 0)
   - Source ID was created
   - Vectors exist in Qdrant

5. Keep under 150 lines

CRITICAL TESTING:
- **If you discover bugs in the services while writing tests, STOP and report them**
- **Explain what the bug is and which service has it**
- **Suggest the fix before completing the test**

After creating the test, provide:
- Any bugs or issues found in the services
- Recommendations for fixes
- Test coverage assessment
- Suggestions for additional tests

You have: Read, Write, Edit, Grep, Glob, TodoWrite, Bash tools.
""",
                model=model,
                tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite', 'Bash']
            ),

            # Agent 5: Test Runner & Validator
            "test-validator": AgentDefinition(
                description="Runs integration test and validates entire pipeline quality",
                prompt="""You are an expert test engineer validating the complete pipeline.

TASK: Run the integration test and validate the entire pipeline

WORKFLOW:
1. **READ ALL CODE:**
   - SimpleCrawlingService
   - SimpleVectorDBService
   - CrawlAndStoreService
   - test_crawl_and_store_real.py

2. **CODE REVIEW:**
   - Check for bugs, bad patterns, missing error handling
   - Verify proper async/await usage
   - Check type hints and docstrings
   - Look for potential issues

3. **RUN THE TEST:**
   ```bash
   cd python && uv run pytest tests/integration/test_crawl_and_store_real.py -v -s
   ```

4. **ANALYZE RESULTS:**
   - If test PASSES: Great! Proceed to validation report
   - If test FAILS: Analyze why, identify the bug, suggest fixes

5. **CREATE VALIDATION REPORT:**
   - File: python/tests/integration/VALIDATION_REPORT.md
   - Include:
     - Test execution results
     - Code quality assessment
     - Bugs found (if any)
     - Recommendations for improvement
     - Confirmation that NO MOCKS are used

CRITICAL VALIDATION:
- **Be honest about failures - don't hide issues**
- **If test fails, explain exactly what's broken**
- **Suggest specific fixes with code examples**
- **Rate the overall quality (1-10)**

After validation, provide:
- Executive summary (pass/fail)
- Critical issues found (if any)
- Overall quality score
- Go/no-go recommendation for production

You have: Read, Write, Edit, Grep, Glob, TodoWrite, Bash tools.
""",
                model=model,
                tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'TodoWrite', 'Bash']
            ),
        }
    )


async def main():
    parser = argparse.ArgumentParser(description="Vector DB Pipeline Builder with Agent Feedback")
    parser.add_argument(
        "--model",
        choices=["opus", "sonnet", "haiku"],
        default="sonnet",
        help="Claude model to use (default: sonnet)"
    )
    args = parser.parse_args()

    console = Console()

    # Welcome banner
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Vector DB Pipeline Builder[/bold cyan]\n"
        "[dim]Building with inter-agent communication and feedback[/dim]\n\n"
        f"Model: [yellow]{args.model}[/yellow]\n"
        "Agents: [green]5[/green] (with feedback loops)",
        border_style="cyan"
    ))
    console.print("\n")

    # Configure agents
    options = create_pipeline_options(model=args.model)

    # The orchestration prompt that coordinates everything
    orchestration_prompt = """
I need you to build a complete web crawling and vector database pipeline by coordinating with specialized agents.

WORKFLOW:
1. Delegate to 'crawling-service' agent to create SimpleCrawlingService
2. Review their work, provide feedback if needed
3. Delegate to 'vectordb-service' agent to create SimpleVectorDBService
   - They should review the crawling service and flag any compatibility issues
4. Review their work and integration concerns
5. Delegate to 'wrapper-service' agent to create CrawlAndStoreService
   - They should review both previous services and identify any issues
   - If they find problems, coordinate fixes
6. Delegate to 'integration-test' agent to create the test
   - They should review all services and report bugs if found
7. Delegate to 'test-validator' agent to run and validate everything
   - They provide final quality assessment

IMPORTANT COORDINATION RULES:
- After each agent completes, REVIEW their output and feedback
- If an agent flags issues, address them before proceeding
- Use TodoWrite to track the pipeline progress
- Keep me updated on progress at each stage
- If bugs are found, coordinate fixes between agents

Your job is to be the project manager - coordinate, review, and ensure quality.
Let's build this pipeline step by step with proper feedback loops!
"""

    try:
        async with ClaudeSDKClient(options=options) as client:
            console.print("[cyan]Starting pipeline build...[/cyan]\n")

            # Send the orchestration prompt
            await client.query(orchestration_prompt)

            # Stream responses and provide real-time feedback
            message_count = 0
            async for message in client.receive_response():
                message_count += 1

                # Handle different message types using isinstance
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Assistant text output
                            console.print(f"[green]{block.text}[/green]")
                        elif isinstance(block, ToolUseBlock):
                            # Tool usage
                            if block.name == "Task":
                                # Agent delegation
                                agent_name = block.input.get("subagent_type", "unknown")
                                console.print(f"\n[bold yellow]→ Delegating to agent:[/bold yellow] [cyan]{agent_name}[/cyan]")
                            else:
                                console.print(f"[blue]🔧 Using tool:[/blue] {block.name}")
                        elif isinstance(block, ThinkingBlock):
                            console.print("[dim]💭 Thinking...[/dim]")

                elif isinstance(message, UserMessage):
                    for block in message.content:
                        if isinstance(block, ToolResultBlock):
                            # Tool result
                            console.print("[dim]✓ Tool completed[/dim]")

                elif isinstance(message, SystemMessage):
                    # System messages (compaction, etc.)
                    console.print(f"[dim]ℹ️  System: {message.subtype}[/dim]")

                elif isinstance(message, ResultMessage):
                    # Session result
                    console.print(f"[dim]Session completed: {message.subtype}[/dim]")

            console.print("\n")
            console.print(Panel.fit(
                "[bold green]✓ Pipeline build completed![/bold green]\n\n"
                "Check the generated files:\n"
                "  • python/src/server/services/simple_crawling_service.py\n"
                "  • python/src/server/services/simple_vectordb_service.py\n"
                "  • python/src/server/services/crawl_and_store_service.py\n"
                "  • python/tests/integration/test_crawl_and_store_real.py\n"
                "  • python/tests/integration/VALIDATION_REPORT.md",
                border_style="green"
            ))

    except KeyboardInterrupt:
        console.print("\n[yellow]Build interrupted by user[/yellow]")
        return
    except Exception as e:
        console.print(f"\n[red]Error during build:[/red] {str(e)}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise


if __name__ == "__main__":
    asyncio.run(main())
