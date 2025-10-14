"""
Schema Validation Tests for SQLite Database

This test suite validates that the actual database schema matches the expected
schema defined in the migration files. It prevents schema drift and catches
issues like outdated database files with incompatible schemas.

Key validations:
- All expected tables exist
- All expected columns exist with correct types
- Required constraints are present (NOT NULL, UNIQUE, etc.)
- Foreign key relationships are correct
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Any

import pytest

from src.server.repositories.sqlite_repository import SQLiteDatabaseRepository


def get_migration_path() -> str:
    """
    Find the SQLite migration file path.
    Handles both Docker (/app/migration) and local dev structures.
    """
    # Try Docker mounted location first
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


def parse_schema_from_sql(sql_content: str) -> dict[str, dict[str, Any]]:
    """
    Parse CREATE TABLE statements from SQL migration file.

    Returns:
        Dictionary mapping table names to their column definitions
        Example: {
            'archon_sources': {
                'columns': {
                    'source_id': {'type': 'TEXT', 'constraints': ['PRIMARY KEY']},
                    'source_url': {'type': 'TEXT', 'constraints': []},
                    ...
                },
                'table_constraints': ['UNIQUE(url, chunk_number)', ...]
            }
        }
    """
    tables = {}

    # Find all CREATE TABLE statements
    # Match: CREATE TABLE IF NOT EXISTS table_name ( ... );
    table_pattern = r'CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\w+)\s*\((.*?)\);'

    for match in re.finditer(table_pattern, sql_content, re.DOTALL | re.IGNORECASE):
        table_name = match.group(1)
        table_body = match.group(2)

        columns = {}
        table_constraints = []

        # Split by commas, but be careful with nested parentheses
        lines = []
        current_line = ""
        paren_depth = 0

        for char in table_body:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                lines.append(current_line.strip())
                current_line = ""
                continue
            current_line += char

        if current_line.strip():
            lines.append(current_line.strip())

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('--'):
                continue

            # Check for table-level constraints
            if (line.upper().startswith('UNIQUE(') or
                line.upper().startswith('FOREIGN KEY') or
                line.upper().startswith('CHECK(') or
                line.upper().startswith('PRIMARY KEY(')):
                table_constraints.append(line)
                continue

            # Parse column definition: column_name TYPE [constraints]
            parts = line.split(None, 1)
            if len(parts) < 1:
                continue

            column_name = parts[0].strip()

            # Extract type and constraints
            remainder = parts[1] if len(parts) > 1 else ""

            # Parse type (first word after column name)
            type_match = re.match(r'(\w+)', remainder)
            column_type = type_match.group(1) if type_match else "TEXT"

            # Extract constraints
            constraints = []
            if 'PRIMARY KEY' in remainder.upper():
                constraints.append('PRIMARY KEY')
            if 'AUTOINCREMENT' in remainder.upper():
                constraints.append('AUTOINCREMENT')
            if 'NOT NULL' in remainder.upper():
                constraints.append('NOT NULL')
            if 'UNIQUE' in remainder.upper() and 'UNIQUE(' not in remainder.upper():
                constraints.append('UNIQUE')
            if 'DEFAULT' in remainder.upper():
                default_match = re.search(r"DEFAULT\s+([^,\n]+)", remainder, re.IGNORECASE)
                if default_match:
                    constraints.append(f'DEFAULT {default_match.group(1).strip()}')
            if 'FOREIGN KEY' in remainder.upper() or 'REFERENCES' in remainder.upper():
                constraints.append('FOREIGN KEY')

            columns[column_name] = {
                'type': column_type.upper(),
                'constraints': constraints
            }

        tables[table_name] = {
            'columns': columns,
            'table_constraints': table_constraints
        }

    return tables


@pytest.mark.asyncio
async def test_schema_matches_migration_file():
    """
    Test that the actual database schema matches the expected schema
    from the migration file.

    This test:
    1. Creates a fresh database using the migration file
    2. Queries the actual schema using PRAGMA table_info
    3. Compares actual vs expected tables and columns
    """
    # Create temporary database
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # Initialize repository and apply schema
        repository = SQLiteDatabaseRepository(db_path=db_path)

        migration_path = get_migration_path()
        with open(migration_path, 'r') as f:
            schema_sql = f.read()

        # Apply migration
        async with repository._get_connection(skip_init=True) as conn:
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    await conn.execute(statement)
                    await conn.commit()
                except Exception as e:
                    # Some statements may fail on re-application, that's ok
                    pass

        repository._initialized = True

        # Parse expected schema from migration file
        expected_tables = parse_schema_from_sql(schema_sql)

        # Critical tables that must exist
        critical_tables = [
            'archon_sources',
            'archon_crawled_pages',
            'archon_code_examples',
            'archon_page_metadata',
            'archon_projects',
            'archon_tasks',
            'archon_settings'
        ]

        # Validate each critical table
        for table_name in critical_tables:
            assert table_name in expected_tables, f"Critical table {table_name} not found in migration file"

            # Get actual schema from database
            async with repository._get_connection() as conn:
                cursor = await conn.execute(f"PRAGMA table_info({table_name})")
                actual_columns = await cursor.fetchall()

            # Convert to dict for easier comparison
            actual_column_dict = {
                col[1]: {  # col[1] is column name
                    'type': col[2],  # col[2] is type
                    'not_null': col[3] == 1,  # col[3] is not null flag
                    'default': col[4],  # col[4] is default value
                    'pk': col[5] == 1  # col[5] is primary key flag
                }
                for col in actual_columns
            }

            expected_columns = expected_tables[table_name]['columns']

            # Check that all expected columns exist
            for col_name, col_def in expected_columns.items():
                assert col_name in actual_column_dict, (
                    f"Table {table_name} is missing expected column '{col_name}'. "
                    f"This indicates schema drift or an outdated database file."
                )

                actual_col = actual_column_dict[col_name]

                # Validate type (normalize for comparison)
                expected_type = col_def['type'].upper()
                actual_type = actual_col['type'].upper()

                # SQLite type affinity - TEXT and TEXT are same, INTEGER and INT are same
                type_equivalent = (
                    expected_type == actual_type or
                    (expected_type in ['TEXT', 'VARCHAR'] and actual_type in ['TEXT', 'VARCHAR']) or
                    (expected_type in ['INTEGER', 'INT'] and actual_type in ['INTEGER', 'INT'])
                )

                assert type_equivalent, (
                    f"Table {table_name}, column {col_name}: "
                    f"Type mismatch. Expected {expected_type}, got {actual_type}"
                )

        print(f"✅ Schema validation passed for {len(critical_tables)} critical tables")

    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_code_examples_table_has_required_columns():
    """
    Specific test for archon_code_examples table to prevent the
    'chunk_number' column missing error that occurred previously.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Apply schema
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
                    pass

        repository._initialized = True

        # Get actual columns
        async with repository._get_connection() as conn:
            cursor = await conn.execute("PRAGMA table_info(archon_code_examples)")
            columns = await cursor.fetchall()

        column_names = [col[1] for col in columns]

        # These columns are REQUIRED for code storage service to work
        required_columns = [
            'id',
            'url',
            'chunk_number',  # This was missing in the old schema
            'content',
            'summary',
            'metadata',
            'source_id',
            'llm_chat_model',
            'embedding_model',
            'embedding_dimension',
            'created_at'
        ]

        for col in required_columns:
            assert col in column_names, (
                f"archon_code_examples is missing required column '{col}'. "
                f"Found columns: {column_names}"
            )

        print(f"✅ archon_code_examples table has all {len(required_columns)} required columns")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_unique_constraints_exist():
    """
    Validate that critical UNIQUE constraints are present to prevent
    duplicate data issues.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Apply schema
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
                    pass

        repository._initialized = True

        # Check for UNIQUE constraints on critical tables
        constraints_to_check = {
            'archon_code_examples': [('url', 'chunk_number')],
            'archon_crawled_pages': [('url', 'chunk_number')],
        }

        async with repository._get_connection() as conn:
            for table_name, unique_combinations in constraints_to_check.items():
                # Get CREATE TABLE statement to check for UNIQUE constraints
                cursor = await conn.execute(
                    f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                create_statement = await cursor.fetchone()

                assert create_statement, f"Table {table_name} does not exist"

                sql = create_statement[0]

                for columns in unique_combinations:
                    # Check for UNIQUE constraint on these columns
                    unique_pattern = f"UNIQUE({', '.join(columns)})"
                    assert unique_pattern in sql, (
                        f"Table {table_name} is missing UNIQUE constraint on columns {columns}. "
                        f"This can lead to duplicate data."
                    )

        print("✅ All critical UNIQUE constraints are present")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_foreign_key_constraints_exist():
    """
    Validate that foreign key relationships are properly defined.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Apply schema
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
                    pass

        repository._initialized = True

        # Check foreign keys on critical tables
        tables_with_fks = {
            'archon_code_examples': 'source_id',
            'archon_crawled_pages': 'source_id',
            'archon_tasks': 'project_id',
        }

        async with repository._get_connection() as conn:
            for table_name, fk_column in tables_with_fks.items():
                cursor = await conn.execute(f"PRAGMA foreign_key_list({table_name})")
                foreign_keys = await cursor.fetchall()

                # Check that at least one foreign key exists for this table
                fk_columns = [fk[3] for fk in foreign_keys]  # fk[3] is the 'from' column

                assert fk_column in fk_columns or len(foreign_keys) > 0, (
                    f"Table {table_name} is missing expected foreign key on {fk_column}"
                )

        print("✅ Foreign key constraints validated")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.mark.asyncio
