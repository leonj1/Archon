"""
Fake in-memory implementation of KnowledgeRepository for testing.
"""
import threading
import hashlib
import random
import math
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse

from ..interfaces.knowledge_repository import KnowledgeRepository
from ...models.knowledge import Source, Document, CodeExample


class FakeKnowledgeRepository(KnowledgeRepository):
    """In-memory implementation of KnowledgeRepository for testing."""
    
    def __init__(self):
        self._sources: Dict[str, Source] = {}
        self._documents: Dict[str, Document] = {}
        self._code_examples: Dict[str, CodeExample] = {}
        self._lock = threading.RLock()
        self._next_source_id = 1
        self._next_doc_id = 1
        self._next_code_id = 1

    def _generate_source_id(self) -> str:
        """Generate a realistic source ID."""
        with self._lock:
            source_id = f"src_{self._next_source_id:06d}"
            self._next_source_id += 1
            return source_id

    def _generate_doc_id(self) -> str:
        """Generate a realistic document ID."""
        with self._lock:
            doc_id = f"doc_{self._next_doc_id:08d}"
            self._next_doc_id += 1
            return doc_id

    def _generate_code_id(self) -> str:
        """Generate a realistic code example ID."""
        with self._lock:
            code_id = f"code_{self._next_code_id:06d}"
            self._next_code_id += 1
            return code_id

    def _generate_fake_embedding(self, text: str, dimensions: int = 1536) -> List[float]:
        """Generate a fake but deterministic embedding for text."""
        # Create deterministic but realistic embedding based on text hash
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Use hash to seed random number generator for consistency
        random.seed(int.from_bytes(hash_bytes[:4], 'big'))
        
        # Generate normalized vector
        vector = [random.gauss(0, 1) for _ in range(dimensions)]
        magnitude = math.sqrt(sum(x * x for x in vector))
        return [x / magnitude for x in vector]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    # Source methods
    async def create_source(
        self,
        url: str,
        source_type: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Source:
        """Create a new source."""
        with self._lock:
            now = datetime.now(timezone.utc)
            
            # Generate title from URL if not provided
            if not title:
                parsed = urlparse(url)
                title = f"{parsed.netloc}{parsed.path}" if parsed.netloc else url
            
            source = Source(
                id=self._generate_source_id(),
                url=url,
                source_type=source_type,
                title=title,
                description=description,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            self._sources[source.id] = source
            return source

    async def get_source(self, source_id: str) -> Optional[Source]:
        """Get a source by ID."""
        with self._lock:
            return self._sources.get(source_id)

    async def get_source_by_url(self, url: str) -> Optional[Source]:
        """Get a source by URL."""
        with self._lock:
            for source in self._sources.values():
                if source.url == url:
                    return source
            return None

    async def list_sources(
        self,
        source_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Source]:
        """List sources with filtering and pagination."""
        with self._lock:
            sources = list(self._sources.values())
            
            if source_type:
                sources = [s for s in sources if s.source_type == source_type]
            
            # Sort by updated_at descending
            sources.sort(key=lambda s: s.updated_at, reverse=True)
            
            return sources[offset:offset + limit]

    async def update_source(
        self,
        source_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Source]:
        """Update a source."""
        with self._lock:
            source = self._sources.get(source_id)
            if not source:
                return None
            
            if title is not None:
                source.title = title
            if description is not None:
                source.description = description
            if metadata is not None:
                source.metadata = metadata
            
            source.updated_at = datetime.now(timezone.utc)
            return source

    async def delete_source(self, source_id: str) -> bool:
        """Delete a source and its documents."""
        with self._lock:
            if source_id not in self._sources:
                return False
            
            # Delete associated documents
            docs_to_delete = [
                doc_id for doc_id, doc in self._documents.items()
                if doc.source_id == source_id
            ]
            for doc_id in docs_to_delete:
                del self._documents[doc_id]
            
            # Delete source
            del self._sources[source_id]
            return True

    # Document methods
    async def create_document(
        self,
        source_id: str,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        chunk_index: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Create a new document with embedding."""
        with self._lock:
            now = datetime.now(timezone.utc)
            
            # Generate embedding from content
            embedding = self._generate_fake_embedding(content)
            
            document = Document(
                id=self._generate_doc_id(),
                source_id=source_id,
                content=content,
                title=title,
                url=url,
                chunk_index=chunk_index,
                embedding=embedding,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            self._documents[document.id] = document
            return document

    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        with self._lock:
            return self._documents.get(document_id)

    async def list_documents(
        self,
        source_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """List documents with filtering and pagination."""
        with self._lock:
            documents = list(self._documents.values())
            
            if source_id:
                documents = [d for d in documents if d.source_id == source_id]
            
            # Sort by created_at descending
            documents.sort(key=lambda d: d.created_at, reverse=True)
            
            return documents[offset:offset + limit]

    async def search_documents(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """Search documents by embedding similarity."""
        with self._lock:
            results = []
            
            for document in self._documents.values():
                if document.embedding:
                    similarity = self._cosine_similarity(query_embedding, document.embedding)
                    if similarity >= similarity_threshold:
                        results.append((document, similarity))
            
            # Sort by similarity descending
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:limit]

    async def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Document]:
        """Update a document."""
        with self._lock:
            document = self._documents.get(document_id)
            if not document:
                return None
            
            if content is not None:
                document.content = content
                # Regenerate embedding for new content
                document.embedding = self._generate_fake_embedding(content)
            if title is not None:
                document.title = title
            if metadata is not None:
                document.metadata = metadata
            
            document.updated_at = datetime.now(timezone.utc)
            return document

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document."""
        with self._lock:
            if document_id in self._documents:
                del self._documents[document_id]
                return True
            return False

    # Code example methods
    async def create_code_example(
        self,
        source_id: str,
        code: str,
        language: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CodeExample:
        """Create a new code example with embedding."""
        with self._lock:
            now = datetime.now(timezone.utc)
            
            # Generate embedding from code content
            embedding_text = f"{title or ''} {description or ''} {code}"
            embedding = self._generate_fake_embedding(embedding_text)
            
            code_example = CodeExample(
                id=self._generate_code_id(),
                source_id=source_id,
                code=code,
                language=language,
                title=title,
                description=description,
                file_path=file_path,
                embedding=embedding,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            self._code_examples[code_example.id] = code_example
            return code_example

    async def get_code_example(self, code_id: str) -> Optional[CodeExample]:
        """Get a code example by ID."""
        with self._lock:
            return self._code_examples.get(code_id)

    async def list_code_examples(
        self,
        source_id: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CodeExample]:
        """List code examples with filtering and pagination."""
        with self._lock:
            examples = list(self._code_examples.values())
            
            if source_id:
                examples = [e for e in examples if e.source_id == source_id]
            if language:
                examples = [e for e in examples if e.language == language]
            
            # Sort by created_at descending
            examples.sort(key=lambda e: e.created_at, reverse=True)
            
            return examples[offset:offset + limit]

    async def search_code_examples(
        self,
        query_embedding: List[float],
        language: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[Tuple[CodeExample, float]]:
        """Search code examples by embedding similarity."""
        with self._lock:
            results = []
            
            for example in self._code_examples.values():
                if language and example.language != language:
                    continue
                
                if example.embedding:
                    similarity = self._cosine_similarity(query_embedding, example.embedding)
                    if similarity >= similarity_threshold:
                        results.append((example, similarity))
            
            # Sort by similarity descending
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:limit]

    async def delete_code_example(self, code_id: str) -> bool:
        """Delete a code example."""
        with self._lock:
            if code_id in self._code_examples:
                del self._code_examples[code_id]
                return True
            return False

    # Statistics methods
    async def get_source_count(self) -> int:
        """Get total number of sources."""
        with self._lock:
            return len(self._sources)

    async def get_document_count(self, source_id: Optional[str] = None) -> int:
        """Get document count, optionally filtered by source."""
        with self._lock:
            if source_id:
                return len([d for d in self._documents.values() if d.source_id == source_id])
            return len(self._documents)

    async def get_code_example_count(self, source_id: Optional[str] = None) -> int:
        """Get code example count, optionally filtered by source."""
        with self._lock:
            if source_id:
                return len([e for e in self._code_examples.values() if e.source_id == source_id])
            return len(self._code_examples)

    # Test utility methods
    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        with self._lock:
            self._sources.clear()
            self._documents.clear()
            self._code_examples.clear()
            self._next_source_id = 1
            self._next_doc_id = 1
            self._next_code_id = 1

    def get_all_sources(self) -> List[Source]:
        """Get all sources (for testing)."""
        with self._lock:
            return list(self._sources.values())

    def get_all_documents(self) -> List[Document]:
        """Get all documents (for testing)."""
        with self._lock:
            return list(self._documents.values())

    def get_all_code_examples(self) -> List[CodeExample]:
        """Get all code examples (for testing)."""
        with self._lock:
            return list(self._code_examples.values())

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query (for testing)."""
        return self._generate_fake_embedding(query)