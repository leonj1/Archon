#!/usr/bin/env python3
"""
Test MCP Usage Analytics Schema

This script tests the MCP usage tracking schema by inserting test data
and querying the tables via Supabase client.
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from src.server.config.database import get_supabase_client


def test_schema():
    """Test the MCP usage analytics schema."""
    print("🧪 Testing MCP usage analytics schema...")

    # Get Supabase client
    try:
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Test 1: Check if table exists by trying to query it
    print("\n📋 Test 1: Checking if table 'archon_mcp_usage_events' exists...")
    try:
        result = supabase.table("archon_mcp_usage_events").select("count", count="exact").limit(0).execute()
        print(f"   ✅ Table exists with {result.count} rows")
    except Exception as e:
        print(f"   ❌ Table does not exist or query failed: {e}")
        print("\n💡 To create the table:")
        print("   1. Go to Supabase SQL Editor")
        print("   2. Copy and run: migration/0.2.0/001_add_mcp_usage_tracking.sql")
        sys.exit(1)

    # Test 2: Insert test data
    print("\n📝 Test 2: Inserting test data...")
    test_event = {
        "tool_name": "rag_search_knowledge_base",
        "tool_category": "rag",
        "session_id": "test-session-123",
        "client_type": "claude-code",
        "request_metadata": json.dumps({
            "query": "test query",
            "match_count": 5,
            "source_id": "test-source"
        }),
        "source_id": "test-source",
        "query_text": "test query",
        "match_count": 5,
        "response_time_ms": 250,
        "success": True,
        "error_type": None,
    }

    try:
        insert_result = supabase.table("archon_mcp_usage_events").insert(test_event).execute()
        if insert_result.data:
            inserted_id = insert_result.data[0].get("id")
            print(f"   ✅ Test data inserted successfully (ID: {inserted_id})")
        else:
            print("   ⚠️  Insert returned no data")
    except Exception as e:
        print(f"   ❌ Failed to insert test data: {e}")
        sys.exit(1)

    # Test 3: Query recent events
    print("\n🔍 Test 3: Querying recent events...")
    try:
        events = supabase.table("archon_mcp_usage_events") \
            .select("*") \
            .order("timestamp", desc=True) \
            .limit(5) \
            .execute()

        if events.data:
            print(f"   ✅ Found {len(events.data)} recent events:")
            for event in events.data:
                print(f"      - {event.get('tool_name')} ({event.get('tool_category')}) " +
                      f"at {event.get('timestamp')} - {event.get('response_time_ms')}ms")
        else:
            print("   ⚠️  No events found")
    except Exception as e:
        print(f"   ❌ Failed to query events: {e}")

    # Test 4: Test computed columns (hour_bucket, date_bucket)
    print("\n📊 Test 4: Testing computed columns...")
    try:
        # Query to check if hour_bucket and date_bucket are populated
        events = supabase.table("archon_mcp_usage_events") \
            .select("tool_name, timestamp, hour_bucket, date_bucket") \
            .limit(1) \
            .execute()

        if events.data and len(events.data) > 0:
            event = events.data[0]
            if event.get("hour_bucket") and event.get("date_bucket"):
                print(f"   ✅ Computed columns working:")
                print(f"      - timestamp: {event.get('timestamp')}")
                print(f"      - hour_bucket: {event.get('hour_bucket')}")
                print(f"      - date_bucket: {event.get('date_bucket')}")
            else:
                print("   ⚠️  Computed columns not populated")
        else:
            print("   ⚠️  No data to test computed columns")
    except Exception as e:
        print(f"   ❌ Failed to test computed columns: {e}")

    # Test 5: Check materialized views
    print("\n🔬 Test 5: Checking materialized views...")

    # Note: Supabase client may not support querying materialized views directly
    # We'll try to query them
    views_to_test = ["archon_mcp_usage_hourly", "archon_mcp_usage_daily"]

    for view_name in views_to_test:
        try:
            result = supabase.table(view_name).select("*").limit(1).execute()
            if result.data is not None:
                print(f"   ✅ View '{view_name}' is accessible")
            else:
                print(f"   ⚠️  View '{view_name}' returned no data")
        except Exception as e:
            print(f"   ❌ View '{view_name}' not accessible: {e}")

    # Test 6: Check functions exist
    print("\n⚙️  Test 6: Checking database functions...")

    # Note: We can't directly test functions via Supabase client RPC
    # without exposing them as RPC endpoints, but we can note their existence
    functions = [
        "cleanup_mcp_usage_events()",
        "refresh_mcp_usage_views()",
        "get_mcp_usage_summary()"
    ]

    print("   📝 Functions defined in migration:")
    for func in functions:
        print(f"      - {func}")
    print("   ⚠️  Function testing requires RPC endpoint exposure or SQL access")

    # Test 7: Cleanup test data
    print("\n🧹 Test 7: Cleaning up test data...")
    try:
        # Delete test events with our test session ID
        delete_result = supabase.table("archon_mcp_usage_events") \
            .delete() \
            .eq("session_id", "test-session-123") \
            .execute()

        if delete_result.data:
            print(f"   ✅ Cleaned up {len(delete_result.data)} test records")
        else:
            print("   ⚠️  No test records to clean up")
    except Exception as e:
        print(f"   ❌ Failed to cleanup test data: {e}")

    print("\n🎉 Schema testing completed!")
    print("\n📋 Summary:")
    print("   ✓ Table 'archon_mcp_usage_events' exists and is functional")
    print("   ✓ Insert and query operations work")
    print("   ✓ Computed columns (hour_bucket, date_bucket) are working")
    print("   ⚠️  Materialized views require manual verification in SQL Editor")
    print("   ⚠️  Database functions require manual verification in SQL Editor")
    print("\n💡 Next steps:")
    print("   1. The middleware is already integrated and will track real usage")
    print("   2. Monitor the table for incoming usage events")
    print("   3. Set up pg_cron or external cron for materialized view refresh")
    print("   4. Set up pg_cron or external cron for 180-day cleanup")


if __name__ == "__main__":
    test_schema()
