"""
Settings Models

Pydantic models for settings and configuration management including categories,
encryption support, and secure storage.
Maps to the archon_settings table.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, SecretStr

from .base_models import BaseEntity, validate_non_empty_string


class SettingCategory(str, Enum):
    """Setting category enumeration."""
    
    SERVER_CONFIG = "server_config"
    RAG_STRATEGY = "rag_strategy"
    API_KEYS = "api_keys"
    MONITORING = "monitoring"
    FEATURES = "features"
    CODE_EXTRACTION = "code_extraction"
    PERFORMANCE = "performance"
    CUSTOM = "custom"
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all valid category values."""
        return [category.value for category in cls]
    
    @classmethod
    def get_sensitive_categories(cls) -> List[str]:
        """Get categories that typically contain sensitive data."""
        return [cls.API_KEYS.value]
    
    def is_sensitive(self) -> bool:
        """Check if this category typically contains sensitive data."""
        return self.value in self.get_sensitive_categories()


class SettingType(str, Enum):
    """Setting data type enumeration."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    SECRET = "secret"  # Encrypted string
    URL = "url"
    EMAIL = "email"
    
    @classmethod
    def get_numeric_types(cls) -> List[str]:
        """Get numeric setting types."""
        return [cls.INTEGER.value, cls.FLOAT.value]
    
    def is_numeric(self) -> bool:
        """Check if this is a numeric type."""
        return self.value in self.get_numeric_types()
    
    def needs_encryption(self) -> bool:
        """Check if this type should be encrypted."""
        return self.value == self.SECRET.value


class Setting(BaseEntity):
    """
    Setting model.
    
    Maps to the archon_settings table with support for encrypted values,
    categories, and type validation.
    """
    
    key: str = Field(
        description="Unique setting key",
        min_length=1,
        max_length=255,
        examples=["OPENAI_API_KEY", "RAG_STRATEGY_ENABLED", "SERVER_PORT"]
    )
    
    value: Optional[str] = Field(
        default=None,
        description="Plain text setting value (for non-encrypted settings)",
        examples=["true", "8080", "gpt-4o-mini"]
    )
    
    encrypted_value: Optional[str] = Field(
        default=None,
        description="Encrypted setting value (for sensitive data)",
        examples=["$2b$12$encrypted_hash_here"]
    )
    
    is_encrypted: bool = Field(
        default=False,
        description="Whether this setting uses encryption"
    )
    
    category: SettingCategory = Field(
        default=SettingCategory.CUSTOM,
        description="Setting category for organization"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of the setting",
        max_length=1000,
        examples=["OpenAI API key for embeddings and LLM operations"]
    )
    
    setting_type: SettingType = Field(
        default=SettingType.STRING,
        description="Data type of the setting value"
    )
    
    default_value: Optional[str] = Field(
        default=None,
        description="Default value for the setting",
        examples=["true", "50", "localhost"]
    )
    
    is_required: bool = Field(
        default=False,
        description="Whether this setting is required for system operation"
    )
    
    is_readonly: bool = Field(
        default=False,
        description="Whether this setting is read-only"
    )
    
    validation_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for value validation",
        examples=["^[0-9]+$", "^https?://.*", "^[a-zA-Z0-9_]+$"]
    )
    
    min_value: Optional[float] = Field(
        default=None,
        description="Minimum value for numeric settings"
    )
    
    max_value: Optional[float] = Field(
        default=None,
        description="Maximum value for numeric settings"
    )
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate setting key format."""
        v = validate_non_empty_string(v, "Setting key")
        
        # Keys should be uppercase with underscores
        if not v.isupper() or ' ' in v:
            # Allow but suggest proper format
            pass
        
        return v
    
    @field_validator('setting_type')
    @classmethod
    def validate_setting_type(cls, v: Union[str, SettingType]) -> SettingType:
        """Validate and convert setting type."""
        if isinstance(v, str):
            try:
                return SettingType(v.lower())
            except ValueError:
                raise ValueError(f"Invalid setting type: {v}")
        return v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v: Union[str, SettingCategory]) -> SettingCategory:
        """Validate and convert category."""
        if isinstance(v, str):
            try:
                return SettingCategory(v.lower())
            except ValueError:
                # Allow custom categories
                return SettingCategory.CUSTOM
        return v
    
    @model_validator(mode='after')
    def validate_setting_consistency(self) -> 'Setting':
        """Validate setting data consistency."""
        # Ensure encrypted settings don't have plain values and vice versa
        if self.is_encrypted:
            if self.value is not None:
                # Clear plain value for encrypted settings
                self.value = None
            if self.setting_type != SettingType.SECRET:
                self.setting_type = SettingType.SECRET
        else:
            if self.encrypted_value is not None:
                # Clear encrypted value for non-encrypted settings
                self.encrypted_value = None
        
        # Auto-set encryption for sensitive categories
        if self.category.is_sensitive() and not self.is_encrypted:
            self.is_encrypted = True
            self.setting_type = SettingType.SECRET
            if self.value:
                # Would need to encrypt the value here in real implementation
                self.encrypted_value = self.value  # Placeholder
                self.value = None
        
        # Validate numeric constraints
        if self.setting_type.is_numeric() and self.value:
            try:
                numeric_value = float(self.value)
                if self.min_value is not None and numeric_value < self.min_value:
                    raise ValueError(f"Value {numeric_value} is below minimum {self.min_value}")
                if self.max_value is not None and numeric_value > self.max_value:
                    raise ValueError(f"Value {numeric_value} is above maximum {self.max_value}")
            except ValueError as e:
                if "could not convert" not in str(e):
                    raise
        
        return self
    
    def get_display_value(self) -> str:
        """Get a safe display value (masked for sensitive data)."""
        if self.is_encrypted:
            return "***ENCRYPTED***"
        elif self.category.is_sensitive():
            return "***SENSITIVE***"
        elif self.value:
            return self.value
        else:
            return self.default_value or ""
    
    def get_actual_value(self, decryptor=None) -> Optional[str]:
        """
        Get the actual setting value, decrypting if necessary.
        
        Args:
            decryptor: Function to decrypt encrypted values
            
        Returns:
            The actual value or None if encrypted and no decryptor provided
        """
        if not self.is_encrypted:
            return self.value or self.default_value
        
        if decryptor and self.encrypted_value:
            try:
                return decryptor(self.encrypted_value)
            except Exception:
                return None
        
        return None
    
    def get_typed_value(self, decryptor=None) -> Any:
        """Get the value converted to its proper type."""
        raw_value = self.get_actual_value(decryptor)
        
        if raw_value is None:
            return None
        
        try:
            if self.setting_type == SettingType.BOOLEAN:
                return raw_value.lower() in ('true', '1', 'yes', 'on')
            elif self.setting_type == SettingType.INTEGER:
                return int(raw_value)
            elif self.setting_type == SettingType.FLOAT:
                return float(raw_value)
            elif self.setting_type == SettingType.JSON:
                import json
                return json.loads(raw_value)
            else:
                return raw_value
        except (ValueError, TypeError):
            # Return as string if conversion fails
            return raw_value
    
    def update_value(self, new_value: str, encryptor=None) -> None:
        """Update the setting value, encrypting if necessary."""
        if self.is_readonly:
            raise ValueError("Cannot update read-only setting")
        
        if self.is_encrypted and encryptor:
            self.encrypted_value = encryptor(new_value)
            self.value = None
        else:
            self.value = new_value
            self.encrypted_value = None
        
        self.updated_at = datetime.utcnow()
    
    def validate_value(self, value: str) -> bool:
        """Validate a value against the setting's constraints."""
        try:
            # Type validation
            if self.setting_type == SettingType.INTEGER:
                int(value)
            elif self.setting_type == SettingType.FLOAT:
                float(value)
            elif self.setting_type == SettingType.BOOLEAN:
                if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                    return False
            elif self.setting_type == SettingType.JSON:
                import json
                json.loads(value)
            elif self.setting_type == SettingType.URL:
                from urllib.parse import urlparse
                result = urlparse(value)
                if not all([result.scheme, result.netloc]):
                    return False
            elif self.setting_type == SettingType.EMAIL:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    return False
            
            # Pattern validation
            if self.validation_pattern:
                import re
                if not re.match(self.validation_pattern, value):
                    return False
            
            # Numeric range validation
            if self.setting_type.is_numeric():
                numeric_value = float(value)
                if self.min_value is not None and numeric_value < self.min_value:
                    return False
                if self.max_value is not None and numeric_value > self.max_value:
                    return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def to_dict_safe(self) -> Dict[str, Any]:
        """Convert to dictionary with sensitive values masked."""
        data = self.to_dict()
        if self.is_encrypted or self.category.is_sensitive():
            data['value'] = self.get_display_value()
            data.pop('encrypted_value', None)
        return data
    
    @property
    def is_sensitive(self) -> bool:
        """Check if setting contains sensitive data."""
        return self.is_encrypted or self.category.is_sensitive()
    
    @property
    def has_value(self) -> bool:
        """Check if setting has a value (encrypted or plain)."""
        return self.value is not None or self.encrypted_value is not None


