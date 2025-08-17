"""
Fake in-memory implementation of SearchRepository for testing.
"""
import threading
import hashlib
import random
import math
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..interfaces.search_repository import SearchRepository


@dataclass
class SearchResult:
    """Search result with content and metadata."""
    content: str
    title: Optional[str]
    url: Optional[str]
    source_type: str
    similarity_score: float
    metadata: Dict[str, Any]


class FakeSearchRepository(SearchRepository):
    """In-memory implementation of SearchRepository for testing."""
    
    def __init__(self):
        self._search_index: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._next_id = 1

    def _generate_id(self) -> str:
        """Generate a unique ID for indexed content."""
        with self._lock:
            search_id = f"search_{self._next_id:08d}"
            self._next_id += 1
            return search_id

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

    def _keyword_similarity(self, query: str, content: str) -> float:
        """Calculate keyword-based similarity score."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # Calculate intersection over union-like metric
        intersection = len(query_words.intersection(content_words))
        union = len(query_words.union(content_words))
        
        return intersection / len(query_words) if query_words else 0.0

    async def index_content(
        self,
        content_id: str,
        content: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        source_type: str = "document",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Index content for search."""
        with self._lock:
            try:
                # Generate embedding for the content
                search_text = f"{title or ''} {content}"
                embedding = self._generate_fake_embedding(search_text)
                
                # Store indexed content
                self._search_index[content_id] = {
                    'content': content,
                    'title': title,
                    'url': url,
                    'source_type': source_type,
                    'metadata': metadata or {},
                    'embedding': embedding,
                    'indexed_at': datetime.now(timezone.utc)
                }
                return True
            except Exception:
                return False

    async def search_content(
        self,
        query: str,
        limit: int = 10,
        similarity_threshold: float = 0.1,
        source_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search indexed content."""
        with self._lock:
            if not query.strip():
                return []
            
            query_embedding = self._generate_fake_embedding(query)
            results = []
            
            for content_id, indexed_item in self._search_index.items():
                # Filter by source type if specified
                if source_types and indexed_item['source_type'] not in source_types:
                    continue
                
                # Calculate vector similarity
                vector_similarity = self._cosine_similarity(
                    query_embedding,
                    indexed_item['embedding']
                )
                
                # Calculate keyword similarity
                keyword_similarity = self._keyword_similarity(
                    query,
                    indexed_item['content']
                )
                
                # Combine similarities (weighted average)
                combined_similarity = (vector_similarity * 0.7 + keyword_similarity * 0.3)
                
                # Apply threshold
                if combined_similarity >= similarity_threshold:
                    result = SearchResult(
                        content=indexed_item['content'],
                        title=indexed_item['title'],
                        url=indexed_item['url'],
                        source_type=indexed_item['source_type'],
                        similarity_score=combined_similarity,
                        metadata=indexed_item['metadata']
                    )
                    results.append(result)
            
            # Sort by similarity score descending
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            
            return results[:limit]

    async def search_by_embedding(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.1,
        source_types: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search indexed content using pre-computed embedding."""
        with self._lock:
            results = []
            
            for content_id, indexed_item in self._search_index.items():
                # Filter by source type if specified
                if source_types and indexed_item['source_type'] not in source_types:
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(
                    query_embedding,
                    indexed_item['embedding']
                )
                
                # Apply threshold
                if similarity >= similarity_threshold:
                    result = SearchResult(
                        content=indexed_item['content'],
                        title=indexed_item['title'],
                        url=indexed_item['url'],
                        source_type=indexed_item['source_type'],
                        similarity_score=similarity,
                        metadata=indexed_item['metadata']
                    )
                    results.append(result)
            
            # Sort by similarity score descending
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            
            return results[:limit]

    async def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 10,
        similarity_threshold: float = 0.1
    ) -> List[SearchResult]:
        """Search for code examples."""
        source_types = ["code"]
        results = await self.search_content(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold,
            source_types=source_types
        )
        
        # Filter by language if specified
        if language:
            filtered_results = []
            for result in results:
                if result.metadata.get('language') == language:
                    filtered_results.append(result)
            return filtered_results
        
        return results

    async def update_content(
        self,
        content_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update indexed content."""
        with self._lock:
            if content_id not in self._search_index:
                return False
            
            indexed_item = self._search_index[content_id]
            
            # Update content and regenerate embedding if content changed
            if content is not None:
                indexed_item['content'] = content
                search_text = f"{title or indexed_item['title'] or ''} {content}"
                indexed_item['embedding'] = self._generate_fake_embedding(search_text)
            
            if title is not None:
                indexed_item['title'] = title
                # Regenerate embedding with new title
                search_text = f"{title} {indexed_item['content']}"
                indexed_item['embedding'] = self._generate_fake_embedding(search_text)
            
            if metadata is not None:
                indexed_item['metadata'].update(metadata)
            
            indexed_item['indexed_at'] = datetime.now(timezone.utc)
            return True

    async def remove_content(self, content_id: str) -> bool:
        """Remove content from search index."""
        with self._lock:
            if content_id in self._search_index:
                del self._search_index[content_id]
                return True
            return False

    async def remove_content_by_source(self, source_id: str) -> int:
        """Remove all content from a specific source."""
        with self._lock:
            removed_count = 0
            content_ids_to_remove = []
            
            for content_id, indexed_item in self._search_index.items():
                if indexed_item['metadata'].get('source_id') == source_id:
                    content_ids_to_remove.append(content_id)
            
            for content_id in content_ids_to_remove:
                del self._search_index[content_id]
                removed_count += 1
            
            return removed_count

    async def get_indexed_content_count(
        self,
        source_type: Optional[str] = None
    ) -> int:
        """Get count of indexed content."""
        with self._lock:
            if not source_type:
                return len(self._search_index)
            
            count = 0
            for indexed_item in self._search_index.values():
                if indexed_item['source_type'] == source_type:
                    count += 1
            return count

    async def get_content_types(self) -> List[str]:
        """Get list of all content types in the index."""
        with self._lock:
            types = set()
            for indexed_item in self._search_index.values():
                types.add(indexed_item['source_type'])
            return sorted(list(types))

    async def clear_index(self) -> bool:
        """Clear the entire search index."""
        with self._lock:
            self._search_index.clear()
            self._next_id = 1
            return True

    async def reindex_all(self) -> bool:
        """Regenerate embeddings for all indexed content."""
        with self._lock:
            try:
                for content_id, indexed_item in self._search_index.items():
                    search_text = f"{indexed_item['title'] or ''} {indexed_item['content']}"
                    indexed_item['embedding'] = self._generate_fake_embedding(search_text)
                    indexed_item['indexed_at'] = datetime.now(timezone.utc)
                return True
            except Exception:
                return False

    # Advanced search features
    async def search_with_filters(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int = 10,
        similarity_threshold: float = 0.1
    ) -> List[SearchResult]:
        """Search with metadata filters."""
        with self._lock:
            if not query.strip():
                return []
            
            query_embedding = self._generate_fake_embedding(query)
            results = []
            
            for content_id, indexed_item in self._search_index.items():
                # Apply metadata filters
                matches_filters = True
                for filter_key, filter_value in filters.items():
                    item_value = indexed_item['metadata'].get(filter_key)
                    if isinstance(filter_value, list):
                        if item_value not in filter_value:
                            matches_filters = False
                            break
                    else:
                        if item_value != filter_value:
                            matches_filters = False
                            break
                
                if not matches_filters:
                    continue
                
                # Calculate similarity
                similarity = self._cosine_similarity(
                    query_embedding,
                    indexed_item['embedding']
                )
                
                if similarity >= similarity_threshold:
                    result = SearchResult(
                        content=indexed_item['content'],
                        title=indexed_item['title'],
                        url=indexed_item['url'],
                        source_type=indexed_item['source_type'],
                        similarity_score=similarity,
                        metadata=indexed_item['metadata']
                    )
                    results.append(result)
            
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            return results[:limit]

    async def suggest_similar_content(
        self,
        content_id: str,
        limit: int = 5,
        similarity_threshold: float = 0.3
    ) -> List[SearchResult]:
        """Find content similar to a specific indexed item."""
        with self._lock:
            if content_id not in self._search_index:
                return []
            
            reference_item = self._search_index[content_id]
            reference_embedding = reference_item['embedding']
            results = []
            
            for other_id, indexed_item in self._search_index.items():
                if other_id == content_id:  # Skip the reference item itself
                    continue
                
                similarity = self._cosine_similarity(
                    reference_embedding,
                    indexed_item['embedding']
                )
                
                if similarity >= similarity_threshold:
                    result = SearchResult(
                        content=indexed_item['content'],
                        title=indexed_item['title'],
                        url=indexed_item['url'],
                        source_type=indexed_item['source_type'],
                        similarity_score=similarity,
                        metadata=indexed_item['metadata']
                    )
                    results.append(result)
            
            results.sort(key=lambda r: r.similarity_score, reverse=True)
            return results[:limit]

    # Test utility methods
    def clear_all(self) -> None:
        """Clear all indexed content (for testing)."""
        with self._lock:
            self._search_index.clear()
            self._next_id = 1

    def get_all_indexed_content(self) -> Dict[str, Dict[str, Any]]:
        """Get all indexed content (for testing)."""
        with self._lock:
            return dict(self._search_index)

    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a query (for testing)."""
        return self._generate_fake_embedding(query)

    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get indexed content by ID (for testing)."""
        with self._lock:
            return self._search_index.get(content_id)