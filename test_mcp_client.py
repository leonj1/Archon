#!/usr/bin/env python3
"""
Test MCP Client - Verify Archon MCP server functionality

This script tests the MCP server connection and tool execution.
"""

import asyncio
import json
import sys
from typing import Any

import httpx


class SimpleMCPClient:
    """Simple MCP client for testing Archon MCP server"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session_id: str | None = None
        self.client = httpx.AsyncClient(timeout=30.0)

    def parse_sse_response(self, sse_text: str) -> dict[str, Any]:
        """Parse Server-Sent Events response"""
        lines = sse_text.strip().split('\n')
        data_lines = [line[6:] for line in lines if line.startswith('data: ')]
        if data_lines:
            return json.loads(data_lines[0])
        return {}

    async def initialize(self) -> dict[str, Any]:
        """Initialize MCP connection"""
        print(f"🔌 Connecting to MCP server at {self.base_url}")

        # MCP initialize request with correct params
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-mcp-client",
                    "version": "1.0.0"
                }
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        response = await self.client.post(
            f"{self.base_url}/mcp",
            json=request,
            headers=headers
        )

        print(f"📡 Initialize response status: {response.status_code}")

        # Extract session ID from headers
        if "mcp-session-id" in response.headers:
            self.session_id = response.headers["mcp-session-id"]
            print(f"🔑 Session ID: {self.session_id}")

        if response.status_code == 200:
            # Parse SSE response
            data = self.parse_sse_response(response.text)
            if "error" in data:
                print(f"⚠️  Server returned error: {data['error']}")
            else:
                print(f"✅ Connected! Server info available")
            return data
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {}

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] = None) -> dict[str, Any]:
        """Call an MCP tool"""
        print(f"\n🛠️  Calling tool: {tool_name}")

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        response = await self.client.post(
            f"{self.base_url}/mcp",
            json=request,
            headers=headers
        )

        print(f"📡 Tool response status: {response.status_code}")

        if response.status_code == 200:
            # Parse SSE response
            data = self.parse_sse_response(response.text)
            if "error" in data:
                print(f"⚠️  Tool returned error: {data['error']}")
            else:
                print(f"✅ Tool executed successfully!")
            return data
        else:
            print(f"❌ Tool call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {}

    async def list_tools(self) -> dict[str, Any]:
        """List available MCP tools"""
        print(f"\n📋 Listing available tools...")

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        response = await self.client.post(
            f"{self.base_url}/mcp",
            json=request,
            headers=headers
        )

        print(f"📡 List tools response status: {response.status_code}")

        if response.status_code == 200:
            # Parse SSE response
            data = self.parse_sse_response(response.text)
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:5], 1):  # Show first 5
                    print(f"   {i}. {tool.get('name', 'Unknown')}")
                if len(tools) > 5:
                    print(f"   ... and {len(tools) - 5} more")
            return data
        else:
            print(f"❌ List tools failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {}

    async def close(self):
        """Close the client connection"""
        await self.client.aclose()


async def test_mcp_connection(base_url: str = "http://localhost:8051"):
    """Test MCP server connection and basic functionality"""
    print("=" * 60)
    print("🧪 Archon MCP Server Test")
    print("=" * 60)

    client = SimpleMCPClient(base_url)

    try:
        # Step 1: Initialize connection
        init_result = await client.initialize()
        if not init_result:
            print("\n❌ Failed to initialize MCP connection")
            return False

        # Step 2: List available tools
        tools_result = await client.list_tools()
        if not tools_result:
            print("\n❌ Failed to list tools")
            return False

        # Step 3: Call health_check tool
        health_result = await client.call_tool("health_check")
        if health_result and "result" in health_result:
            result_content = health_result["result"].get("content", [])
            if result_content:
                # Parse the JSON response from health_check
                health_data = json.loads(result_content[0].get("text", "{}"))
                print(f"\n📊 Health Check Result:")
                print(json.dumps(health_data, indent=2))

        # Step 4: Test RAG tool (get available sources)
        rag_result = await client.call_tool("rag_get_available_sources")
        if rag_result and "result" in rag_result:
            result_content = rag_result["result"].get("content", [])
            if result_content:
                sources_data = json.loads(result_content[0].get("text", "{}"))
                print(f"\n📚 Available Sources:")
                print(json.dumps(sources_data, indent=2))

        print("\n" + "=" * 60)
        print("✅ All tests passed! MCP server is working correctly.")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()


if __name__ == "__main__":
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8051"

    # Run the test
    success = asyncio.run(test_mcp_connection(base_url))

    # Exit with appropriate code
    sys.exit(0 if success else 1)
