"""
Test code example insertion with SQLite repository.

This test validates that code examples can be successfully inserted into
the SQLite database with the correct schema.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.server.repositories.sqlite_repository import SQLiteDatabaseRepository


def get_migration_path():
    """
    Find the migration file path.
    Handles both Docker (/app/migration) and local dev (Archon/migration) structures.
    """
    # Try Docker mounted location first (archon-server mounts ./migration:/app/migration)
    docker_path = Path("/app/migration/sqlite/001_initial_schema.sql")
    if docker_path.exists():
        return str(docker_path)

    # Calculate from test file location for local dev
    test_file = Path(__file__).resolve()
    python_root = test_file.parent.parent  # tests/ -> python/
    project_root = python_root.parent      # python/ -> Archon/
    local_path = project_root / "migration" / "sqlite" / "001_initial_schema.sql"

    if local_path.exists():
        return str(local_path)

    raise FileNotFoundError(
        f"Could not find migration file. Searched:\n"
        f"1. {docker_path} (Docker mount)\n"
        f"2. {local_path} (Local dev)"
    )


@pytest.mark.asyncio
async def test_insert_code_example_with_sqlite():
    """Test inserting a single code example using SQLite repository."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # Initialize repository with schema
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Manually apply schema from migration file
        migration_path = get_migration_path()
        async with repository._get_connection(skip_init=True) as conn:
            with open(migration_path, 'r') as f:
                schema_sql = f.read()
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    await conn.execute(statement)
                    await conn.commit()
                except Exception:
                    pass  # Ignore errors for duplicate table creation

        repository._initialized = True

        # Create a test source first
        source_data = {
            'source_id': str(uuid4()),
            'source_url': 'https://docs.claude.com/en/docs/claude-code/plugins-reference',
            'source_display_name': 'Claude Code Docs',
            'title': 'Claude Code Plugins Reference',
            'summary': 'Documentation for Claude Code plugins'
        }
        await repository.upsert_source(source_data)

        # Prepare code example data matching what code_storage_service sends
        code_example_data = {
            'url': 'https://docs.claude.com/en/docs/claude-code/plugins-reference',
            'chunk_number': 1,
            'content': 'function example() { return "Hello World"; }',
            'summary': 'A simple JavaScript function example',
            'metadata': {
                'language': 'javascript',
                'extracted_at': '2025-01-01T00:00:00Z'
            },
            'source_id': source_data['source_id'],
            'llm_chat_model': 'gpt-4o-mini',
            'embedding_model': 'text-embedding-3-small',
            'embedding_dimension': 1536
        }

        # Insert the code example
        result = await repository.insert_code_example(code_example_data)

        # Verify the insertion
        assert result is not None
        assert 'id' in result
        assert result['url'] == code_example_data['url']
        assert result['source_id'] == source_data['source_id']

        # Retrieve and verify
        examples = await repository.get_code_examples_by_source(source_data['source_id'])
        assert len(examples) == 1
        assert examples[0]['content'] == code_example_data['content']
        assert examples[0]['summary'] == code_example_data['summary']

        print("✅ Single code example insertion test passed")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_insert_code_examples_batch_with_sqlite():
    """Test inserting multiple code examples in batch using SQLite repository."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # Initialize repository with schema
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Manually apply schema from migration file
        migration_path = get_migration_path()
        async with repository._get_connection(skip_init=True) as conn:
            with open(migration_path, 'r') as f:
                schema_sql = f.read()
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    await conn.execute(statement)
                    await conn.commit()
                except Exception:
                    pass  # Ignore errors for duplicate table creation

        repository._initialized = True

        # Create a test source first
        source_data = {
            'source_id': str(uuid4()),
            'source_url': 'https://docs.example.com',
            'source_display_name': 'Example Docs',
            'title': 'Example Documentation',
            'summary': 'Test documentation'
        }
        await repository.upsert_source(source_data)

        # Prepare batch of code examples
        code_examples = [
            {
                'url': 'https://docs.example.com/page1',
                'chunk_number': 1,
                'content': 'def hello(): return "Hello"',
                'summary': 'Python hello function',
                'metadata': {'language': 'python'},
                'source_id': source_data['source_id'],
                'llm_chat_model': 'gpt-4o-mini',
                'embedding_model': 'text-embedding-3-small',
                'embedding_dimension': 1536
            },
            {
                'url': 'https://docs.example.com/page2',
                'chunk_number': 1,
                'content': 'const world = () => "World";',
                'summary': 'JavaScript world function',
                'metadata': {'language': 'javascript'},
                'source_id': source_data['source_id'],
                'llm_chat_model': 'gpt-4o-mini',
                'embedding_model': 'text-embedding-3-small',
                'embedding_dimension': 1536
            },
            {
                'url': 'https://docs.example.com/page3',
                'chunk_number': 1,
                'content': 'public class Test { }',
                'summary': 'Java test class',
                'metadata': {'language': 'java'},
                'source_id': source_data['source_id'],
                'llm_chat_model': 'gpt-4o-mini',
                'embedding_model': 'text-embedding-3-small',
                'embedding_dimension': 1536
            }
        ]

        # Insert batch
        results = await repository.insert_code_examples_batch(code_examples)

        # Verify batch insertion
        assert len(results) == 3
        for result in results:
            assert 'id' in result

        # Retrieve and verify
        examples = await repository.get_code_examples_by_source(source_data['source_id'])
        assert len(examples) == 3

        # Verify content
        contents = [ex['content'] for ex in examples]
        assert 'def hello(): return "Hello"' in contents
        assert 'const world = () => "World";' in contents
        assert 'public class Test { }' in contents

        print("✅ Batch code example insertion test passed")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_code_example_backward_compatibility():
    """Test that code examples work with legacy 'code' field name."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # Initialize repository with schema
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Manually apply schema from migration file
        migration_path = get_migration_path()
        async with repository._get_connection(skip_init=True) as conn:
            with open(migration_path, 'r') as f:
                schema_sql = f.read()
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    await conn.execute(statement)
                    await conn.commit()
                except Exception:
                    pass  # Ignore errors for duplicate table creation

        repository._initialized = True

        # Create a test source
        source_data = {
            'source_id': str(uuid4()),
            'source_url': 'https://test.com',
            'source_display_name': 'Test',
            'title': 'Test',
            'summary': 'Test'
        }
        await repository.upsert_source(source_data)

        # Test with legacy 'code' field (should be mapped to 'content')
        code_example_data = {
            'url': 'https://test.com/legacy',
            'chunk_number': 1,
            'code': 'legacy code example',  # Using 'code' instead of 'content'
            'summary': 'Legacy format test',
            'metadata': {},
            'source_id': source_data['source_id'],
            'llm_chat_model': 'gpt-4o-mini',
            'embedding_model': 'text-embedding-3-small',
            'embedding_dimension': 1536
        }

        # Insert should work with backward compatibility
        result = await repository.insert_code_example(code_example_data)
        assert result is not None

        # Retrieve and verify content was stored
        examples = await repository.get_code_examples_by_source(source_data['source_id'])
        assert len(examples) == 1
        assert examples[0]['content'] == 'legacy code example'

        print("✅ Backward compatibility test passed")

    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == '__main__':
    # Run tests directly
    asyncio.run(test_insert_code_example_with_sqlite())
    asyncio.run(test_insert_code_examples_batch_with_sqlite())
    asyncio.run(test_code_example_backward_compatibility())
    print("\n✅ All tests passed!")
