"""
Knowledge Models

Pydantic models for knowledge base management including sources, documents, and code examples.
Maps to the archon_sources, archon_crawled_pages, and archon_code_examples tables.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .base_models import (
    BaseEntity, 
    MetadataMixin, 
    StatusMixin, 
    VectorMixin,
    validate_language_code,
    validate_non_empty_string,
    validate_url
)


class Source(BaseEntity, MetadataMixin, StatusMixin):
    """
    Knowledge source model.
    
    Maps to the archon_sources table and represents crawled websites, uploaded documents,
    or other knowledge sources.
    """
    
    source_id: str = Field(
        description="Unique source identifier",
        examples=["website_docs.python.org", "upload_readme_md_20241215"]
    )
    
    title: Optional[str] = Field(
        default=None,
        description="Human-readable source title",
        max_length=500,
        examples=["Python Documentation", "FastAPI User Guide"]
    )
    
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the source content",
        max_length=2000,
        examples=["Comprehensive Python documentation covering language features, standard library, and best practices"]
    )
    
    total_word_count: int = Field(
        default=0,
        ge=0,
        description="Total word count across all documents from this source",
        examples=[15420, 8950]
    )
    
    # Additional fields not in the base database schema but useful for the domain
    url: Optional[str] = Field(
        default=None,
        description="Primary URL for web sources",
        examples=["https://docs.python.org/3/", "https://fastapi.tiangolo.com/"]
    )
    
    domain: Optional[str] = Field(
        default=None,
        description="Domain for web sources",
        examples=["docs.python.org", "fastapi.tiangolo.com"]
    )
    
    content_type: Optional[str] = Field(
        default=None,
        description="Type of content source",
        examples=["documentation", "tutorial", "api_reference", "blog", "upload"]
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Primary language of the content",
        examples=["en", "es", "python", "javascript"]
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the source",
        examples=[["python", "web-framework"], ["authentication", "security"]]
    )
    
    last_crawled: Optional[datetime] = Field(
        default=None,
        description="Last time this source was crawled or updated"
    )
    
    favicon_url: Optional[str] = Field(
        default=None,
        description="URL to the source's favicon",
        examples=["https://docs.python.org/favicon.ico"]
    )
    
    @field_validator('source_id')
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        """Validate source ID format."""
        return validate_non_empty_string(v, "Source ID")
    
    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format."""
        if v is None:
            return None
        return validate_url(v)
    
    @field_validator('language')
    @classmethod
    def validate_language_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code."""
        if v is None:
            return None
        return validate_language_code(v)
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate content type."""
        if v is None:
            return None
        
        valid_types = [
            "documentation", "tutorial", "api_reference", "blog", 
            "upload", "wiki", "forum", "news", "academic"
        ]
        v_lower = v.lower()
        if v_lower not in valid_types:
            # Allow custom content types but normalize
            pass
        return v_lower
    
    @model_validator(mode='after')
    def extract_domain_from_url(self) -> 'Source':
        """Extract domain from URL if not provided."""
        if self.url and not self.domain:
            try:
                parsed = urlparse(self.url)
                self.domain = parsed.netloc
            except Exception:
                pass
        return self
    
    @property
    def is_web_source(self) -> bool:
        """Check if this is a web-based source."""
        return self.url is not None and self.url.startswith(('http://', 'https://'))
    
    @property
    def is_upload_source(self) -> bool:
        """Check if this is an uploaded document."""
        return self.content_type == "upload" or (self.source_id and "upload_" in self.source_id)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the source."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the source."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_crawl_time(self) -> None:
        """Update the last crawled timestamp."""
        self.last_crawled = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_summary(self) -> Dict[str, Any]:
        """Get source summary for listings."""
        return {
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "content_type": self.content_type,
            "language": self.language,
            "status": self.status,
            "total_word_count": self.total_word_count,
            "tags": self.tags,
            "last_crawled": self.last_crawled,
            "created_at": self.created_at,
        }


