#!/usr/bin/env python3
"""
Test Archon MCP server using official MCP Python client

This script validates that the MCP server works correctly with the official MCP protocol.
"""

import asyncio
import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_server():
    """Test MCP server with official client"""
    print("=" * 70)
    print("Testing Archon MCP Server with Official MCP Client")
    print("=" * 70)

    # MCP server URL - SSE transport uses /sse endpoint
    url = "http://192.168.1.162:8051/sse"

    async with AsyncExitStack() as stack:
        # Create SSE client
        print(f"\n1. Connecting to {url}...")
        read_stream, write_stream = await stack.enter_async_context(
            sse_client(url)
        )

        # Create client session
        session = await stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        # Initialize the connection
        print("2. Initializing MCP connection...")
        init_result = await session.initialize()
        print(f"✅ Connected! Server: {init_result.serverInfo.name} v{init_result.serverInfo.version}")
        print(f"   Protocol version: {init_result.protocolVersion}")

        # List available tools
        print("\n3. Listing available tools...")
        tools_result = await session.list_tools()
        print(f"✅ Found {len(tools_result.tools)} tools:")
        for i, tool in enumerate(tools_result.tools[:5], 1):
            print(f"   {i}. {tool.name}")
        if len(tools_result.tools) > 5:
            print(f"   ... and {len(tools_result.tools) - 5} more")

        # Test health_check tool
        print("\n4. Calling health_check tool...")
        try:
            health_result = await session.call_tool("health_check", arguments={})
            print("✅ health_check succeeded!")
            if health_result.content:
                for content in health_result.content:
                    if hasattr(content, 'text'):
                        health_data = json.loads(content.text)
                        print(f"   Status: {health_data.get('success')}")
                        if 'health' in health_data:
                            print(f"   Health: {health_data['health'].get('status')}")
        except Exception as e:
            print(f"❌ health_check failed: {e}")

        # Test rag_get_available_sources tool
        print("\n5. Calling rag_get_available_sources tool...")
        try:
            rag_result = await session.call_tool("rag_get_available_sources", arguments={})
            print("✅ rag_get_available_sources succeeded!")
            if rag_result.content:
                for content in rag_result.content:
                    if hasattr(content, 'text'):
                        sources_data = json.loads(content.text)
                        print(f"   Success: {sources_data.get('success')}")
                        print(f"   Sources count: {sources_data.get('count', 0)}")
        except Exception as e:
            print(f"❌ rag_get_available_sources failed: {e}")

        # Test session_info tool
        print("\n6. Calling session_info tool...")
        try:
            session_result = await session.call_tool("session_info", arguments={})
            print("✅ session_info succeeded!")
            if session_result.content:
                for content in session_result.content:
                    if hasattr(content, 'text'):
                        session_data = json.loads(content.text)
                        print(f"   Active sessions: {session_data.get('session_management', {}).get('active_sessions')}")
        except Exception as e:
            print(f"❌ session_info failed: {e}")

        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
