#!/usr/bin/env python3
"""Generate correct stub implementations based on abstract method signatures."""

import ast
import re
from pathlib import Path

def extract_abstract_methods_full(file_path):
    """Extract all abstract methods with full information."""
    with open(file_path) as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    abstract_methods = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef):
                    # Check if it has @abstractmethod decorator
                    has_abstract = any(
                        isinstance(dec, ast.Name) and dec.id == 'abstractmethod'
                        for dec in item.decorator_list
                    )
                    
                    if has_abstract:
                        method_info = {
                            'name': item.name,
                            'params': [],
                            'return_type': 'None'
                        }
                        
                        # Get parameters with defaults
                        args_without_self = item.args.args[1:]  # Skip 'self'
                        num_args = len(args_without_self)
                        num_defaults = len(item.args.defaults)
                        
                        for i, arg in enumerate(args_without_self):
                            param_info = {'name': arg.arg}
                            
                            # Get type annotation
                            if arg.annotation:
                                param_info['type'] = ast.unparse(arg.annotation)
                            else:
                                param_info['type'] = 'Any'
                            
                            # Check for default value
                            # Defaults apply to the last N parameters
                            default_offset = num_args - num_defaults
                            if i >= default_offset:
                                default_index = i - default_offset
                                param_info['default'] = ast.unparse(item.args.defaults[default_index])
                            
                            method_info['params'].append(param_info)
                        
                        # Get return type
                        if item.returns:
                            method_info['return_type'] = ast.unparse(item.returns)
                        
                        abstract_methods[item.name] = method_info
    
    return abstract_methods

def generate_stub_method(method_info):
    """Generate a stub method implementation."""
    method_name = method_info['name']
    
    # Build parameter list
    params = ['self']
    for param in method_info['params']:
        param_str = f"{param['name']}: {param['type']}"
        if 'default' in param:
            param_str += f" = {param['default']}"
        params.append(param_str)
    
    # Determine return value based on return type
    return_type = method_info['return_type']
    return_value = get_stub_return_value(return_type)
    
    # Generate docstring
    docstring = f'"""Stub implementation of {method_name}."""'
    
    # Build method
    lines = []
    lines.append(f"    async def {method_name}(")
    
    # Format parameters nicely
    if len(params) <= 2:
        lines[-1] += ", ".join(params) + f") -> {return_type}:"
    else:
        lines[-1] += "self,"
        for i, param in enumerate(params[1:]):
            if i < len(params) - 2:
                lines.append(f"        {param},")
            else:
                lines.append(f"        {param}")
        lines.append(f"    ) -> {return_type}:")
    
    lines.append(f"        {docstring}")
    lines.append(f"        return {return_value}")
    
    return "\n".join(lines)

def get_stub_return_value(return_type):
    """Get appropriate stub return value for a return type."""
    # Clean up the type
    clean_type = return_type.replace(" ", "")
    
    # Handle None and optional types
    if clean_type == 'None':
        return 'None'
    if '|None' in clean_type or 'Optional[' in clean_type:
        # Return None for optional types
        return 'None'
    
    # Handle basic types
    if clean_type == 'bool':
        return 'True'
    if clean_type == 'int':
        return '0'
    if clean_type == 'float':
        return '0.0'
    if clean_type == 'str':
        return '""'
    
    # Handle Any
    if clean_type == 'Any':
        return 'None'
    
    # Handle collections
    if 'list[' in clean_type or 'List[' in clean_type:
        return '[]'
    if 'dict[' in clean_type or 'Dict[' in clean_type:
        return '{}'
    if 'tuple[' in clean_type or 'Tuple[' in clean_type:
        # Count the number of elements in tuple
        if ',' in clean_type:
            # Multiple element tuple
            inner = clean_type[clean_type.find('[')+1:clean_type.rfind(']')]
            elements = inner.split(',')
            if elements[-1].strip() == 'int':
                # Special case for (list, int) return type
                return '([], 0)'
            return '()'
        return '()'
    
    # Default for complex types - return as dict
    return '{}'

def main():
    # Extract abstract methods
    base_file = Path("/home/jose/src/Archon/python/src/server/repositories/database_repository.py")
    abstract_methods = extract_abstract_methods_full(base_file)
    
    print("# Generated SQLite Repository Stub Methods\n")
    print("# Add these to SQLiteRepositoryStubsMixin class in sqlite_repository_stubs.py\n")
    print("from typing import Any, Dict, List, Optional\n")
    
    # Group by category for better organization
    categories = {
        'page_': 'Page operations',
        'document': 'Document operations',
        'code_example': 'Code example operations',
        'setting': 'Settings operations',
        'project': 'Project operations',
        'task': 'Task operations',
        'source': 'Source operations',
        'crawled': 'Crawled page operations',
        'migration': 'Migration operations',
        'link': 'Project-source linking',
        'execute_rpc': 'RPC operations',
        'get_all_prompts': 'Prompt operations',
        'get_table_count': 'Utility operations'
    }
    
    # Sort methods by category
    categorized_methods = {}
    for method_name, method_info in sorted(abstract_methods.items()):
        category_found = False
        for prefix, cat_name in categories.items():
            if prefix in method_name:
                if cat_name not in categorized_methods:
                    categorized_methods[cat_name] = []
                categorized_methods[cat_name].append(method_info)
                category_found = True
                break
        
        if not category_found:
            if 'Other' not in categorized_methods:
                categorized_methods['Other'] = []
            categorized_methods['Other'].append(method_info)
    
    # Generate methods by category
    for category, methods in categorized_methods.items():
        print(f"\n    # {category}")
        for method_info in methods:
            print(generate_stub_method(method_info))
            print()

if __name__ == "__main__":
    main()
