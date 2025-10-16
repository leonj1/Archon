#!/usr/bin/env python3
"""
PostToolUse hook: Validate function arguments and return types use Pydantic models

Ensures strong typing with Pydantic:
- Function parameters use Pydantic models (not primitive types or dicts)
- Return types are Pydantic models (not dicts or Any)
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
STATE_DIR = Path.home() / ".claude" / "hook_state" / "pydantic_types"
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Allowed primitive types (for simple cases)
ALLOWED_PRIMITIVES = {'str', 'int', 'float', 'bool', 'None'}

# Allowed standard library types
ALLOWED_STD_TYPES = {'list', 'dict', 'List', 'Dict', 'Optional', 'Union', 'tuple', 'Tuple', 'set', 'Set'}


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


def get_type_str(node) -> str:
    """Extract type annotation as string"""
    if node is None:
        return "None"
    return ast.unparse(node)


def is_pydantic_model(type_str: str) -> bool:
    """Check if type annotation is a Pydantic model"""
    # Common patterns for Pydantic models:
    # - BaseModel subclasses (capitalized)
    # - Not primitive types
    # - Not standard library types

    # Remove Optional/List wrappers to get core type
    core_type = re.sub(r'^(Optional|List|Dict|Union)\[(.+)\]$', r'\2', type_str)
    core_type = core_type.strip()

    # If it's a primitive or standard type, not Pydantic
    if core_type in ALLOWED_PRIMITIVES or core_type in ALLOWED_STD_TYPES:
        return False

    # If it contains 'dict' or 'Dict', not strongly typed
    if 'dict' in core_type.lower():
        return False

    # Check if it looks like a class name (starts with uppercase)
    if core_type and core_type[0].isupper():
        # Likely a Pydantic model or dataclass
        return True

    return False


def should_check_parameter(param_name: str, type_str: str) -> bool:
    """Determine if parameter should require Pydantic model"""
    # Skip 'self' and simple ID/string parameters
    if param_name in ['self', 'cls']:
        return False

    # Simple identifiers (IDs, names) can be primitives
    if param_name.endswith('_id') or param_name == 'id':
        return False

    # If it's a dict, definitely should be Pydantic
    if 'dict' in type_str.lower():
        return True

    # Complex data structures should use Pydantic
    if type_str and type_str not in ALLOWED_PRIMITIVES:
        # If it's not a primitive but also not Pydantic, flag it
        return not is_pydantic_model(type_str)

    return False


def analyze_function_types(tree: ast.AST) -> tuple[bool, list[dict]]:
    """
    Analyze functions for proper Pydantic type usage
    Returns: (all_valid, list of violations)
    """
    violations = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        # Skip private methods and __init__
        if node.name.startswith('_'):
            continue

        # Skip test functions
        if node.name.startswith('test_'):
            continue

        # Check return type
        if node.returns:
            return_type = get_type_str(node.returns)

            # Skip if returns None/bool (common for validators)
            if return_type not in ['None', 'bool', 'int', 'str']:
                if 'dict' in return_type.lower() or not is_pydantic_model(return_type):
                    violations.append({
                        'function': node.name,
                        'issue': 'return_type',
                        'current_type': return_type,
                        'line': node.lineno,
                        'message': f"Return type '{return_type}' should be a Pydantic model"
                    })

        # Check parameters (skip self/cls)
        for arg in node.args.args:
            if arg.arg in ['self', 'cls']:
                continue

            type_str = get_type_str(arg.annotation)

            # Check if parameter uses dict or untyped
            if 'dict' in type_str.lower() and type_str != 'None':
                violations.append({
                    'function': node.name,
                    'issue': 'parameter_type',
                    'parameter': arg.arg,
                    'current_type': type_str,
                    'line': node.lineno,
                    'message': f"Parameter '{arg.arg}: {type_str}' should use Pydantic model instead of dict"
                })

            # Check for missing type annotation on complex parameters
            elif type_str == 'None' and not arg.arg.endswith('_id'):
                # Skip if it's a simple name/ID parameter
                if arg.arg not in ['id', 'name', 'key', 'value']:
                    violations.append({
                        'function': node.name,
                        'issue': 'missing_type',
                        'parameter': arg.arg,
                        'current_type': 'None',
                        'line': node.lineno,
                        'message': f"Parameter '{arg.arg}' missing type annotation (use Pydantic model)"
                    })

    return len(violations) == 0, violations


def format_violation_message(violations: list[dict], file_path: str, retry_count: int) -> str:
    """Format detailed feedback for the agent"""
    msg = f"PYDANTIC TYPE VALIDATION FAILED ({retry_count}/{MAX_RETRIES})\n\n"
    msg += f"File: {file_path}\n\n"

    # Group by issue type
    return_types = [v for v in violations if v['issue'] == 'return_type']
    param_types = [v for v in violations if v['issue'] == 'parameter_type']
    missing_types = [v for v in violations if v['issue'] == 'missing_type']

    if return_types:
        msg += f"❌ Return types should be Pydantic models:\n\n"
        for v in return_types:
            msg += f"  • {v['function']}() -> {v['current_type']} (line {v['line']})\n"
            msg += f"    {v['message']}\n"
        msg += f"\n"

    if param_types:
        msg += f"❌ Parameters should use Pydantic models (not dict):\n\n"
        for v in param_types:
            msg += f"  • {v['function']}({v['parameter']}: {v['current_type']}) (line {v['line']})\n"
            msg += f"    {v['message']}\n"
        msg += f"\n"

    if missing_types:
        msg += f"❌ Missing type annotations:\n\n"
        for v in missing_types:
            msg += f"  • {v['function']}({v['parameter']}) (line {v['line']})\n"
            msg += f"    {v['message']}\n"
        msg += f"\n"

    msg += f"📋 PYDANTIC STRONG TYPING PATTERN:\n\n"
    msg += f"✅ CORRECT - Pydantic models:\n"
    msg += f"```python\n"
    msg += f"from pydantic import BaseModel\n\n"
    msg += f"class DocumentRequest(BaseModel):\n"
    msg += f"    content: str\n"
    msg += f"    metadata: dict[str, str]\n"
    msg += f"    tags: list[str]\n\n"
    msg += f"class DocumentResponse(BaseModel):\n"
    msg += f"    doc_id: str\n"
    msg += f"    status: str\n"
    msg += f"    created_at: datetime\n\n"
    msg += f"def process_document(self, \n"
    msg += f"                     request: DocumentRequest) -> DocumentResponse:\n"
    msg += f"    # Strongly typed input and output\n"
    msg += f"    return DocumentResponse(\n"
    msg += f"        doc_id=generate_id(),\n"
    msg += f"        status='processed',\n"
    msg += f"        created_at=datetime.now()\n"
    msg += f"    )\n"
    msg += f"```\n\n"

    msg += f"❌ WRONG - Using dict:\n"
    msg += f"```python\n"
    msg += f"def process_document(self, data: dict) -> dict:\n"
    msg += f"    # BAD: No type safety, hard to validate\n"
    msg += f"    return {{'doc_id': '123', 'status': 'done'}}\n"
    msg += f"```\n\n"

    msg += f"💡 BENEFITS:\n"
    msg += f"  • Runtime validation\n"
    msg += f"  • IDE autocomplete\n"
    msg += f"  • Clear API contracts\n"
    msg += f"  • Automatic JSON serialization\n\n"

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

    # Only check Python service files
    if not file_path.endswith('.py'):
        print(json.dumps({"decision": "allow"}))
        return

    # Skip test files, protocol files, and __init__.py
    if any(x in file_path for x in ['test_', '_test.py', 'protocol', 'interface', '__init__.py']):
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
            "reason": f"⚠️ CIRCUIT BREAKER: Pydantic type validation bypassed\n"
                     f"Reason: {bypass_reason}\n"
                     f"File: {file_path}"
        }
        print(json.dumps(output), file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Validate Pydantic types
    is_valid, violations = analyze_function_types(tree)

    if not is_valid:
        breaker.record_attempt()
        retry_count = breaker.get_retry_count()

        output = {
            "decision": "block",
            "reason": format_violation_message(violations, file_path, retry_count),
            "additionalContext": "Use Pydantic BaseModel for parameters and return types (strong typing)"
        }
        print(json.dumps(output))
        sys.exit(2)  # Blocking error

    # Validation passed
    breaker.reset()
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
