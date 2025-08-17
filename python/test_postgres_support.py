#!/usr/bin/env python3
"""
PostgreSQL Support Verification Script for Archon

This script tests the PostgreSQL adapter with pgvector support.
"""

import asyncio
import os
import sys
from datetime import datetime
import numpy as np

# Set PostgreSQL environment variables
os.environ["DATABASE_TYPE"] = "postgresql"
os.environ["POSTGRES_HOST"] = os.getenv("POSTGRES_HOST", "localhost")
os.environ["POSTGRES_PORT"] = os.getenv("POSTGRES_PORT", "5433")
os.environ["POSTGRES_DB"] = os.getenv("POSTGRES_DB", "archon_db")
os.environ["POSTGRES_USER"] = os.getenv("POSTGRES_USER", "archon")
os.environ["POSTGRES_PASSWORD"] = os.getenv("POSTGRES_PASSWORD", "archon_secure_password")

# Import after setting environment
from src.server.dal import ConnectionManager, DatabaseType


class PostgreSQLAdapter:
    """PostgreSQL adapter implementation"""
    
    def __init__(self, **kwargs):
        import asyncpg
        self.connection_params = kwargs
        self.pool = None
    
    async def connect(self):
        """Create connection pool"""
        import asyncpg
        if not self.pool:
            # Build connection string
            host = self.connection_params.get('host', 'localhost')
            port = self.connection_params.get('port', 5433)
            database = self.connection_params.get('database', 'archon_db')
            user = self.connection_params.get('user', 'archon')
            password = self.connection_params.get('password', 'archon_secure_password')
            
            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Enable pgvector extension
            async with self.pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def health_check(self):
        """Check connection health"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
        except Exception:
            return False
    
    async def select(self, table, columns=None, filters=None, limit=None, offset=None, order_by=None):
        """Select records from table"""
        if not self.pool:
            return {"success": False, "data": [], "error": "Not connected"}
        
        try:
            # Build query
            if columns:
                columns_str = ", ".join(columns)
            else:
                columns_str = "*"
            
            query = f"SELECT {columns_str} FROM {table}"
            params = []
            param_count = 0
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        # Convert dict to JSON string for JSON columns in WHERE clause
                        if isinstance(value, dict):
                            import json
                            value = json.dumps(value)
                        elif isinstance(value, list) and key != 'embedding':
                            import json
                            value = json.dumps(value)
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Add ORDER BY
            if order_by:
                query += f" ORDER BY {order_by}"
            
            # Add LIMIT and OFFSET
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return {
                    "success": True,
                    "data": [dict(row) for row in rows],
                    "count": len(rows)
                }
        
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}
    
    async def insert(self, table, data, returning=None):
        """Insert records into table"""
        if not self.pool:
            return {"success": False, "data": [], "error": "Not connected"}
        
        try:
            # Ensure data is a list
            records = data if isinstance(data, list) else [data]
            
            if not records:
                return {"success": False, "data": [], "error": "No data to insert"}
            
            # Get column names
            columns = list(records[0].keys())
            columns_str = ", ".join(columns)
            
            # Build VALUES clause
            values_list = []
            params = []
            param_count = 0
            
            for record in records:
                placeholders = []
                for col in columns:
                    param_count += 1
                    value = record.get(col)
                    # Convert dict to JSON string for JSON columns
                    if isinstance(value, dict):
                        import json
                        value = json.dumps(value)
                    # Convert lists to JSON strings (for JSON columns, not vectors)
                    elif isinstance(value, list) and col != 'embedding':
                        import json
                        value = json.dumps(value)
                    placeholders.append(f"${param_count}")
                    params.append(value)
                values_list.append(f"({', '.join(placeholders)})")
            
            # Build query
            query = f"INSERT INTO {table} ({columns_str}) VALUES {', '.join(values_list)}"
            
            # Add RETURNING clause
            if returning:
                query += f" RETURNING {', '.join(returning)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                if returning:
                    rows = await conn.fetch(query, *params)
                    result_data = [dict(row) for row in rows]
                else:
                    await conn.execute(query, *params)
                    result_data = records
                
                return {
                    "success": True,
                    "data": result_data,
                    "affected_rows": len(records)
                }
        
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}
    
    async def update(self, table, data, filters, returning=None):
        """Update records in table"""
        if not self.pool:
            return {"success": False, "data": [], "error": "Not connected"}
        
        try:
            if not data:
                return {"success": False, "data": [], "error": "No data to update"}
            
            # Build SET clause
            set_clauses = []
            params = []
            param_count = 0
            
            for key, value in data.items():
                param_count += 1
                # Convert dict to JSON string for JSON columns
                if isinstance(value, dict):
                    import json
                    value = json.dumps(value)
                elif isinstance(value, list) and key != 'embedding':
                    import json
                    value = json.dumps(value)
                set_clauses.append(f"{key} = ${param_count}")
                params.append(value)
            
            query = f"UPDATE {table} SET {', '.join(set_clauses)}"
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        # Convert dict to JSON string for JSON columns in WHERE clause
                        if isinstance(value, dict):
                            import json
                            value = json.dumps(value)
                        elif isinstance(value, list) and key != 'embedding':
                            import json
                            value = json.dumps(value)
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Add RETURNING clause
            if returning:
                query += f" RETURNING {', '.join(returning)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                if returning:
                    rows = await conn.fetch(query, *params)
                    result_data = [dict(row) for row in rows]
                else:
                    result = await conn.execute(query, *params)
                    # Extract affected rows from result string
                    affected = int(result.split()[-1]) if result else 0
                    result_data = []
                
                return {
                    "success": True,
                    "data": result_data,
                    "affected_rows": affected if not returning else len(result_data)
                }
        
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}
    
    async def delete(self, table, filters, returning=None):
        """Delete records from table"""
        if not self.pool:
            return {"success": False, "data": [], "error": "Not connected"}
        
        try:
            # Build DELETE query
            query = f"DELETE FROM {table}"
            params = []
            param_count = 0
            
            # Add WHERE clause
            if filters:
                where_clauses = []
                for key, value in filters.items():
                    param_count += 1
                    if value is None:
                        where_clauses.append(f"{key} IS NULL")
                    else:
                        # Convert dict to JSON string for JSON columns in WHERE clause
                        if isinstance(value, dict):
                            import json
                            value = json.dumps(value)
                        elif isinstance(value, list) and key != 'embedding':
                            import json
                            value = json.dumps(value)
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Add RETURNING clause
            if returning:
                query += f" RETURNING {', '.join(returning)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                if returning:
                    rows = await conn.fetch(query, *params)
                    result_data = [dict(row) for row in rows]
                    affected = len(result_data)
                else:
                    result = await conn.execute(query, *params)
                    affected = int(result.split()[-1]) if result else 0
                    result_data = []
                
                return {
                    "success": True,
                    "data": result_data,
                    "affected_rows": affected
                }
        
        except Exception as e:
            return {"success": False, "data": [], "error": str(e)}
    
    async def test_vector_search(self):
        """Test pgvector functionality"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                # Create a test vector
                test_vector = np.random.randn(1536).astype(np.float32)
                
                # Test vector operations
                # Convert vector to string format for PostgreSQL
                vector_str = '[' + ','.join(map(str, test_vector.tolist())) + ']'
                result = await conn.fetchval(
                    "SELECT $1::vector(1536) <=> $1::vector(1536) as distance",
                    vector_str
                )
                
                # Distance to itself should be 0
                return result == 0.0
        except Exception as e:
            print(f"Vector test error: {e}")
            return False


