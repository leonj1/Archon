"""
Search Repository Interface

Interface for vector search and similarity operations including
embedding search, RAG queries, and semantic search functionality.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ...interfaces import IVectorStore, VectorSearchResult
from .base_repository import BaseRepository


class SearchResult:
    """Search result representation with enhanced metadata."""
    
    def __init__(
        self,
        id: str,
        content: str,
        score: float,
        source_id: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        content_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        highlights: Optional[List[str]] = None,
        chunk_number: Optional[int] = None,
        language: Optional[str] = None,
    ):
        self.id = id
        self.content = content
        self.score = score
        self.source_id = source_id
        self.title = title
        self.url = url
        self.content_type = content_type
        self.metadata = metadata or {}
        self.highlights = highlights or []
        self.chunk_number = chunk_number
        self.language = language
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "source_id": self.source_id,
            "title": self.title,
            "url": self.url,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "highlights": self.highlights,
            "chunk_number": self.chunk_number,
            "language": self.language,
        }
    
    @classmethod
    def from_vector_result(
        cls, 
        vector_result: VectorSearchResult,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> "SearchResult":
        """Create SearchResult from VectorSearchResult."""
        data = additional_data or {}
        return cls(
            id=vector_result.id,
            content=vector_result.content or "",
            score=vector_result.score,
            metadata=vector_result.metadata,
            **data
        )


class CodeSearchResult:
    """Code search result representation."""
    
    def __init__(
        self,
        id: str,
        code_content: str,
        language: str,
        file_path: str,
        score: float,
        function_name: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        line_numbers: Optional[Tuple[int, int]] = None,
    ):
        self.id = id
        self.code_content = code_content
        self.language = language
        self.file_path = file_path
        self.score = score
        self.function_name = function_name
        self.class_name = class_name
        self.description = description
        self.source_id = source_id
        self.metadata = metadata or {}
        self.line_numbers = line_numbers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "code_content": self.code_content,
            "language": self.language,
            "file_path": self.file_path,
            "score": self.score,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "description": self.description,
            "source_id": self.source_id,
            "metadata": self.metadata,
            "line_numbers": self.line_numbers,
        }


class ISearchRepository(BaseRepository):
    """
    Interface for search repository operations.
    Handles vector search, similarity queries, and search optimization.
    """
    
    def __init__(self, database, vector_store: IVectorStore):
        """
        Initialize search repository.
        
        Args:
            database: Database interface
            vector_store: Vector store interface
        """
        super().__init__(database, "documents")  # Primary table for search
        self._vector_store = vector_store
    
    @property
    def vector_store(self) -> IVectorStore:
        """Get the vector store interface."""
        return self._vector_store
    
    # Vector Search Operations
    @abstractmethod
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        collection: str = "documents",
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """
        Perform similarity search using vector embeddings.
        
        Args:
            query_embedding: Query vector
            collection: Vector collection name
            top_k: Number of results to return
            filters: Optional metadata filters
            min_score: Minimum similarity score threshold
            
        Returns:
            List of search results ordered by similarity
        """
        pass
    
    @abstractmethod
    async def hybrid_search(
        self,
        query_text: str,
        query_embedding: np.ndarray,
        collection: str = "documents",
        top_k: int = 10,
        text_weight: float = 0.3,
        vector_weight: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining text and vector search.
        
        Args:
            query_text: Text query for keyword search
            query_embedding: Query vector for semantic search
            collection: Vector collection name
            top_k: Number of results to return
            text_weight: Weight for text search results (0.0-1.0)
            vector_weight: Weight for vector search results (0.0-1.0)
            filters: Optional metadata filters
            
        Returns:
            List of search results with combined scoring
        """
        pass
    
    @abstractmethod
    async def search_documents(
        self,
        query: str,
        match_count: int = 5,
        source_id: Optional[str] = None,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search documents with text-based query.
        
        Args:
            query: Search query
            match_count: Number of results to return
            source_id: Optional source filter
            content_type: Optional content type filter
            language: Optional language filter
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def search_code_examples(
        self,
        query: str,
        match_count: int = 3,
        language: Optional[str] = None,
        function_name: Optional[str] = None,
    ) -> List[CodeSearchResult]:
        """
        Search code examples with text-based query.
        
        Args:
            query: Search query
            match_count: Number of results to return
            language: Optional programming language filter
            function_name: Optional function name filter
            
        Returns:
            List of matching code examples
        """
        pass
    
    @abstractmethod
    async def rag_query(
        self,
        query: str,
        query_embedding: Optional[np.ndarray] = None,
        match_count: int = 5,
        source_filters: Optional[List[str]] = None,
        content_type_filters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform RAG (Retrieval Augmented Generation) query.
        
        Args:
            query: User query
            query_embedding: Optional pre-computed query embedding
            match_count: Number of context documents to retrieve
            source_filters: Optional source ID filters
            content_type_filters: Optional content type filters
            
        Returns:
            Dictionary with context documents and query metadata
        """
        pass
    
    # Semantic Search
    @abstractmethod
    async def find_similar_documents(
        self,
        document_id: str,
        top_k: int = 5,
        exclude_same_source: bool = False,
    ) -> List[SearchResult]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: Reference document ID
            top_k: Number of similar documents to return
            exclude_same_source: Whether to exclude docs from same source
            
        Returns:
            List of similar documents
        """
        pass
    
    @abstractmethod
    async def cluster_documents(
        self,
        source_id: Optional[str] = None,
        num_clusters: int = 5,
        min_cluster_size: int = 2,
    ) -> Dict[str, Any]:
        """
        Cluster documents based on semantic similarity.
        
        Args:
            source_id: Optional source filter
            num_clusters: Number of clusters to create
            min_cluster_size: Minimum documents per cluster
            
        Returns:
            Clustering results with document assignments
        """
        pass
    
    # Search Analytics & Optimization
    @abstractmethod
    async def get_search_statistics(
        self,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get search usage statistics.
        
        Args:
            time_range_days: Time range for statistics
            
        Returns:
            Dictionary with search statistics
        """
        pass
    
    @abstractmethod
    async def log_search_query(
        self,
        query: str,
        results_count: int,
        search_type: str,
        execution_time_ms: float,
        filters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Log search query for analytics.
        
        Args:
            query: Search query
            results_count: Number of results returned
            search_type: Type of search performed
            execution_time_ms: Query execution time
            filters: Filters applied
            
        Returns:
            True if logged successfully
        """
        pass
    
    @abstractmethod
    async def get_popular_queries(
        self,
        limit: int = 10,
        time_range_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get most popular search queries.
        
        Args:
            limit: Number of queries to return
            time_range_days: Time range for analysis
            
        Returns:
            List of popular queries with frequency
        """
        pass
    
    # Index Management
    @abstractmethod
    async def rebuild_search_index(
        self,
        collection: str = "documents",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Rebuild search index for better performance.
        
        Args:
            collection: Collection to rebuild
            batch_size: Processing batch size
            
        Returns:
            Rebuild statistics
        """
        pass
    
    @abstractmethod
    async def optimize_search_index(self, collection: str = "documents") -> bool:
        """
        Optimize search index for better performance.
        
        Args:
            collection: Collection to optimize
            
        Returns:
            True if optimization succeeded
        """
        pass
    
    @abstractmethod
    async def validate_embeddings(
        self,
        collection: str = "documents",
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Validate embedding quality and consistency.
        
        Args:
            collection: Collection to validate
            sample_size: Number of embeddings to sample
            
        Returns:
            Validation results
        """
        pass
    
    # Advanced Search Features
    @abstractmethod
    async def search_with_facets(
        self,
        query: str,
        facet_fields: List[str],
        match_count: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search with faceted navigation.
        
        Args:
            query: Search query
            facet_fields: Fields to create facets for
            match_count: Number of results
            filters: Optional filters
            
        Returns:
            Search results with facet counts
        """
        pass
    
    @abstractmethod
    async def search_suggestions(
        self,
        partial_query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get search query suggestions/autocomplete.
        
        Args:
            partial_query: Partial query text
            limit: Number of suggestions
            
        Returns:
            List of suggested queries
        """
        pass
    
    @abstractmethod
    async def batch_similarity_search(
        self,
        query_embeddings: List[np.ndarray],
        collection: str = "documents",
        top_k: int = 5,
    ) -> List[List[SearchResult]]:
        """
        Perform batch similarity search for multiple queries.
        
        Args:
            query_embeddings: List of query vectors
            collection: Vector collection name
            top_k: Number of results per query
            
        Returns:
            List of result lists for each query
        """
        pass