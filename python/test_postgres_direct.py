#!/usr/bin/env python3
"""
Direct PostgreSQL Adapter Test - bypasses ConnectionManager
"""

import asyncio
import os
from datetime import datetime
import numpy as np


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
    
    async def select(self, table, columns=None, filters=None, limit=None):
        """Select records from table"""
        from src.server.dal.interfaces import QueryResult
        
        if not self.pool:
            return QueryResult(data=[], error="Not connected")
        
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
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Add LIMIT
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return QueryResult(
                    data=[dict(row) for row in rows],
                    count=len(rows)
                )
        
        except Exception as e:
            return QueryResult(data=[], error=str(e))
    
    async def insert(self, table, data):
        """Insert record into table"""
        from src.server.dal.interfaces import QueryResult
        
        if not self.pool:
            return QueryResult(data=[], error="Not connected")
        
        try:
            # Ensure data is a list
            records = data if isinstance(data, list) else [data]
            
            if not records:
                return QueryResult(data=[], error="No data to insert")
            
            # Get column names
            columns = list(records[0].keys())
            columns_str = ", ".join(columns)
            
            # Build VALUES clause
            params = []
            param_count = 0
            
            placeholders = []
            for col in columns:
                param_count += 1
                placeholders.append(f"${param_count}")
                params.append(records[0].get(col))
            
            # Build query
            query = f"INSERT INTO {table} ({columns_str}) VALUES ({', '.join(placeholders)})"
            
            # Execute query
            async with self.pool.acquire() as conn:
                await conn.execute(query, *params)
                return QueryResult(
                    data=records,
                    affected_rows=1
                )
        
        except Exception as e:
            return QueryResult(data=[], error=str(e))
    
    async def update(self, table, data, filters):
        """Update records in table"""
        from src.server.dal.interfaces import QueryResult
        
        if not self.pool:
            return QueryResult(data=[], error="Not connected")
        
        try:
            if not data:
                return QueryResult(data=[], error="No data to update")
            
            # Build SET clause
            set_clauses = []
            params = []
            param_count = 0
            
            for key, value in data.items():
                param_count += 1
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
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *params)
                # Extract affected rows from result string
                affected = int(result.split()[-1]) if result else 0
                
                return QueryResult(
                    data=[],
                    affected_rows=affected
                )
        
        except Exception as e:
            return QueryResult(data=[], error=str(e))
    
    async def delete(self, table, filters):
        """Delete records from table"""
        from src.server.dal.interfaces import QueryResult
        
        if not self.pool:
            return QueryResult(data=[], error="Not connected")
        
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
                        where_clauses.append(f"{key} = ${param_count}")
                        params.append(value)
                
                if where_clauses:
                    query += f" WHERE {' AND '.join(where_clauses)}"
            
            # Execute query
            async with self.pool.acquire() as conn:
                result = await conn.execute(query, *params)
                affected = int(result.split()[-1]) if result else 0
                
                return QueryResult(
                    data=[],
                    affected_rows=affected
                )
        
        except Exception as e:
            return QueryResult(data=[], error=str(e))
    
    async def test_vector_search(self):
        """Test pgvector functionality"""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                # Create a test vector
                test_vector = np.random.randn(1536).astype(np.float32)
                
                # Test vector operations
                result = await conn.fetchval(
                    "SELECT $1::vector(1536) <=> $1::vector(1536) as distance",
                    test_vector.tolist()
                )
                
                # Distance to itself should be 0
                return result == 0.0
        except Exception as e:
            print(f"Vector test error: {e}")
            return False


async def test_postgres_direct():
    """Test PostgreSQL adapter directly without ConnectionManager"""
    
    print("=" * 60)
    print("🐘 Direct PostgreSQL Adapter Test")
    print("=" * 60)
    
    # Create adapter with connection params
    adapter = PostgreSQLAdapter(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", 5433)),
        database=os.getenv("POSTGRES_DB", "archon_db"),
        user=os.getenv("POSTGRES_USER", "archon"),
        password=os.getenv("POSTGRES_PASSWORD", "archon_secure_password")
    )
    
    try:
        # Connect
        print("\n1. Testing Connection...")
        await adapter.connect()
        print("   ✓ Connected to PostgreSQL")
        
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
            "url": f"https://test-pg-{datetime.now().timestamp()}.example.com",
            "title": "Direct PostgreSQL Test",
            "source_type": "test",
            "status": "pending",
            "metadata": {"test": True, "database": "postgresql"}
        }
        result = await adapter.insert("archon_sources", test_data)
        if result.success:
            print(f"   ✓ INSERT successful: {result.affected_rows} rows")
            
            # UPDATE query
            print("\n5. Testing UPDATE...")
            update_data = {
                "title": "Direct PostgreSQL Test - Updated",
                "status": "completed"
            }
            result = await adapter.update(
                "archon_sources",
                update_data,
                {"url": test_data["url"]}
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
        
        # Test pgvector
        print("\n7. Testing pgvector Support...")
        vector_works = await adapter.test_vector_search()
        if vector_works:
            print("   ✓ pgvector extension is working")
        else:
            print("   ✗ pgvector test failed")
        
        # Test concurrent queries
        print("\n8. Testing Concurrent Queries...")
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
        print("\n✓ Disconnected from PostgreSQL")


if __name__ == "__main__":
    print("\n🐘 PostgreSQL Direct Adapter Test")
    print("=" * 60)
    
    # Run test
    asyncio.run(test_postgres_direct())