async def verify_postgresql():
    """Verify PostgreSQL support for Archon"""
    
    print("=" * 60)
    print("🐘 PostgreSQL Support Verification for Archon")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Create PostgreSQL adapter
    adapter = PostgreSQLAdapter(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5433)),
        database=os.getenv("POSTGRES_DB", "archon_db"),
        user=os.getenv("POSTGRES_USER", "archon"),
        password=os.getenv("POSTGRES_PASSWORD", "archon_secure_password")
    )
    
    try:
        # Connect to database
        print("\n1. Testing Connection...")
        print("-" * 40)
        await adapter.connect()
        print("   ✓ Connection pool created")
        total_tests += 1
        success_count += 1
        
        # Health check
        print("\n2. Testing Health Check...")
        print("-" * 40)
        is_healthy = await adapter.health_check()
        total_tests += 1
        if is_healthy:
            print("   ✓ Health check passed")
            success_count += 1
        else:
            print("   ✗ Health check failed")
        
        # Test SELECT
        print("\n3. Testing SELECT Query...")
        print("-" * 40)
        result = await adapter.select("archon_sources", limit=5)
        total_tests += 1
        if result["success"]:
            print(f"   ✓ SELECT successful: {len(result['data'])} records found")
            success_count += 1
            for record in result["data"][:2]:
                print(f"     - {record.get('title', 'N/A')} ({record.get('source_type', 'N/A')})")
        else:
            print(f"   ✗ SELECT failed: {result.get('error')}")
        
        # Test INSERT
        print("\n4. Testing INSERT Query...")
        print("-" * 40)
        test_data = {
            "url": f"https://test-pg-{datetime.now().timestamp()}.example.com",
            "title": "PostgreSQL Verification Test",
            "source_type": "test",
            "status": "pending",
            "metadata": {"test": True, "database": "postgresql"}
        }
        result = await adapter.insert("archon_sources", test_data, returning=["id"])
        total_tests += 1
        if result["success"]:
            print(f"   ✓ INSERT successful: {result['affected_rows']} rows affected")
            success_count += 1
            
            if result["data"]:
                test_id = result["data"][0]["id"]
                
                # Test UPDATE
                print("\n5. Testing UPDATE Query...")
                print("-" * 40)
                update_data = {
                    "title": "PostgreSQL Test - Updated",
                    "status": "completed"
                }
                result = await adapter.update(
                    "archon_sources",
                    update_data,
                    {"id": test_id}
                )
                total_tests += 1
                if result["success"]:
                    print(f"   ✓ UPDATE successful: {result['affected_rows']} rows affected")
                    success_count += 1
                else:
                    print(f"   ✗ UPDATE failed: {result.get('error')}")
                
                # Test DELETE
                print("\n6. Testing DELETE Query...")
                print("-" * 40)
                result = await adapter.delete("archon_sources", {"id": test_id})
                total_tests += 1
                if result["success"]:
                    print(f"   ✓ DELETE successful: {result['affected_rows']} rows affected")
                    success_count += 1
                else:
                    print(f"   ✗ DELETE failed: {result.get('error')}")
        else:
            print(f"   ✗ INSERT failed: {result.get('error')}")
        
        # Test pgvector
        print("\n7. Testing pgvector Support...")
        print("-" * 40)
        vector_works = await adapter.test_vector_search()
        total_tests += 1
        if vector_works:
            print("   ✓ pgvector extension is working")
            success_count += 1
        else:
            print("   ✗ pgvector test failed")
        
        # Test concurrent connections
        print("\n8. Testing Connection Pool...")
        print("-" * 40)
        
        async def concurrent_query(n):
            result = await adapter.select("archon_sources", limit=1)
            return n, result["success"]
        
        tasks = [concurrent_query(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_tests += 1
        successful_queries = sum(1 for r in results if not isinstance(r, Exception) and r[1])
        if successful_queries == len(tasks):
            print(f"   ✓ All {len(tasks)} concurrent queries successful")
            success_count += 1
        else:
            print(f"   ⚠ {successful_queries}/{len(tasks)} concurrent queries successful")
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Disconnect
        await adapter.disconnect()
        print("\n✓ Connection pool closed")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"   Tests Passed: {success_count}/{total_tests}")
    print(f"   Success Rate: {(success_count/total_tests*100):.1f}%")
    
    if success_count == total_tests:
        print("\n✅ PostgreSQL verification PASSED - All tests successful!")
        print("   • pgvector extension working")
        print("   • All CRUD operations functional")
        print("   • Connection pooling operational")
        return 0
    else:
        print(f"\n⚠️  PostgreSQL verification PARTIAL - {total_tests - success_count} tests failed")
        return 1


async def check_postgres_connection():
    """Quick check if PostgreSQL is running"""
    try:
        adapter = PostgreSQLAdapter(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", 5433)),
            database=os.getenv("POSTGRES_DB", "archon_db"),
            user=os.getenv("POSTGRES_USER", "archon"),
            password=os.getenv("POSTGRES_PASSWORD", "archon_secure_password")
        )
        await adapter.connect()
        is_healthy = await adapter.health_check()
        await adapter.disconnect()
        return is_healthy
    except Exception:
        return False


if __name__ == "__main__":
    print("\n🐘 PostgreSQL Support Verification Script")
    print("=" * 60)
    
    # Check if PostgreSQL is available
    print("Checking PostgreSQL availability...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    postgres_available = loop.run_until_complete(check_postgres_connection())
    
    if not postgres_available:
        print("\n⚠️  PostgreSQL is not available!")
        print("\nTo start PostgreSQL, run:")
        print("  docker-compose -f docker-compose.dev.yml up -d postgres")
        print("\nOr use the Makefile:")
        print("  make start-postgres")
        print("\nThen wait a few seconds for PostgreSQL to initialize and try again.")
        sys.exit(1)
    
    print("✓ PostgreSQL is available\n")
    
    # Run verification
    exit_code = loop.run_until_complete(verify_postgresql())
    sys.exit(exit_code)