class Document(BaseEntity, MetadataMixin, VectorMixin):
    """
    Document chunk model.
    
    Maps to the archon_crawled_pages table and represents processed document chunks
    with embeddings for semantic search.
    """
    
    source_id: str = Field(
        description="ID of the source this document belongs to",
        examples=["website_docs.python.org"]
    )
    
    url: str = Field(
        description="URL of the specific page or document",
        examples=["https://docs.python.org/3/tutorial/introduction.html"]
    )
    
    chunk_number: int = Field(
        default=0,
        ge=0,
        description="Chunk number within the document (for pagination)",
        examples=[0, 1, 2]
    )
    
    content: str = Field(
        description="The main text content of the document chunk",
        min_length=1,
        examples=["Python is an easy to learn, powerful programming language..."]
    )
    
    title: Optional[str] = Field(
        default=None,
        description="Document or page title",
        max_length=500,
        examples=["An Informal Introduction to Python"]
    )
    
    summary: Optional[str] = Field(
        default=None,
        description="AI-generated summary of the content",
        max_length=1000,
        examples=["Introduction to Python syntax, data types, and control structures"]
    )
    
    keywords: List[str] = Field(
        default_factory=list,
        description="Extracted keywords for search",
        examples=[["python", "programming", "syntax", "tutorial"]]
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Content language",
        examples=["en", "es", "fr"]
    )
    
    content_type: str = Field(
        default="text",
        description="Type of content",
        examples=["text", "code", "markdown", "html"]
    )
    
    @field_validator('source_id')
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        """Validate source ID."""
        return validate_non_empty_string(v, "Source ID")
    
    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v: str) -> str:
        """Validate URL."""
        return validate_url(v)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content."""
        return validate_non_empty_string(v, "Content")
    
    @field_validator('language')
    @classmethod
    def validate_language_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate language code."""
        if v is None:
            return None
        return validate_language_code(v)
    
    @property
    def word_count(self) -> int:
        """Calculate word count of content."""
        return len(self.content.split())
    
    @property
    def character_count(self) -> int:
        """Get character count of content."""
        return len(self.content)
    
    def add_keyword(self, keyword: str) -> None:
        """Add a keyword."""
        keyword = keyword.strip().lower()
        if keyword and keyword not in self.keywords:
            self.keywords.append(keyword)
            self.updated_at = datetime.utcnow()
    
    def extract_keywords(self, max_keywords: int = 10) -> List[str]:
        """Simple keyword extraction from content."""
        # Basic keyword extraction - could be enhanced with NLP
        words = self.content.lower().split()
        # Filter out common stop words and short words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Count frequency and return most common
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, _ in word_counts.most_common(max_keywords)]


