"""
Base Models

Base classes and common utilities for all domain models.
Provides shared functionality and validation patterns.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BaseEntity(BaseModel):
    """Base entity class with common fields and validation."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        validate_default=True,
        frozen=False,
    )
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entity",
        examples=["01HQ2VPZ62KSF185Y54MQ93VD2"]
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entity was created",
        examples=["2024-01-15T10:30:00Z"]
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entity was last updated",
        examples=["2024-01-15T14:22:00Z"]
    )
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID format."""
        if not v or not isinstance(v, str):
            raise ValueError("ID must be a non-empty string")
        return v.strip()
    
    @model_validator(mode='before')
    @classmethod
    def set_updated_at(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure updated_at is set on modifications."""
        if isinstance(data, dict):
            # If this is an update (has created_at but no updated_at)
            if 'created_at' in data and 'updated_at' not in data:
                data['updated_at'] = datetime.utcnow()
        return data
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump(exclude_none=exclude_none, mode='json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEntity":
        """Create model from dictionary."""
        return cls.model_validate(data)
    
    def update_fields(self, **kwargs) -> "BaseEntity":
        """Update specific fields and return new instance."""
        update_data = self.model_dump()
        update_data.update(kwargs)
        update_data['updated_at'] = datetime.utcnow()
        return self.__class__.model_validate(update_data)


class TimestampMixin(BaseModel):
    """Mixin for entities with timestamp fields."""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )


class MetadataMixin(BaseModel):
    """Mixin for entities with metadata fields."""
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata as key-value pairs",
        examples=[{"source": "web", "language": "en", "quality": "high"}]
    )
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata is a dictionary."""
        if not isinstance(v, dict):
            raise ValueError("Metadata must be a dictionary")
        return v
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a metadata value safely."""
        return self.metadata.get(key, default)
    
    def set_metadata_value(self, key: str, value: Any) -> None:
        """Set a metadata value."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def remove_metadata_key(self, key: str) -> bool:
        """Remove a metadata key."""
        if key in self.metadata:
            del self.metadata[key]
            self.updated_at = datetime.utcnow()
            return True
        return False


class VectorMixin(BaseModel):
    """Mixin for entities with vector embeddings."""
    
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding for semantic search",
        examples=[[0.1, -0.2, 0.3, 0.0]]
    )
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding vector."""
        if v is None:
            return None
        
        if not isinstance(v, list):
            raise ValueError("Embedding must be a list of floats")
        
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Embedding must contain only numeric values")
        
        # Check for common embedding dimensions
        valid_dimensions = [384, 512, 768, 1024, 1536, 3072]
        if len(v) not in valid_dimensions:
            # Allow any dimension but warn about non-standard sizes
            pass
        
        return [float(x) for x in v]
    
    @property
    def has_embedding(self) -> bool:
        """Check if entity has an embedding."""
        return self.embedding is not None and len(self.embedding) > 0
    
    @property
    def embedding_dimension(self) -> Optional[int]:
        """Get embedding dimension."""
        return len(self.embedding) if self.embedding else None


class StatusMixin(BaseModel):
    """Mixin for entities with status fields."""
    
    status: str = Field(
        default="active",
        description="Entity status",
        examples=["active", "inactive", "archived", "pending"]
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status format."""
        if not v or not isinstance(v, str):
            raise ValueError("Status must be a non-empty string")
        return v.strip().lower()
    
    @property
    def is_active(self) -> bool:
        """Check if entity is active."""
        return self.status == "active"
    
    @property
    def is_archived(self) -> bool:
        """Check if entity is archived."""
        return self.status == "archived"


class SearchResult(BaseModel):
    """Generic search result model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Result ID")
    score: float = Field(description="Relevance score", ge=0.0, le=1.0)
    content: str = Field(description="Result content")
    title: Optional[str] = Field(default=None, description="Result title")
    url: Optional[str] = Field(default=None, description="Source URL")
    content_type: str = Field(default="text", description="Content type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    highlights: List[str] = Field(default_factory=list, description="Highlighted text snippets")
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Validate score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class ValidationError(Exception):
    """Custom validation error for domain models."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


def validate_url(url: str) -> str:
    """Validate URL format."""
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValueError("URL must start with http:// or https://")
    
    return url


def validate_language_code(language: str) -> str:
    """Validate language code format."""
    if not language or not isinstance(language, str):
        raise ValueError("Language must be a non-empty string")
    
    language = language.strip().lower()
    
    # Allow ISO 639-1 codes (2 letters) or programming language names
    if len(language) < 2:
        raise ValueError("Language code must be at least 2 characters")
    
    return language


def validate_non_empty_string(value: str, field_name: str = "field") -> str:
    """Validate that a string is not empty."""
    if not value or not isinstance(value, str):
        raise ValueError(f"{field_name} must be a non-empty string")
    
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty or whitespace only")
    
    return value


def sanitize_json_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize metadata to ensure JSON serialization compatibility."""
    def sanitize_value(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [sanitize_value(item) for item in value]
        elif isinstance(value, (datetime, UUID)):
            return str(value)
        elif value is None or isinstance(value, (str, int, float, bool)):
            return value
        else:
            return str(value)
    
    return sanitize_value(metadata)


class PaginationParams(BaseModel):
    """Pagination parameters model."""
    
    limit: int = Field(default=50, ge=1, le=1000, description="Number of items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    order_by: Optional[str] = Field(default=None, description="Field to order by")
    order_direction: str = Field(default="desc", description="Order direction")
    
    @field_validator('order_direction')
    @classmethod
    def validate_order_direction(cls, v: str) -> str:
        """Validate order direction."""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("Order direction must be 'asc' or 'desc'")
        return v.lower()
    
    @property
    def has_ordering(self) -> bool:
        """Check if ordering is specified."""
        return self.order_by is not None


class FilterParams(BaseModel):
    """Generic filter parameters model."""
    
    filters: Dict[str, Union[str, List[str]]] = Field(
        default_factory=dict,
        description="Filter criteria"
    )
    search_term: Optional[str] = Field(default=None, description="Text search term")
    date_from: Optional[datetime] = Field(default=None, description="Filter from date")
    date_to: Optional[datetime] = Field(default=None, description="Filter to date")
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'FilterParams':
        """Validate date range."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before date_to")
        return self