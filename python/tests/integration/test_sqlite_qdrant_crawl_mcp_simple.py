"""
Simplified Integration Test: Qdrant Workflow Demo

This test demonstrates the workflow without complex dependencies:
1. Generate embeddings using OpenAI directly
2. Store vectors in Qdrant (in-memory)
3. Perform semantic search

Run with: make test-integration-sqlite-qdrant
"""

import os
import uuid

import pytest
from openai import AsyncOpenAI

# Check for optional dependencies
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Skip if dependencies not available
pytestmark = [
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set - required for embeddings"
    ),
    pytest.mark.skipif(
        not QDRANT_AVAILABLE,
        reason="qdrant-client not installed - optional integration test"
    )
]


class TestSQLiteQdrantWorkflow:
    """Simplified integration test demonstrating the workflow."""

    @pytest.mark.asyncio
    async def test_embedding_and_search_workflow(self):
        """
        Demonstrate the complete workflow:
        1. Create sample documents (simulating crawl results)
        2. Generate embeddings using OpenAI directly
        3. Store in Qdrant (in-memory mode)
        4. Perform semantic search
        """

        print("\n" + "="*80)
        print("SIMPLIFIED INTEGRATION TEST")
        print("Demonstrating: OpenAI Embeddings → Qdrant → Semantic Search")
        print("="*80)

        # Step 1: Simulate crawled documents
        print("\nStep 1: Creating sample documents...")
        sample_docs = [
            {
                "id": "doc_1",
                "url": "https://github.com/The-Pocket/PocketFlow",
                "content": "PocketFlow is a workflow automation tool for developers. It helps streamline development processes and CI/CD.",
                "source_id": "src_001",
            },
            {
                "id": "doc_2",
                "url": "https://github.com/The-Pocket/PocketFlow/features",
                "content": "Key features include continuous integration, automated testing, deployment pipelines, and GitHub Actions integration.",
                "source_id": "src_001",
            },
            {
                "id": "doc_3",
                "url": "https://github.com/The-Pocket/PocketFlow/getting-started",
                "content": "Getting started with PocketFlow is easy. Install via npm, configure your workflow YAML file, and run your first automation.",
                "source_id": "src_001",
            },
        ]

        print(f"✓ Created {len(sample_docs)} sample documents")

        # Step 2: Generate embeddings using OpenAI directly
        print("\nStep 2: Generating embeddings with OpenAI...")

        api_key = os.getenv("OPENAI_API_KEY")
        client = AsyncOpenAI(api_key=api_key)

        doc_texts = [doc["content"] for doc in sample_docs]

        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=doc_texts
        )

        embeddings = [item.embedding for item in response.data]

        assert len(embeddings) == len(sample_docs), f"Embedding count mismatch: got {len(embeddings)}, expected {len(sample_docs)}"
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0])}")
        print(f"✓ Model used: {response.model}")

        # Step 3: Store in Qdrant (in-memory mode)
        print("\nStep 3: Storing vectors in Qdrant...")

        # Use in-memory Qdrant client
        qdrant_client = QdrantClient(":memory:")
        collection_name = "test_pocketflow"

        # Create collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=len(embeddings[0]),
                distance=Distance.COSINE
            )
        )
        print(f"✓ Created Qdrant collection: {collection_name}")

        # Store vectors
        points = []
        for doc, embedding in zip(sample_docs, embeddings):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "doc_id": doc["id"],
                    "url": doc["url"],
                    "content": doc["content"],
                    "source_id": doc["source_id"],
                }
            )
            points.append(point)

        qdrant_client.upsert(collection_name=collection_name, points=points)
        print(f"✓ Stored {len(points)} vectors in Qdrant")

        # Verify collection
        collection_info = qdrant_client.get_collection(collection_name)
        print(f"\n📊 Qdrant Collection Stats:")
        print(f"  - Name: {collection_name}")
        print(f"  - Vectors count: {collection_info.vectors_count}")
        print(f"  - Points count: {collection_info.points_count}")
        print(f"  - Status: {collection_info.status.value}")

        # Step 4: Perform semantic search
        print("\nStep 4: Performing Semantic Search...")

        test_query = "How do I get started with workflow automation?"
        print(f"🔍 Query: '{test_query}'")

        # Generate query embedding
        query_response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=[test_query]
        )
        query_embedding = query_response.data[0].embedding
        print(f"✓ Generated query embedding")

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=3
        )

        assert len(search_results) > 0, "No search results found"
        print(f"✓ Found {len(search_results)} relevant results")

        # Display results
        print(f"\n🎯 Search Results (ranked by relevance):")
        for i, result in enumerate(search_results, 1):
            print(f"\n  #{i} - Score: {result.score:.4f}")
            print(f"      URL: {result.payload['url']}")
            print(f"      Content: {result.payload['content'][:120]}...")

        # Step 5: Validate MCP-style workflow
        print("\nStep 5: MCP-Style Workflow Validation...")

        # Simulate what MCP search would return
        mcp_results = []
        for result in search_results:
            mcp_results.append({
                "url": result.payload["url"],
                "content": result.payload["content"],
                "similarity_score": result.score,
                "source_id": result.payload["source_id"],
            })

        print(f"✓ MCP would return {len(mcp_results)} enriched results")

        # Validate structure
        for result in mcp_results:
            assert "url" in result
            assert "content" in result
            assert "similarity_score" in result
            assert result['similarity_score'] > 0

        print("✓ MCP response structure validated")

        # Verify the best result makes sense for the query
        best_match = search_results[0]
        assert "getting-started" in best_match.payload['url'].lower() or "start" in best_match.payload['content'].lower(), \
            "Expected 'getting started' doc to be top result for 'how to get started' query"

        print(f"✓ Semantic search returned relevant result (getting-started doc)")

        # Final Summary
        print("\n" + "="*80)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"\nWorkflow Demonstrated:")
        print(f"  ✓ Generated embeddings for {len(sample_docs)} documents")
        print(f"  ✓ Stored {collection_info.points_count} vectors in Qdrant")
        print(f"  ✓ Performed semantic search")
        print(f"  ✓ Returned {len(search_results)} relevant results")
        print(f"  ✓ Top result score: {search_results[0].score:.4f}")
        print(f"  ✓ Best match: {search_results[0].payload['url']}")
        print(f"\nThis demonstrates the core workflow:")
        print(f"  1. Crawl website → documents")
        print(f"  2. Documents → OpenAI embeddings")
        print(f"  3. Embeddings → Qdrant vector storage")
        print(f"  4. Query → semantic search → relevant results")
        print(f"  5. MCP tools can expose this workflow to AI IDEs")
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
