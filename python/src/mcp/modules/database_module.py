"""
Database Management Module for Archon MCP Server

This module provides tools for:
- Database health monitoring across all adapters
- Database switching and configuration
- Connection pool management
- Database type detection and validation

This version uses HTTP calls to the server service for database operations,
maintaining the microservices architecture.
"""

import json
import logging
import os
from typing import Any, Dict
from urllib.parse import urljoin

import httpx

from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP communication
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_database_tools(mcp: FastMCP):
    """Register all database management tools with the MCP server."""

    @mcp.tool()
    async def check_database_health(ctx: Context) -> str:
        """
        Check the health status of all database connections and adapters.
        
        This tool provides comprehensive health monitoring for:
        - Primary database connection
        - Read replica connections (if configured)
        - Vector store connection
        - Connection pool status
        - Adapter-specific health metrics
        
        Returns:
            JSON string with detailed health status for all database connections
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/database/health"))
                
                if response.status_code == 200:
                    health_data = response.json()
                    return json.dumps({
                        "success": True,
                        "health_status": health_data,
                        "timestamp": health_data.get("timestamp"),
                        "summary": _generate_health_summary(health_data)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Health check failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error checking database health: {e}")
            return json.dumps({
                "success": False,
                "error": f"Health check error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def get_database_config(ctx: Context) -> str:
        """
        Get current database configuration and adapter information.
        
        This tool returns:
        - Currently active database type
        - Connection parameters (non-sensitive)
        - Available database adapters
        - Environment configuration
        - Connection pool settings
        
        Returns:
            JSON string with current database configuration
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/database/config"))
                
                if response.status_code == 200:
                    config_data = response.json()
                    return json.dumps({
                        "success": True,
                        "configuration": config_data,
                        "recommendations": _generate_config_recommendations(config_data)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to get config: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error getting database config: {e}")
            return json.dumps({
                "success": False,
                "error": f"Config retrieval error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def switch_database_type(
        ctx: Context, 
        database_type: str,
        validate_only: bool = False
    ) -> str:
        """
        Switch to a different database type or validate the configuration.
        
        Supported database types:
        - "supabase": Supabase (PostgreSQL with pgvector)
        - "postgresql": Direct PostgreSQL connection
        - "mysql": MySQL 8.0+ with JSON support
        - "sqlite": SQLite (development only)
        
        Args:
            database_type: Target database type to switch to
            validate_only: If True, only validate configuration without switching
            
        Returns:
            JSON string with switch operation results
            
        Note: This operation may require environment variable updates and service restart.
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(60.0, connect=10.0)  # Longer timeout for switching
            
            request_data = {
                "database_type": database_type,
                "validate_only": validate_only
            }
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    urljoin(api_url, "/api/database/switch"),
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "operation": "validation" if validate_only else "switch",
                        "target_database": database_type,
                        "result": result,
                        "next_steps": _generate_switch_next_steps(result, validate_only)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Database switch failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error switching database: {e}")
            return json.dumps({
                "success": False,
                "error": f"Switch operation error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def get_connection_metrics(ctx: Context) -> str:
        """
        Get detailed connection pool metrics and performance statistics.
        
        This tool provides:
        - Connection pool utilization
        - Active vs idle connections
        - Connection latency metrics
        - Query performance statistics
        - Error rates and patterns
        
        Returns:
            JSON string with connection pool metrics and performance data
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/database/metrics"))
                
                if response.status_code == 200:
                    metrics_data = response.json()
                    return json.dumps({
                        "success": True,
                        "metrics": metrics_data,
                        "analysis": _analyze_connection_metrics(metrics_data),
                        "alerts": _generate_metric_alerts(metrics_data)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Metrics retrieval failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error getting connection metrics: {e}")
            return json.dumps({
                "success": False,
                "error": f"Metrics error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def validate_database_schema(
        ctx: Context,
        target_database: str = None
    ) -> str:
        """
        Validate database schema consistency across different adapter types.
        
        This tool checks:
        - Table structure compatibility
        - Index consistency
        - Data type mappings
        - Vector extension support
        - Migration requirements
        
        Args:
            target_database: Database type to validate against (optional)
            
        Returns:
            JSON string with schema validation results and migration recommendations
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(45.0, connect=10.0)
            
            params = {}
            if target_database:
                params["target_database"] = target_database
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    urljoin(api_url, "/api/database/validate-schema"),
                    params=params
                )
                
                if response.status_code == 200:
                    validation_data = response.json()
                    return json.dumps({
                        "success": True,
                        "validation": validation_data,
                        "compatibility": _assess_schema_compatibility(validation_data),
                        "migration_plan": _generate_migration_plan(validation_data)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Schema validation failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            return json.dumps({
                "success": False,
                "error": f"Schema validation error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def validate_database_config(ctx: Context) -> str:
        """
        Validate environment variable configuration for database connectivity.
        
        This tool validates all required and optional environment variables
        for the current database type and provides detailed recommendations
        for configuration improvements.
        
        Returns:
            JSON string with detailed validation results, scores, and recommendations
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/database/validate-config"))
                
                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "validation": result["validation"],
                        "summary": _generate_config_summary(result["validation"])
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Configuration validation failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error validating database configuration: {e}")
            return json.dumps({
                "success": False,
                "error": f"Configuration validation error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def validate_all_database_configs(ctx: Context) -> str:
        """
        Validate environment variable configuration for all database types.
        
        This tool provides a comprehensive analysis of configuration readiness
        for all supported database types (MySQL, PostgreSQL, Supabase).
        Useful for planning database switches and ensuring proper setup.
        
        Returns:
            JSON string with validation results for all database types
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, "/api/database/validate-all-configs"))
                
                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "summary": result["summary"],
                        "recommendations": _generate_multi_db_recommendations(result["summary"])
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"All configurations validation failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error validating all database configurations: {e}")
            return json.dumps({
                "success": False,
                "error": f"All configurations validation error: {str(e)}"
            }, indent=2)

    @mcp.tool()
    async def get_database_config_template(
        ctx: Context,
        database_type: str
    ) -> str:
        """
        Get environment variable template for a specific database type.
        
        This tool generates a complete .env template with all required and
        optional environment variables for the specified database type.
        Useful for setting up new database configurations.
        
        Args:
            database_type: Database type (mysql, postgresql, supabase)
            
        Returns:
            JSON string with template content and setup instructions
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(urljoin(api_url, f"/api/database/config-template/{database_type}"))
                
                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "database_type": result["database_type"],
                        "template": result["template"],
                        "filename": result["filename"],
                        "setup_instructions": _generate_setup_instructions(database_type)
                    }, indent=2)
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Template generation failed: HTTP {response.status_code}: {error_detail}"
                    }, indent=2)
                    
        except Exception as e:
            logger.error(f"Error getting database config template: {e}")
            return json.dumps({
                "success": False,
                "error": f"Template generation error: {str(e)}"
            }, indent=2)

    logger.info("✓ Database Management Module registered with 8 tools")


def _generate_health_summary(health_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a human-readable health summary."""
    summary = {
        "overall_status": "healthy",
        "warnings": [],
        "errors": [],
        "recommendations": []
    }
    
    # Analyze primary database
    if primary := health_data.get("primary"):
        if not primary.get("healthy", False):
            summary["overall_status"] = "unhealthy"
            summary["errors"].append("Primary database connection is unhealthy")
    
    # Analyze read replicas
    replicas = health_data.get("read_replicas", [])
    unhealthy_replicas = [r for r in replicas if not r.get("healthy", False)]
    if unhealthy_replicas:
        summary["warnings"].append(f"{len(unhealthy_replicas)} read replica(s) are unhealthy")
    
    # Connection pool analysis
    if primary and primary.get("in_use", 0) / max(primary.get("pool_size", 1), 1) > 0.8:
        summary["warnings"].append("High connection pool utilization detected")
        summary["recommendations"].append("Consider increasing connection pool size")
    
    return summary


def _generate_config_recommendations(config_data: Dict[str, Any]) -> list[str]:
    """Generate configuration recommendations based on current setup."""
    recommendations = []
    
    db_type = config_data.get("database_type", "").lower()
    
    if db_type == "mysql":
        recommendations.append("Consider enabling vector search fallback for improved performance")
        recommendations.append("Ensure MySQL 8.0+ is used for optimal JSON support")
    elif db_type == "postgresql":
        recommendations.append("Consider installing pgvector extension for native vector support")
    elif db_type == "sqlite":
        recommendations.append("SQLite is for development only - use PostgreSQL or MySQL in production")
    
    pool_size = config_data.get("pool_size", 0)
    if pool_size < 5:
        recommendations.append("Consider increasing connection pool size for better concurrency")
    
    return recommendations


def _generate_switch_next_steps(result: Dict[str, Any], validate_only: bool) -> list[str]:
    """Generate next steps after database switch operation."""
    if validate_only:
        if result.get("valid", False):
            return [
                "Configuration is valid",
                "Run with validate_only=False to perform the actual switch",
                "Ensure all required environment variables are set",
                "Consider backing up current data before switching"
            ]
        else:
            return [
                "Configuration validation failed",
                "Check and update required environment variables",
                "Verify database server is accessible",
                "Review error details for specific issues"
            ]
    else:
        return [
            "Database switch initiated",
            "Monitor application logs for connection status",
            "Test critical functionality after switch",
            "Run schema validation to ensure compatibility"
        ]


def _analyze_connection_metrics(metrics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze connection metrics and provide insights."""
    analysis = {
        "performance": "good",
        "utilization": "normal",
        "trends": []
    }
    
    # Analyze connection utilization
    total_connections = metrics_data.get("total_connections", 0)
    active_connections = metrics_data.get("active_connections", 0)
    
    if total_connections > 0:
        utilization_rate = active_connections / total_connections
        if utilization_rate > 0.9:
            analysis["utilization"] = "high"
            analysis["trends"].append("Very high connection utilization")
        elif utilization_rate > 0.7:
            analysis["utilization"] = "moderate"
            analysis["trends"].append("Moderate connection utilization")
    
    # Analyze error rates
    error_rate = metrics_data.get("error_rate", 0)
    if error_rate > 0.05:  # 5% error rate
        analysis["performance"] = "poor"
        analysis["trends"].append("High error rate detected")
    elif error_rate > 0.01:  # 1% error rate
        analysis["performance"] = "fair"
        analysis["trends"].append("Elevated error rate")
    
    return analysis


def _generate_metric_alerts(metrics_data: Dict[str, Any]) -> list[str]:
    """Generate alerts based on connection metrics."""
    alerts = []
    
    # Connection pool alerts
    pool_utilization = metrics_data.get("pool_utilization", 0)
    if pool_utilization > 90:
        alerts.append("CRITICAL: Connection pool utilization above 90%")
    elif pool_utilization > 80:
        alerts.append("WARNING: Connection pool utilization above 80%")
    
    # Error rate alerts
    error_rate = metrics_data.get("error_rate", 0)
    if error_rate > 0.1:  # 10% error rate
        alerts.append("CRITICAL: Database error rate above 10%")
    elif error_rate > 0.05:  # 5% error rate
        alerts.append("WARNING: Database error rate above 5%")
    
    # Response time alerts
    avg_response_time = metrics_data.get("avg_response_time_ms", 0)
    if avg_response_time > 1000:  # 1 second
        alerts.append("WARNING: Average response time above 1 second")
    
    return alerts


def _assess_schema_compatibility(validation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess schema compatibility between database types."""
    compatibility = {
        "level": "full",
        "issues": [],
        "warnings": []
    }
    
    schema_issues = validation_data.get("schema_issues", [])
    if schema_issues:
        compatibility["level"] = "partial"
        compatibility["issues"] = schema_issues
    
    vector_support = validation_data.get("vector_support", {})
    if not vector_support.get("native", False):
        compatibility["warnings"].append("Target database lacks native vector support")
    
    return compatibility


def _generate_migration_plan(validation_data: Dict[str, Any]) -> list[str]:
    """Generate a migration plan based on validation results."""
    plan = []
    
    schema_issues = validation_data.get("schema_issues", [])
    if schema_issues:
        plan.append("1. Review and resolve schema compatibility issues")
        plan.append("2. Create migration scripts for data type conversions")
    
    vector_support = validation_data.get("vector_support", {})
    if not vector_support.get("native", False):
        plan.append("3. Set up vector search fallback mechanisms")
        plan.append("4. Test vector similarity search functionality")
    
    plan.extend([
        f"{len(plan) + 1}. Backup current database before migration",
        f"{len(plan) + 2}. Perform test migration with sample data",
        f"{len(plan) + 3}. Execute full migration during maintenance window",
        f"{len(plan) + 4}. Validate data integrity after migration"
    ])
    
    return plan


def _generate_config_summary(validation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a configuration validation summary."""
    summary = {
        "database_type": validation_data.get("database_type", "unknown"),
        "overall_health": "excellent" if validation_data.get("overall_score", 0) >= 90 else
                         "good" if validation_data.get("overall_score", 0) >= 75 else
                         "fair" if validation_data.get("overall_score", 0) >= 50 else "poor",
        "score": validation_data.get("overall_score", 0),
        "critical_issues": len(validation_data.get("errors", [])),
        "warnings": len(validation_data.get("warnings", [])),
        "ready_for_production": validation_data.get("valid", False) and validation_data.get("overall_score", 0) >= 80
    }
    
    # Add quick recommendations
    if summary["critical_issues"] > 0:
        summary["priority_action"] = "Fix critical configuration errors before proceeding"
    elif summary["warnings"] > 0:
        summary["priority_action"] = "Address configuration warnings for optimal performance"
    else:
        summary["priority_action"] = "Configuration looks good - ready for use"
    
    return summary


def _generate_multi_db_recommendations(summary_data: Dict[str, Any]) -> List[str]:
    """Generate recommendations for multi-database configuration."""
    recommendations = []
    
    ready_databases = summary_data.get("ready_databases", [])
    total_errors = summary_data.get("total_errors", 0)
    average_score = summary_data.get("average_score", 0)
    
    if len(ready_databases) == 0:
        recommendations.append("No databases are properly configured - start with one database type first")
    elif len(ready_databases) == 1:
        recommendations.append(f"Only {ready_databases[0]} is configured - consider setting up backup database options")
    else:
        recommendations.append(f"Multiple databases configured ({', '.join(ready_databases)}) - good for flexibility")
    
    if total_errors > 0:
        recommendations.append(f"Fix {total_errors} configuration error(s) across all database types")
    
    if average_score < 70:
        recommendations.append("Overall configuration quality is low - review all database settings")
    elif average_score >= 90:
        recommendations.append("Excellent configuration quality across all database types")
    
    # Database-specific recommendations
    validations = summary_data.get("validations", {})
    
    if "mysql" in validations and validations["mysql"]["valid"]:
        recommendations.append("MySQL is ready - remember it uses fallback vector search")
    
    if "postgresql" in validations and validations["postgresql"]["valid"]:
        recommendations.append("PostgreSQL is ready - install pgvector for optimal vector support")
    
    if "supabase" in validations and validations["supabase"]["valid"]:
        recommendations.append("Supabase is ready - ensure proper RLS configuration for production")
    
    return recommendations


def _generate_setup_instructions(database_type: str) -> List[str]:
    """Generate setup instructions for a database type."""
    instructions = [
        f"1. Save the template as .env.{database_type}",
        "2. Fill in all required environment variables",
        "3. Copy to .env file for active use"
    ]
    
    if database_type == "mysql":
        instructions.extend([
            "4. Ensure MySQL 8.0+ is installed for JSON support",
            "5. Create database and user with appropriate permissions",
            "6. Test connection before switching DATABASE_TYPE"
        ])
    elif database_type == "postgresql":
        instructions.extend([
            "4. Install PostgreSQL 12+ with pgvector extension",
            "5. Create database and configure connection pooling",
            "6. Set up proper user permissions and SSL if needed"
        ])
    elif database_type == "supabase":
        instructions.extend([
            "4. Create new project at supabase.com",
            "5. Get project URL and service role key from settings",
            "6. Enable required database extensions (pgvector is included)"
        ])
    
    instructions.append("7. Use validate_database_config tool to verify setup")
    
    return instructions