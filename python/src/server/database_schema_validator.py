"""
Database Schema Validator for Multi-Database Support

This module validates schema consistency across MySQL, PostgreSQL, and Supabase adapters.
Ensures all adapters can work with the same data structures and operations.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .dal import ConnectionManager, DatabaseType
from .dal.adapters import MySQLAdapter, PostgreSQLAdapter, SupabaseAdapter

logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Standard field types across databases."""
    UUID = "uuid"
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"
    JSON = "json"
    VECTOR = "vector"
    BLOB = "blob"


@dataclass
class FieldDefinition:
    """Definition of a database field."""
    name: str
    field_type: FieldType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[Any] = None
    max_length: Optional[int] = None
    vector_dimensions: Optional[int] = None


@dataclass
class TableDefinition:
    """Definition of a database table."""
    name: str
    fields: List[FieldDefinition]
    indexes: List[Dict[str, Any]] = None
    constraints: List[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of schema validation."""
    table_name: str
    database_type: str
    compatible: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]


class ArchonSchemaDefinition:
    """Canonical schema definition for Archon database."""
    
    @classmethod
    def get_schema(cls) -> Dict[str, TableDefinition]:
        """Get the canonical Archon database schema."""
        return {
            "sources": TableDefinition(
                name="sources",
                fields=[
                    FieldDefinition("source_id", FieldType.TEXT, nullable=False, primary_key=True),
                    FieldDefinition("url", FieldType.TEXT, nullable=False),
                    FieldDefinition("domain", FieldType.TEXT, nullable=False),
                    FieldDefinition("title", FieldType.TEXT, nullable=True),
                    FieldDefinition("description", FieldType.TEXT, nullable=True),
                    FieldDefinition("content_summary", FieldType.TEXT, nullable=True),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("last_crawled", FieldType.TIMESTAMP, nullable=True),
                    FieldDefinition("metadata", FieldType.JSON, nullable=True),
                    FieldDefinition("tags", FieldType.JSON, nullable=True),
                    FieldDefinition("status", FieldType.TEXT, nullable=False, default="active"),
                    FieldDefinition("content_type", FieldType.TEXT, nullable=True),
                    FieldDefinition("language", FieldType.TEXT, nullable=True),
                    FieldDefinition("favicon_url", FieldType.TEXT, nullable=True),
                ],
                indexes=[
                    {"name": "idx_sources_domain", "columns": ["domain"]},
                    {"name": "idx_sources_status", "columns": ["status"]},
                    {"name": "idx_sources_created_at", "columns": ["created_at"]},
                ]
            ),
            
            "documents": TableDefinition(
                name="documents",
                fields=[
                    FieldDefinition("id", FieldType.UUID, nullable=False, primary_key=True),
                    FieldDefinition("source_id", FieldType.TEXT, nullable=False),
                    FieldDefinition("url", FieldType.TEXT, nullable=False),
                    FieldDefinition("title", FieldType.TEXT, nullable=True),
                    FieldDefinition("content", FieldType.TEXT, nullable=False),
                    FieldDefinition("summary", FieldType.TEXT, nullable=True),
                    FieldDefinition("chunk_number", FieldType.INTEGER, nullable=False, default=0),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("metadata", FieldType.JSON, nullable=True),
                    FieldDefinition("embedding", FieldType.VECTOR, nullable=True, vector_dimensions=1536),
                    FieldDefinition("keywords", FieldType.JSON, nullable=True),
                    FieldDefinition("language", FieldType.TEXT, nullable=True),
                    FieldDefinition("content_type", FieldType.TEXT, nullable=False, default="text"),
                ],
                indexes=[
                    {"name": "idx_documents_source_id", "columns": ["source_id"]},
                    {"name": "idx_documents_url", "columns": ["url"]},
                    {"name": "idx_documents_created_at", "columns": ["created_at"]},
                    {"name": "idx_documents_chunk_number", "columns": ["chunk_number"]},
                ]
            ),
            
            "settings": TableDefinition(
                name="settings",
                fields=[
                    FieldDefinition("id", FieldType.UUID, nullable=False, primary_key=True),
                    FieldDefinition("key", FieldType.TEXT, nullable=False, unique=True),
                    FieldDefinition("value", FieldType.TEXT, nullable=True),
                    FieldDefinition("encrypted_value", FieldType.TEXT, nullable=True),
                    FieldDefinition("is_encrypted", FieldType.BOOLEAN, nullable=False, default=False),
                    FieldDefinition("category", FieldType.TEXT, nullable=True),
                    FieldDefinition("description", FieldType.TEXT, nullable=True),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                ],
                indexes=[
                    {"name": "idx_settings_key", "columns": ["key"], "unique": True},
                    {"name": "idx_settings_category", "columns": ["category"]},
                ]
            ),
            
            "projects": TableDefinition(
                name="projects",
                fields=[
                    FieldDefinition("id", FieldType.UUID, nullable=False, primary_key=True),
                    FieldDefinition("title", FieldType.TEXT, nullable=False),
                    FieldDefinition("description", FieldType.TEXT, nullable=True),
                    FieldDefinition("status", FieldType.TEXT, nullable=False, default="active"),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("metadata", FieldType.JSON, nullable=True),
                    FieldDefinition("github_repo", FieldType.TEXT, nullable=True),
                    FieldDefinition("features", FieldType.JSON, nullable=True),
                    FieldDefinition("docs", FieldType.JSON, nullable=True),
                    FieldDefinition("version", FieldType.INTEGER, nullable=False, default=1),
                ],
                indexes=[
                    {"name": "idx_projects_status", "columns": ["status"]},
                    {"name": "idx_projects_created_at", "columns": ["created_at"]},
                ]
            ),
            
            "tasks": TableDefinition(
                name="tasks",
                fields=[
                    FieldDefinition("id", FieldType.UUID, nullable=False, primary_key=True),
                    FieldDefinition("project_id", FieldType.UUID, nullable=False),
                    FieldDefinition("title", FieldType.TEXT, nullable=False),
                    FieldDefinition("description", FieldType.TEXT, nullable=True),
                    FieldDefinition("status", FieldType.TEXT, nullable=False, default="todo"),
                    FieldDefinition("assignee", FieldType.TEXT, nullable=False, default="User"),
                    FieldDefinition("task_order", FieldType.INTEGER, nullable=False, default=0),
                    FieldDefinition("feature", FieldType.TEXT, nullable=True),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("metadata", FieldType.JSON, nullable=True),
                    FieldDefinition("sources", FieldType.JSON, nullable=True),
                    FieldDefinition("code_examples", FieldType.JSON, nullable=True),
                    FieldDefinition("estimated_hours", FieldType.FLOAT, nullable=True),
                ],
                indexes=[
                    {"name": "idx_tasks_project_id", "columns": ["project_id"]},
                    {"name": "idx_tasks_status", "columns": ["status"]},
                    {"name": "idx_tasks_assignee", "columns": ["assignee"]},
                    {"name": "idx_tasks_task_order", "columns": ["task_order"]},
                ]
            ),
            
            "code_examples": TableDefinition(
                name="code_examples",
                fields=[
                    FieldDefinition("id", FieldType.UUID, nullable=False, primary_key=True),
                    FieldDefinition("source_id", FieldType.TEXT, nullable=False),
                    FieldDefinition("file_path", FieldType.TEXT, nullable=False),
                    FieldDefinition("language", FieldType.TEXT, nullable=False),
                    FieldDefinition("code_content", FieldType.TEXT, nullable=False),
                    FieldDefinition("function_name", FieldType.TEXT, nullable=True),
                    FieldDefinition("class_name", FieldType.TEXT, nullable=True),
                    FieldDefinition("description", FieldType.TEXT, nullable=True),
                    FieldDefinition("created_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("updated_at", FieldType.TIMESTAMP, nullable=False),
                    FieldDefinition("metadata", FieldType.JSON, nullable=True),
                ],
                indexes=[
                    {"name": "idx_code_examples_source_id", "columns": ["source_id"]},
                    {"name": "idx_code_examples_language", "columns": ["language"]},
                    {"name": "idx_code_examples_function_name", "columns": ["function_name"]},
                ]
            ),
        }


class DatabaseSchemaValidator:
    """Validates database schema compatibility across different adapters."""
    
    def __init__(self):
        self.canonical_schema = ArchonSchemaDefinition.get_schema()
    
    async def validate_all_adapters(self) -> Dict[str, List[ValidationResult]]:
        """Validate schema compatibility for all registered adapters."""
        results = {}
        
        for db_type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
            if db_type in ConnectionManager.ADAPTERS:
                results[db_type.value] = await self.validate_adapter(db_type)
            else:
                logger.warning(f"Adapter for {db_type.value} not registered")
        
        return results
    
    async def validate_adapter(self, db_type: DatabaseType) -> List[ValidationResult]:
        """Validate schema compatibility for a specific adapter."""
        results = []
        
        for table_name, table_def in self.canonical_schema.items():
            result = await self._validate_table_for_adapter(table_def, db_type)
            results.append(result)
        
        return results
    
    async def _validate_table_for_adapter(
        self, 
        table_def: TableDefinition, 
        db_type: DatabaseType
    ) -> ValidationResult:
        """Validate a specific table for an adapter."""
        result = ValidationResult(
            table_name=table_def.name,
            database_type=db_type.value,
            compatible=True,
            issues=[],
            warnings=[],
            suggestions=[]
        )
        
        # Check field compatibility
        for field in table_def.fields:
            field_issues = self._validate_field_for_adapter(field, db_type)
            
            if field_issues["critical"]:
                result.compatible = False
                result.issues.extend(field_issues["critical"])
            
            result.warnings.extend(field_issues["warnings"])
            result.suggestions.extend(field_issues["suggestions"])
        
        # Check vector support
        vector_fields = [f for f in table_def.fields if f.field_type == FieldType.VECTOR]
        if vector_fields:
            vector_validation = self._validate_vector_support(db_type)
            
            if not vector_validation["supported"] and not vector_validation["fallback"]:
                result.compatible = False
                result.issues.append(f"Vector fields not supported and no fallback available")
            elif not vector_validation["supported"] and vector_validation["fallback"]:
                result.warnings.append(f"Vector fields will use fallback implementation")
                result.suggestions.append(f"Consider using native vector support for better performance")
        
        # Check JSON support
        json_fields = [f for f in table_def.fields if f.field_type == FieldType.JSON]
        if json_fields:
            json_validation = self._validate_json_support(db_type)
            
            if not json_validation["supported"]:
                result.compatible = False
                result.issues.append(f"JSON fields not supported")
            elif json_validation["limitations"]:
                result.warnings.extend(json_validation["limitations"])
        
        return result
    
    def _validate_field_for_adapter(self, field: FieldDefinition, db_type: DatabaseType) -> Dict[str, List[str]]:
        """Validate a specific field for an adapter."""
        issues = {"critical": [], "warnings": [], "suggestions": []}
        
        # Type mapping validation
        type_mapping = self._get_type_mapping(field.field_type, db_type)
        
        if not type_mapping["supported"]:
            issues["critical"].append(
                f"Field {field.name}: {field.field_type.value} not supported in {db_type.value}"
            )
        elif type_mapping["limitations"]:
            issues["warnings"].extend([
                f"Field {field.name}: {limitation}" 
                for limitation in type_mapping["limitations"]
            ])
        
        # UUID field validation
        if field.field_type == FieldType.UUID and field.primary_key:
            if db_type == DatabaseType.MYSQL:
                issues["suggestions"].append(
                    f"Field {field.name}: Consider using VARCHAR(36) for UUID in MySQL"
                )
        
        return issues
    
    def _get_type_mapping(self, field_type: FieldType, db_type: DatabaseType) -> Dict[str, Any]:
        """Get type mapping information for a field type and database."""
        mappings = {
            DatabaseType.MYSQL: {
                FieldType.UUID: {"supported": True, "native_type": "VARCHAR(36)", "limitations": ["No native UUID type"]},
                FieldType.TEXT: {"supported": True, "native_type": "TEXT", "limitations": []},
                FieldType.INTEGER: {"supported": True, "native_type": "INT", "limitations": []},
                FieldType.FLOAT: {"supported": True, "native_type": "FLOAT", "limitations": []},
                FieldType.BOOLEAN: {"supported": True, "native_type": "BOOLEAN", "limitations": []},
                FieldType.TIMESTAMP: {"supported": True, "native_type": "TIMESTAMP", "limitations": []},
                FieldType.JSON: {"supported": True, "native_type": "JSON", "limitations": ["Requires MySQL 5.7+"]},
                FieldType.VECTOR: {"supported": False, "native_type": "BLOB", "limitations": ["No native vector support"]},
                FieldType.BLOB: {"supported": True, "native_type": "BLOB", "limitations": []},
            },
            DatabaseType.POSTGRESQL: {
                FieldType.UUID: {"supported": True, "native_type": "UUID", "limitations": []},
                FieldType.TEXT: {"supported": True, "native_type": "TEXT", "limitations": []},
                FieldType.INTEGER: {"supported": True, "native_type": "INTEGER", "limitations": []},
                FieldType.FLOAT: {"supported": True, "native_type": "REAL", "limitations": []},
                FieldType.BOOLEAN: {"supported": True, "native_type": "BOOLEAN", "limitations": []},
                FieldType.TIMESTAMP: {"supported": True, "native_type": "TIMESTAMP", "limitations": []},
                FieldType.JSON: {"supported": True, "native_type": "JSONB", "limitations": []},
                FieldType.VECTOR: {"supported": True, "native_type": "VECTOR", "limitations": ["Requires pgvector extension"]},
                FieldType.BLOB: {"supported": True, "native_type": "BYTEA", "limitations": []},
            },
            DatabaseType.SUPABASE: {
                FieldType.UUID: {"supported": True, "native_type": "UUID", "limitations": []},
                FieldType.TEXT: {"supported": True, "native_type": "TEXT", "limitations": []},
                FieldType.INTEGER: {"supported": True, "native_type": "INTEGER", "limitations": []},
                FieldType.FLOAT: {"supported": True, "native_type": "REAL", "limitations": []},
                FieldType.BOOLEAN: {"supported": True, "native_type": "BOOLEAN", "limitations": []},
                FieldType.TIMESTAMP: {"supported": True, "native_type": "TIMESTAMP", "limitations": []},
                FieldType.JSON: {"supported": True, "native_type": "JSONB", "limitations": []},
                FieldType.VECTOR: {"supported": True, "native_type": "VECTOR", "limitations": []},
                FieldType.BLOB: {"supported": True, "native_type": "BYTEA", "limitations": []},
            },
        }
        
        return mappings.get(db_type, {}).get(field_type, {"supported": False, "limitations": ["Unknown type"]})
    
    def _validate_vector_support(self, db_type: DatabaseType) -> Dict[str, bool]:
        """Validate vector support for a database type."""
        support_matrix = {
            DatabaseType.MYSQL: {"supported": False, "fallback": True},
            DatabaseType.POSTGRESQL: {"supported": True, "fallback": False},
            DatabaseType.SUPABASE: {"supported": True, "fallback": False},
        }
        
        return support_matrix.get(db_type, {"supported": False, "fallback": False})
    
    def _validate_json_support(self, db_type: DatabaseType) -> Dict[str, Any]:
        """Validate JSON support for a database type."""
        support_matrix = {
            DatabaseType.MYSQL: {
                "supported": True, 
                "limitations": ["Requires MySQL 5.7+", "Different query syntax than PostgreSQL"]
            },
            DatabaseType.POSTGRESQL: {
                "supported": True, 
                "limitations": []
            },
            DatabaseType.SUPABASE: {
                "supported": True, 
                "limitations": []
            },
        }
        
        return support_matrix.get(db_type, {"supported": False, "limitations": ["JSON not supported"]})
    
    def generate_migration_script(self, source_db: DatabaseType, target_db: DatabaseType) -> str:
        """Generate a migration script between database types."""
        script_lines = [
            f"-- Migration script from {source_db.value} to {target_db.value}",
            f"-- Generated by Archon Database Schema Validator",
            "",
        ]
        
        for table_name, table_def in self.canonical_schema.items():
            script_lines.append(f"-- Table: {table_name}")
            script_lines.append(self._generate_create_table_sql(table_def, target_db))
            script_lines.append("")
        
        return "\n".join(script_lines)
    
    def _generate_create_table_sql(self, table_def: TableDefinition, db_type: DatabaseType) -> str:
        """Generate CREATE TABLE SQL for a specific database type."""
        fields_sql = []
        
        for field in table_def.fields:
            field_sql = self._generate_field_sql(field, db_type)
            fields_sql.append(field_sql)
        
        # Add constraints
        constraints = []
        for field in table_def.fields:
            if field.primary_key:
                constraints.append(f"PRIMARY KEY ({field.name})")
            if field.unique and not field.primary_key:
                constraints.append(f"UNIQUE ({field.name})")
        
        all_fields = fields_sql + constraints
        
        if db_type == DatabaseType.MYSQL:
            table_name = f"`{table_def.name}`"
        else:
            table_name = table_def.name
        
        return f"CREATE TABLE {table_name} (\n    " + ",\n    ".join(all_fields) + "\n);"
    
    def _generate_field_sql(self, field: FieldDefinition, db_type: DatabaseType) -> str:
        """Generate SQL for a specific field."""
        type_mapping = self._get_type_mapping(field.field_type, db_type)
        native_type = type_mapping.get("native_type", "TEXT")
        
        # Handle vector dimensions
        if field.field_type == FieldType.VECTOR and field.vector_dimensions:
            if db_type in [DatabaseType.POSTGRESQL, DatabaseType.SUPABASE]:
                native_type = f"VECTOR({field.vector_dimensions})"
        
        # Handle text max length
        if field.field_type == FieldType.TEXT and field.max_length:
            if db_type == DatabaseType.MYSQL:
                native_type = f"VARCHAR({field.max_length})"
            else:
                native_type = f"VARCHAR({field.max_length})"
        
        field_sql = f"{field.name} {native_type}"
        
        if not field.nullable:
            field_sql += " NOT NULL"
        
        if field.default is not None:
            if isinstance(field.default, str):
                field_sql += f" DEFAULT '{field.default}'"
            else:
                field_sql += f" DEFAULT {field.default}"
        
        return field_sql


async def run_schema_validation() -> Dict[str, Any]:
    """Run complete schema validation for all adapters."""
    logger.info("Starting database schema validation...")
    
    # Register all adapters
    ConnectionManager.register_adapter(DatabaseType.MYSQL, MySQLAdapter)
    ConnectionManager.register_adapter(DatabaseType.POSTGRESQL, PostgreSQLAdapter)
    ConnectionManager.register_adapter(DatabaseType.SUPABASE, SupabaseAdapter)
    
    validator = DatabaseSchemaValidator()
    results = await validator.validate_all_adapters()
    
    # Generate summary
    summary = {
        "validation_results": results,
        "overall_compatibility": {},
        "recommendations": [],
        "migration_required": {}
    }
    
    for db_type, table_results in results.items():
        compatible_tables = sum(1 for r in table_results if r.compatible)
        total_tables = len(table_results)
        
        summary["overall_compatibility"][db_type] = {
            "compatible_tables": compatible_tables,
            "total_tables": total_tables,
            "compatibility_percentage": (compatible_tables / total_tables * 100) if total_tables > 0 else 0
        }
        
        # Check if migration is needed
        has_issues = any(r.issues for r in table_results)
        summary["migration_required"][db_type] = has_issues
        
        # Collect recommendations
        all_issues = [issue for r in table_results for issue in r.issues]
        all_warnings = [warning for r in table_results for warning in r.warnings]
        
        if all_issues:
            summary["recommendations"].append(
                f"{db_type}: Critical issues found - {len(all_issues)} issues across tables"
            )
        if all_warnings:
            summary["recommendations"].append(
                f"{db_type}: {len(all_warnings)} warnings - review for optimal performance"
            )
    
    logger.info("Schema validation completed")
    return summary


if __name__ == "__main__":
    asyncio.run(run_schema_validation())