class SettingEntity(Setting):
    """Alias for compatibility with repository interfaces."""
    pass


class SettingCreate(BaseModel):
    """Model for creating new settings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    key: str = Field(description="Setting key", min_length=1, max_length=255)
    value: Optional[str] = Field(default=None, description="Setting value")
    category: SettingCategory = Field(default=SettingCategory.CUSTOM, description="Setting category")
    description: Optional[str] = Field(default=None, description="Setting description")
    setting_type: SettingType = Field(default=SettingType.STRING, description="Value type")
    is_encrypted: bool = Field(default=False, description="Whether to encrypt the value")
    is_required: bool = Field(default=False, description="Whether setting is required")
    default_value: Optional[str] = Field(default=None, description="Default value")
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        return validate_non_empty_string(v, "Setting key")


class SettingUpdate(BaseModel):
    """Model for updating existing settings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    value: Optional[str] = Field(default=None, description="New value")
    description: Optional[str] = Field(default=None, description="New description")
    category: Optional[SettingCategory] = Field(default=None, description="New category")
    is_required: Optional[bool] = Field(default=None, description="New required status")
    default_value: Optional[str] = Field(default=None, description="New default value")


class SettingFilter(BaseModel):
    """Model for filtering settings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    category: Optional[Union[SettingCategory, List[SettingCategory]]] = Field(
        default=None, description="Category filter"
    )
    setting_type: Optional[Union[SettingType, List[SettingType]]] = Field(
        default=None, description="Type filter"
    )
    is_encrypted: Optional[bool] = Field(default=None, description="Encryption filter")
    is_required: Optional[bool] = Field(default=None, description="Required filter")
    is_readonly: Optional[bool] = Field(default=None, description="Read-only filter")
    has_value: Optional[bool] = Field(default=None, description="Has value filter")
    search_term: Optional[str] = Field(default=None, description="Search in key/description")


class SettingsSummary(BaseModel):
    """Settings summary statistics model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    total_settings: int = Field(description="Total number of settings")
    encrypted_settings: int = Field(description="Number of encrypted settings")
    required_settings: int = Field(description="Number of required settings")
    settings_with_values: int = Field(description="Number of settings with values")
    
    category_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Settings count by category"
    )
    
    type_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Settings count by type"
    )
    
    missing_required: List[str] = Field(
        default_factory=list,
        description="Required settings without values"
    )
    
    @property
    def encryption_rate(self) -> float:
        """Calculate encryption rate."""
        if self.total_settings == 0:
            return 0.0
        return self.encrypted_settings / self.total_settings
    
    @property
    def completion_rate(self) -> float:
        """Calculate settings completion rate."""
        if self.total_settings == 0:
            return 0.0
        return self.settings_with_values / self.total_settings


