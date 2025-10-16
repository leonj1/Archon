#!/usr/bin/env python3
"""Simple test of Claude Agent SDK"""

import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AgentDefinition
from dotenv import load_dotenv

load_dotenv()

async def test():
    print("Testing Claude Agent SDK...")

    options = ClaudeAgentOptions(
        model="sonnet",
        permission_mode="acceptEdits",
        setting_sources=["project"],
        allowed_tools=["Read", "Write", "Task"],
        agents={
            "test-agent": AgentDefinition(
                description="A simple test agent",
                prompt="You are a test agent. Just say hello and exit.",
                model="sonnet",
                tools=["Read", "Write"],
            )
        }
    )

    try:
        async with ClaudeSDKClient(options=options) as client:
            print("Client created successfully")
            await client.query("Delegate to test-agent to say hello")

            async for message in client.receive_response():
                print(f"Message: {message}")

            print("Test completed successfully")
            return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    success = asyncio.run(test())
    exit(0 if success else 1)