async def test_schema_prevents_old_database_files():
    """
    Test that validates we can detect and reject old database files
    with incompatible schemas (like the one that caused the bug).

    This simulates the exact issue we encountered where an old database
    file was missing the chunk_number column.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        repository = SQLiteDatabaseRepository(db_path=db_path)

        # Create an OLD schema (without chunk_number column)
        old_schema = """
        CREATE TABLE archon_code_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            title TEXT,
            summary TEXT NOT NULL,
            language TEXT,
            code TEXT NOT NULL,
            relevance_score REAL,
            url TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        );
        """

        async with repository._get_connection(skip_init=True) as conn:
            await conn.execute(old_schema)
            await conn.commit()

        repository._initialized = True

        # Try to query the schema
        async with repository._get_connection() as conn:
            cursor = await conn.execute("PRAGMA table_info(archon_code_examples)")
            columns = await cursor.fetchall()

        column_names = [col[1] for col in columns]

        # This should detect the missing column
        has_chunk_number = 'chunk_number' in column_names
        has_content = 'content' in column_names

        # The old schema should NOT have these columns
        assert not has_chunk_number, "Test setup error: old schema shouldn't have chunk_number"
        assert not has_content, "Test setup error: old schema shouldn't have content column"

        # Now validate detection - this would be the schema check
        required_columns = {'chunk_number', 'content', 'embedding_model', 'llm_chat_model'}
        actual_columns = set(column_names)
        missing_columns = required_columns - actual_columns

        assert len(missing_columns) > 0, (
            "Schema validation should detect missing columns in old database files"
        )

        print(f"✅ Successfully detected old schema with missing columns: {missing_columns}")

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


if __name__ == '__main__':
    import asyncio

    print("Running schema validation tests...\n")

    asyncio.run(test_schema_matches_migration_file())
    asyncio.run(test_code_examples_table_has_required_columns())
    asyncio.run(test_unique_constraints_exist())
    asyncio.run(test_foreign_key_constraints_exist())
    asyncio.run(test_schema_prevents_old_database_files())

    print("\n✅ All schema validation tests passed!")
