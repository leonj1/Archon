"""
Knowledge Repository Interface

Interface for knowledge base operations including sources, documents,
code examples, and content management.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_repository import BaseRepository


class SourceEntity:
    """Source entity representation."""
    
    def __init__(
        self,
        source_id: str,
        url: str,
        domain: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content_summary: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_crawled: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        status: str = "active",
        content_type: Optional[str] = None,
        language: Optional[str] = None,
        favicon_url: Optional[str] = None,
    ):
        self.source_id = source_id
        self.url = url
        self.domain = domain
        self.title = title
        self.description = description
        self.content_summary = content_summary
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_crawled = last_crawled
        self.metadata = metadata or {}
        self.tags = tags or []
        self.status = status
        self.content_type = content_type
        self.language = language
        self.favicon_url = favicon_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "source_id": self.source_id,
            "url": self.url,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "content_summary": self.content_summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_crawled": self.last_crawled,
            "metadata": self.metadata,
            "tags": self.tags,
            "status": self.status,
            "content_type": self.content_type,
            "language": self.language,
            "favicon_url": self.favicon_url,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceEntity":
        """Create entity from dictionary."""
        return cls(**data)


class DocumentEntity:
    """Document entity representation."""
    
    def __init__(
        self,
        id: str,
        source_id: str,
        url: str,
        content: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        chunk_number: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        keywords: Optional[List[str]] = None,
        language: Optional[str] = None,
        content_type: str = "text",
    ):
        self.id = id
        self.source_id = source_id
        self.url = url
        self.content = content
        self.title = title
        self.summary = summary
        self.chunk_number = chunk_number
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
        self.embedding = embedding
        self.keywords = keywords or []
        self.language = language
        self.content_type = content_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "url": self.url,
            "content": self.content,
            "title": self.title,
            "summary": self.summary,
            "chunk_number": self.chunk_number,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "keywords": self.keywords,
            "language": self.language,
            "content_type": self.content_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentEntity":
        """Create entity from dictionary."""
        return cls(**data)


class CodeExampleEntity:
    """Code example entity representation."""
    
    def __init__(
        self,
        id: str,
        source_id: str,
        file_path: str,
        language: str,
        code_content: str,
        function_name: Optional[str] = None,
        class_name: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.source_id = source_id
        self.file_path = file_path
        self.language = language
        self.code_content = code_content
        self.function_name = function_name
        self.class_name = class_name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "file_path": self.file_path,
            "language": self.language,
            "code_content": self.code_content,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeExampleEntity":
        """Create entity from dictionary."""
        return cls(**data)


class IKnowledgeRepository(BaseRepository):
    """
    Interface for knowledge base repository operations.
    Manages sources, documents, and code examples.
    """
    
    # Source Management
    @abstractmethod
    async def create_source(self, source_data: Dict[str, Any]) -> Optional[SourceEntity]:
        """
        Create a new knowledge source.
        
        Args:
            source_data: Source data
            
        Returns:
            Created source entity or None if creation failed
        """
        pass
    
    @abstractmethod
    async def get_source(self, source_id: str) -> Optional[SourceEntity]:
        """
        Get source by ID.
        
        Args:
            source_id: Source ID
            
        Returns:
            Source entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_source_by_url(self, url: str) -> Optional[SourceEntity]:
        """
        Get source by URL.
        
        Args:
            url: Source URL
            
        Returns:
            Source entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_sources_by_domain(self, domain: str) -> List[SourceEntity]:
        """
        Get all sources from a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of sources from the domain
        """
        pass
    
    @abstractmethod
    async def get_sources_by_status(self, status: str) -> List[SourceEntity]:
        """
        Get all sources with a specific status.
        
        Args:
            status: Source status
            
        Returns:
            List of sources with the specified status
        """
        pass
    
    @abstractmethod
    async def update_source_crawl_time(self, source_id: str) -> bool:
        """
        Update the last crawled timestamp for a source.
        
        Args:
            source_id: Source ID
            
        Returns:
            True if updated successfully
        """
        pass
    
    @abstractmethod
    async def search_sources(self, keyword: str) -> List[SourceEntity]:
        """
        Search sources by keyword in title or description.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching sources
        """
        pass
    
    # Document Management
    @abstractmethod
    async def create_document(self, document_data: Dict[str, Any]) -> Optional[DocumentEntity]:
        """
        Create a new document.
        
        Args:
            document_data: Document data
            
        Returns:
            Created document entity or None if creation failed
        """
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[DocumentEntity]:
        """
        Get document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_documents_by_source(self, source_id: str) -> List[DocumentEntity]:
        """
        Get all documents from a specific source.
        
        Args:
            source_id: Source ID
            
        Returns:
            List of documents from the source
        """
        pass
    
    @abstractmethod
    async def get_documents_by_url(self, url: str) -> List[DocumentEntity]:
        """
        Get all documents from a specific URL.
        
        Args:
            url: URL
            
        Returns:
            List of documents from the URL
        """
        pass
    
    @abstractmethod
    async def update_document_embedding(
        self, 
        document_id: str, 
        embedding: List[float]
    ) -> bool:
        """
        Update document embedding.
        
        Args:
            document_id: Document ID
            embedding: Vector embedding
            
        Returns:
            True if updated successfully
        """
        pass
    
    @abstractmethod
    async def search_documents(
        self, 
        keyword: str,
        source_id: Optional[str] = None
    ) -> List[DocumentEntity]:
        """
        Search documents by keyword in content or title.
        
        Args:
            keyword: Search keyword
            source_id: Optional source ID to filter by
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def get_documents_without_embeddings(
        self, 
        limit: Optional[int] = None
    ) -> List[DocumentEntity]:
        """
        Get documents that don't have embeddings yet.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of documents without embeddings
        """
        pass
    
    # Code Example Management
    @abstractmethod
    async def create_code_example(
        self, 
        code_example_data: Dict[str, Any]
    ) -> Optional[CodeExampleEntity]:
        """
        Create a new code example.
        
        Args:
            code_example_data: Code example data
            
        Returns:
            Created code example entity or None if creation failed
        """
        pass
    
    @abstractmethod
    async def get_code_example(self, code_example_id: str) -> Optional[CodeExampleEntity]:
        """
        Get code example by ID.
        
        Args:
            code_example_id: Code example ID
            
        Returns:
            Code example entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_code_examples_by_source(self, source_id: str) -> List[CodeExampleEntity]:
        """
        Get all code examples from a specific source.
        
        Args:
            source_id: Source ID
            
        Returns:
            List of code examples from the source
        """
        pass
    
    @abstractmethod
    async def get_code_examples_by_language(self, language: str) -> List[CodeExampleEntity]:
        """
        Get all code examples in a specific language.
        
        Args:
            language: Programming language
            
        Returns:
            List of code examples in the language
        """
        pass
    
    @abstractmethod
    async def search_code_examples(
        self, 
        keyword: str,
        language: Optional[str] = None
    ) -> List[CodeExampleEntity]:
        """
        Search code examples by keyword.
        
        Args:
            keyword: Search keyword
            language: Optional language filter
            
        Returns:
            List of matching code examples
        """
        pass
    
    @abstractmethod
    async def get_code_examples_by_function(self, function_name: str) -> List[CodeExampleEntity]:
        """
        Get code examples containing a specific function.
        
        Args:
            function_name: Function name
            
        Returns:
            List of code examples with the function
        """
        pass
    
    # Bulk Operations
    @abstractmethod
    async def bulk_create_documents(
        self, 
        documents_data: List[Dict[str, Any]]
    ) -> List[DocumentEntity]:
        """
        Create multiple documents in bulk.
        
        Args:
            documents_data: List of document data dictionaries
            
        Returns:
            List of created document entities
        """
        pass
    
    @abstractmethod
    async def bulk_update_embeddings(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        """
        Update embeddings for multiple documents in bulk.
        
        Args:
            embeddings_data: List of {document_id, embedding} dictionaries
            
        Returns:
            Number of documents successfully updated
        """
        pass
    
    @abstractmethod
    async def delete_source_and_related(self, source_id: str) -> bool:
        """
        Delete a source and all its related documents and code examples.
        
        Args:
            source_id: Source ID
            
        Returns:
            True if deletion was successful
        """
        pass