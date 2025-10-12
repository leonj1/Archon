#!/usr/bin/env python3
"""Extract and compare abstract method signatures with stub implementations."""

import ast
import re
from pathlib import Path

def extract_abstract_methods(file_path):
    """Extract all abstract methods from a file."""
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
                        # Extract method signature
                        method_name = item.name
                        
                        # Get parameters
                        params = []
                        for arg in item.args.args[1:]:  # Skip 'self'
                            param_name = arg.arg
                            # Try to get type annotation
                            if arg.annotation:
                                params.append(f"{param_name}: {ast.unparse(arg.annotation)}")
                            else:
                                params.append(param_name)
                        
                        # Get return type
                        return_type = "None"
                        if item.returns:
                            return_type = ast.unparse(item.returns)
                        
                        signature = f"async def {method_name}({', '.join(params)}) -> {return_type}"
                        abstract_methods[method_name] = signature
    
    return abstract_methods

def extract_stub_methods(file_path):
    """Extract all methods from stub implementation."""
    with open(file_path) as f:
        content = f.read()
    
    tree = ast.parse(content)
    
    stub_methods = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef):
                    method_name = item.name
                    
                    # Get parameters
                    params = []
                    for arg in item.args.args[1:]:  # Skip 'self'
                        param_name = arg.arg
                        # Try to get type annotation
                        if arg.annotation:
                            params.append(f"{param_name}: {ast.unparse(arg.annotation)}")
                        else:
                            params.append(param_name)
                    
                    # Get return type
                    return_type = "None"
                    if item.returns:
                        return_type = ast.unparse(item.returns)
                    
                    signature = f"async def {method_name}({', '.join(params)}) -> {return_type}"
                    stub_methods[method_name] = signature
    
    return stub_methods

def main():
    # Extract abstract methods
    base_file = Path("/home/jose/src/Archon/python/src/server/repositories/database_repository.py")
    abstract_methods = extract_abstract_methods(base_file)
    
    # Extract stub methods
    stub_file = Path("/home/jose/src/Archon/python/src/server/repositories/sqlite_repository_stubs.py")
    stub_methods = extract_stub_methods(stub_file)
    
    print("## SIGNATURE COMPARISON REPORT\n")
    print(f"Total abstract methods: {len(abstract_methods)}")
    print(f"Total stub methods: {len(stub_methods)}\n")
    
    # Find missing methods
    missing_in_stubs = set(abstract_methods.keys()) - set(stub_methods.keys())
    if missing_in_stubs:
        print("### ❌ MISSING IN STUBS (need to add):")
        for method in sorted(missing_in_stubs):
            print(f"  - {method}")
            print(f"    Expected: {abstract_methods[method]}")
        print()
    
    # Find mismatched signatures
    print("### ⚠️ SIGNATURE MISMATCHES (need to fix):\n")
    mismatch_count = 0
    for method_name in sorted(abstract_methods.keys()):
        if method_name in stub_methods:
            abstract_sig = abstract_methods[method_name]
            stub_sig = stub_methods[method_name]
            
            # Normalize for comparison (handle Optional, Union variations)
            abstract_norm = abstract_sig.replace("dict[", "Dict[").replace("list[", "List[")
            stub_norm = stub_sig.replace("dict[", "Dict[").replace("list[", "List[")
            
            if abstract_norm != stub_norm:
                mismatch_count += 1
                print(f"#### {method_name}:")
                print(f"  Abstract: {abstract_sig}")
                print(f"  Stub:     {stub_sig}")
                print()
    
    if mismatch_count == 0:
        print("  ✅ All signatures match!\n")
    else:
        print(f"Total mismatches: {mismatch_count}\n")
    
    # Find extra methods in stubs
    extra_in_stubs = set(stub_methods.keys()) - set(abstract_methods.keys())
    if extra_in_stubs:
        print("### ℹ️ EXTRA IN STUBS (can remove if not needed):")
        for method in sorted(extra_in_stubs):
            print(f"  - {method}")
        print()

if __name__ == "__main__":
    main()
