#!/usr/bin/env python3
"""
Quick test to verify investigation script can initialize.
This doesn't run the full investigation - just tests imports and setup.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing investigation script setup...")
print()

try:
    # Test SDK imports
    from claude_agent_sdk import (
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AgentDefinition,
        tool,
        create_sdk_mcp_server,
    )
    print("✓ Claude Agent SDK imports successful")

    # Test utility imports
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    print("✓ Rich console imports successful")

    # Test async support
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    print("✓ Async support configured")

    # Test dotenv
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded")

    # Test that we can create tools
    @tool("test_tool", "Test tool for validation", {})
    async def test_tool(args):
        return {"content": [{"type": "text", "text": "Test"}]}

    print("✓ Tool decorator works")

    # Test that we can create an MCP server
    test_server = create_sdk_mcp_server(
        name="test_server",
        version="1.0.0",
        tools=[test_tool]
    )
    print("✓ MCP server creation works")

    # Test that we can create agent options
    options = ClaudeAgentOptions(
        model="sonnet-4",
        permission_mode="acceptEdits",
        allowed_tools=["Read"],
        mcp_servers={"test": test_server},
    )
    print("✓ Agent options creation works")

    print()
    print("=" * 60)
    print("✓ All imports and setup successful!")
    print("=" * 60)
    print()
    print("The investigation script is ready to run.")
    print("Run it with: ./run_investigation.sh")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("✗ Setup test failed!")
    print("=" * 60)
    print()
    print(f"Error: {e}")
    print()
    print("Please install dependencies:")
    print("  uv add claude-agent-sdk qdrant-client rich nest-asyncio")
    print()
    sys.exit(1)
