"""
Search Models

Pydantic models for search operations including search results, queries, and analytics.
Supports vector search, hybrid search, and RAG operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .base_models import BaseEntity, validate_non_empty_string


class SearchType(str, Enum):
    """Search type enumeration."""
    
    VECTOR = "vector"
    TEXT = "text"
    HYBRID = "hybrid"
    RAG = "rag"
    CODE = "code"
    SEMANTIC = "semantic"
    FACETED = "faceted"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all search types."""
        return [search_type.value for search_type in cls]
    
    def requires_embedding(self) -> bool:
        """Check if search type requires embeddings."""
        return self.value in [self.VECTOR.value, self.HYBRID.value, self.SEMANTIC.value]


class SearchResult(BaseModel):
    """
    Enhanced search result model with comprehensive metadata.
    
    Represents a single search result from any type of search operation.
    """
    
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    id: str = Field(
        description="Unique result identifier",
        examples=["doc_123", "code_456"]
    )
    
    content: str = Field(
        description="Main content of the result",
        examples=["This is the main text content of the document..."]
    )
    
    score: float = Field(
        description="Relevance score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
        examples=[0.95, 0.78, 0.42]
    )
    
    source_id: Optional[str] = Field(
        default=None,
        description="Source ID this result belongs to",
        examples=["website_docs.python.org"]
    )
    
    title: Optional[str] = Field(
        default=None,
        description="Result title or heading",
        examples=["Python Functions", "Authentication Guide"]
    )
    
    url: Optional[str] = Field(
        default=None,
        description="Source URL of the result",
        examples=["https://docs.python.org/3/tutorial/functions.html"]
    )
    
    content_type: str = Field(
        default="text",
        description="Type of content",
        examples=["text", "code", "markdown", "html"]
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the result",
        examples=[{"language": "en", "section": "tutorial", "difficulty": "beginner"}]
    )
    
    highlights: List[str] = Field(
        default_factory=list,
        description="Highlighted text snippets that match the query",
        examples=[["Python functions are defined using the **def** keyword"]]
    )
    
    chunk_number: Optional[int] = Field(
        default=None,
        description="Chunk number within the source document",
        examples=[0, 1, 5]
    )
    
    language: Optional[str] = Field(
        default=None,
        description="Content language",
        examples=["en", "es", "python", "javascript"]
    )
    
    # Search-specific fields
    search_type: Optional[SearchType] = Field(
        default=None,
        description="Type of search that produced this result"
    )
    
    vector_score: Optional[float] = Field(
        default=None,
        description="Vector similarity score component",
        ge=0.0,
        le=1.0
    )
    
    text_score: Optional[float] = Field(
        default=None,
        description="Text search score component",
        ge=0.0,
        le=1.0
    )
    
    rerank_score: Optional[float] = Field(
        default=None,
        description="Reranking score if reranking was applied",
        ge=0.0,
        le=1.0
    )
    
    @field_validator('score', 'vector_score', 'text_score', 'rerank_score')
    @classmethod
    def validate_scores(cls, v: Optional[float]) -> Optional[float]:
        """Validate score ranges."""
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError("Scores must be between 0.0 and 1.0")
        return v
    
    @property
    def has_highlights(self) -> bool:
        """Check if result has highlights."""
        return len(self.highlights) > 0
    
    @property
    def content_preview(self, max_length: int = 200) -> str:
        """Get a preview of the content."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length].rsplit(' ', 1)[0] + "..."
    
    def add_highlight(self, highlight: str) -> None:
        """Add a highlight to the result."""
        if highlight and highlight not in self.highlights:
            self.highlights.append(highlight)
    
    def get_display_title(self) -> str:
        """Get the best available title for display."""
        if self.title:
            return self.title
        elif self.url:
            return self.url.split('/')[-1] or self.url
        else:
            return f"Result {self.id}"


class CodeSearchResult(BaseModel):
    """
    Specialized search result for code examples.
    
    Extends basic search result with code-specific metadata.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(description="Code example ID")
    
    code_content: str = Field(
        description="The actual code content",
        examples=["def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"]
    )
    
    language: str = Field(
        description="Programming language",
        examples=["python", "javascript", "java", "rust"]
    )
    
    file_path: str = Field(
        description="File path or location",
        examples=["src/utils/math.py", "components/UserForm.jsx"]
    )
    
    score: float = Field(
        description="Relevance score",
        ge=0.0,
        le=1.0
    )
    
    function_name: Optional[str] = Field(
        default=None,
        description="Main function name",
        examples=["fibonacci", "calculateDistance", "parseJson"]
    )
    
    class_name: Optional[str] = Field(
        default=None,
        description="Class name if applicable",
        examples=["UserManager", "DatabaseConnection", "ApiClient"]
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Description of what the code does",
        examples=["Recursive function to calculate Fibonacci numbers"]
    )
    
    source_id: Optional[str] = Field(
        default=None,
        description="Source ID this code belongs to"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional code metadata"
    )
    
    line_numbers: Optional[Tuple[int, int]] = Field(
        default=None,
        description="Start and end line numbers",
        examples=[(15, 25), (100, 150)]
    )
    
    complexity: Optional[str] = Field(
        default=None,
        description="Code complexity assessment",
        examples=["simple", "moderate", "complex"]
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Code tags",
        examples=[["algorithm", "recursion"], ["authentication", "jwt"]]
    )
    
    @property
    def line_count(self) -> int:
        """Get number of lines in the code."""
        return len(self.code_content.splitlines())
    
    @property
    def has_function(self) -> bool:
        """Check if code has a function name."""
        return self.function_name is not None
    
    @property
    def has_class(self) -> bool:
        """Check if code has a class name."""
        return self.class_name is not None
    
    def get_display_name(self) -> str:
        """Get the best display name for the code."""
        if self.function_name:
            return self.function_name
        elif self.class_name:
            return self.class_name
        elif self.file_path:
            return self.file_path.split('/')[-1]
        else:
            return f"Code {self.id}"
    
    def to_search_result(self) -> SearchResult:
        """Convert to generic SearchResult."""
        return SearchResult(
            id=self.id,
            content=self.code_content,
            score=self.score,
            source_id=self.source_id,
            title=self.get_display_name(),
            url=None,  # Code doesn't have URLs typically
            content_type="code",
            metadata={
                **self.metadata,
                "language": self.language,
                "function_name": self.function_name,
                "class_name": self.class_name,
                "file_path": self.file_path,
                "line_numbers": self.line_numbers,
                "complexity": self.complexity,
                "tags": self.tags
            },
            language=self.language,
            search_type=SearchType.CODE
        )