class CodeExample(BaseEntity, MetadataMixin, VectorMixin):
    """
    Code example model.
    
    Maps to the archon_code_examples table and represents extracted code snippets
    with context and metadata.
    """
    
    source_id: str = Field(
        description="ID of the source this code example belongs to",
        examples=["website_docs.python.org"]
    )
    
    url: str = Field(
        description="URL where the code example was found",
        examples=["https://docs.python.org/3/tutorial/classes.html"]
    )
    
    chunk_number: int = Field(
        default=0,
        ge=0,
        description="Chunk number within the page",
        examples=[0, 1, 2]
    )
    
    content: str = Field(
        description="The actual code content",
        min_length=1,
        examples=["def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"]
    )
    
    summary: str = Field(
        description="AI-generated summary of what the code does",
        min_length=1,
        examples=["Recursive function to calculate Fibonacci numbers"]
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Programming language",
        examples=["python", "javascript", "java", "rust"]
    )
    
    function_name: Optional[str] = Field(
        default=None,
        description="Main function name if applicable",
        examples=["fibonacci", "calculate_distance", "parse_json"]
    )
    
    class_name: Optional[str] = Field(
        default=None,
        description="Class name if applicable",
        examples=["UserManager", "DatabaseConnection", "ApiClient"]
    )
    
    file_path: Optional[str] = Field(
        default=None,
        description="File path if from a repository",
        examples=["src/utils/math.py", "components/UserForm.jsx"]
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the code",
        max_length=2000,
        examples=["This function implements the classic recursive Fibonacci algorithm..."]
    )
    
    complexity: Optional[str] = Field(
        default=None,
        description="Code complexity assessment",
        examples=["simple", "moderate", "complex"]
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorizing the code",
        examples=[["algorithm", "recursion"], ["authentication", "jwt"]]
    )
    
    @field_validator('source_id')
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        """Validate source ID."""
        return validate_non_empty_string(v, "Source ID")
    
    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v: str) -> str:
        """Validate URL."""
        return validate_url(v)
    
    @field_validator('content', 'summary')
    @classmethod
    def validate_required_content(cls, v: str) -> str:
        """Validate required content fields."""
        return validate_non_empty_string(v)
    
    @field_validator('language')
    @classmethod
    def validate_language_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate programming language."""
        if v is None:
            return None
        
        # Common programming languages
        common_languages = [
            "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
            "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
            "sql", "html", "css", "shell", "bash", "powershell"
        ]
        
        v_lower = v.lower()
        if v_lower in common_languages:
            return v_lower
        
        # Allow custom languages but normalize
        return v_lower
    
    @field_validator('complexity')
    @classmethod
    def validate_complexity(cls, v: Optional[str]) -> Optional[str]:
        """Validate complexity level."""
        if v is None:
            return None
        
        valid_complexity = ["simple", "moderate", "complex", "advanced"]
        v_lower = v.lower()
        if v_lower not in valid_complexity:
            raise ValueError(f"Complexity must be one of: {', '.join(valid_complexity)}")
        return v_lower
    
    @property
    def line_count(self) -> int:
        """Get number of lines in the code."""
        return len(self.content.splitlines())
    
    @property
    def character_count(self) -> int:
        """Get character count of code."""
        return len(self.content)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the code example."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def estimate_complexity(self) -> str:
        """Estimate code complexity based on simple heuristics."""
        lines = self.line_count
        
        # Simple heuristics
        if lines <= 10:
            return "simple"
        elif lines <= 50:
            return "moderate"
        elif lines <= 200:
            return "complex"
        else:
            return "advanced"


class KnowledgeItem(BaseModel):
    """
    Unified knowledge item model for API responses.
    
    Represents a knowledge item that could be a document or code example.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Item ID")
    source_id: str = Field(description="Source ID")
    item_type: str = Field(description="Type of item: document or code_example")
    title: Optional[str] = Field(default=None, description="Item title")
    content: str = Field(description="Item content")
    summary: Optional[str] = Field(default=None, description="Item summary")
    url: str = Field(description="Source URL")
    language: Optional[str] = Field(default=None, description="Content language")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    score: Optional[float] = Field(default=None, description="Search relevance score")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Update timestamp")
    
    # Code-specific fields (when item_type is code_example)
    function_name: Optional[str] = Field(default=None, description="Function name")
    class_name: Optional[str] = Field(default=None, description="Class name")
    file_path: Optional[str] = Field(default=None, description="File path")
    
    @classmethod
    def from_document(cls, document: Document, score: Optional[float] = None) -> "KnowledgeItem":
        """Create KnowledgeItem from Document."""
        return cls(
            id=document.id,
            source_id=document.source_id,
            item_type="document",
            title=document.title,
            content=document.content,
            summary=document.summary,
            url=document.url,
            language=document.language,
            metadata=document.metadata,
            score=score,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
    
    @classmethod
    def from_code_example(cls, code_example: CodeExample, score: Optional[float] = None) -> "KnowledgeItem":
        """Create KnowledgeItem from CodeExample."""
        return cls(
            id=code_example.id,
            source_id=code_example.source_id,
            item_type="code_example",
            title=f"{code_example.function_name or code_example.class_name or 'Code Example'}",
            content=code_example.content,
            summary=code_example.summary,
            url=code_example.url,
            language=code_example.language,
            metadata=code_example.metadata,
            score=score,
            created_at=code_example.created_at,
            updated_at=code_example.updated_at,
            function_name=code_example.function_name,
            class_name=code_example.class_name,
            file_path=code_example.file_path
        )


class SourceCreate(BaseModel):
    """Model for creating new sources."""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_id: str = Field(description="Unique source identifier")
    title: Optional[str] = Field(default=None, description="Source title")
    url: Optional[str] = Field(default=None, description="Source URL")
    content_type: Optional[str] = Field(default=None, description="Content type")
    language: Optional[str] = Field(default=None, description="Content language")
    tags: List[str] = Field(default_factory=list, description="Source tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentCreate(BaseModel):
    """Model for creating new documents."""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_id: str = Field(description="Source ID")
    url: str = Field(description="Document URL")
    content: str = Field(description="Document content", min_length=1)
    title: Optional[str] = Field(default=None, description="Document title")
    chunk_number: int = Field(default=0, description="Chunk number")
    language: Optional[str] = Field(default=None, description="Content language")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CodeExampleCreate(BaseModel):
    """Model for creating new code examples."""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_id: str = Field(description="Source ID")
    url: str = Field(description="Code source URL")
    content: str = Field(description="Code content", min_length=1)
    summary: str = Field(description="Code summary", min_length=1)
    language: Optional[str] = Field(default=None, description="Programming language")
    function_name: Optional[str] = Field(default=None, description="Function name")
    class_name: Optional[str] = Field(default=None, description="Class name")
    chunk_number: int = Field(default=0, description="Chunk number")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class KnowledgeFilter(BaseModel):
    """Model for filtering knowledge items."""
    
    model_config = ConfigDict(from_attributes=True)
    
    source_id: Optional[str] = Field(default=None, description="Source ID filter")
    content_type: Optional[str] = Field(default=None, description="Content type filter")
    language: Optional[str] = Field(default=None, description="Language filter")
    item_type: Optional[str] = Field(default=None, description="Item type filter")
    tags: Optional[List[str]] = Field(default=None, description="Tags filter")
    search_term: Optional[str] = Field(default=None, description="Search term")
    has_embedding: Optional[bool] = Field(default=None, description="Has embedding filter")
    created_after: Optional[datetime] = Field(default=None, description="Created after date")
    created_before: Optional[datetime] = Field(default=None, description="Created before date")
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'KnowledgeFilter':
        """Validate date range."""
        if (self.created_after and self.created_before and 
            self.created_after > self.created_before):
            raise ValueError("created_after must be before created_before")
        return self