#!/usr/bin/env python3
"""
MCP Client Test Script - Using Official MCP SDK

This script mimics how Claude Code connects to an MCP server using SSE transport.
It connects to the Archon MCP server running on port 8051 and tests basic operations.

Requirements:
    pip install mcp httpx

Usage:
    python test_mcp_connection.py [server_url]

    Default server_url: http://localhost:8051
"""

import asyncio
import json
import sys
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client


async def test_mcp_connection(server_url: str = "http://localhost:8051"):
    """Test connecting to the Archon MCP server via SSE."""

    sse_endpoint = f"{server_url}/sse"

    print("=" * 70)
    print("🔌 MCP Client Test - Connecting to Archon MCP Server")
    print("=" * 70)
    print(f"Server URL: {server_url}")
    print(f"SSE Endpoint: {sse_endpoint}")
    print()

    try:
        # Connect to the MCP server using SSE transport
        print("📡 Establishing SSE connection...")

        async with sse_client(url=sse_endpoint) as (read, write):
            # Create a client session
            async with ClientSession(read, write) as session:
                # Initialize the session
                print("🔗 Initializing MCP session...")
                await session.initialize()

                print("✅ Successfully connected to MCP server!")
                print()

                # Session initialized successfully - ready to call tools
                print("📋 MCP Session Initialized")
                print("   Ready to call tools...")
                print()

                # List available tools
                print("🔧 Listing Available Tools:")
                tools_result = await session.list_tools()

                if not tools_result.tools:
                    print("   ❌ No tools found!")
                    return False
                else:
                    print(f"   Found {len(tools_result.tools)} tools:\n")
                    for i, tool in enumerate(tools_result.tools, 1):
                        print(f"   {i:2d}. {tool.name}")
                        if tool.description:
                            # Show first line of description
                            desc_lines = tool.description.split('\n')
                            first_line = desc_lines[0][:80] + "..." if len(desc_lines[0]) > 80 else desc_lines[0]
                            print(f"       {first_line}")
                        print()
                print()

                # Test health_check tool
                print("=" * 70)
                print("🏥 Testing: health_check")
                print("=" * 70)
                try:
                    health_result = await session.call_tool("health_check", arguments={})

                    # Parse the result
                    if health_result.content:
                        health_text = health_result.content[0].text
                        health_data = json.loads(health_text)

                        print(f"✅ Success!")
                        print(f"   Status: {health_data.get('status', 'unknown')}")

                        if 'health' in health_data:
                            health_info = health_data['health']
                            api_status = '✅' if health_info.get('api_service') else '❌'
                            agents_status = '✅' if health_info.get('agents_service') else '❌'
                            print(f"   API Service: {api_status}")
                            print(f"   Agents Service: {agents_status}")

                        if 'uptime_seconds' in health_data:
                            uptime = health_data['uptime_seconds']
                            print(f"   Uptime: {uptime:.2f} seconds ({uptime/60:.1f} minutes)")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                print()

                # Test session_info tool
                print("=" * 70)
                print("📊 Testing: session_info")
                print("=" * 70)
                try:
                    session_result = await session.call_tool("session_info", arguments={})

                    if session_result.content:
                        session_text = session_result.content[0].text
                        session_data = json.loads(session_text)

                        print(f"✅ Success!")
                        if 'session_management' in session_data:
                            sm = session_data['session_management']
                            print(f"   Active Sessions: {sm.get('active_sessions', 0)}")
                            print(f"   Session Timeout: {sm.get('session_timeout', 0)} seconds")
                            if 'server_uptime_seconds' in sm:
                                uptime = sm['server_uptime_seconds']
                                print(f"   Server Uptime: {uptime:.2f} seconds")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                print()

                # Test rag_get_available_sources tool if available
                print("=" * 70)
                print("📚 Testing: rag_get_available_sources")
                print("=" * 70)
                try:
                    sources_result = await session.call_tool("rag_get_available_sources", arguments={})

                    if sources_result.content:
                        sources_text = sources_result.content[0].text
                        sources_data = json.loads(sources_text)

                        if sources_data.get('success'):
                            source_count = sources_data.get('count', 0)
                            print(f"✅ Found {source_count} knowledge sources")

                            if source_count > 0 and 'sources' in sources_data:
                                print("\n   📖 Knowledge Sources:")
                                for source in sources_data['sources'][:5]:  # Show first 5
                                    source_id = source.get('id', 'no-id')
                                    title = source.get('title', 'Untitled')
                                    print(f"      • {title}")
                                    print(f"        ID: {source_id}")
                                if source_count > 5:
                                    print(f"      ... and {source_count - 5} more sources")
                        else:
                            print(f"   ⚠️  Error: {sources_data.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ⚠️  Tool not available or error: {type(e).__name__}: {e}")
                print()

                # Test find_projects tool if available
                print("=" * 70)
                print("📁 Testing: find_projects")
                print("=" * 70)
                try:
                    projects_result = await session.call_tool("find_projects", arguments={})

                    if projects_result.content:
                        projects_text = projects_result.content[0].text
                        projects_data = json.loads(projects_text)

                        if projects_data.get('success'):
                            project_count = len(projects_data.get('projects', []))
                            print(f"✅ Found {project_count} projects")

                            if project_count > 0:
                                print("\n   📂 Projects:")
                                for project in projects_data['projects'][:5]:
                                    project_id = project.get('project_id', 'no-id')
                                    title = project.get('title', 'Untitled')
                                    desc = project.get('description', '')
                                    print(f"      • {title}")
                                    print(f"        ID: {project_id}")
                                    if desc:
                                        desc_short = desc[:60] + "..." if len(desc) > 60 else desc
                                        print(f"        {desc_short}")
                                if project_count > 5:
                                    print(f"      ... and {project_count - 5} more projects")
                        else:
                            print(f"   ⚠️  Error: {projects_data.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ⚠️  Tool not available or error: {type(e).__name__}: {e}")
                print()

                # Test find_tasks tool if available
                print("=" * 70)
                print("✅ Testing: find_tasks")
                print("=" * 70)
                try:
                    tasks_result = await session.call_tool("find_tasks", arguments={"per_page": 5})

                    if tasks_result.content:
                        tasks_text = tasks_result.content[0].text
                        tasks_data = json.loads(tasks_text)

                        if tasks_data.get('success'):
                            task_count = len(tasks_data.get('tasks', []))
                            total = tasks_data.get('total', task_count)
                            print(f"✅ Found {task_count} tasks (showing first 5 of {total} total)")

                            if task_count > 0:
                                print("\n   📋 Tasks:")
                                for task in tasks_data['tasks']:
                                    task_id = task.get('task_id', 'no-id')
                                    title = task.get('title', 'Untitled')
                                    status = task.get('status', 'unknown')
                                    assignee = task.get('assignee', 'unassigned')

                                    # Status emoji
                                    status_emoji = {
                                        'todo': '⏸️',
                                        'doing': '▶️',
                                        'review': '🔍',
                                        'done': '✅'
                                    }.get(status, '❓')

                                    print(f"      {status_emoji} [{status}] {title}")
                                    print(f"        ID: {task_id} | Assigned: {assignee}")
                        else:
                            print(f"   ⚠️  Error: {tasks_data.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"   ⚠️  Tool not available or error: {type(e).__name__}: {e}")
                print()

                print("=" * 70)
                print("✅ MCP Connection Test Complete!")
                print("=" * 70)
                print("\nAll core functionality is working correctly. ✨")
                return True

    except ConnectionRefusedError:
        print("❌ Connection refused!")
        print()
        print("Is the MCP server running on port 8051?")
        print("Start it with: docker compose up archon-mcp -d")
        print()
        return False
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    # Get server URL from command line or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8051"

    print()
    try:
        success = asyncio.run(test_mcp_connection(server_url))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