class VectorSearchResult(BaseModel):
    """
    Vector search result model.
    
    Represents results from pure vector similarity search.
    """
    
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    id: str = Field(description="Document or item ID")
    content: Optional[str] = Field(default=None, description="Content text")
    score: float = Field(description="Similarity score", ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Item metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")
    
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
        
        return [float(x) for x in v]
    
    def to_search_result(self, additional_data: Optional[Dict[str, Any]] = None) -> SearchResult:
        """Convert to generic SearchResult."""
        data = additional_data or {}
        return SearchResult(
            id=self.id,
            content=self.content or "",
            score=self.score,
            metadata=self.metadata,
            search_type=SearchType.VECTOR,
            vector_score=self.score,
            **data
        )


class SearchQuery(BaseModel):
    """
    Search query model with comprehensive parameters.
    
    Represents a search request with all possible parameters and filters.
    """
    
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    query: str = Field(
        description="Search query text",
        min_length=1,
        examples=["python functions", "JWT authentication", "database migration"]
    )
    
    search_type: SearchType = Field(
        default=SearchType.HYBRID,
        description="Type of search to perform"
    )
    
    match_count: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results to return"
    )
    
    # Vector search parameters
    query_embedding: Optional[List[float]] = Field(
        default=None,
        description="Pre-computed query embedding"
    )
    
    min_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold"
    )
    
    # Hybrid search parameters
    text_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for text search component in hybrid search"
    )
    
    vector_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for vector search component in hybrid search"
    )
    
    # Filters
    source_filters: Optional[List[str]] = Field(
        default=None,
        description="Source IDs to filter by"
    )
    
    content_type_filters: Optional[List[str]] = Field(
        default=None,
        description="Content types to filter by"
    )
    
    language_filters: Optional[List[str]] = Field(
        default=None,
        description="Languages to filter by"
    )
    
    date_range: Optional[Tuple[datetime, datetime]] = Field(
        default=None,
        description="Date range filter (start, end)"
    )
    
    metadata_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata-based filters"
    )
    
    # Search options
    include_highlights: bool = Field(
        default=True,
        description="Whether to include highlighted snippets"
    )
    
    enable_reranking: bool = Field(
        default=False,
        description="Whether to apply reranking to results"
    )
    
    expand_query: bool = Field(
        default=False,
        description="Whether to expand the query with synonyms"
    )
    
    # Code search specific
    programming_language: Optional[str] = Field(
        default=None,
        description="Programming language filter for code search"
    )
    
    function_name: Optional[str] = Field(
        default=None,
        description="Function name filter for code search"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query text."""
        return validate_non_empty_string(v, "Search query")
    
    @model_validator(mode='after')
    def validate_weights(self) -> 'SearchQuery':
        """Validate hybrid search weights sum to 1.0."""
        if self.search_type == SearchType.HYBRID:
            weight_sum = self.text_weight + self.vector_weight
            if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point errors
                raise ValueError("text_weight and vector_weight must sum to 1.0")
        return self
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'SearchQuery':
        """Validate date range."""
        if self.date_range and len(self.date_range) == 2:
            start, end = self.date_range
            if start > end:
                raise ValueError("Date range start must be before end")
        return self
    
    @property
    def requires_embedding(self) -> bool:
        """Check if query requires embeddings."""
        return self.search_type.requires_embedding()
    
    @property
    def is_code_search(self) -> bool:
        """Check if this is a code search query."""
        return self.search_type == SearchType.CODE
    
    def to_dict_for_logging(self) -> Dict[str, Any]:
        """Convert to dictionary for logging (exclude large embeddings)."""
        data = self.model_dump()
        if self.query_embedding:
            data['query_embedding'] = f"[{len(self.query_embedding)} dimensions]"
        return data


class SearchResponse(BaseModel):
    """
    Comprehensive search response model.
    
    Contains search results and metadata about the search operation.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    query: str = Field(description="Original search query")
    
    results: List[SearchResult] = Field(
        default_factory=list,
        description="Search results"
    )
    
    code_results: Optional[List[CodeSearchResult]] = Field(
        default=None,
        description="Code search results (if applicable)"
    )
    
    total_found: int = Field(
        default=0,
        description="Total number of results found (before limiting)"
    )
    
    search_type: SearchType = Field(description="Type of search performed")
    
    execution_time_ms: float = Field(
        description="Search execution time in milliseconds",
        ge=0.0
    )
    
    # Search metadata
    used_embedding: bool = Field(
        default=False,
        description="Whether embeddings were used"
    )
    
    applied_reranking: bool = Field(
        default=False,
        description="Whether reranking was applied"
    )
    
    query_expansion: Optional[str] = Field(
        default=None,
        description="Expanded query if query expansion was used"
    )
    
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters that were applied"
    )
    
    # Statistics
    avg_score: Optional[float] = Field(
        default=None,
        description="Average score of returned results"
    )
    
    score_distribution: Optional[Dict[str, int]] = Field(
        default=None,
        description="Distribution of scores in ranges"
    )
    
    source_breakdown: Optional[Dict[str, int]] = Field(
        default=None,
        description="Number of results per source"
    )
    
    @model_validator(mode='after')
    def calculate_statistics(self) -> 'SearchResponse':
        """Calculate response statistics."""
        if self.results:
            # Calculate average score
            scores = [r.score for r in self.results]
            self.avg_score = sum(scores) / len(scores)
            
            # Calculate score distribution
            self.score_distribution = {
                "0.9-1.0": len([s for s in scores if 0.9 <= s <= 1.0]),
                "0.8-0.9": len([s for s in scores if 0.8 <= s < 0.9]),
                "0.7-0.8": len([s for s in scores if 0.7 <= s < 0.8]),
                "0.6-0.7": len([s for s in scores if 0.6 <= s < 0.7]),
                "0.0-0.6": len([s for s in scores if 0.0 <= s < 0.6]),
            }
            
            # Calculate source breakdown
            source_counts = {}
            for result in self.results:
                if result.source_id:
                    source_counts[result.source_id] = source_counts.get(result.source_id, 0) + 1
            self.source_breakdown = source_counts
        
        return self
    
    @property
    def has_results(self) -> bool:
        """Check if response has any results."""
        return len(self.results) > 0 or (self.code_results and len(self.code_results) > 0)
    
    @property
    def result_count(self) -> int:
        """Get total number of results returned."""
        count = len(self.results)
        if self.code_results:
            count += len(self.code_results)
        return count
    
    def get_top_sources(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get top sources by result count."""
        if not self.source_breakdown:
            return []
        
        return sorted(self.source_breakdown.items(), key=lambda x: x[1], reverse=True)[:limit]


class SearchAnalytics(BaseModel):
    """
    Search analytics and metrics model.
    
    Tracks search usage patterns and performance metrics.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Query metrics
    total_queries: int = Field(default=0, description="Total number of queries")
    unique_queries: int = Field(default=0, description="Number of unique queries")
    avg_execution_time: float = Field(default=0.0, description="Average execution time")
    
    # Result metrics
    avg_results_returned: float = Field(default=0.0, description="Average results per query")
    zero_result_queries: int = Field(default=0, description="Queries with no results")
    
    # Search type breakdown
    search_type_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Query count by search type"
    )
    
    # Popular queries
    popular_queries: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most frequent queries"
    )
    
    # Performance metrics
    slow_queries: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Slowest queries"
    )
    
    # Time period
    period_start: datetime = Field(description="Analytics period start")
    period_end: datetime = Field(description="Analytics period end")
    
    @property
    def zero_result_rate(self) -> float:
        """Calculate zero result rate."""
        if self.total_queries == 0:
            return 0.0
        return self.zero_result_queries / self.total_queries
    
    @property
    def query_diversity(self) -> float:
        """Calculate query diversity (unique queries / total queries)."""
        if self.total_queries == 0:
            return 0.0
        return self.unique_queries / self.total_queries