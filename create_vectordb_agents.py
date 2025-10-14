"""
Claude Code Agents for Vector Database Pipeline

This script creates specialized agents to build a complete crawling and vector storage pipeline.

Agents:
1. crawling-service-builder: Creates a service class for web crawling
2. vectordb-service-builder: Creates a service class for Qdrant vector storage
3. wrapper-service-builder: Creates a unified service wrapping both services
4. integration-test-builder: Creates a real integration test (no mocks)
5. test-validator: Validates tests pass and use appropriate mocking

Usage:
    python create_vectordb_agents.py --model sonnet

Requirements:
    - ANTHROPIC_API_KEY in .env
    - OPENAI_API_KEY in .env (for integration tests)
"""

import asyncio
import nest_asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from rich.console import Console
from rich.prompt import Prompt
from dotenv import load_dotenv
import argparse

load_dotenv()
nest_asyncio.apply()


def create_agent_options(model: str = "sonnet") -> ClaudeAgentOptions:
    """
    Configure Claude Code agents with specialized tools and definitions.
    """

    # Core tools needed for all agents
    base_tools = [
        'Read',
        'Write',
        'Edit',
        'MultiEdit',
        'Grep',
        'Glob',
        'Task',  # Required for subagents
        'TodoWrite',
        'Bash',
    ]

    return ClaudeAgentOptions(
        model=model,
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=base_tools,
        agents={
            # Agent 1: Crawling Service Builder
            "crawling-service-builder": AgentDefinition(
                description="Expert at creating web crawling service classes by analyzing and adapting existing codebase patterns.",
                prompt="""You are an expert Python developer specializing in web crawling services.

Your task is to create a NEW service class `SimpleCrawlingService` in `python/src/server/services/simple_crawling_service.py`.

REQUIREMENTS:
1. Analyze the existing crawling logic in `python/src/server/services/crawling/crawling_service.py`
2. Create a SIMPLIFIED service that:
   - Accepts a URL as input
   - Crawls the URL and extracts content (markdown/text)
   - Returns a list of crawled documents with structure: [{"url": str, "content": str, "title": str}]
   - Handles single pages, recursive crawling, and sitemaps
   - Uses existing helpers from the crawling module where possible
3. Keep dependencies minimal - reuse existing code patterns
4. Add proper error handling and logging
5. Make it async and type-hinted
6. Add docstrings explaining the API

IMPORTANT PATTERNS TO FOLLOW:
- Import from existing crawling modules (crawling_service, helpers)
- Use the same Crawl4AI patterns if possible
- Follow the repository pattern (DatabaseRepository)
- Use logfire for logging: `from ...config.logfire_config import get_logger`

OUTPUT:
- Create the new file with a complete, working implementation
- Add a simple example in the docstring showing how to use it
- Keep it under 300 lines - focus on clarity and reusability

You have access to: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=[
                    'Read',
                    'Write',
                    'Edit',
                    'MultiEdit',
                    'Grep',
                    'Glob',
                    'TodoWrite',
                ]
            ),

            # Agent 2: VectorDB Service Builder
            "vectordb-service-builder": AgentDefinition(
                description="Expert at creating vector database service classes for Qdrant integration.",
                prompt="""You are an expert Python developer specializing in vector databases and embeddings.

Your task is to create a NEW service class `SimpleVectorDBService` in `python/src/server/services/simple_vectordb_service.py`.

REQUIREMENTS:
1. Analyze the existing storage logic:
   - `python/src/server/services/storage/qdrant_vector_service.py`
   - `python/src/server/services/storage/document_storage_service.py`
   - `python/src/server/services/embeddings/embedding_service.py`
2. Create a SIMPLIFIED service that:
   - Accepts crawled documents: [{"url": str, "content": str, "title": str}]
   - Chunks the content into smaller pieces (use smart_chunk_text_async pattern)
   - Generates embeddings using OpenAI API
   - Stores vectors in Qdrant
   - Returns statistics: {"chunks_stored": int, "source_id": str}
3. Use existing embedding and chunking logic where possible
4. Support configurable chunk size (default: 5000 characters)
5. Handle batch processing for efficiency
6. Add proper error handling and logging

IMPORTANT PATTERNS TO FOLLOW:
- Use `QdrantVectorService` from storage module
- Use `create_embeddings_batch` from embedding_service
- Import chunking from `storage_services.py` BaseStorageService
- Use logfire for logging
- Make it async with proper type hints

CONFIGURATION:
- Qdrant URL: http://localhost:6333 (or from env QDRANT_URL)
- Collection name: "archon_documents" (or configurable)
- OpenAI API key: from environment OPENAI_API_KEY

OUTPUT:
- Create the new file with complete implementation
- Add docstrings with usage examples
- Keep it under 250 lines
- Focus on clarity and ease of use

You have access to: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=[
                    'Read',
                    'Write',
                    'Edit',
                    'MultiEdit',
                    'Grep',
                    'Glob',
                    'TodoWrite',
                ]
            ),

            # Agent 3: Wrapper Service Builder
            "wrapper-service-builder": AgentDefinition(
                description="Expert at creating unified service wrappers that combine multiple service classes.",
                prompt="""You are an expert Python developer specializing in service orchestration and API design.

Your task is to create a NEW unified service class `CrawlAndStoreService` in `python/src/server/services/crawl_and_store_service.py`.

REQUIREMENTS:
1. Import and compose the two previously created services:
   - `SimpleCrawlingService` from simple_crawling_service
   - `SimpleVectorDBService` from simple_vectordb_service
2. Create a single method `async def crawl_and_store(url: str, **kwargs)` that:
   - Accepts a URL
   - Crawls the URL using SimpleCrawlingService
   - Stores the results in Qdrant using SimpleVectorDBService
   - Returns a complete result dictionary with both crawl and storage stats
3. Add progress tracking and status updates
4. Handle errors gracefully (if crawl fails, don't attempt storage)
5. Support optional parameters:
   - `source_id`: Custom source ID (default: generated from URL)
   - `chunk_size`: Chunk size for vectorization (default: 5000)
   - `max_depth`: For recursive crawling (default: 1)

IMPORTANT PATTERNS:
- Use composition, not inheritance
- Add proper logging at each stage
- Return structured results: {"crawl": {...}, "storage": {...}, "success": bool}
- Make it easy to use with minimal configuration
- Add comprehensive docstrings

EXAMPLE USAGE PATTERN:
```python
service = CrawlAndStoreService()
result = await service.crawl_and_store(
    "https://example.com",
    max_depth=2,
    chunk_size=3000
)
print(f"Stored {result['storage']['chunks_stored']} chunks")
```

OUTPUT:
- Create the new file with complete implementation
- Add usage examples in docstring
- Keep it under 200 lines
- Make it production-ready

You have access to: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=[
                    'Read',
                    'Write',
                    'Edit',
                    'MultiEdit',
                    'Grep',
                    'Glob',
                    'TodoWrite',
                ]
            ),

            # Agent 4: Integration Test Builder
            "integration-test-builder": AgentDefinition(
                description="Expert at creating comprehensive integration tests with real external dependencies.",
                prompt="""You are an expert Python test engineer specializing in integration testing.

Your task is to create a REAL integration test in `python/tests/integration/test_crawl_and_store_real.py`.

REQUIREMENTS:
1. Test the complete pipeline with REAL external calls:
   - Real crawling of https://github.com/The-Pocket/PocketFlow
   - Real OpenAI API calls for embeddings (using OPENAI_API_KEY)
   - Real Qdrant vector storage
2. Use pytest-asyncio for async tests
3. Test structure:
   ```python
   @pytest.mark.asyncio
   @pytest.mark.integration
   async def test_real_crawl_and_store():
       # Real crawl, real embeddings, real storage
       # NO MOCKS
   ```
4. Assertions to verify:
   - Crawl returns documents with content
   - Embeddings are generated (non-zero vectors)
   - Vectors are stored in Qdrant
   - Source ID is created
   - Chunks count > 0
5. Add cleanup logic to delete test data after test runs
6. Skip test if OPENAI_API_KEY is not set (use pytest.skip)

IMPORTANT:
- This is an INTEGRATION test - use real services
- Add @pytest.mark.integration marker
- Add proper error messages for assertions
- Test should be self-contained and idempotent
- Use pytest fixtures if needed for setup/teardown

DEPENDENCIES TO CHECK:
- Qdrant running on localhost:6333
- OpenAI API key in environment
- Internet connection for crawling

OUTPUT:
- Create the test file with complete implementation
- Add module-level docstring explaining it's a real integration test
- Include setup and teardown logic
- Keep it under 150 lines
- Make assertions clear and specific

You have access to: Read, Write, Edit, Grep, Glob, TodoWrite tools.
""",
                model=model,
                tools=[
                    'Read',
                    'Write',
                    'Edit',
                    'MultiEdit',
                    'Grep',
                    'Glob',
                    'TodoWrite',
                ]
            ),

            # Agent 5: Test Validator
            "test-validator": AgentDefinition(
                description="Expert at validating test implementations and ensuring proper test hygiene.",
                prompt="""You are an expert test engineer specializing in test validation and quality assurance.

Your task is to validate the integration test and ensure it follows best practices.

VALIDATION CHECKLIST:
1. Run the test and verify it passes:
   ```bash
   cd python && uv run pytest tests/integration/test_crawl_and_store_real.py -v
   ```
2. Check the test file for:
   - Proper async/await usage
   - Real external calls (NO mocks for integration test)
   - Proper cleanup in teardown/finally blocks
   - Clear assertion messages
   - @pytest.mark.integration marker present
   - Skips gracefully if OPENAI_API_KEY missing
3. Verify the test actually:
   - Makes real HTTP requests
   - Calls OpenAI API
   - Stores data in Qdrant
   - Cleans up after itself
4. Check for anti-patterns:
   - No hardcoded secrets
   - No leftover test data
   - No test pollution (side effects)
   - Proper error handling

VALIDATION OUTPUTS:
1. Run the test and report results
2. If test fails, analyze why and suggest fixes
3. If test passes, create a validation report at `python/tests/integration/VALIDATION_REPORT.md` with:
   - Test execution summary
   - Confirmed behaviors (what was actually tested)
   - Recommendations for improvement
   - Confirmation that NO MOCKS are used (this is integration test)

IMPORTANT:
- You can run bash commands to execute tests
- Read the test file to validate structure
- Check that dependencies are working (Qdrant, OpenAI)
- Ensure test is repeatable and reliable

If test fails, work with the integration-test-builder agent to fix it.

You have access to: Read, Write, Edit, Grep, Glob, TodoWrite, Bash tools.
""",
                model=model,
                tools=[
                    'Read',
                    'Write',
                    'Edit',
                    'MultiEdit',
                    'Grep',
                    'Glob',
                    'TodoWrite',
                    'Bash',
                ]
            ),
        }
    )


async def main():
    parser = argparse.ArgumentParser(description="Claude Code Agent SDK - Vector DB Pipeline Builder")
    parser.add_argument(
        "--model",
        choices=["opus", "sonnet", "haiku"],
        default="sonnet",
        help="Claude model to use (default: sonnet)"
    )
    parser.add_argument(
        "--agent",
        choices=[
            "crawling-service-builder",
            "vectordb-service-builder",
            "wrapper-service-builder",
            "integration-test-builder",
            "test-validator"
        ],
        help="Specific agent to run (default: interactive mode)"
    )
    args = parser.parse_args()

    console = Console()
    console.print("\n[bold cyan]🤖 Vector DB Pipeline Agent Builder[/bold cyan]\n")
    console.print(f"Model: [yellow]{args.model}[/yellow]\n")

    # Configure agents
    options = create_agent_options(model=args.model)

    # Agent descriptions for menu
    agent_descriptions = {
        "crawling-service-builder": "1️⃣  Create SimpleCrawlingService (web crawling)",
        "vectordb-service-builder": "2️⃣  Create SimpleVectorDBService (Qdrant storage)",
        "wrapper-service-builder": "3️⃣  Create CrawlAndStoreService (unified wrapper)",
        "integration-test-builder": "4️⃣  Create integration test (real API calls)",
        "test-validator": "5️⃣  Validate test passes and check quality",
    }

    async with ClaudeSDKClient(options=options) as client:

        if args.agent:
            # Run specific agent
            selected_agent = args.agent
            console.print(f"\n[green]Running agent:[/green] {agent_descriptions[selected_agent]}\n")
        else:
            # Interactive mode - show menu
            console.print("[bold]Available agents:[/bold]\n")
            for key, desc in agent_descriptions.items():
                console.print(f"  {desc}")
            console.print("\n  [dim]6️⃣  Exit[/dim]\n")

            choice = Prompt.ask(
                "Select an agent to run",
                choices=["1", "2", "3", "4", "5", "6"],
                default="1"
            )

            if choice == "6":
                console.print("\n[yellow]Exiting...[/yellow]\n")
                return

            # Map choice to agent name
            agent_map = {
                "1": "crawling-service-builder",
                "2": "vectordb-service-builder",
                "3": "wrapper-service-builder",
                "4": "integration-test-builder",
                "5": "test-validator",
            }
            selected_agent = agent_map[choice]
            console.print(f"\n[green]Selected:[/green] {agent_descriptions[selected_agent]}\n")

        # Prepare prompt for the agent
        prompts = {
            "crawling-service-builder": "Create the SimpleCrawlingService class that crawls URLs and returns structured document data. Use the existing codebase patterns from python/src/server/services/crawling/.",
            "vectordb-service-builder": "Create the SimpleVectorDBService class that chunks documents, generates embeddings, and stores vectors in Qdrant. Use existing patterns from storage and embeddings modules.",
            "wrapper-service-builder": "Create the CrawlAndStoreService wrapper class that combines SimpleCrawlingService and SimpleVectorDBService into a single easy-to-use API.",
            "integration-test-builder": "Create a real integration test in python/tests/integration/test_crawl_and_store_real.py that crawls https://github.com/The-Pocket/PocketFlow for real using OpenAI API and stores in Qdrant. NO MOCKS.",
            "test-validator": "Run and validate the integration test at python/tests/integration/test_crawl_and_store_real.py. Verify it passes and uses real external services. Create a validation report.",
        }

        query_prompt = prompts[selected_agent]
        console.print(f"[dim]Prompt: {query_prompt}[/dim]\n")

        # Use Task tool to delegate to the specialized agent
        await client.query(f"/task {selected_agent} {query_prompt}")

        # Stream the response
        async for message in client.receive_response():
            # Print messages as they arrive
            if message.get("type") == "text":
                console.print(message.get("text", ""))
            elif message.get("type") == "tool_use":
                tool_name = message.get("name", "unknown")
                console.print(f"\n[blue]🔧 Using tool:[/blue] {tool_name}")
            elif message.get("type") == "tool_result":
                console.print("[dim]✓ Tool completed[/dim]")

        console.print("\n[green]✓ Agent task completed![/green]\n")


if __name__ == "__main__":
    asyncio.run(main())
