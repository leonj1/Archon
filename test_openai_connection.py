"""Test OpenAI API connectivity"""
import asyncio
import os
import sys

async def test_openai_connection():
    """Test if we can connect to OpenAI API"""
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not set")
            return False

        print(f"✓ OPENAI_API_KEY is set (length: {len(api_key)})")

        # Create client with timeout settings
        client = openai.AsyncOpenAI(
            api_key=api_key,
            timeout=30.0,  # Add explicit timeout
        )

        print("Attempting to create a test embedding...")

        try:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=["test"],
            )

            print(f"✅ Success! Created embedding with {len(response.data[0].embedding)} dimensions")
            return True

        except openai.APIConnectionError as e:
            print(f"❌ Connection Error: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   This suggests a network connectivity issue")
            return False

        except openai.AuthenticationError as e:
            print(f"❌ Authentication Error: {e}")
            print(f"   Your API key may be invalid or expired")
            return False

        except Exception as e:
            print(f"❌ Unexpected Error: {type(e).__name__}: {e}")
            return False

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_connection())
    sys.exit(0 if result else 1)
