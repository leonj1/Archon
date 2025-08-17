#!/usr/bin/env python3
"""
MySQL Support Verification Script for Archon

This script tests the MySQL adapter and verifies that Archon can work with MySQL.
"""

import asyncio
import os
import sys
from datetime import datetime

# Set MySQL environment variables
os.environ["DATABASE_TYPE"] = "mysql"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "3306"
os.environ["MYSQL_DATABASE"] = "archon_db"
os.environ["MYSQL_USER"] = "archon"
os.environ["MYSQL_PASSWORD"] = "archon_secure_password"

from src.server.dal import ConnectionManager, DatabaseType
from src.server.dal.adapters import MySQLAdapter


async def verify_mysql():
    """Verify MySQL support for Archon"""
    
    print("=" * 60)
    print("🔍 MySQL Support Verification for Archon")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Register MySQL adapter
    ConnectionManager.register_adapter(DatabaseType.MYSQL, MySQLAdapter)
    print("✓ MySQL adapter registered")
    
    # Create connection manager
    manager = ConnectionManager.from_env()
    print(f"✓ Connection manager created for {manager.environment.value} environment")
    
    try:
        # Initialize connections
        print("\n1. Testing Connection...")
        print("-" * 40)
        await manager.initialize()
        print("   ✓ Connection pool initialized")
        total_tests += 1
        success_count += 1
        
        # Test primary connection
        async with manager.get_primary() as conn:
            print("   ✓ Acquired primary connection")
            
            # Health check
            print("\n2. Testing Health Check...")
            print("-" * 40)
            is_healthy = await conn.health_check()
            total_tests += 1
            if is_healthy:
                print("   ✓ Health check passed")
                success_count += 1
            else:
                print("   ✗ Health check failed")
            
            # Test SELECT
            print("\n3. Testing SELECT Query...")
            print("-" * 40)
            result = await conn.select("archon_sources", limit=5)
            total_tests += 1
            if result.success:
                print(f"   ✓ SELECT successful: {len(result.data)} records found")
                success_count += 1
                for record in result.data[:2]:  # Show first 2 records
                    print(f"     - {record.get('title', 'N/A')} ({record.get('source_type', 'N/A')})")
            else:
                print(f"   ✗ SELECT failed: {result.error}")
            
            # Test INSERT
            print("\n4. Testing INSERT Query...")
            print("-" * 40)
            test_data = {
                "url": f"https://test-{datetime.now().timestamp()}.example.com",
                "title": "MySQL Verification Test",
                "source_type": "test",
                "status": "pending",
                "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
            }
            result = await conn.insert("archon_sources", test_data)
            total_tests += 1
            if result.success:
                print(f"   ✓ INSERT successful: {result.affected_rows} rows affected")
                success_count += 1
                
                # Store ID for later operations
                if result.data and len(result.data) > 0:
                    test_id = result.data[0].get("id")
                else:
                    # MySQL doesn't return data by default, need to query
                    select_result = await conn.select(
                        "archon_sources",
                        filters={"url": test_data["url"]}
                    )
                    if select_result.data:
                        test_id = select_result.data[0]["id"]
                    else:
                        test_id = None
                
                if test_id:
                    # Test UPDATE
                    print("\n5. Testing UPDATE Query...")
                    print("-" * 40)
                    update_data = {
                        "title": "MySQL Test - Updated",
                        "status": "completed",
                        "metadata": {"test": True, "updated": True}
                    }
                    result = await conn.update(
                        "archon_sources",
                        update_data,
                        {"id": test_id}
                    )
                    total_tests += 1
                    if result.success:
                        print(f"   ✓ UPDATE successful: {result.affected_rows} rows affected")
                        success_count += 1
                    else:
                        print(f"   ✗ UPDATE failed: {result.error}")
                    
                    # Test DELETE
                    print("\n6. Testing DELETE Query...")
                    print("-" * 40)
                    result = await conn.delete("archon_sources", {"id": test_id})
                    total_tests += 1
                    if result.success:
                        print(f"   ✓ DELETE successful: {result.affected_rows} rows affected")
                        success_count += 1
                    else:
                        print(f"   ✗ DELETE failed: {result.error}")
            else:
                print(f"   ✗ INSERT failed: {result.error}")
        
        # Test concurrent connections
        print("\n7. Testing Connection Pool...")
        print("-" * 40)
        
        async def concurrent_query(n):
            async with manager.get_reader() as conn:
                result = await conn.select("archon_sources", limit=1)
                return n, result.success
        
        tasks = [concurrent_query(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_tests += 1
        successful_queries = sum(1 for r in results if not isinstance(r, Exception) and r[1])
        if successful_queries == len(tasks):
            print(f"   ✓ All {len(tasks)} concurrent queries successful")
            success_count += 1
        else:
            print(f"   ⚠ {successful_queries}/{len(tasks)} concurrent queries successful")
        
        # Test transaction
        print("\n8. Testing Transactions...")
        print("-" * 40)
        async with manager.get_primary() as conn:
            try:
                async with await conn.begin_transaction() as tx:
                    # Insert within transaction
                    result1 = await conn.insert(
                        "archon_sources",
                        {"url": "https://tx-test.com", "title": "Transaction Test"}
                    )
                    
                    # This should succeed
                    if result1.success:
                        print("   ✓ Insert within transaction successful")
                    
                    # Commit happens automatically
                
                # Verify the record exists
                result2 = await conn.select(
                    "archon_sources",
                    filters={"url": "https://tx-test.com"}
                )
                
                total_tests += 1
                if result2.data:
                    print("   ✓ Transaction committed successfully")
                    success_count += 1
                    
                    # Clean up
                    await conn.delete("archon_sources", {"url": "https://tx-test.com"})
                else:
                    print("   ✗ Transaction test failed")
            except Exception as e:
                print(f"   ✗ Transaction error: {e}")
        
        # Get health status
        print("\n9. Final Health Check...")
        print("-" * 40)
        health_status = await manager.health_check()
        print(f"   Environment: {health_status['environment']}")
        
        if health_status['primary']:
            status = health_status['primary']
            print(f"   Primary DB: {status['type']} ({'healthy' if status['healthy'] else 'unhealthy'})")
            print(f"   Pool size: {status.get('pool_size', 'N/A')}")
            print(f"   In use: {status.get('in_use', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connections with timeout
        try:
            await asyncio.wait_for(manager.close(), timeout=5.0)
            print("\n✓ All connections closed")
        except asyncio.TimeoutError:
            print("\n⚠️  Connection close timed out after 5 seconds")
            print("   (This may indicate hanging connections in the pool)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"   Tests Passed: {success_count}/{total_tests}")
    print(f"   Success Rate: {(success_count/total_tests*100):.1f}%")
    
    if success_count == total_tests:
        print("\n✅ MySQL verification PASSED - All tests successful!")
        return 0
    else:
        print(f"\n⚠️  MySQL verification PARTIAL - {total_tests - success_count} tests failed")
        return 1


async def check_mysql_connection():
    """Quick check if MySQL is running"""
    try:
        adapter = MySQLAdapter()
        await adapter.connect()
        is_healthy = await adapter.health_check()
        await adapter.disconnect()
        return is_healthy
    except Exception:
        return False


if __name__ == "__main__":
    print("\n🐬 MySQL Support Verification Script")
    print("=" * 60)
    
    # Check if MySQL is available
    print("Checking MySQL availability...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    mysql_available = loop.run_until_complete(check_mysql_connection())
    
    if not mysql_available:
        print("\n⚠️  MySQL is not available!")
        print("\nTo start MySQL, run:")
        print("  docker-compose -f docker-compose.dev.yml up -d mysql")
        print("\nThen wait a few seconds for MySQL to initialize and try again.")
        sys.exit(1)
    
    print("✓ MySQL is available\n")
    
    # Run verification
    exit_code = loop.run_until_complete(verify_mysql())
    sys.exit(exit_code)