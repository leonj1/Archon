#!/usr/bin/env python3
"""
Test script for validation hooks

Tests each hook with valid and invalid code samples to ensure they work correctly.
"""
import json
import subprocess
import sys
from pathlib import Path


def test_hook(hook_path: str, test_name: str, payload: dict, expect_allow: bool):
    """Test a single hook with given payload"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Hook: {hook_path}")
    print(f"Expected: {'ALLOW' if expect_allow else 'BLOCK'}")
    print(f"{'='*60}")

    result = subprocess.run(
        ['python', hook_path],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )

    try:
        output = json.loads(result.stdout)
        decision = output.get('decision', 'unknown')

        if expect_allow:
            if decision == 'allow':
                print(f"✅ PASS: Hook allowed as expected")
                return True
            else:
                print(f"❌ FAIL: Hook blocked but should allow")
                print(f"Reason: {output.get('reason', 'No reason provided')}")
                return False
        else:
            if decision == 'block':
                print(f"✅ PASS: Hook blocked as expected")
                print(f"Reason: {output.get('reason', 'No reason provided')[:200]}...")
                return True
            else:
                print(f"❌ FAIL: Hook allowed but should block")
                return False

    except json.JSONDecodeError:
        print(f"❌ ERROR: Invalid JSON output")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return False


def main():
    print("🧪 Validation Hooks Test Suite")
    print("=" * 60)

    hooks_dir = Path('.claude/hooks')
    results = []

    # Test 1: Function Length - Valid code (short function)
    results.append(test_hook(
        str(hooks_dir / 'validate_function_length.py'),
        "Function Length - Valid (short function)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/test_service.py",
                "content": """
class TestService:
    def short_function(self):
        # Only 3 lines
        result = self.calculate()
        return result
"""
            }
        },
        expect_allow=True
    ))

    # Test 2: Function Length - Invalid code (long function)
    results.append(test_hook(
        str(hooks_dir / 'validate_function_length.py'),
        "Function Length - Invalid (50-line function)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/test_service.py",
                "content": """
class TestService:
    def very_long_function(self):
""" + "\n".join([f"        line_{i} = {i}" for i in range(50)])
            }
        },
        expect_allow=False
    ))

    # Test 3: Constructor Dependencies - Valid
    results.append(test_hook(
        str(hooks_dir / 'validate_constructor_dependencies.py'),
        "Constructor Dependencies - Valid (deps in __init__)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/document_service.py",
                "content": """
class DocumentService:
    def __init__(self, database_repo: IDatabaseRepository, http_client: IHttpClient):
        self.db = database_repo
        self.http = http_client

    def process_document(self, doc_id: str):
        # Uses self.db, not in params - CORRECT
        return self.db.get(doc_id)
"""
            }
        },
        expect_allow=True
    ))

    # Test 4: Constructor Dependencies - Invalid (repo in method param)
    results.append(test_hook(
        str(hooks_dir / 'validate_constructor_dependencies.py'),
        "Constructor Dependencies - Invalid (repo in method)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/document_service.py",
                "content": """
class DocumentService:
    def __init__(self):
        pass

    def process_document(self, doc_id: str, database_repo: IDatabaseRepository):
        # BAD: database_repo should be in __init__
        return database_repo.get(doc_id)
"""
            }
        },
        expect_allow=False
    ))

    # Test 5: Pydantic Types - Valid
    results.append(test_hook(
        str(hooks_dir / 'validate_pydantic_types.py'),
        "Pydantic Types - Valid (Pydantic models)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/document_service.py",
                "content": """
from pydantic import BaseModel

class DocumentRequest(BaseModel):
    content: str

class DocumentResponse(BaseModel):
    doc_id: str

class DocumentService:
    def process_document(self, request: DocumentRequest) -> DocumentResponse:
        return DocumentResponse(doc_id="123")
"""
            }
        },
        expect_allow=True
    ))

    # Test 6: Pydantic Types - Invalid (using dict)
    results.append(test_hook(
        str(hooks_dir / 'validate_pydantic_types.py'),
        "Pydantic Types - Invalid (dict instead of Pydantic)",
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "services/document_service.py",
                "content": """
class DocumentService:
    def process_document(self, data: dict) -> dict:
        # BAD: Using dict instead of Pydantic models
        return {'doc_id': '123'}
"""
            }
        },
        expect_allow=False
    ))

    # Print results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {percentage:.1f}%")

    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
