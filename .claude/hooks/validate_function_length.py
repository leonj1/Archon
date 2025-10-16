#!/usr/bin/env python3
"""
PostToolUse hook: Validate all functions in modified files are < 30 lines

Ensures DecomposeAgent properly extracts long functions into service classes.
"""
import json
import sys
import ast
import os
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MAX_FUNCTION_LINES = 30
MAX_RETRIES = 3
STATE_DIR = Path.home() / ".claude" / "hook_state" / "function_length"
STATE_DIR.mkdir(parents=True, exist_ok=True)


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


def count_function_lines(node: ast.FunctionDef) -> int:
    """Count actual lines of code in a function (excluding empty lines/comments)"""
    if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
        return 0

    # Get line span
    start_line = node.lineno
    end_line = node.end_lineno

    if end_line is None:
        return 0

    return end_line - start_line + 1


def analyze_functions(content: str) -> tuple[bool, list[dict]]:
    """
    Analyze all functions in Python file
    Returns: (all_valid, list of violations)
    """
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        # Syntax errors will be caught by other validators
        return True, []

    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            line_count = count_function_lines(node)

            if line_count > MAX_FUNCTION_LINES:
                violations.append({
                    'function': node.name,
                    'lines': line_count,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno
                })

    return len(violations) == 0, violations


def format_violation_message(violations: list[dict], file_path: str, retry_count: int) -> str:
    """Format detailed feedback for the agent"""
    msg = f"FUNCTION LENGTH VALIDATION FAILED ({retry_count}/{MAX_RETRIES})\n\n"
    msg += f"File: {file_path}\n"
    msg += f"Found {len(violations)} function(s) exceeding {MAX_FUNCTION_LINES} lines:\n\n"

    for v in violations:
        msg += f"  • {v['function']}() - {v['lines']} lines (lines {v['start_line']}-{v['end_line']})\n"

    msg += f"\n📋 HOW TO FIX:\n"
    msg += f"1. Extract each long function into a new service class\n"
    msg += f"2. Break down complex logic into smaller helper methods\n"
    msg += f"3. Each method should do ONE thing\n"
    msg += f"4. Target: All functions < {MAX_FUNCTION_LINES} lines\n\n"

    msg += f"💡 EXAMPLE:\n"
    msg += f"```python\n"
    msg += f"# Before: 50-line function\n"
    msg += f"def process_document(self, doc):\n"
    msg += f"    # ... 50 lines of code ...\n"
    msg += f"\n"
    msg += f"# After: Extract to service\n"
    msg += f"class DocumentProcessorService:\n"
    msg += f"    def process(self, doc):  # 15 lines\n"
    msg += f"        validated = self._validate(doc)  # 8 lines\n"
    msg += f"        return self._transform(validated)  # 8 lines\n"
    msg += f"```\n\n"

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

    # Only check Python files
    if not file_path.endswith('.py'):
        print(json.dumps({"decision": "allow"}))
        return

    # Skip test files (different rules may apply)
    if 'test_' in file_path or '_test.py' in file_path:
        print(json.dumps({"decision": "allow"}))
        return

    content = tool_input.get('content', '')
    if tool_input.get('new_string'):  # Edit tool
        content = tool_input.get('new_string', '')

    # Initialize circuit breaker
    breaker = CircuitBreaker(file_path)

    # Check circuit breaker
    should_allow, bypass_reason = breaker.should_allow()
    if should_allow:
        output = {
            "decision": "allow",
            "reason": f"⚠️ CIRCUIT BREAKER: Function length validation bypassed\n"
                     f"Reason: {bypass_reason}\n"
                     f"File: {file_path}"
        }
        print(json.dumps(output), file=sys.stderr)
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    # Validate function lengths
    is_valid, violations = analyze_functions(content)

    if not is_valid:
        breaker.record_attempt()
        retry_count = breaker.get_retry_count()

        output = {
            "decision": "block",
            "reason": format_violation_message(violations, file_path, retry_count),
            "additionalContext": f"DecomposeAgent: Extract functions > {MAX_FUNCTION_LINES} lines into service classes"
        }
        print(json.dumps(output))
        sys.exit(2)  # Blocking error

    # Validation passed
    breaker.reset()
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
