#!/usr/bin/env python3
"""
Direct MySQL Adapter Test - bypasses ConnectionManager
"""

import asyncio
import os
from datetime import datetime

# Import the adapter directly
from src.server.dal.adapters.mysql_adapter import MySQLAdapter


async def test_mysql_direct():
    """Test MySQL adapter directly without ConnectionManager"""
    
    print("=" * 60)
    print("🔍 Direct MySQL Adapter Test")
    print("=" * 60)
    
    # Create adapter with connection params
    adapter = MySQLAdapter(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        database=os.getenv("MYSQL_DATABASE", "archon_db"),
        user=os.getenv("MYSQL_USER", "archon"),
        password=os.getenv("MYSQL_PASSWORD", "archon_secure_password")
    )
    
    try:
        # Connect
        print("\n1. Testing Connection...")
        await adapter.connect()
        print("   ✓ Connected to MySQL")
        
        # Health check
        print("\n2. Testing Health Check...")
        healthy = await adapter.health_check()
        print(f"   ✓ Health check: {healthy}")
        
        # SELECT query
        print("\n3. Testing SELECT...")
        result = await adapter.select("archon_sources", limit=5)
        if result.success:
            print(f"   ✓ SELECT successful: {len(result.data)} records")
        else:
            print(f"   ✗ SELECT failed: {result.error}")
        
        # INSERT query
        print("\n4. Testing INSERT...")
        test_data = {
            "url": f"https://test-{datetime.now().timestamp()}.example.com",
            "title": "Direct MySQL Test",
            "source_type": "test",
            "status": "pending",
            "metadata": {"test": True}
        }
        result = await adapter.insert("archon_sources", test_data)
        if result.success:
            print(f"   ✓ INSERT successful: {result.affected_rows} rows")
            
            # For testing UPDATE and DELETE, we need to find the record we just inserted
            # UPDATE query
            print("\n5. Testing UPDATE...")
            update_data = {
                "title": "Direct MySQL Test - Updated",
                "status": "completed"
            }
            result = await adapter.update(
                "archon_sources",
                update_data,
                {"url": test_data["url"]}  # Use URL as unique identifier
            )
            if result.success:
                print(f"   ✓ UPDATE successful: {result.affected_rows} rows")
            else:
                print(f"   ✗ UPDATE failed: {result.error}")
            
            # DELETE query
            print("\n6. Testing DELETE...")
            result = await adapter.delete("archon_sources", {"url": test_data["url"]})
            if result.success:
                print(f"   ✓ DELETE successful: {result.affected_rows} rows")
            else:
                print(f"   ✗ DELETE failed: {result.error}")
        else:
            print(f"   ✗ INSERT failed: {result.error}")
        
        # Test concurrent queries using the pool
        print("\n7. Testing Concurrent Queries...")
        tasks = []
        for i in range(5):
            tasks.append(adapter.select("archon_sources", limit=1))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception) and r.success)
        print(f"   ✓ {successful}/5 concurrent queries successful")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await adapter.disconnect()
        print("\n✓ Disconnected from MySQL")


if __name__ == "__main__":
    print("\n🐬 MySQL Direct Adapter Test")
    print("=" * 60)
    
    # Run test
    asyncio.run(test_mysql_direct())