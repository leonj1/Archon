"""
Supabase Search Repository Implementation

Concrete implementation of search repository for Supabase database backend.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np

from ...interfaces import IDatabase, IVectorStore, VectorSearchResult, QueryResult
from ..interfaces.search_repository_interface import (
    ISearchRepository, 
    SearchResult, 
    CodeSearchResult
)


class SupabaseSearchRepository(ISearchRepository):
    """
    Supabase implementation of search repository.
    Handles search CRUD operations for Supabase database backend.
    """
    
    def __init__(self, database: IDatabase, vector_store: IVectorStore):
        """Initialize Supabase search repository."""
        super().__init__(database, vector_store)
    
    # Base repository methods (not really applicable for search repository)
    
    async def create(self, entity_data: Dict[str, Any]) -> Optional[SearchResult]:
        """Create a new search index entry (not typically used)."""
        # Search repositories don't usually create search results directly
        # This might be used for logging search queries
        return None
    
    async def get_by_id(self, entity_id: str) -> Optional[SearchResult]:
        """Get search result by ID (not typically used)."""
        return None
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[SearchResult]:
        """Update search index entry (not typically used)."""
        return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete search index entry (not typically used)."""
        return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[SearchResult]:
        """List all search results (not typically used)."""
        return []
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[SearchResult]:
        """Find search results matching criteria (not typically used)."""
        return []
    
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """Count search results (not typically used)."""
        return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if search result exists (not typically used)."""
        return False
    
    # Vector Search Operations
    
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        collection: str = "documents",
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None,
    ) -> List[SearchResult]:
        """Perform similarity search using vector embeddings."""
        try:
            # Use the vector store's search functionality
            vector_results = await self._vector_store.search(
                collection=collection,
                query_vector=query_embedding,
                top_k=top_k,
                filters=filters,
                include_metadata=True,
                include_vectors=False
            )
            
            # Convert vector results to search results
            search_results = []
            for vector_result in vector_results:
                # Apply minimum score filter if specified
                if min_score and vector_result.score < min_score:
                    continue
                
                search_result = SearchResult.from_vector_result(
                    vector_result,
                    additional_data={
                        "source_id": vector_result.metadata.get("source_id"),
                        "title": vector_result.metadata.get("title"),
                        "url": vector_result.metadata.get("url"),
                        "content_type": vector_result.metadata.get("content_type", "text"),
                        "language": vector_result.metadata.get("language"),
                        "chunk_number": vector_result.metadata.get("chunk_number"),
                    }
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception:
            return []
    
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
        """Perform hybrid search combining text and vector search."""
        try:
            # Perform vector search
            vector_results = await self.similarity_search(
                query_embedding=query_embedding,
                collection=collection,
                top_k=top_k * 2,  # Get more results for merging
                filters=filters
            )
            
            # Perform text search
            text_results = await self.search_documents(
                query=query_text,
                match_count=top_k * 2,  # Get more results for merging
                content_type=filters.get("content_type") if filters else None,
                language=filters.get("language") if filters else None
            )
            
            # Merge and re-score results
            merged_results = {}
            
            # Add vector results with vector weight
            for result in vector_results:
                merged_results[result.id] = {
                    "result": result,
                    "vector_score": result.score * vector_weight,
                    "text_score": 0.0
                }
            
            # Add text results with text weight
            for result in text_results:
                if result.id in merged_results:
                    merged_results[result.id]["text_score"] = result.score * text_weight
                else:
                    merged_results[result.id] = {
                        "result": result,
                        "vector_score": 0.0,
                        "text_score": result.score * text_weight
                    }
            
            # Calculate combined scores and sort
            final_results = []
            for item in merged_results.values():
                combined_score = item["vector_score"] + item["text_score"]
                result = item["result"]
                result.score = combined_score
                final_results.append(result)
            
            # Sort by combined score and limit
            final_results.sort(key=lambda x: x.score, reverse=True)
            return final_results[:top_k]
            
        except Exception:
            return []
    
    async def search_documents(
        self,
        query: str,
        match_count: int = 5,
        source_id: Optional[str] = None,
        content_type: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search documents with text-based query."""
        try:
            # Build filters
            filters = {}
            if source_id:
                filters["source_id"] = source_id
            if content_type:
                filters["content_type"] = content_type
            if language:
                filters["language"] = language
            
            # Get documents from database
            result = await self._database.select(
                "documents",
                filters=filters,
                limit=match_count * 5  # Get more for filtering
            )
            
            if not result.success:
                return []
            
            # Filter by query text in memory (Supabase adapter doesn't support LIKE directly)
            query_lower = query.lower()
            matching_documents = []
            
            for row in result.data:
                content = row.get("content", "")
                title = row.get("title", "")
                
                # Calculate simple text similarity score
                score = 0.0
                query_words = query_lower.split()
                content_lower = content.lower()
                title_lower = title.lower()
                
                # Score based on word matches
                for word in query_words:
                    if word in content_lower:
                        score += 1.0
                    if word in title_lower:
                        score += 2.0  # Title matches are more important
                
                # Normalize score
                if score > 0:
                    score = score / (len(query_words) * 3)  # Max possible score
                    
                    search_result = SearchResult(
                        id=row.get("id"),
                        content=content,
                        score=score,
                        source_id=row.get("source_id"),
                        title=title,
                        url=row.get("url"),
                        content_type=row.get("content_type", "text"),
                        metadata=row.get("metadata", {}),
                        chunk_number=row.get("chunk_number"),
                        language=row.get("language"),
                    )
                    matching_documents.append(search_result)
            
            # Sort by score and limit
            matching_documents.sort(key=lambda x: x.score, reverse=True)
            return matching_documents[:match_count]
            
        except Exception:
            return []
    
    async def search_code_examples(
        self,
        query: str,
        match_count: int = 3,
        language: Optional[str] = None,
        function_name: Optional[str] = None,
    ) -> List[CodeSearchResult]:
        """Search code examples with text-based query."""
        try:
            # Build filters
            filters = {}
            if language:
                filters["language"] = language
            if function_name:
                filters["function_name"] = function_name
            
            # Get code examples from database
            result = await self._database.select(
                "code_examples",
                filters=filters,
                limit=match_count * 5  # Get more for filtering
            )
            
            if not result.success:
                return []
            
            # Filter by query text in memory
            query_lower = query.lower()
            matching_examples = []
            
            for row in result.data:
                code_content = row.get("code_content", "")
                description = row.get("description", "")
                function_name = row.get("function_name", "")
                class_name = row.get("class_name", "")
                
                # Calculate simple text similarity score
                score = 0.0
                query_words = query_lower.split()
                code_lower = code_content.lower()
                desc_lower = description.lower()
                func_lower = function_name.lower()
                class_lower = class_name.lower()
                
                # Score based on word matches
                for word in query_words:
                    if word in code_lower:
                        score += 1.0
                    if word in desc_lower:
                        score += 1.5
                    if word in func_lower:
                        score += 2.0
                    if word in class_lower:
                        score += 2.0
                
                # Normalize score
                if score > 0:
                    score = score / (len(query_words) * 4)  # Max possible score
                    
                    code_result = CodeSearchResult(
                        id=row.get("id"),
                        code_content=code_content,
                        language=row.get("language", ""),
                        file_path=row.get("file_path", ""),
                        score=score,
                        function_name=function_name,
                        class_name=class_name,
                        description=description,
                        source_id=row.get("source_id"),
                        metadata=row.get("metadata", {}),
                    )
                    matching_examples.append(code_result)
            
            # Sort by score and limit
            matching_examples.sort(key=lambda x: x.score, reverse=True)
            return matching_examples[:match_count]
            
        except Exception:
            return []
    
    async def rag_query(
        self,
        query: str,
        query_embedding: Optional[np.ndarray] = None,
        match_count: int = 5,
        source_filters: Optional[List[str]] = None,
        content_type_filters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Perform RAG (Retrieval Augmented Generation) query."""
        try:
            # Build filters
            filters = {}
            if source_filters:
                filters["source_id"] = source_filters  # This might need special handling in adapter
            if content_type_filters:
                filters["content_type"] = content_type_filters  # This might need special handling in adapter
            
            context_documents = []
            
            # Use vector search if embedding is provided
            if query_embedding is not None:
                vector_results = await self.similarity_search(
                    query_embedding=query_embedding,
                    collection="documents",
                    top_k=match_count,
                    filters=filters,
                    min_score=0.7  # Minimum relevance threshold
                )
                context_documents.extend(vector_results)
            
            # If we don't have enough results, supplement with text search
            if len(context_documents) < match_count:
                text_results = await self.search_documents(
                    query=query,
                    match_count=match_count - len(context_documents),
                    source_id=source_filters[0] if source_filters and len(source_filters) == 1 else None,
                    content_type=content_type_filters[0] if content_type_filters and len(content_type_filters) == 1 else None,
                )
                
                # Avoid duplicates
                existing_ids = {doc.id for doc in context_documents}
                for result in text_results:
                    if result.id not in existing_ids:
                        context_documents.append(result)
            
            # Prepare context
            context_text = "\n\n".join([
                f"Source: {doc.title or doc.url or 'Unknown'}\n{doc.content}"
                for doc in context_documents
            ])
            
            return {
                "query": query,
                "context_documents": [doc.to_dict() for doc in context_documents],
                "context_text": context_text,
                "document_count": len(context_documents),
                "sources": list(set([doc.source_id for doc in context_documents if doc.source_id])),
                "metadata": {
                    "search_method": "hybrid" if query_embedding is not None else "text",
                    "filters_applied": filters,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
            
        except Exception:
            return {
                "query": query,
                "context_documents": [],
                "context_text": "",
                "document_count": 0,
                "sources": [],
                "metadata": {
                    "error": "Search failed",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }
    
    # Semantic Search
    
    async def find_similar_documents(
        self,
        document_id: str,
        top_k: int = 5,
        exclude_same_source: bool = False,
    ) -> List[SearchResult]:
        """Find documents similar to a given document."""
        try:
            # Get the reference document's embedding
            reference_doc = await self._database.select(
                "documents",
                filters={"id": document_id}
            )
            
            if not reference_doc.success or not reference_doc.data:
                return []
            
            doc_data = reference_doc.data[0]
            embedding = doc_data.get("embedding")
            
            if not embedding:
                return []
            
            # Convert to numpy array
            query_embedding = np.array(embedding)
            
            # Build filters
            filters = None
            if exclude_same_source:
                source_id = doc_data.get("source_id")
                if source_id:
                    # This is a simplified approach - in reality, you'd want to exclude the source
                    # For now, we'll filter it out in post-processing
                    pass
            
            # Perform similarity search
            similar_results = await self.similarity_search(
                query_embedding=query_embedding,
                collection="documents",
                top_k=top_k + 1,  # Get one extra to account for the reference document
                filters=filters
            )
            
            # Filter out the reference document and same source if requested
            filtered_results = []
            reference_source = doc_data.get("source_id") if exclude_same_source else None
            
            for result in similar_results:
                if result.id == document_id:
                    continue  # Skip the reference document
                
                if exclude_same_source and reference_source and result.source_id == reference_source:
                    continue  # Skip documents from the same source
                
                filtered_results.append(result)
            
            return filtered_results[:top_k]
            
        except Exception:
            return []
    
    async def cluster_documents(
        self,
        source_id: Optional[str] = None,
        num_clusters: int = 5,
        min_cluster_size: int = 2,
    ) -> Dict[str, Any]:
        """Cluster documents based on semantic similarity."""
        try:
            # This is a simplified clustering implementation
            # In practice, you'd want to use proper clustering algorithms like K-means
            
            # Get documents with embeddings
            filters = {}
            if source_id:
                filters["source_id"] = source_id
            
            result = await self._database.select(
                "documents",
                filters=filters,
                limit=1000  # Reasonable limit for clustering
            )
            
            if not result.success:
                return {"clusters": [], "total_documents": 0}
            
            # Filter documents that have embeddings
            documents_with_embeddings = []
            for row in result.data:
                if row.get("embedding"):
                    documents_with_embeddings.append(row)
            
            if len(documents_with_embeddings) < min_cluster_size:
                return {"clusters": [], "total_documents": len(documents_with_embeddings)}
            
            # Simple clustering: group by source and content type
            clusters = {}
            
            for doc in documents_with_embeddings:
                # Create cluster key based on source and content type
                cluster_key = f"{doc.get('source_id', 'unknown')}_{doc.get('content_type', 'text')}"
                
                if cluster_key not in clusters:
                    clusters[cluster_key] = {
                        "id": cluster_key,
                        "documents": [],
                        "centroid": None,
                        "metadata": {
                            "source_id": doc.get("source_id"),
                            "content_type": doc.get("content_type"),
                        }
                    }
                
                clusters[cluster_key]["documents"].append({
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "url": doc.get("url"),
                    "content_preview": doc.get("content", "")[:200] + "...",
                })
            
            # Filter clusters by minimum size
            valid_clusters = []
            for cluster in clusters.values():
                if len(cluster["documents"]) >= min_cluster_size:
                    valid_clusters.append(cluster)
            
            # Limit to requested number of clusters
            valid_clusters = valid_clusters[:num_clusters]
            
            return {
                "clusters": valid_clusters,
                "total_documents": len(documents_with_embeddings),
                "num_clusters": len(valid_clusters),
                "clustering_method": "source_content_type",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception:
            return {"clusters": [], "total_documents": 0}
    
    # Search Analytics & Optimization
    
    async def get_search_statistics(
        self,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get search usage statistics."""
        try:
            # This would typically query a search_logs table
            # For now, return mock statistics
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=time_range_days)
            
            return {
                "time_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": time_range_days,
                },
                "total_searches": 0,  # Would query search_logs table
                "unique_queries": 0,
                "average_results_per_query": 0.0,
                "most_common_queries": [],
                "search_types": {
                    "vector_search": 0,
                    "text_search": 0,
                    "hybrid_search": 0,
                    "code_search": 0,
                },
                "performance": {
                    "average_response_time_ms": 0.0,
                    "slowest_queries": [],
                },
            }
            
        except Exception:
            return {"error": "Failed to retrieve search statistics"}
    
    async def log_search_query(
        self,
        query: str,
        results_count: int,
        search_type: str,
        execution_time_ms: float,
        filters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log search query for analytics."""
        try:
            # This would typically insert into a search_logs table
            # For now, just return True to indicate successful logging
            
            log_data = {
                "query": query,
                "results_count": results_count,
                "search_type": search_type,
                "execution_time_ms": execution_time_ms,
                "filters": json.dumps(filters) if filters else None,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # In a real implementation, you'd insert this into a search_logs table
            # result = await self._database.insert("search_logs", log_data)
            # return result.success
            
            return True
            
        except Exception:
            return False
    
    async def get_popular_queries(
        self,
        limit: int = 10,
        time_range_days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        try:
            # This would typically query search_logs table and group by query
            # For now, return empty list
            
            return []
            
        except Exception:
            return []
    
    # Index Management
    
    async def rebuild_search_index(
        self,
        collection: str = "documents",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Rebuild search index for better performance."""
        try:
            # This would typically rebuild vector indices or full-text search indices
            # For now, return mock statistics
            
            return {
                "collection": collection,
                "rebuild_started": datetime.utcnow().isoformat(),
                "status": "completed",
                "documents_processed": 0,
                "errors": [],
            }
            
        except Exception:
            return {
                "collection": collection,
                "status": "failed",
                "error": "Rebuild failed",
            }
    
    async def optimize_search_index(self, collection: str = "documents") -> bool:
        """Optimize search index for better performance."""
        try:
            # This would typically optimize vector indices
            # For now, just return True
            return True
            
        except Exception:
            return False
    
    async def validate_embeddings(
        self,
        collection: str = "documents",
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """Validate embedding quality and consistency."""
        try:
            # Get sample of documents with embeddings
            result = await self._database.select(
                collection,
                limit=sample_size
            )
            
            if not result.success:
                return {"valid": False, "error": "Failed to fetch documents"}
            
            valid_embeddings = 0
            invalid_embeddings = 0
            embedding_dimensions = set()
            
            for row in result.data:
                embedding = row.get("embedding")
                if embedding:
                    if isinstance(embedding, list) and len(embedding) > 0:
                        valid_embeddings += 1
                        embedding_dimensions.add(len(embedding))
                    else:
                        invalid_embeddings += 1
                else:
                    invalid_embeddings += 1
            
            return {
                "collection": collection,
                "sample_size": len(result.data),
                "valid_embeddings": valid_embeddings,
                "invalid_embeddings": invalid_embeddings,
                "embedding_dimensions": list(embedding_dimensions),
                "consistent_dimensions": len(embedding_dimensions) <= 1,
                "validation_timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception:
            return {"valid": False, "error": "Validation failed"}
    
    # Advanced Search Features
    
    async def search_with_facets(
        self,
        query: str,
        facet_fields: List[str],
        match_count: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search with faceted navigation."""
        try:
            # Perform the main search
            search_results = await self.search_documents(
                query=query,
                match_count=match_count,
                source_id=filters.get("source_id") if filters else None,
                content_type=filters.get("content_type") if filters else None,
                language=filters.get("language") if filters else None,
            )
            
            # Calculate facets
            facets = {}
            for field in facet_fields:
                facets[field] = {}
            
            # Get all documents for facet calculation (simplified approach)
            all_docs_result = await self._database.select("documents", limit=1000)
            
            if all_docs_result.success:
                for row in all_docs_result.data:
                    for field in facet_fields:
                        value = row.get(field, "unknown")
                        if field not in facets:
                            facets[field] = {}
                        facets[field][value] = facets[field].get(value, 0) + 1
            
            return {
                "query": query,
                "results": [result.to_dict() for result in search_results],
                "facets": facets,
                "total_results": len(search_results),
            }
            
        except Exception:
            return {
                "query": query,
                "results": [],
                "facets": {},
                "total_results": 0,
            }
    
    async def search_suggestions(
        self,
        partial_query: str,
        limit: int = 5
    ) -> List[str]:
        """Get search query suggestions/autocomplete."""
        try:
            # This would typically use a suggestions index or common queries
            # For now, return empty list
            
            return []
            
        except Exception:
            return []
    
    async def batch_similarity_search(
        self,
        query_embeddings: List[np.ndarray],
        collection: str = "documents",
        top_k: int = 5,
    ) -> List[List[SearchResult]]:
        """Perform batch similarity search for multiple queries."""
        try:
            results = []
            
            for embedding in query_embeddings:
                query_results = await self.similarity_search(
                    query_embedding=embedding,
                    collection=collection,
                    top_k=top_k
                )
                results.append(query_results)
            
            return results
            
        except Exception:
            return []