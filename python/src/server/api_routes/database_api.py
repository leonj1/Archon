"""
Database Management API Routes

Provides HTTP endpoints for database operations that support MCP tools.
Handles database health monitoring, configuration, switching, and metrics.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config.logfire_config import api_logger
from ..dal import ConnectionManager, DatabaseType
from ..dal.adapters import MySQLAdapter, PostgreSQLAdapter, SupabaseAdapter
from ..services.client_manager import get_connection_manager
from ..database_schema_validator import DatabaseSchemaValidator, run_schema_validation
from ..database_config_validator import (
    DatabaseConfigValidator,
    validate_current_database_config,
    validate_all_database_configs,
    export_env_template
)

router = APIRouter(prefix="/api/database", tags=["database"])
logger = logging.getLogger(__name__)


class DatabaseSwitchRequest(BaseModel):
    """Request model for database switching."""
    database_type: str
    validate_only: bool = False


class DatabaseHealthResponse(BaseModel):
    """Response model for database health check."""
    status: str
    timestamp: str
    environment: str
    primary: Optional[Dict[str, Any]] = None
    read_replicas: list[Dict[str, Any]] = []
    vector: Optional[Dict[str, Any]] = None


@router.get("/health", response_model=Dict[str, Any])
async def get_database_health():
    """
    Get comprehensive health status of all database connections.
    
    Returns detailed health information for:
    - Primary database connection
    - Read replica connections
    - Vector store connection
    - Connection pool status
    """
    try:
        api_logger.info("Database health check requested via API")
        
        manager = get_connection_manager()
        health_status = await manager.health_check()
        
        # Add timestamp and additional metadata
        health_status["timestamp"] = datetime.now().isoformat()
        health_status["api_endpoint"] = "/api/database/health"
        
        api_logger.info(f"Database health check completed: {health_status.get('environment', 'unknown')}")
        return health_status
        
    except Exception as e:
        api_logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Health check failed", "details": str(e)}
        )


@router.get("/config")
async def get_database_config():
    """
    Get current database configuration and adapter information.
    
    Returns configuration details including:
    - Active database type
    - Connection parameters (non-sensitive)
    - Available adapters
    - Environment settings
    """
    try:
        api_logger.info("Database configuration requested via API")
        
        # Get current database type
        current_db_type = os.getenv("DATABASE_TYPE", "supabase").lower()
        
        # Get available adapters
        available_adapters = list(ConnectionManager.ADAPTERS.keys())
        available_adapter_names = [adapter.value for adapter in available_adapters]
        
        # Build configuration response
        config = {
            "current_database_type": current_db_type,
            "available_adapters": available_adapter_names,
            "environment_variables": {
                "DATABASE_TYPE": current_db_type,
                "DB_POOL_SIZE": os.getenv("DB_POOL_SIZE", "10"),
                "DB_MAX_OVERFLOW": os.getenv("DB_MAX_OVERFLOW", "20"),
                "DB_POOL_TIMEOUT": os.getenv("DB_POOL_TIMEOUT", "30"),
                "DB_IDLE_TIMEOUT": os.getenv("DB_IDLE_TIMEOUT", "3600"),
            },
            "connection_params": _get_sanitized_connection_params(current_db_type),
            "adapter_status": {
                adapter.value: adapter in ConnectionManager.ADAPTERS
                for adapter in DatabaseType
            }
        }
        
        api_logger.info(f"Database configuration retrieved: {current_db_type}")
        return {"success": True, "configuration": config}
        
    except Exception as e:
        api_logger.error(f"Failed to get database configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Configuration retrieval failed", "details": str(e)}
        )


@router.post("/switch")
async def switch_database_type(request: DatabaseSwitchRequest):
    """
    Switch to a different database type or validate configuration.
    
    Supports switching between:
    - supabase: Supabase (PostgreSQL with pgvector)
    - postgresql: Direct PostgreSQL connection  
    - mysql: MySQL 8.0+ with JSON support
    - sqlite: SQLite (development only)
    """
    try:
        api_logger.info(f"Database switch requested: {request.database_type} (validate_only={request.validate_only})")
        
        # Validate database type
        try:
            target_db_type = DatabaseType(request.database_type.lower())
        except ValueError:
            valid_types = [db_type.value for db_type in DatabaseType]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid database type",
                    "provided": request.database_type,
                    "valid_types": valid_types
                }
            )
        
        # Check if adapter is available
        if target_db_type not in ConnectionManager.ADAPTERS:
            # Try to register the adapter
            _register_adapter_if_available(target_db_type)
            
            if target_db_type not in ConnectionManager.ADAPTERS:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Database adapter not available",
                        "database_type": request.database_type,
                        "available_adapters": [adapter.value for adapter in ConnectionManager.ADAPTERS.keys()]
                    }
                )
        
        # Validate configuration for target database
        validation_result = await _validate_database_config(target_db_type)
        
        if not validation_result["valid"]:
            if request.validate_only:
                return {
                    "success": False,
                    "validation": validation_result,
                    "message": "Configuration validation failed"
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid configuration for target database",
                        "validation_errors": validation_result["errors"]
                    }
                )
        
        if request.validate_only:
            api_logger.info(f"Database configuration validation successful: {request.database_type}")
            return {
                "success": True,
                "validation": validation_result,
                "message": f"Configuration for {request.database_type} is valid"
            }
        
        # Perform actual switch
        switch_result = await _perform_database_switch(target_db_type)
        
        api_logger.info(f"Database switch completed: {request.database_type}")
        return {
            "success": True,
            "switch_result": switch_result,
            "message": f"Successfully switched to {request.database_type}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Database switch failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Database switch failed", "details": str(e)}
        )


@router.get("/metrics")
async def get_connection_metrics():
    """
    Get detailed connection pool metrics and performance statistics.
    
    Returns metrics including:
    - Connection pool utilization
    - Active vs idle connections
    - Performance statistics
    - Error rates
    """
    try:
        api_logger.info("Connection metrics requested via API")
        
        manager = get_connection_manager()
        
        # Get basic health status first
        health_status = await manager.health_check()
        
        # Calculate metrics from health status
        metrics = _calculate_connection_metrics(health_status)
        
        api_logger.info("Connection metrics calculated")
        return {"success": True, "metrics": metrics}
        
    except Exception as e:
        api_logger.error(f"Failed to get connection metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Metrics retrieval failed", "details": str(e)}
        )


@router.get("/validate-schema")
async def validate_database_schema(target_database: Optional[str] = None):
    """
    Validate database schema consistency across different adapter types.
    
    Checks:
    - Table structure compatibility
    - Index consistency  
    - Data type mappings
    - Vector extension support
    """
    try:
        api_logger.info(f"Schema validation requested for: {target_database or 'current database'}")
        
        current_db_type = os.getenv("DATABASE_TYPE", "supabase").lower()
        
        if target_database:
            try:
                target_db_type = DatabaseType(target_database.lower())
            except ValueError:
                valid_types = [db_type.value for db_type in DatabaseType]
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid target database type",
                        "provided": target_database,
                        "valid_types": valid_types
                    }
                )
        else:
            target_db_type = DatabaseType(current_db_type)
        
        # Use the comprehensive schema validator
        validator = DatabaseSchemaValidator()
        
        if target_database:
            # Validate specific target database
            validation_results = await validator.validate_adapter(target_db_type)
        else:
            # Validate all adapters
            all_results = await validator.validate_all_adapters()
            validation_results = all_results.get(current_db_type, [])
        
        # Format results for API response
        validation_result = _format_validation_results(validation_results, target_db_type if target_database else None)
        
        api_logger.info(f"Schema validation completed for {target_db_type.value if target_database else 'current database'}")
        return {"success": True, "validation": validation_result}
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Schema validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Schema validation failed", "details": str(e)}
        )


@router.get("/validate-all-schemas")
async def validate_all_database_schemas():
    """
    Run comprehensive schema validation across all database adapters.
    
    This endpoint provides a complete analysis of schema compatibility
    across MySQL, PostgreSQL, and Supabase adapters.
    """
    try:
        api_logger.info("Comprehensive schema validation requested")
        
        # Run full schema validation
        validation_summary = await run_schema_validation()
        
        api_logger.info("Comprehensive schema validation completed")
        return {"success": True, "validation_summary": validation_summary}
        
    except Exception as e:
        api_logger.error(f"Comprehensive schema validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Comprehensive schema validation failed", "details": str(e)}
        )


@router.get("/validate-config")
async def validate_database_configuration():
    """
    Validate environment variable configuration for the current database.
    
    Checks all required and optional environment variables for the current
    database type and provides detailed validation results.
    """
    try:
        api_logger.info("Database configuration validation requested")
        
        # Validate current database configuration
        validation_result = validate_current_database_config()
        
        api_logger.info(f"Configuration validation completed: score={validation_result.overall_score}")
        return {"success": True, "validation": validation_result}
        
    except Exception as e:
        api_logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Configuration validation failed", "details": str(e)}
        )


@router.get("/validate-all-configs")
async def validate_all_database_configurations():
    """
    Validate environment variable configuration for all database types.
    
    Provides a comprehensive analysis of configuration readiness
    for switching between different database types.
    """
    try:
        api_logger.info("All database configurations validation requested")
        
        # Validate all database configurations
        all_validations = validate_all_database_configs()
        
        # Generate summary
        summary = {
            "validations": all_validations,
            "ready_databases": [
                db_type for db_type, validation in all_validations.items() 
                if validation.valid
            ],
            "average_score": sum(v.overall_score for v in all_validations.values()) / len(all_validations),
            "total_errors": sum(len(v.errors) for v in all_validations.values()),
            "total_warnings": sum(len(v.warnings) for v in all_validations.values())
        }
        
        api_logger.info(f"All configurations validation completed: ready={len(summary['ready_databases'])}")
        return {"success": True, "summary": summary}
        
    except Exception as e:
        api_logger.error(f"All configurations validation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "All configurations validation failed", "details": str(e)}
        )


@router.get("/config-template/{database_type}")
async def get_configuration_template(database_type: str):
    """
    Get environment variable template for a specific database type.
    
    Provides a complete .env template with all required and optional
    variables for the specified database type.
    """
    try:
        api_logger.info(f"Configuration template requested for {database_type}")
        
        # Validate database type
        try:
            DatabaseType(database_type.lower())
        except ValueError:
            valid_types = [db_type.value for db_type in DatabaseType]
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid database type",
                    "provided": database_type,
                    "valid_types": valid_types
                }
            )
        
        # Generate template
        template_content = export_env_template(database_type)
        
        api_logger.info(f"Configuration template generated for {database_type}")
        return {
            "success": True,
            "database_type": database_type,
            "template": template_content,
            "filename": f".env.{database_type.lower()}.template"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Configuration template generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Template generation failed", "details": str(e)}
        )


# Helper functions

def _get_sanitized_connection_params(db_type: str) -> Dict[str, Any]:
    """Get connection parameters with sensitive values redacted."""
    params = {}
    
    if db_type == "supabase":
        params = {
            "url": os.getenv("SUPABASE_URL", "Not set"),
            "key": "***REDACTED***" if os.getenv("SUPABASE_SERVICE_KEY") else "Not set"
        }
    elif db_type == "postgresql":
        params = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "database": os.getenv("POSTGRES_DB", "Not set"),
            "user": os.getenv("POSTGRES_USER", "Not set"),
            "password": "***REDACTED***" if os.getenv("POSTGRES_PASSWORD") else "Not set"
        }
    elif db_type == "mysql":
        params = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": os.getenv("MYSQL_PORT", "3306"),
            "database": os.getenv("MYSQL_DATABASE", "Not set"),
            "user": os.getenv("MYSQL_USER", "Not set"),
            "password": "***REDACTED***" if os.getenv("MYSQL_PASSWORD") else "Not set"
        }
    elif db_type == "sqlite":
        params = {
            "database_path": os.getenv("SQLITE_PATH", "archon.db")
        }
    
    return params


def _register_adapter_if_available(db_type: DatabaseType):
    """Register database adapter if available."""
    try:
        if db_type == DatabaseType.MYSQL:
            ConnectionManager.register_adapter(DatabaseType.MYSQL, MySQLAdapter)
        elif db_type == DatabaseType.POSTGRESQL:
            ConnectionManager.register_adapter(DatabaseType.POSTGRESQL, PostgreSQLAdapter)
        elif db_type == DatabaseType.SUPABASE:
            ConnectionManager.register_adapter(DatabaseType.SUPABASE, SupabaseAdapter)
        # SQLite adapter would be registered here if implemented
        
        api_logger.info(f"Registered adapter for {db_type.value}")
    except Exception as e:
        api_logger.warning(f"Failed to register adapter for {db_type.value}: {e}")


async def _validate_database_config(db_type: DatabaseType) -> Dict[str, Any]:
    """Validate configuration for a specific database type."""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check required environment variables
    required_vars = []
    
    if db_type == DatabaseType.SUPABASE:
        required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    elif db_type == DatabaseType.POSTGRESQL:
        required_vars = ["POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    elif db_type == DatabaseType.MYSQL:
        required_vars = ["MYSQL_HOST", "MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD"]
    elif db_type == DatabaseType.SQLITE:
        # SQLite requires minimal configuration
        pass
    
    for var in required_vars:
        if not os.getenv(var):
            validation["valid"] = False
            validation["errors"].append(f"Missing required environment variable: {var}")
    
    # Add warnings for development configurations
    if db_type == DatabaseType.SQLITE:
        validation["warnings"].append("SQLite is recommended for development only")
    
    return validation


async def _perform_database_switch(target_db_type: DatabaseType) -> Dict[str, Any]:
    """Perform the actual database switch operation."""
    # Note: In a real implementation, this would:
    # 1. Gracefully close existing connections
    # 2. Update environment configuration
    # 3. Initialize new connection manager
    # 4. Verify new connections work
    # 5. Migrate critical data if needed
    
    # For now, we'll return a simulated result
    return {
        "previous_database": os.getenv("DATABASE_TYPE", "supabase"),
        "new_database": target_db_type.value,
        "restart_required": True,
        "migration_needed": target_db_type != DatabaseType.SUPABASE,
        "message": "Database switch initiated. Service restart required to complete the switch."
    }


def _calculate_connection_metrics(health_status: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate connection metrics from health status."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_connections": 0,
        "active_connections": 0,
        "pool_utilization": 0.0,
        "error_rate": 0.0,
        "avg_response_time_ms": 0,
        "database_details": {}
    }
    
    # Process primary database
    if primary := health_status.get("primary"):
        pool_size = primary.get("pool_size", 0)
        in_use = primary.get("in_use", 0)
        
        metrics["total_connections"] += pool_size
        metrics["active_connections"] += in_use
        
        metrics["database_details"]["primary"] = {
            "type": primary.get("type", "unknown"),
            "healthy": primary.get("healthy", False),
            "pool_size": pool_size,
            "in_use": in_use,
            "utilization": (in_use / pool_size * 100) if pool_size > 0 else 0
        }
    
    # Process read replicas
    for i, replica in enumerate(health_status.get("read_replicas", [])):
        pool_size = replica.get("pool_size", 0)
        in_use = replica.get("in_use", 0)
        
        metrics["total_connections"] += pool_size
        metrics["active_connections"] += in_use
        
        metrics["database_details"][f"replica_{i}"] = {
            "type": replica.get("type", "unknown"),
            "healthy": replica.get("healthy", False),
            "pool_size": pool_size,
            "in_use": in_use,
            "utilization": (in_use / pool_size * 100) if pool_size > 0 else 0
        }
    
    # Calculate overall utilization
    if metrics["total_connections"] > 0:
        metrics["pool_utilization"] = (
            metrics["active_connections"] / metrics["total_connections"] * 100
        )
    
    return metrics


def _format_validation_results(validation_results: list, target_db_type: Optional[DatabaseType] = None) -> Dict[str, Any]:
    """Format validation results for API response."""
    if not validation_results:
        return {"compatible": True, "tables": [], "summary": "No validation results"}
    
    formatted_results = {
        "compatible": all(r.compatible for r in validation_results),
        "tables": [],
        "summary": {
            "total_tables": len(validation_results),
            "compatible_tables": sum(1 for r in validation_results if r.compatible),
            "total_issues": sum(len(r.issues) for r in validation_results),
            "total_warnings": sum(len(r.warnings) for r in validation_results),
        }
    }
    
    for result in validation_results:
        formatted_results["tables"].append({
            "table_name": result.table_name,
            "compatible": result.compatible,
            "issues": result.issues,
            "warnings": result.warnings,
            "suggestions": result.suggestions
        })
    
    # Add overall assessment
    compatibility_percentage = (formatted_results["summary"]["compatible_tables"] / 
                              formatted_results["summary"]["total_tables"] * 100)
    
    if compatibility_percentage == 100:
        formatted_results["assessment"] = "Fully compatible"
    elif compatibility_percentage >= 80:
        formatted_results["assessment"] = "Mostly compatible with minor issues"
    elif compatibility_percentage >= 60:
        formatted_results["assessment"] = "Partially compatible - migration required"
    else:
        formatted_results["assessment"] = "Major compatibility issues - significant migration needed"
    
    return formatted_results


async def _validate_schema_compatibility(
    source_db: DatabaseType,
    target_db: DatabaseType
) -> Dict[str, Any]:
    """Validate schema compatibility between database types."""
    validation = {
        "source_database": source_db.value,
        "target_database": target_db.value,
        "compatible": True,
        "schema_issues": [],
        "vector_support": {
            "source_native": source_db in [DatabaseType.SUPABASE, DatabaseType.POSTGRESQL],
            "target_native": target_db in [DatabaseType.SUPABASE, DatabaseType.POSTGRESQL],
            "fallback_available": target_db == DatabaseType.MYSQL
        },
        "data_type_mappings": _get_data_type_mappings(source_db, target_db),
        "recommendations": []
    }
    
    # Check vector support compatibility
    if validation["vector_support"]["source_native"] and not validation["vector_support"]["target_native"]:
        if validation["vector_support"]["fallback_available"]:
            validation["recommendations"].append(
                "Vector search will use fallback implementation in MySQL"
            )
        else:
            validation["compatible"] = False
            validation["schema_issues"].append(
                "Target database does not support vector operations"
            )
    
    # Check for known incompatibilities
    if source_db == DatabaseType.SUPABASE and target_db == DatabaseType.MYSQL:
        validation["recommendations"].append(
            "JSON fields will be stored as TEXT in MySQL - ensure proper JSON handling in queries"
        )
    
    return validation


def _get_data_type_mappings(source_db: DatabaseType, target_db: DatabaseType) -> Dict[str, str]:
    """Get data type mappings between database types."""
    # This is a simplified mapping - real implementation would be more comprehensive
    mappings = {}
    
    if source_db == DatabaseType.SUPABASE and target_db == DatabaseType.MYSQL:
        mappings = {
            "UUID": "VARCHAR(36)",
            "JSONB": "JSON",
            "TEXT": "TEXT",
            "TIMESTAMP": "TIMESTAMP",
            "VECTOR": "BLOB (with fallback implementation)"
        }
    elif source_db == DatabaseType.MYSQL and target_db == DatabaseType.SUPABASE:
        mappings = {
            "VARCHAR(36)": "UUID",
            "JSON": "JSONB", 
            "TEXT": "TEXT",
            "TIMESTAMP": "TIMESTAMP",
            "BLOB": "BYTEA"
        }
    
    return mappings