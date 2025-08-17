"""
Supabase Knowledge Repository Implementation

Concrete implementation of knowledge repository for Supabase database backend.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from ...interfaces import IDatabase, QueryResult
from ..interfaces.knowledge_repository_interface import (
    IKnowledgeRepository, 
    SourceEntity, 
    DocumentEntity, 
    CodeExampleEntity
)


class SupabaseKnowledgeRepository(IKnowledgeRepository):
    """
    Supabase implementation of knowledge repository.
    Handles knowledge CRUD operations for Supabase database backend.
    """
    
    def __init__(self, database: IDatabase, table_name: str = "documents"):
        """Initialize Supabase knowledge repository."""
        super().__init__(database, table_name)
    
    # Base repository methods (documents are primary entity)
    
    async def create(self, entity_data: Dict[str, Any]) -> Optional[DocumentEntity]:
        """Create a new document entity."""
        return await self.create_document(entity_data)
    
    async def get_by_id(self, entity_id: str) -> Optional[DocumentEntity]:
        """Get document entity by ID."""
        return await self.get_document(entity_id)
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[DocumentEntity]:
        """Update an existing document entity."""
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._database.update(
                "documents",
                update_data,
                filters={"id": entity_id}
            )
            
            if result.success and result.data:
                return DocumentEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete a document entity by ID."""
        try:
            result = await self._database.delete(
                "documents",
                filters={"id": entity_id}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[DocumentEntity]:
        """List all document entities."""
        try:
            result = await self._database.select(
                "documents",
                order_by=order_by or "updated_at DESC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [DocumentEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[DocumentEntity]:
        """Find document entities matching criteria."""
        try:
            result = await self._database.select(
                "documents",
                filters=criteria,
                order_by=order_by or "updated_at DESC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [DocumentEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """Count document entities."""
        try:
            return await self._database.count("documents", criteria)
        except Exception:
            return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if document entity exists."""
        try:
            return await self._database.exists("documents", {"id": entity_id})
        except Exception:
            return False
    
    # Source Management
    
    async def create_source(self, source_data: Dict[str, Any]) -> Optional[SourceEntity]:
        """Create a new knowledge source."""
        try:
            # Ensure required fields are present
            if "source_id" not in source_data:
                source_data["source_id"] = f"source-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
            
            # Set timestamps
            now = datetime.utcnow()
            source_data.setdefault("created_at", now.isoformat())
            source_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            source_data.setdefault("status", "active")
            source_data.setdefault("metadata", {})
            source_data.setdefault("tags", [])
            
            # Use the sources table
            result = await self._database.insert("sources", source_data)
            
            if result.success and result.data:
                return SourceEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_source(self, source_id: str) -> Optional[SourceEntity]:
        """Get source by ID."""
        try:
            result = await self._database.select(
                "sources",
                filters={"source_id": source_id}
            )
            
            if result.success and result.data:
                return SourceEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_source_by_url(self, url: str) -> Optional[SourceEntity]:
        """Get source by URL."""
        try:
            result = await self._database.select(
                "sources",
                filters={"url": url}
            )
            
            if result.success and result.data:
                return SourceEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_sources_by_domain(self, domain: str) -> List[SourceEntity]:
        """Get all sources from a specific domain."""
        try:
            result = await self._database.select(
                "sources",
                filters={"domain": domain},
                order_by="updated_at DESC"
            )
            
            if result.success:
                return [SourceEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def get_sources_by_status(self, status: str) -> List[SourceEntity]:
        """Get all sources with a specific status."""
        try:
            result = await self._database.select(
                "sources",
                filters={"status": status},
                order_by="updated_at DESC"
            )
            
            if result.success:
                return [SourceEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def update_source_crawl_time(self, source_id: str) -> bool:
        """Update the last crawled timestamp for a source."""
        try:
            result = await self._database.update(
                "sources",
                {
                    "last_crawled": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"source_id": source_id}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def search_sources(self, keyword: str) -> List[SourceEntity]:
        """Search sources by keyword in title or description."""
        try:
            # Get all sources and filter in memory
            # (Supabase adapter doesn't support LIKE queries directly)
            result = await self._database.select("sources")
            
            if not result.success:
                return []
            
            keyword_lower = keyword.lower()
            matching_sources = []
            
            for row in result.data:
                source = SourceEntity.from_dict(row)
                if (keyword_lower in (source.title or "").lower() or 
                    keyword_lower in (source.description or "").lower()):
                    matching_sources.append(source)
            
            return matching_sources
            
        except Exception:
            return []
    
    # Document Management
    
    async def create_document(self, document_data: Dict[str, Any]) -> Optional[DocumentEntity]:
        """Create a new document."""
        try:
            # Ensure required fields are present
            if "id" not in document_data:
                document_data["id"] = f"doc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
            
            # Set timestamps
            now = datetime.utcnow()
            document_data.setdefault("created_at", now.isoformat())
            document_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            document_data.setdefault("chunk_number", 0)
            document_data.setdefault("metadata", {})
            document_data.setdefault("keywords", [])
            document_data.setdefault("content_type", "text")
            
            result = await self._database.insert("documents", document_data)
            
            if result.success and result.data:
                return DocumentEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_document(self, document_id: str) -> Optional[DocumentEntity]:
        """Get document by ID."""
        try:
            result = await self._database.select(
                "documents",
                filters={"id": document_id}
            )
            
            if result.success and result.data:
                return DocumentEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_documents_by_source(self, source_id: str) -> List[DocumentEntity]:
        """Get all documents from a specific source."""
        try:
            result = await self._database.select(
                "documents",
                filters={"source_id": source_id},
                order_by="chunk_number ASC"
            )
            
            if result.success:
                return [DocumentEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def get_documents_by_url(self, url: str) -> List[DocumentEntity]:
        """Get all documents from a specific URL."""
        try:
            result = await self._database.select(
                "documents",
                filters={"url": url},
                order_by="chunk_number ASC"
            )
            
            if result.success:
                return [DocumentEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def update_document_embedding(
        self, 
        document_id: str, 
        embedding: List[float]
    ) -> bool:
        """Update document embedding."""
        try:
            result = await self._database.update(
                "documents",
                {
                    "embedding": embedding,
                    "updated_at": datetime.utcnow().isoformat()
                },
                filters={"id": document_id}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def search_documents(
        self, 
        keyword: str,
        source_id: Optional[str] = None
    ) -> List[DocumentEntity]:
        """Search documents by keyword in content or title."""
        try:
            # Base filters
            filters = {}
            if source_id:
                filters["source_id"] = source_id
            
            # Get all matching documents and filter in memory
            result = await self._database.select("documents", filters=filters)
            
            if not result.success:
                return []
            
            keyword_lower = keyword.lower()
            matching_documents = []
            
            for row in result.data:
                document = DocumentEntity.from_dict(row)
                if (keyword_lower in (document.title or "").lower() or 
                    keyword_lower in document.content.lower()):
                    matching_documents.append(document)
            
            return matching_documents
            
        except Exception:
            return []
    
    async def get_documents_without_embeddings(
        self, 
        limit: Optional[int] = None
    ) -> List[DocumentEntity]:
        """Get documents that don't have embeddings yet."""
        try:
            # Use a simple filter - embeddings are null or empty
            result = await self._database.select(
                "documents",
                order_by="created_at ASC",
                limit=limit
            )
            
            if not result.success:
                return []
            
            # Filter in memory for documents without embeddings
            documents_without_embeddings = []
            for row in result.data:
                document = DocumentEntity.from_dict(row)
                if not document.embedding:
                    documents_without_embeddings.append(document)
            
            return documents_without_embeddings
            
        except Exception:
            return []
    
    # Code Example Management
    
    async def create_code_example(
        self, 
        code_example_data: Dict[str, Any]
    ) -> Optional[CodeExampleEntity]:
        """Create a new code example."""
        try:
            # Ensure required fields are present
            if "id" not in code_example_data:
                code_example_data["id"] = f"code-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
            
            # Set timestamps
            now = datetime.utcnow()
            code_example_data.setdefault("created_at", now.isoformat())
            code_example_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            code_example_data.setdefault("metadata", {})
            
            result = await self._database.insert("code_examples", code_example_data)
            
            if result.success and result.data:
                return CodeExampleEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_code_example(self, code_example_id: str) -> Optional[CodeExampleEntity]:
        """Get code example by ID."""
        try:
            result = await self._database.select(
                "code_examples",
                filters={"id": code_example_id}
            )
            
            if result.success and result.data:
                return CodeExampleEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_code_examples_by_source(self, source_id: str) -> List[CodeExampleEntity]:
        """Get all code examples from a specific source."""
        try:
            result = await self._database.select(
                "code_examples",
                filters={"source_id": source_id},
                order_by="created_at DESC"
            )
            
            if result.success:
                return [CodeExampleEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def get_code_examples_by_language(self, language: str) -> List[CodeExampleEntity]:
        """Get all code examples in a specific language."""
        try:
            result = await self._database.select(
                "code_examples",
                filters={"language": language},
                order_by="created_at DESC"
            )
            
            if result.success:
                return [CodeExampleEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def search_code_examples(
        self, 
        keyword: str,
        language: Optional[str] = None
    ) -> List[CodeExampleEntity]:
        """Search code examples by keyword."""
        try:
            # Base filters
            filters = {}
            if language:
                filters["language"] = language
            
            # Get all matching code examples and filter in memory
            result = await self._database.select("code_examples", filters=filters)
            
            if not result.success:
                return []
            
            keyword_lower = keyword.lower()
            matching_examples = []
            
            for row in result.data:
                example = CodeExampleEntity.from_dict(row)
                if (keyword_lower in example.code_content.lower() or 
                    keyword_lower in (example.description or "").lower() or
                    keyword_lower in (example.function_name or "").lower() or
                    keyword_lower in (example.class_name or "").lower()):
                    matching_examples.append(example)
            
            return matching_examples
            
        except Exception:
            return []
    
    async def get_code_examples_by_function(self, function_name: str) -> List[CodeExampleEntity]:
        """Get code examples containing a specific function."""
        try:
            result = await self._database.select(
                "code_examples",
                filters={"function_name": function_name},
                order_by="created_at DESC"
            )
            
            if result.success:
                return [CodeExampleEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    # Bulk Operations
    
    async def bulk_create_documents(
        self, 
        documents_data: List[Dict[str, Any]]
    ) -> List[DocumentEntity]:
        """Create multiple documents in bulk."""
        try:
            created_documents = []
            
            # Process in batches to avoid overwhelming the database
            batch_size = 100
            for i in range(0, len(documents_data), batch_size):
                batch = documents_data[i:i + batch_size]
                
                # Prepare batch data
                prepared_batch = []
                for doc_data in batch:
                    # Ensure required fields are present
                    if "id" not in doc_data:
                        doc_data["id"] = f"doc-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
                    
                    # Set timestamps
                    now = datetime.utcnow()
                    doc_data.setdefault("created_at", now.isoformat())
                    doc_data.setdefault("updated_at", now.isoformat())
                    
                    # Set defaults
                    doc_data.setdefault("chunk_number", 0)
                    doc_data.setdefault("metadata", {})
                    doc_data.setdefault("keywords", [])
                    doc_data.setdefault("content_type", "text")
                    
                    prepared_batch.append(doc_data)
                
                # Insert batch
                result = await self._database.insert("documents", prepared_batch)
                
                if result.success and result.data:
                    batch_entities = [DocumentEntity.from_dict(row) for row in result.data]
                    created_documents.extend(batch_entities)
            
            return created_documents
            
        except Exception:
            return []
    
    async def bulk_update_embeddings(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        """Update embeddings for multiple documents in bulk."""
        try:
            updated_count = 0
            
            for embedding_data in embeddings_data:
                document_id = embedding_data.get("document_id")
                embedding = embedding_data.get("embedding")
                
                if document_id and embedding:
                    success = await self.update_document_embedding(document_id, embedding)
                    if success:
                        updated_count += 1
            
            return updated_count
            
        except Exception:
            return 0
    
    async def delete_source_and_related(self, source_id: str) -> bool:
        """Delete a source and all its related documents and code examples."""
        try:
            # Delete related documents
            doc_result = await self._database.delete(
                "documents",
                filters={"source_id": source_id}
            )
            
            # Delete related code examples
            code_result = await self._database.delete(
                "code_examples",
                filters={"source_id": source_id}
            )
            
            # Delete the source itself
            source_result = await self._database.delete(
                "sources",
                filters={"source_id": source_id}
            )
            
            return source_result.success
            
        except Exception:
            return False