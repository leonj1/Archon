"""
Connection Manager for Database Abstraction Layer

Manages database connections, pooling, and adapter selection based on environment.
Supports multiple database backends with automatic failover and load balancing.
"""

import asyncio
import os
import random
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from ..config.logfire_config import search_logger
from .interfaces import IDatabase, IVectorStore


class DatabaseType(Enum):
    """Supported database types"""
    SUPABASE = "supabase"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class Environment(Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConnectionConfig:
    """Database connection configuration"""
    
    def __init__(
        self,
        database_type: DatabaseType,
        connection_params: Dict[str, Any],
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        idle_timeout: int = 3600,
        ssl_enabled: bool = False,
        ssl_config: Optional[Dict[str, Any]] = None,
    ):
        self.database_type = database_type
        self.connection_params = connection_params
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.idle_timeout = idle_timeout
        self.ssl_enabled = ssl_enabled
        self.ssl_config = ssl_config or {}
    
    @classmethod
    def from_env(cls, env_prefix: str = "") -> "ConnectionConfig":
        """
        Create configuration from environment variables
        
        Args:
            env_prefix: Prefix for environment variables (e.g., "READ_REPLICA_")
            
        Returns:
            ConnectionConfig instance
        """
        # Detect database type
        db_type_env = f"{env_prefix}DATABASE_TYPE" if env_prefix else "DATABASE_TYPE"
        db_type = DatabaseType(os.getenv(db_type_env, "supabase").lower())
        
        # Build connection parameters based on database type
        connection_params = {}
        
        if db_type == DatabaseType.SUPABASE:
            connection_params = {
                "url": os.getenv(f"{env_prefix}SUPABASE_URL"),
                "key": os.getenv(f"{env_prefix}SUPABASE_SERVICE_KEY"),
            }
        elif db_type == DatabaseType.POSTGRESQL:
            connection_params = {
                "connection_string": os.getenv(f"{env_prefix}DATABASE_URL"),
                "host": os.getenv(f"{env_prefix}POSTGRES_HOST", "localhost"),
                "port": int(os.getenv(f"{env_prefix}POSTGRES_PORT", "5432")),
                "database": os.getenv(f"{env_prefix}POSTGRES_DB"),
                "user": os.getenv(f"{env_prefix}POSTGRES_USER"),
                "password": os.getenv(f"{env_prefix}POSTGRES_PASSWORD"),
            }
        elif db_type == DatabaseType.MYSQL:
            connection_params = {
                "host": os.getenv(f"{env_prefix}MYSQL_HOST", "localhost"),
                "port": int(os.getenv(f"{env_prefix}MYSQL_PORT", "3306")),
                "database": os.getenv(f"{env_prefix}MYSQL_DATABASE"),
                "user": os.getenv(f"{env_prefix}MYSQL_USER"),
                "password": os.getenv(f"{env_prefix}MYSQL_PASSWORD"),
            }
        elif db_type == DatabaseType.SQLITE:
            connection_params = {
                "database_path": os.getenv(f"{env_prefix}SQLITE_PATH", "archon.db"),
            }
        
        # Pool configuration
        pool_size = int(os.getenv(f"{env_prefix}DB_POOL_SIZE", "10"))
        max_overflow = int(os.getenv(f"{env_prefix}DB_MAX_OVERFLOW", "20"))
        pool_timeout = int(os.getenv(f"{env_prefix}DB_POOL_TIMEOUT", "30"))
        idle_timeout = int(os.getenv(f"{env_prefix}DB_IDLE_TIMEOUT", "3600"))
        
        # SSL configuration
        ssl_enabled = os.getenv(f"{env_prefix}DB_SSL_ENABLED", "false").lower() == "true"
        ssl_config = {}
        if ssl_enabled:
            ssl_config = {
                "ca_cert": os.getenv(f"{env_prefix}DB_SSL_CA_CERT"),
                "client_cert": os.getenv(f"{env_prefix}DB_SSL_CLIENT_CERT"),
                "client_key": os.getenv(f"{env_prefix}DB_SSL_CLIENT_KEY"),
                "verify_mode": os.getenv(f"{env_prefix}DB_SSL_VERIFY_MODE", "required"),
            }
        
        return cls(
            database_type=db_type,
            connection_params=connection_params,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            idle_timeout=idle_timeout,
            ssl_enabled=ssl_enabled,
            ssl_config=ssl_config,
        )


class ConnectionPool:
    """Database connection pool manager"""
    
    def __init__(self, adapter: IDatabase, config: ConnectionConfig):
        self.adapter = adapter
        self.config = config
        self.connections: List[IDatabase] = []
        self.available_connections: asyncio.Queue = asyncio.Queue()
        self.in_use_connections: set = set()
        self.lock = asyncio.Lock()
        self.health_check_interval = 60  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        self._closed = False
    
    async def initialize(self):
        """Initialize the connection pool"""
        async with self.lock:
            # Create initial connections
            for _ in range(self.config.pool_size):
                conn = await self._create_connection()
                self.connections.append(conn)
                await self.available_connections.put(conn)
            
            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            search_logger.info(
                f"Connection pool initialized with {self.config.pool_size} connections "
                f"for {self.config.database_type.value}"
            )
    
    async def _create_connection(self) -> IDatabase:
        """Create a new database connection"""
        # This would create a new instance of the adapter
        # For now, we'll reuse the adapter instance
        # In a real implementation, each connection would be separate
        await self.adapter.connect()
        return self.adapter
    
    async def acquire(self, timeout: Optional[float] = None) -> IDatabase:
        """
        Acquire a connection from the pool
        
        Args:
            timeout: Maximum time to wait for a connection
            
        Returns:
            Database connection
            
        Raises:
            TimeoutError: If unable to acquire connection within timeout
        """
        timeout = timeout or self.config.pool_timeout
        
        try:
            conn = await asyncio.wait_for(
                self.available_connections.get(),
                timeout=timeout
            )
            async with self.lock:
                self.in_use_connections.add(conn)
            return conn
        except asyncio.TimeoutError:
            # Try to create a new connection if under max_overflow
            async with self.lock:
                total_connections = len(self.connections)
                if total_connections < self.config.pool_size + self.config.max_overflow:
                    conn = await self._create_connection()
                    self.connections.append(conn)
                    self.in_use_connections.add(conn)
                    search_logger.info(
                        f"Created overflow connection. Total: {total_connections + 1}"
                    )
                    return conn
            
            raise TimeoutError(
                f"Unable to acquire database connection within {timeout} seconds"
            )
    
    async def release(self, conn: IDatabase):
        """
        Release a connection back to the pool
        
        Args:
            conn: Connection to release
        """
        async with self.lock:
            if conn in self.in_use_connections:
                self.in_use_connections.remove(conn)
                
                # Check if connection is still healthy
                try:
                    if await conn.health_check():
                        await self.available_connections.put(conn)
                    else:
                        # Replace unhealthy connection
                        self.connections.remove(conn)
                        await conn.disconnect()
                        new_conn = await self._create_connection()
                        self.connections.append(new_conn)
                        await self.available_connections.put(new_conn)
                        search_logger.warning("Replaced unhealthy connection in pool")
                except Exception as e:
                    search_logger.error(f"Error checking connection health: {e}")
                    # Create new connection as fallback
                    try:
                        self.connections.remove(conn)
                        new_conn = await self._create_connection()
                        self.connections.append(new_conn)
                        await self.available_connections.put(new_conn)
                    except Exception as create_error:
                        search_logger.error(f"Failed to create replacement connection: {create_error}")
    
    async def _health_check_loop(self):
        """Periodically check health of idle connections"""
        while not self._closed:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_idle_connections()
            except Exception as e:
                search_logger.error(f"Error in health check loop: {e}")
    
    async def _check_idle_connections(self):
        """Check and refresh idle connections"""
        async with self.lock:
            # Get all available connections
            idle_connections = []
            while not self.available_connections.empty():
                try:
                    conn = self.available_connections.get_nowait()
                    idle_connections.append(conn)
                except asyncio.QueueEmpty:
                    break
            
            # Check each connection
            healthy_connections = []
            for conn in idle_connections:
                try:
                    if await conn.health_check():
                        healthy_connections.append(conn)
                    else:
                        # Replace unhealthy connection
                        self.connections.remove(conn)
                        await conn.disconnect()
                        new_conn = await self._create_connection()
                        self.connections.append(new_conn)
                        healthy_connections.append(new_conn)
                        search_logger.info("Replaced unhealthy idle connection")
                except Exception as e:
                    search_logger.error(f"Error checking idle connection: {e}")
            
            # Put healthy connections back
            for conn in healthy_connections:
                await self.available_connections.put(conn)
    
    async def close(self):
        """Close all connections in the pool"""
        self._closed = True
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        async with self.lock:
            # Close all connections
            for conn in self.connections:
                try:
                    await conn.disconnect()
                except Exception as e:
                    search_logger.error(f"Error closing connection: {e}")
            
            self.connections.clear()
            self.in_use_connections.clear()
            
            # Clear the queue
            while not self.available_connections.empty():
                try:
                    self.available_connections.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        search_logger.info("Connection pool closed")


class ConnectionManager:
    """
    Manages database connections and adapter selection.
    Supports multiple database backends with load balancing and failover.
    """
    
    # Registry of database adapters (to be populated by adapter implementations)
    ADAPTERS: Dict[DatabaseType, Type[IDatabase]] = {}
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.primary_pool: Optional[ConnectionPool] = None
        self.read_replica_pools: List[ConnectionPool] = []
        self.vector_pool: Optional[ConnectionPool] = None
        self._initialized = False
        self._round_robin_counter = 0
    
    @classmethod
    def register_adapter(cls, database_type: DatabaseType, adapter_class: Type[IDatabase]):
        """
        Register a database adapter
        
        Args:
            database_type: Type of database
            adapter_class: Adapter class implementing IDatabase
        """
        cls.ADAPTERS[database_type] = adapter_class
        search_logger.info(f"Registered adapter for {database_type.value}")
    
    def _detect_environment(self) -> Environment:
        """Detect current environment from environment variables"""
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        env_map = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "staging": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
        }
        
        return env_map.get(env, Environment.DEVELOPMENT)
    
    @classmethod
    def from_env(cls) -> "ConnectionManager":
        """
        Create connection manager from environment variables
        
        Returns:
            Configured ConnectionManager instance
        """
        manager = cls()
        
        # Configure primary database
        primary_config = ConnectionConfig.from_env()
        manager._setup_primary_pool(primary_config)
        
        # Configure read replicas if specified
        replica_count = int(os.getenv("READ_REPLICA_COUNT", "0"))
        for i in range(replica_count):
            replica_config = ConnectionConfig.from_env(f"READ_REPLICA_{i}_")
            manager._add_read_replica(replica_config)
        
        # Configure vector database if different from primary
        if os.getenv("VECTOR_DATABASE"):
            vector_config = manager._create_vector_config()
            manager._setup_vector_pool(vector_config)
        
        search_logger.info(
            f"ConnectionManager configured for {manager.environment.value} environment "
            f"with {len(manager.read_replica_pools)} read replicas"
        )
        
        return manager
    
    def _setup_primary_pool(self, config: ConnectionConfig):
        """Setup primary database connection pool"""
        adapter_class = self.ADAPTERS.get(config.database_type)
        if not adapter_class:
            # Fallback to Supabase adapter if available
            from .adapters.supabase_adapter import SupabaseAdapter
            self.register_adapter(DatabaseType.SUPABASE, SupabaseAdapter)
            adapter_class = SupabaseAdapter
        
        adapter = adapter_class(**config.connection_params)
        self.primary_pool = ConnectionPool(adapter, config)
    
    def _add_read_replica(self, config: ConnectionConfig):
        """Add a read replica connection pool"""
        adapter_class = self.ADAPTERS.get(config.database_type)
        if not adapter_class:
            search_logger.warning(f"No adapter found for {config.database_type.value}")
            return
        
        adapter = adapter_class(**config.connection_params)
        pool = ConnectionPool(adapter, config)
        self.read_replica_pools.append(pool)
    
    def _setup_vector_pool(self, config: ConnectionConfig):
        """Setup vector database connection pool"""
        adapter_class = self.ADAPTERS.get(config.database_type)
        if not adapter_class:
            search_logger.warning(f"No vector adapter found for {config.database_type.value}")
            return
        
        adapter = adapter_class(**config.connection_params)
        self.vector_pool = ConnectionPool(adapter, config)
    
    def _create_vector_config(self) -> ConnectionConfig:
        """Create configuration for external vector database"""
        vector_type = os.getenv("VECTOR_DATABASE", "").lower()
        
        if vector_type == "pinecone":
            return ConnectionConfig(
                database_type=DatabaseType.SUPABASE,  # Placeholder, need Pinecone type
                connection_params={
                    "api_key": os.getenv("PINECONE_API_KEY"),
                    "environment": os.getenv("PINECONE_ENVIRONMENT"),
                },
                pool_size=5,
            )
        elif vector_type == "weaviate":
            return ConnectionConfig(
                database_type=DatabaseType.SUPABASE,  # Placeholder, need Weaviate type
                connection_params={
                    "url": os.getenv("WEAVIATE_URL"),
                    "api_key": os.getenv("WEAVIATE_API_KEY"),
                },
                pool_size=5,
            )
        else:
            # Use primary database for vectors
            return ConnectionConfig.from_env()
    
    async def initialize(self):
        """Initialize all connection pools"""
        if self._initialized:
            return
        
        tasks = []
        
        if self.primary_pool:
            tasks.append(self.primary_pool.initialize())
        
        for pool in self.read_replica_pools:
            tasks.append(pool.initialize())
        
        if self.vector_pool and self.vector_pool != self.primary_pool:
            tasks.append(self.vector_pool.initialize())
        
        await asyncio.gather(*tasks)
        self._initialized = True
        
        search_logger.info("All connection pools initialized successfully")
    
    @asynccontextmanager
    async def get_primary(self):
        """
        Get primary database connection for writes
        
        Yields:
            Database connection
        """
        if not self.primary_pool:
            raise RuntimeError("No primary database configured")
        
        if not self._initialized:
            await self.initialize()
        
        conn = await self.primary_pool.acquire()
        try:
            yield conn
        finally:
            await self.primary_pool.release(conn)
    
    @asynccontextmanager
    async def get_reader(self):
        """
        Get database connection for reads with load balancing
        
        Yields:
            Database connection
        """
        if not self._initialized:
            await self.initialize()
        
        # Use read replicas if available, otherwise use primary
        if self.read_replica_pools:
            # Round-robin load balancing
            pool = self.read_replica_pools[
                self._round_robin_counter % len(self.read_replica_pools)
            ]
            self._round_robin_counter += 1
            
            try:
                conn = await pool.acquire()
                try:
                    yield conn
                finally:
                    await pool.release(conn)
            except Exception as e:
                search_logger.warning(f"Read replica failed, falling back to primary: {e}")
                # Fallback to primary
                async with self.get_primary() as conn:
                    yield conn
        else:
            # No read replicas, use primary
            async with self.get_primary() as conn:
                yield conn
    
    @asynccontextmanager
    async def get_vector_store(self):
        """
        Get vector store connection
        
        Yields:
            Vector store connection
        """
        if not self._initialized:
            await self.initialize()
        
        pool = self.vector_pool or self.primary_pool
        if not pool:
            raise RuntimeError("No vector store configured")
        
        conn = await pool.acquire()
        try:
            # Check if connection supports vector operations
            if not isinstance(conn, IVectorStore):
                raise RuntimeError(
                    f"Database {conn.__class__.__name__} does not support vector operations"
                )
            yield conn
        finally:
            await pool.release(conn)
    
    async def close(self):
        """Close all connection pools"""
        tasks = []
        
        if self.primary_pool:
            tasks.append(self.primary_pool.close())
        
        for pool in self.read_replica_pools:
            tasks.append(pool.close())
        
        if self.vector_pool and self.vector_pool != self.primary_pool:
            tasks.append(self.vector_pool.close())
        
        await asyncio.gather(*tasks)
        self._initialized = False
        
        search_logger.info("ConnectionManager closed all pools")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all connections
        
        Returns:
            Health status of all connection pools
        """
        status = {
            "environment": self.environment.value,
            "primary": None,
            "read_replicas": [],
            "vector": None,
        }
        
        # Check primary
        if self.primary_pool:
            try:
                async with self.get_primary() as conn:
                    status["primary"] = {
                        "healthy": await conn.health_check(),
                        "type": self.primary_pool.config.database_type.value,
                        "pool_size": len(self.primary_pool.connections),
                        "in_use": len(self.primary_pool.in_use_connections),
                    }
            except Exception as e:
                status["primary"] = {"healthy": False, "error": str(e)}
        
        # Check read replicas
        for i, pool in enumerate(self.read_replica_pools):
            try:
                conn = await pool.acquire(timeout=5)
                try:
                    replica_status = {
                        "healthy": await conn.health_check(),
                        "type": pool.config.database_type.value,
                        "pool_size": len(pool.connections),
                        "in_use": len(pool.in_use_connections),
                    }
                finally:
                    await pool.release(conn)
                status["read_replicas"].append(replica_status)
            except Exception as e:
                status["read_replicas"].append({"healthy": False, "error": str(e)})
        
        # Check vector store
        if self.vector_pool and self.vector_pool != self.primary_pool:
            try:
                async with self.get_vector_store() as conn:
                    status["vector"] = {
                        "healthy": await conn.health_check(),
                        "type": self.vector_pool.config.database_type.value,
                        "pool_size": len(self.vector_pool.connections),
                        "in_use": len(self.vector_pool.in_use_connections),
                    }
            except Exception as e:
                status["vector"] = {"healthy": False, "error": str(e)}
        
        return status


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """
    Get the global connection manager instance
    
    Returns:
        ConnectionManager instance
    """
    global _connection_manager
    if not _connection_manager:
        _connection_manager = ConnectionManager.from_env()
    return _connection_manager


async def initialize_connections():
    """Initialize all database connections"""
    manager = get_connection_manager()
    await manager.initialize()


async def close_connections():
    """Close all database connections"""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None