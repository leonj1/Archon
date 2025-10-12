#!/usr/bin/env python3
"""Generate documentation for all 71 SQLite methods that need implementation."""

import ast
import sys
sys.path.insert(0, 'python/src')

def generate_methods_documentation():
    with open('python/src/server/repositories/database_repository.py') as f:
        content = f.read()
        tree = ast.parse(content)
    
    # Extract all abstract methods with docstrings and signatures
    methods_by_category = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'DatabaseRepository':
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef):
                    # Check for abstractmethod decorator
                    if any(isinstance(dec, ast.Name) and dec.id == 'abstractmethod' 
                           for dec in item.decorator_list):
                        # Get method info
                        method_name = item.name
                        
                        # Get docstring
                        docstring = ast.get_docstring(item) or 'No documentation'
                        
                        # Get parameters
                        params = []
                        defaults = item.args.defaults
                        args_without_self = item.args.args[1:]
                        num_defaults = len(defaults)
                        
                        for i, arg in enumerate(args_without_self):
                            param_str = arg.arg
                            if arg.annotation:
                                param_str += ': ' + ast.unparse(arg.annotation)
                            
                            # Check for default
                            default_idx = i - (len(args_without_self) - num_defaults)
                            if default_idx >= 0:
                                param_str += ' = ' + ast.unparse(defaults[default_idx])
                                
                            params.append(param_str)
                        
                        # Get return type
                        return_type = ast.unparse(item.returns) if item.returns else 'None'
                        
                        # Categorize method
                        if 'page_metadata' in method_name:
                            category = '1. Page Metadata Operations'
                        elif method_name.startswith('search_documents'):
                            category = '2. Document Search Operations'
                        elif 'document' in method_name and 'version' in method_name:
                            category = '9. Document Version Operations'
                        elif 'document' in method_name:
                            category = '3. Document Operations'
                        elif 'code_example' in method_name:
                            category = '4. Code Example Operations'
                        elif 'setting' in method_name:
                            category = '5. Settings Operations'
                        elif 'project' in method_name or method_name == 'unpin_all_projects_except':
                            category = '6. Project Operations'
                        elif 'task' in method_name:
                            category = '7. Task Operations'
                        elif 'source' in method_name or 'link_project_source' in method_name or 'unlink_project_source' in method_name:
                            category = '8. Source Operations'
                        elif 'crawled' in method_name:
                            category = '10. Crawled Page Operations'
                        elif 'migration' in method_name or method_name == 'get_applied_migrations':
                            category = '11. Migration Operations'
                        elif method_name == 'execute_rpc':
                            category = '12. RPC Operations'
                        elif method_name == 'get_all_prompts':
                            category = '13. Prompt Operations'
                        elif method_name == 'get_table_count':
                            category = '14. Utility Operations'
                        elif method_name == 'get_first_url_by_sources':
                            category = '10. Crawled Page Operations'
                        else:
                            category = '15. Other Operations'
                        
                        if category not in methods_by_category:
                            methods_by_category[category] = []
                        
                        methods_by_category[category].append({
                            'name': method_name,
                            'params': params,
                            'return_type': return_type,
                            'docstring': docstring.split('\n')[0] if docstring else 'No description'
                        })
    
    # Generate markdown documentation
    print('# SQLite Implementation - All 71 Methods Documentation')
    print()
    print('This document lists all 71 abstract methods from the DatabaseRepository interface that need SQLite query implementations.')
    print()
    print('## Current Status')
    print('- ✅ All methods have stub implementations that return appropriate empty/default values')
    print('- ❌ No actual SQLite queries implemented yet')
    print('- 📋 Methods are organized by functional category')
    print()
    print('## Implementation Checklist')
    print()
    
    # Sort categories for consistent output
    sorted_categories = sorted(methods_by_category.keys())
    
    total_methods = 0
    for category in sorted_categories:
        methods = sorted(methods_by_category[category], key=lambda x: x['name'])
        total_methods += len(methods)
        
        # Clean category name for display
        display_category = category.split('. ', 1)[1] if '. ' in category else category
        print(f'### {category} ({len(methods)} methods)')
        print()
        
        for method in methods:
            print(f"- [ ] `{method['name']}()` - {method['docstring'][:80]}")
        print()
    
    print(f'## Detailed Method Specifications')
    print()
    
    for category in sorted_categories:
        methods = sorted(methods_by_category[category], key=lambda x: x['name'])
        display_category = category.split('. ', 1)[1] if '. ' in category else category
        
        print(f'## {category}')
        print()
        
        for i, method in enumerate(methods, 1):
            print(f"### `{method['name']}()`")
            print()
            print('```python')
            params_str = ', '.join(method['params']) if method['params'] else ''
            if len(params_str) > 70:
                # Format multiline for long signatures
                params_formatted = '\n    ' + ',\n    '.join(method['params'])
                print(f"async def {method['name']}({params_formatted}\n) -> {method['return_type']}")
            else:
                print(f"async def {method['name']}({params_str}) -> {method['return_type']}")
            print('```')
            print()
            print(f"**Purpose:** {method['docstring']}")
            print()
            print('**SQLite Implementation Needed:**')
            print('- [ ] Write SQL query')
            print('- [ ] Handle transactions if needed')
            print('- [ ] Add proper error handling')
            print('- [ ] Test with sample data')
            print()
    
    print(f'## Summary Statistics')
    print()
    print(f'| Metric | Count |')
    print(f'|--------|-------|')
    print(f'| Total Methods | {total_methods} |')
    print(f'| Categories | {len(methods_by_category)} |')
    print(f'| Implemented | 0 |')
    print(f'| Remaining | {total_methods} |')
    print()
    print('## Implementation Priority')
    print()
    print('### 🔴 High Priority (Core Functionality)')
    print('1. **Settings Operations** - Required for configuration persistence')
    print('2. **Source Operations** - Required for knowledge base management')
    print('3. **Document Operations** - Required for content storage and retrieval')
    print('4. **Document Search Operations** - Required for RAG functionality')
    print()
    print('### 🟡 Medium Priority (Features)')
    print('5. **Project Operations** - For project management features')
    print('6. **Task Operations** - For task tracking functionality')
    print('7. **Page Metadata Operations** - For documentation storage')
    print('8. **Code Example Operations** - For code snippet management')
    print()
    print('### 🟢 Low Priority (Advanced/Optional)')
    print('9. **Document Version Operations** - For version control features')
    print('10. **Crawled Page Operations** - For web crawling functionality')
    print('11. **Migration Operations** - Already handled by Flyway')
    print('12. **RPC Operations** - For stored procedures (may not be needed)')
    print('13. **Prompt Operations** - For prompt management')
    print('14. **Utility Operations** - Helper functions')
    print()
    print('## Next Steps')
    print()
    print('1. Start with high-priority methods')
    print('2. Implement actual SQLite queries using aiosqlite')
    print('3. Add proper error handling and logging')
    print('4. Write unit tests for each implemented method')
    print('5. Update this document as methods are completed')

if __name__ == '__main__':
    generate_methods_documentation()
