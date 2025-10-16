#!/usr/bin/env python3
"""
PostToolUse hook: Validate constructors have fundamental dependencies

Ensures service classes follow dependency injection pattern with:
- HTTP clients, database repositories, config in constructor
- NOT in function parameters (only changing values in functions)
"""
import json
import sys
import ast
import os
import re
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MAX_RETRIES = 3
STATE_DIR = Path.home() / ".claude" / "hook_state" / "constructor_deps"
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Fundamental dependencies (should be in __init__)
FUNDAMENTAL_DEPS = {
    'client', 'repository', 'repo', 'database', 'db', 'http',
    'service', 'config', 'settings', 'session', 'connection', 'conn'
}


class CircuitBreaker:
    """Prevent infinite validation loops"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.state_file = STATE_DIR / f"{Path(file_path).name}.state.json"

    def get_state(self) -> dict:
        if not self.state_file.exists():
            return {'attempts': [], 'retry_count': 0}
        try:
            return json.loads(self.state_file.read_text())
        except:
            return {'attempts': [], 'retry_count': 0}

    def save_state(self, state: dict):
        self.state_file.write_text(json.dumps(state, indent=2))

    def record_attempt(self):
        state = self.get_state()
        state['attempts'].append(datetime.now().isoformat())
        state['retry_count'] = state.get('retry_count', 0) + 1
        state['attempts'] = state['attempts'][-10:]
        self.save_state(state)

    def get_retry_count(self) -> int:
        state = self.get_state()
        attempts = state.get('attempts', [])
        if attempts:
            last = datetime.fromisoformat(attempts[-1])
            if datetime.now() - last > timedelta(minutes=5):
                self.reset()
                return 0
        return state.get('retry_count', 0)

    def reset(self):
        if self.state_file.exists():
            self.state_file.unlink()

    def should_allow(self) -> tuple[bool, str]:
        if os.getenv('SKIP_VALIDATION') == '1':
            return True, "User requested validation skip"

        retry_count = self.get_retry_count()
        if retry_count >= MAX_RETRIES:
            self.reset()
            return True, f"Max retries ({MAX_RETRIES}) exceeded"

        return False, ""


def is_fundamental_param(param_name: str) -> bool:
    """Check if parameter name suggests a fundamental dependency"""
    param_lower = param_name.lower()
    return any(dep in param_lower for dep in FUNDAMENTAL_DEPS)


def has_type_annotation(node: ast.arg) -> bool:
    """Check if parameter has type annotation"""
    return node.annotation is not None


def get_type_annotation_str(node: ast.arg) -> str:
    """Extract type annotation as string"""
    if not node.annotation:
        return "None"

    if isinstance(node.annotation, ast.Name):
        return node.annotation.id
    elif isinstance(node.annotation, ast.Subscript):
        # Handle List[X], Optional[X], etc.
        return ast.unparse(node.annotation)
    else:
        return ast.unparse(node.annotation)


def is_protocol_or_interface(type_str: str) -> bool:
    """Check if type annotation suggests a Protocol/Interface"""
    # Common patterns: IDatabase, DatabaseProtocol, AbstractClient, etc.
    patterns = [
        r'^I[A-Z]',  # IDatabase, IClient
        r'Protocol$',  # DatabaseProtocol
        r'Interface$',  # ClientInterface
        r'Abstract',  # AbstractClient
    ]
    return any(re.search(pattern, type_str) for pattern in patterns)


def analyze_class_dependencies(tree: ast.AST) -> tuple[bool, list[dict]]:
    """
    Analyze classes for proper dependency injection
    Returns: (all_valid, list of violations)
    """
    violations = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Skip test classes
        if node.name.startswith('Test') or node.name.endswith('Test'):
            continue

        # Find __init__ method
        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_method = item
                break

        if not init_method:
            continue

        # Get __init__ parameters (excluding 'self')
        init_params = [arg for arg in init_method.args.args if arg.arg != 'self']
        init_param_names = {arg.arg for arg in init_params}

        # Check all other methods for fundamental dependencies in parameters
        for method in node.body:
            if not isinstance(method, ast.FunctionDef):
                continue
            if method.name == '__init__':
                continue
            if method.name.startswith('_'):  # Skip private methods
                continue

            # Get method parameters (excluding 'self')
            method_params = [arg for arg in method.args.args if arg.arg != 'self']

            for param in method_params:
                param_name = param.arg

                # Check if this looks like a fundamental dependency
                if is_fundamental_param(param_name):
                    # Check if it's in __init__ instead
                    if param_name not in init_param_names:
                        type_hint = get_type_annotation_str(param)

                        violations.append({
                            'class': node.name,
                            'method': method.name,
                            'parameter': param_name,
                            'type': type_hint,
                            'issue': 'fundamental_in_method',
                            'line': method.lineno
                        })

        # Also check that __init__ HAS fundamental dependencies (for service classes)
        # Only check classes that end with 'Service' or 'Client'
        if node.name.endswith('Service') or node.name.endswith('Client'):
            has_fundamental_deps = any(
                is_fundamental_param(arg.arg) for arg in init_params
            )

            if not has_fundamental_deps and len(init_params) == 0:
                violations.append({
                    'class': node.name,
                    'method': '__init__',
                    'parameter': None,
                    'type': None,
                    'issue': 'no_dependencies',
                    'line': init_method.lineno if init_method else node.lineno
                })

    return len(violations) == 0, violations


def format_violation_message(violations: list[dict], file_path: str, retry_count: int) -> str:
    """Format detailed feedback for the agent"""
    msg = f"CONSTRUCTOR DEPENDENCY VALIDATION FAILED ({retry_count}/{MAX_RETRIES})\n\n"
    msg += f"File: {file_path}\n\n"

    # Group by issue type
    fundamental_in_method = [v for v in violations if v['issue'] == 'fundamental_in_method']
    no_dependencies = [v for v in violations if v['issue'] == 'no_dependencies']

    if fundamental_in_method:
        msg += f"❌ Fundamental dependencies found in method parameters (should be in __init__):\n\n"
        for v in fundamental_in_method:
            msg += f"  • {v['class']}.{v['method']}({v['parameter']}: {v['type']}) - line {v['line']}\n"
        msg += f"\n"

    if no_dependencies:
        msg += f"❌ Service classes missing dependencies in __init__:\n\n"
        for v in no_dependencies:
            msg += f"  • {v['class']} - line {v['line']}\n"
        msg += f"\n"

    msg += f"📋 DEPENDENCY INJECTION PATTERN:\n\n"
    msg += f"✅ CORRECT - Dependencies in constructor:\n"
    msg += f"```python\n"
    msg += f"class DocumentService:\n"
    msg += f"    def __init__(self, \n"
    msg += f"                 database_repo: IDatabaseRepository,  # Fundamental\n"
    msg += f"                 http_client: IHttpClient,           # Fundamental\n"
    msg += f"                 config: ServiceConfig):             # Fundamental\n"
    msg += f"        self.db = database_repo\n"
    msg += f"        self.http = http_client\n"
    msg += f"        self.config = config\n"
    msg += f"    \n"
    msg += f"    def process_document(self, doc_id: str, options: ProcessOptions):\n"
    msg += f"        # Uses self.db, self.http - NOT in parameters\n"
    msg += f"        # Only 'doc_id' and 'options' (changing values) in parameters\n"
    msg += f"        return self.db.get(doc_id)\n"
    msg += f"```\n\n"

    msg += f"❌ WRONG - Dependency in method parameter:\n"
    msg += f"```python\n"
    msg += f"class DocumentService:\n"
    msg += f"    def process_document(self, doc_id: str, database_repo: IDatabase):\n"
    msg += f"        # BAD: database_repo should be in __init__, not here\n"
    msg += f"        return database_repo.get(doc_id)\n"
    msg += f"```\n\n"

    msg += f"💡 RULE: Fundamental dependencies (clients, repos, config) in __init__\n"
    msg += f"        Only changing values (IDs, data, options) in method parameters\n\n"

    msg += f"To bypass: SKIP_VALIDATION=1\n"

    return msg


def main():
    payload = json.load(sys.stdin)

    tool_name = payload.get('tool_name', '')
    tool_input = payload.get('tool_input', {})

    # Only validate Write/Edit operations on Python files
    if tool_name not in ['Write', 'Edit']:
        print(json.dumps({"decision": "allow"}))
        return

    file_path = tool_input.get('file_path', '')

    # Only check Python service/client files
    if not file_path.endswith('.py'):
        print(json.dumps({"decision": "allow"}))
        return

    # Skip test files
    if 'test_' in file_path or '_test.py' in file_path:
        print(json.dumps({"decision": "allow"}))
        return

    # Skip protocol/interface files
    if 'protocol' in file_path.lower() or 'interface' in file_path.lower():
        print(json.dumps({"decision": "allow"}))
        return

    content = tool_input.get('content', '')
    if tool_input.get('new_string'):  # Edit tool
        content = tool_input.get('new_string', '')

    # Parse Python code
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # Syntax errors will be caught by other validators
        print(json.dumps({"decision": "allow"}))
        return

    # Initialize circuit breaker
    breaker = CircuitBreaker(file_path)

    # Check circuit breaker
    should_allow, bypass_reason = breaker.should_allow()
    if should_allow:
        output = {
            "decision": "allow",
            "reason": f"⚠️ CIRCUIT BREAKER: Constructor dependency validation bypassed\n"
                     f"Reason: {bypass_reason}\n"
                     f"File: {file_path}"
        }
        print(json.dumps(output), file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Validate dependencies
    is_valid, violations = analyze_class_dependencies(tree)

    if not is_valid:
        breaker.record_attempt()
        retry_count = breaker.get_retry_count()

        output = {
            "decision": "block",
            "reason": format_violation_message(violations, file_path, retry_count),
            "additionalContext": "Use dependency injection: fundamental deps in __init__, only changing values in method params"
        }
        print(json.dumps(output))
        sys.exit(2)  # Blocking error

    # Validation passed
    breaker.reset()
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
