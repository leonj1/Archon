#!/usr/bin/env python3
import sqlite3

DB_PATH = "data/archon.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
