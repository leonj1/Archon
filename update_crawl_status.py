#!/usr/bin/env python3
"""
Direct database update script to set crawl_status to 'completed' for all sources.
"""
import sqlite3
import json

DB_PATH = "data/archon.db"

def main():
    print("🔍 Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n📊 Checking current status...")
    cursor.execute("SELECT source_id, title, metadata FROM archon_sources")
    rows = cursor.fetchall()

    print(f"Found {len(rows)} sources\n")

    for source_id, title, metadata_str in rows:
        print(f"  Source: {title}")
        print(f"    ID: {source_id}")

        # Parse metadata JSON
        metadata = json.loads(metadata_str) if metadata_str else {}
        current_status = metadata.get("crawl_status", "pending")
        print(f"    Current status: {current_status}")

        if current_status == "pending":
            # Update metadata to set crawl_status to completed
            metadata["crawl_status"] = "completed"
            new_metadata_str = json.dumps(metadata)

            # Update the database
            cursor.execute(
                "UPDATE archon_sources SET metadata = ? WHERE source_id = ?",
                (new_metadata_str, source_id)
            )
            print(f"    ✅ Updated to 'completed'")
        else:
            print(f"    ⏭️  Skipping (already {current_status})")

        print()

    # Commit the changes
    conn.commit()
    print("💾 Changes committed to database")

    # Verify the updates
    print("\n🔍 Verifying updates...")
    cursor.execute("SELECT source_id, title, metadata FROM archon_sources")
    rows = cursor.fetchall()

    for source_id, title, metadata_str in rows:
        metadata = json.loads(metadata_str) if metadata_str else {}
        status = metadata.get("crawl_status", "N/A")
        print(f"  {title}: {status}")

    conn.close()
    print("\n✨ Done!")

if __name__ == "__main__":
    main()
