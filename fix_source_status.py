#!/usr/bin/env python3
"""
Script to fix crawl_status for existing sources.
Updates sources with documents from 'pending' to 'completed'.
"""
import requests
import json

BASE_URL = "http://localhost:8181/api"

def get_sources():
    """Get all knowledge sources."""
    response = requests.get(f"{BASE_URL}/rag/sources")
    response.raise_for_status()
    data = response.json()
    return data.get("sources", [])

def get_database_metrics():
    """Get database metrics."""
    response = requests.get(f"{BASE_URL}/database/metrics")
    response.raise_for_status()
    return response.json()

def update_source_metadata(source_id, updates):
    """Update source metadata."""
    response = requests.put(f"{BASE_URL}/knowledge-items/{source_id}", json=updates)
    response.raise_for_status()
    return response.json()

def main():
    print("🔍 Fetching sources...")
    sources = get_sources()
    print(f"Found {len(sources)} sources")

    print("\n📊 Checking database metrics...")
    metrics = get_database_metrics()
    total_pages = metrics.get("tables", {}).get("crawled_pages", 0)
    print(f"Total crawled pages in database: {total_pages}")

    if total_pages == 0:
        print("✅ No crawled pages found - nothing to update")
        return

    print("\n🔄 Updating source statuses...")
    for source in sources:
        source_id = source["source_id"]
        metadata = json.loads(source.get("metadata", "{}"))
        current_status = metadata.get("crawl_status", "pending")

        print(f"\n  Source: {source['title']}")
        print(f"    ID: {source_id}")
        print(f"    Current status: {current_status}")

        if current_status == "pending":
            # Update metadata to set crawl_status to completed
            metadata["crawl_status"] = "completed"

            try:
                update_source_metadata(source_id, {"metadata": metadata})
                print(f"    ✅ Updated to 'completed'")
            except Exception as e:
                print(f"    ❌ Failed to update: {e}")
        else:
            print(f"    ⏭️  Skipping (already {current_status})")

    print("\n✨ Done!")

if __name__ == "__main__":
    main()