class SettingsExport(BaseModel):
    """Model for exporting settings data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    export_timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0", description="Export format version")
    include_encrypted: bool = Field(description="Whether encrypted values were included")
    category_filter: Optional[str] = Field(default=None, description="Category filter applied")
    
    settings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Exported settings data"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Export metadata"
    )
    
    @property
    def setting_count(self) -> int:
        """Get number of exported settings."""
        return len(self.settings)


class DefaultSettings(BaseModel):
    """Model for default system settings."""
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def get_default_settings(cls) -> List[SettingCreate]:
        """Get list of default settings that should be created on first run."""
        return [
            # Server Configuration
            SettingCreate(
                key="MCP_TRANSPORT",
                value="dual",
                category=SettingCategory.SERVER_CONFIG,
                setting_type=SettingType.STRING,
                description="MCP server transport mode - sse (web clients), stdio (IDE clients), or dual (both)",
                is_required=True
            ),
            SettingCreate(
                key="HOST",
                value="localhost",
                category=SettingCategory.SERVER_CONFIG,
                setting_type=SettingType.STRING,
                description="Host to bind to if using sse as the transport",
                default_value="localhost"
            ),
            SettingCreate(
                key="PORT",
                value="8051",
                category=SettingCategory.SERVER_CONFIG,
                setting_type=SettingType.INTEGER,
                description="Port to listen on if using sse as the transport",
                default_value="8051"
            ),
            
            # RAG Strategy
            SettingCreate(
                key="USE_HYBRID_SEARCH",
                value="true",
                category=SettingCategory.RAG_STRATEGY,
                setting_type=SettingType.BOOLEAN,
                description="Combines vector similarity search with keyword search for better results",
                default_value="true"
            ),
            SettingCreate(
                key="USE_RERANKING",
                value="true",
                category=SettingCategory.RAG_STRATEGY,
                setting_type=SettingType.BOOLEAN,
                description="Applies cross-encoder reranking to improve search result relevance",
                default_value="true"
            ),
            SettingCreate(
                key="EMBEDDING_MODEL",
                value="text-embedding-3-small",
                category=SettingCategory.RAG_STRATEGY,
                setting_type=SettingType.STRING,
                description="Embedding model for vector search and similarity matching",
                is_required=True
            ),
            
            # Features
            SettingCreate(
                key="PROJECTS_ENABLED",
                value="true",
                category=SettingCategory.FEATURES,
                setting_type=SettingType.BOOLEAN,
                description="Enable or disable Projects and Tasks functionality",
                default_value="true"
            ),
            
            # API Keys (encrypted)
            SettingCreate(
                key="OPENAI_API_KEY",
                value=None,
                category=SettingCategory.API_KEYS,
                setting_type=SettingType.SECRET,
                is_encrypted=True,
                description="OpenAI API Key for embedding model (text-embedding-3-small)",
                is_required=True
            ),
        ]