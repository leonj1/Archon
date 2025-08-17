"""
Database Configuration Validator

Validates environment variables and configuration for all database adapters.
Ensures proper configuration before attempting database connections.
"""

import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .dal import DatabaseType

logger = logging.getLogger(__name__)


class ConfigSeverity(Enum):
    """Configuration validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ConfigValidationResult:
    """Result of a configuration validation check."""
    field: str
    severity: ConfigSeverity
    message: str
    current_value: Optional[str] = None
    recommended_value: Optional[str] = None
    documentation_link: Optional[str] = None


@dataclass
class DatabaseConfigValidation:
    """Complete validation result for a database configuration."""
    database_type: str
    valid: bool
    errors: List[ConfigValidationResult]
    warnings: List[ConfigValidationResult]
    info: List[ConfigValidationResult]
    overall_score: int  # 0-100 score
    recommendations: List[str]


class DatabaseConfigValidator:
    """Validates database configuration for all supported database types."""
    
    def __init__(self):
        self.validation_rules = self._build_validation_rules()
    
    def validate_all_databases(self) -> Dict[str, DatabaseConfigValidation]:
        """Validate configuration for all database types."""
        results = {}
        
        for db_type in DatabaseType:
            results[db_type.value] = self.validate_database(db_type)
        
        return results
    
    def validate_database(self, db_type: DatabaseType) -> DatabaseConfigValidation:
        """Validate configuration for a specific database type."""
        logger.info(f"Validating configuration for {db_type.value}")
        
        results = []
        rules = self.validation_rules.get(db_type, [])
        
        for rule in rules:
            result = self._apply_validation_rule(rule)
            if result:
                results.append(result)
        
        # Categorize results
        errors = [r for r in results if r.severity == ConfigSeverity.ERROR]
        warnings = [r for r in results if r.severity == ConfigSeverity.WARNING]
        info = [r for r in results if r.severity == ConfigSeverity.INFO]
        
        # Calculate overall score
        total_checks = len(rules)
        error_count = len(errors)
        warning_count = len(warnings)
        
        if total_checks == 0:
            score = 100
        else:
            # Errors are weighted more heavily than warnings
            penalty = (error_count * 20) + (warning_count * 5)
            score = max(0, 100 - penalty)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(db_type, errors, warnings)
        
        validation = DatabaseConfigValidation(
            database_type=db_type.value,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            overall_score=score,
            recommendations=recommendations
        )
        
        logger.info(f"Configuration validation for {db_type.value}: score={score}, valid={validation.valid}")
        return validation
    
    def get_current_database_validation(self) -> DatabaseConfigValidation:
        """Validate configuration for the currently active database."""
        current_db_type = os.getenv("DATABASE_TYPE", "supabase").lower()
        
        try:
            db_type = DatabaseType(current_db_type)
            return self.validate_database(db_type)
        except ValueError:
            # Invalid database type
            error_result = ConfigValidationResult(
                field="DATABASE_TYPE",
                severity=ConfigSeverity.ERROR,
                message=f"Invalid database type: {current_db_type}",
                current_value=current_db_type,
                recommended_value="supabase"
            )
            
            return DatabaseConfigValidation(
                database_type=current_db_type,
                valid=False,
                errors=[error_result],
                warnings=[],
                info=[],
                overall_score=0,
                recommendations=["Set DATABASE_TYPE to a valid value: supabase, postgresql, mysql"]
            )
    
    def _build_validation_rules(self) -> Dict[DatabaseType, List[Dict[str, Any]]]:
        """Build validation rules for each database type."""
        return {
            DatabaseType.SUPABASE: [
                {
                    "field": "SUPABASE_URL",
                    "required": True,
                    "validator": self._validate_supabase_url,
                    "description": "Supabase project URL"
                },
                {
                    "field": "SUPABASE_SERVICE_KEY", 
                    "required": True,
                    "validator": self._validate_supabase_key,
                    "description": "Supabase service role key"
                },
                {
                    "field": "DATABASE_TYPE",
                    "required": True,
                    "validator": lambda v: self._validate_enum_value(v, ["supabase"]),
                    "description": "Database type should be 'supabase'"
                }
            ],
            
            DatabaseType.POSTGRESQL: [
                {
                    "field": "POSTGRES_HOST",
                    "required": True,
                    "validator": self._validate_hostname,
                    "description": "PostgreSQL server hostname"
                },
                {
                    "field": "POSTGRES_PORT",
                    "required": False,
                    "validator": self._validate_port,
                    "description": "PostgreSQL server port",
                    "default": "5432"
                },
                {
                    "field": "POSTGRES_DB",
                    "required": True,
                    "validator": self._validate_database_name,
                    "description": "PostgreSQL database name"
                },
                {
                    "field": "POSTGRES_USER",
                    "required": True,
                    "validator": self._validate_username,
                    "description": "PostgreSQL username"
                },
                {
                    "field": "POSTGRES_PASSWORD",
                    "required": True,
                    "validator": self._validate_password,
                    "description": "PostgreSQL password"
                },
                {
                    "field": "DATABASE_TYPE",
                    "required": True,
                    "validator": lambda v: self._validate_enum_value(v, ["postgresql"]),
                    "description": "Database type should be 'postgresql'"
                }
            ],
            
            DatabaseType.MYSQL: [
                {
                    "field": "MYSQL_HOST",
                    "required": True,
                    "validator": self._validate_hostname,
                    "description": "MySQL server hostname"
                },
                {
                    "field": "MYSQL_PORT",
                    "required": False,
                    "validator": self._validate_port,
                    "description": "MySQL server port",
                    "default": "3306"
                },
                {
                    "field": "MYSQL_DATABASE",
                    "required": True,
                    "validator": self._validate_database_name,
                    "description": "MySQL database name"
                },
                {
                    "field": "MYSQL_USER",
                    "required": True,
                    "validator": self._validate_username,
                    "description": "MySQL username"
                },
                {
                    "field": "MYSQL_PASSWORD",
                    "required": True,
                    "validator": self._validate_password,
                    "description": "MySQL password"
                },
                {
                    "field": "DATABASE_TYPE",
                    "required": True,
                    "validator": lambda v: self._validate_enum_value(v, ["mysql"]),
                    "description": "Database type should be 'mysql'"
                }
            ]
        }
    
    def _apply_validation_rule(self, rule: Dict[str, Any]) -> Optional[ConfigValidationResult]:
        """Apply a single validation rule."""
        field = rule["field"]
        required = rule.get("required", False)
        validator = rule.get("validator")
        description = rule.get("description", "")
        default = rule.get("default")
        
        current_value = os.getenv(field)
        
        # Check if required field is missing
        if required and not current_value:
            return ConfigValidationResult(
                field=field,
                severity=ConfigSeverity.ERROR,
                message=f"Required environment variable {field} is not set",
                current_value=None,
                recommended_value=default or "Please set this value",
                documentation_link=self._get_documentation_link(field)
            )
        
        # Check if optional field has default
        if not required and not current_value and default:
            return ConfigValidationResult(
                field=field,
                severity=ConfigSeverity.INFO,
                message=f"Using default value for {field}",
                current_value=None,
                recommended_value=default,
                documentation_link=self._get_documentation_link(field)
            )
        
        # Validate field value if present and validator exists
        if current_value and validator:
            validation_result = validator(current_value)
            
            if not validation_result["valid"]:
                return ConfigValidationResult(
                    field=field,
                    severity=validation_result.get("severity", ConfigSeverity.ERROR),
                    message=validation_result["message"],
                    current_value=current_value,
                    recommended_value=validation_result.get("recommended"),
                    documentation_link=self._get_documentation_link(field)
                )
        
        return None
    
    def _validate_supabase_url(self, value: str) -> Dict[str, Any]:
        """Validate Supabase URL format."""
        pattern = r"https://[a-zA-Z0-9-]+\.supabase\.co"
        
        if not re.match(pattern, value):
            return {
                "valid": False,
                "message": "Invalid Supabase URL format",
                "recommended": "https://your-project.supabase.co"
            }
        
        return {"valid": True}
    
    def _validate_supabase_key(self, value: str) -> Dict[str, Any]:
        """Validate Supabase service key format."""
        # Service keys typically start with 'eyJ' (JWT format)
        if not value.startswith("eyJ") or len(value) < 100:
            return {
                "valid": False,
                "severity": ConfigSeverity.WARNING,
                "message": "Supabase key format appears invalid - should be a JWT token",
                "recommended": "Check your Supabase project settings for the correct service role key"
            }
        
        return {"valid": True}
    
    def _validate_hostname(self, value: str) -> Dict[str, Any]:
        """Validate hostname or IP address."""
        # Basic hostname/IP validation
        if not value or len(value) > 255:
            return {
                "valid": False,
                "message": "Invalid hostname length",
                "recommended": "localhost or valid hostname/IP"
            }
        
        # Check for valid characters
        if not re.match(r"^[a-zA-Z0-9.-]+$", value):
            return {
                "valid": False,
                "message": "Hostname contains invalid characters",
                "recommended": "Use only alphanumeric characters, dots, and hyphens"
            }
        
        return {"valid": True}
    
    def _validate_port(self, value: str) -> Dict[str, Any]:
        """Validate port number."""
        try:
            port = int(value)
            if port < 1 or port > 65535:
                return {
                    "valid": False,
                    "message": "Port number out of valid range (1-65535)",
                    "recommended": "Use a port between 1 and 65535"
                }
        except ValueError:
            return {
                "valid": False,
                "message": "Port must be a number",
                "recommended": "Use a numeric port value"
            }
        
        return {"valid": True}
    
    def _validate_database_name(self, value: str) -> Dict[str, Any]:
        """Validate database name."""
        if not value:
            return {
                "valid": False,
                "message": "Database name cannot be empty"
            }
        
        # Basic database name validation
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            return {
                "valid": False,
                "message": "Database name contains invalid characters",
                "recommended": "Use only alphanumeric characters and underscores"
            }
        
        if len(value) > 64:
            return {
                "valid": False,
                "message": "Database name too long (max 64 characters)",
                "recommended": "Shorten the database name"
            }
        
        return {"valid": True}
    
    def _validate_username(self, value: str) -> Dict[str, Any]:
        """Validate database username."""
        if not value:
            return {
                "valid": False,
                "message": "Username cannot be empty"
            }
        
        if len(value) > 32:
            return {
                "valid": False,
                "message": "Username too long (max 32 characters)",
                "recommended": "Shorten the username"
            }
        
        return {"valid": True}
    
    def _validate_password(self, value: str) -> Dict[str, Any]:
        """Validate database password."""
        if not value:
            return {
                "valid": False,
                "message": "Password cannot be empty"
            }
        
        if len(value) < 8:
            return {
                "valid": False,
                "severity": ConfigSeverity.WARNING,
                "message": "Password is shorter than recommended (8+ characters)",
                "recommended": "Use a longer password for better security"
            }
        
        return {"valid": True}
    
    def _validate_enum_value(self, value: str, valid_values: List[str]) -> Dict[str, Any]:
        """Validate that value is one of the allowed enum values."""
        if value not in valid_values:
            return {
                "valid": False,
                "message": f"Invalid value. Must be one of: {', '.join(valid_values)}",
                "recommended": valid_values[0]
            }
        
        return {"valid": True}
    
    def _generate_recommendations(
        self, 
        db_type: DatabaseType, 
        errors: List[ConfigValidationResult],
        warnings: List[ConfigValidationResult]
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if errors:
            recommendations.append(f"Fix {len(errors)} critical configuration error(s) before using {db_type.value}")
            
            # Specific recommendations for common errors
            missing_fields = [e.field for e in errors if "not set" in e.message]
            if missing_fields:
                recommendations.append(f"Set required environment variables: {', '.join(missing_fields)}")
        
        if warnings:
            recommendations.append(f"Address {len(warnings)} configuration warning(s) for optimal performance")
        
        # Database-specific recommendations
        if db_type == DatabaseType.MYSQL:
            recommendations.append("Ensure MySQL 8.0+ for optimal JSON support")
            recommendations.append("Consider enabling slow query log for performance monitoring")
        elif db_type == DatabaseType.POSTGRESQL:
            recommendations.append("Install pgvector extension for native vector support")
            recommendations.append("Configure connection pooling for production use")
        elif db_type == DatabaseType.SUPABASE:
            recommendations.append("Use service role key, not anon key, for backend operations")
            recommendations.append("Enable RLS (Row Level Security) for production applications")
        
        # General recommendations
        if not errors and not warnings:
            recommendations.append("Configuration looks good! Consider setting up monitoring and backups")
        
        return recommendations
    
    def _get_documentation_link(self, field: str) -> Optional[str]:
        """Get documentation link for a configuration field."""
        doc_links = {
            "SUPABASE_URL": "https://supabase.com/docs/guides/database",
            "SUPABASE_SERVICE_KEY": "https://supabase.com/docs/guides/api/api-keys",
            "POSTGRES_HOST": "https://www.postgresql.org/docs/current/runtime-config-connection.html",
            "MYSQL_HOST": "https://dev.mysql.com/doc/refman/8.0/en/connecting.html",
        }
        
        return doc_links.get(field)
    
    def generate_configuration_report(self, validations: Dict[str, DatabaseConfigValidation]) -> str:
        """Generate a human-readable configuration report."""
        report_lines = [
            "Database Configuration Validation Report",
            "=" * 50,
            ""
        ]
        
        for db_type, validation in validations.items():
            report_lines.extend([
                f"Database: {db_type.upper()}",
                "-" * 30,
                f"Overall Score: {validation.overall_score}/100",
                f"Status: {'✓ Valid' if validation.valid else '✗ Invalid'}",
                ""
            ])
            
            if validation.errors:
                report_lines.append("Errors:")
                for error in validation.errors:
                    report_lines.append(f"  • {error.field}: {error.message}")
                report_lines.append("")
            
            if validation.warnings:
                report_lines.append("Warnings:")
                for warning in validation.warnings:
                    report_lines.append(f"  • {warning.field}: {warning.message}")
                report_lines.append("")
            
            if validation.recommendations:
                report_lines.append("Recommendations:")
                for rec in validation.recommendations:
                    report_lines.append(f"  • {rec}")
                report_lines.append("")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def export_configuration_template(self, db_type: DatabaseType) -> str:
        """Export a .env template for a specific database type."""
        rules = self.validation_rules.get(db_type, [])
        
        template_lines = [
            f"# Database Configuration Template for {db_type.value.upper()}",
            f"# Generated by Archon Database Config Validator",
            "",
            f"# Set the database type",
            f"DATABASE_TYPE={db_type.value}",
            ""
        ]
        
        for rule in rules:
            field = rule["field"]
            description = rule.get("description", "")
            required = rule.get("required", False)
            default = rule.get("default")
            
            if field == "DATABASE_TYPE":
                continue  # Already added above
            
            template_lines.append(f"# {description}")
            if required:
                template_lines.append(f"# REQUIRED")
            else:
                template_lines.append(f"# Optional")
            
            if default:
                template_lines.append(f"# Default: {default}")
            
            if required:
                template_lines.append(f"{field}=")
            else:
                template_lines.append(f"# {field}={default or ''}")
            
            template_lines.append("")
        
        return "\n".join(template_lines)


# Utility functions for external use

def validate_current_database_config() -> DatabaseConfigValidation:
    """Validate the current database configuration."""
    validator = DatabaseConfigValidator()
    return validator.get_current_database_validation()


def validate_all_database_configs() -> Dict[str, DatabaseConfigValidation]:
    """Validate configuration for all database types."""
    validator = DatabaseConfigValidator()
    return validator.validate_all_databases()


def generate_config_report() -> str:
    """Generate a configuration report for all databases."""
    validator = DatabaseConfigValidator()
    validations = validator.validate_all_databases()
    return validator.generate_configuration_report(validations)


def export_env_template(db_type: str) -> str:
    """Export environment template for a database type."""
    validator = DatabaseConfigValidator()
    try:
        database_type = DatabaseType(db_type.lower())
        return validator.export_configuration_template(database_type)
    except ValueError:
        return f"# Invalid database type: {db_type}\n# Valid types: supabase, postgresql, mysql"


if __name__ == "__main__":
    # Run validation for current configuration
    validation = validate_current_database_config()
    print(f"Current database ({validation.database_type}) validation:")
    print(f"Valid: {validation.valid}")
    print(f"Score: {validation.overall_score}/100")
    
    if validation.errors:
        print("\nErrors:")
        for error in validation.errors:
            print(f"  - {error.field}: {error.message}")
    
    if validation.warnings:
        print("\nWarnings:")
        for warning in validation.warnings:
            print(f"  - {warning.field}: {warning.message}")
    
    if validation.recommendations:
        print("\nRecommendations:")
        for rec in validation.recommendations:
            print(f"  - {rec}")