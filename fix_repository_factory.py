#!/usr/bin/env python3
"""
Fix all hardcoded SupabaseDatabaseRepository references to use get_repository() factory.
This ensures the ARCHON_DB_BACKEND environment variable is respected.
"""

import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix a single Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the imports
    content = re.sub(
        r'from \.\.\.repositories\.supabase_repository import SupabaseDatabaseRepository\n',
        '',
        content
    )
    content = re.sub(
        r'from \.\.repositories\.supabase_repository import SupabaseDatabaseRepository\n',
        '',
        content
    )
    
    # Replace utils import if it's only used for get_supabase_client
    content = re.sub(
        r'from \.\.\.utils import get_supabase_client\n',
        '',
        content
    )
    content = re.sub(
        r'from \.\.utils import get_supabase_client\n',
        '',
        content
    )
    
    # Add get_repository import if we're making changes and it's not already there
    if 'SupabaseDatabaseRepository(get_supabase_client())' in content:
        if 'from ...repositories.repository_factory import get_repository' not in content:
            # Find where to add the import (after DatabaseRepository import)
            content = re.sub(
                r'(from \.\.\.repositories(?:\.database_repository)? import DatabaseRepository)',
                r'\1\nfrom ...repositories.repository_factory import get_repository',
                content
            )
            # Handle two-dot imports too
            content = re.sub(
                r'(from \.\.repositories(?:\.database_repository)? import DatabaseRepository)',
                r'\1\nfrom ..repositories.repository_factory import get_repository',
                content
            )
    
    # Replace the actual usage
    content = re.sub(
        r'SupabaseDatabaseRepository\(get_supabase_client\(\)\)',
        r'get_repository()',
        content
    )
    
    # Clean up double blank lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in the server directory."""
    server_dir = Path('/home/jose/src/Archon/python/src/server')
    
    fixed_files = []
    for py_file in server_dir.rglob('*.py'):
        if fix_file(py_file):
            fixed_files.append(py_file)
    
    print(f"Fixed {len(fixed_files)} files:")
    for f in fixed_files:
        print(f"  - {f.relative_to(server_dir.parent.parent)}")

if __name__ == '__main__':
    main()
