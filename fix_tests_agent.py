#!/usr/bin/env python3
"""
Multi-agent test fixer using Claude Agent SDK.

Agent1: Identifies failing tests by running 'make test'
Agent2: Fixes individual failing tests

The script iterates until all tests pass.
"""

import asyncio
import re
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
import os

load_dotenv()

console = Console()


@dataclass
class FailingTest:
    """Represents a failing test."""
    file_path: str
    test_name: str
    error_message: str
    full_output: str


class TestFixerOrchestrator:
    """Orchestrates the test fixing process using multiple agents."""

    def __init__(self):
        self.max_iterations = 10
        self.fixed_tests: List[str] = []

    def run_tests(self) -> str:
        """Run make test and capture output."""
        try:
            result = subprocess.run(
                ['make', 'test'],
                cwd='/home/jose/src/Archon',
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "Test execution timed out"
        except Exception as e:
            return f"Error running tests: {str(e)}"

    def parse_test_failures(self, test_output: str) -> List[FailingTest]:
        """Parse test output to extract failing tests from both pytest and Vitest."""
        failures = []
        lines = test_output.split('\n')

        # Parse pytest failures (FAILED/ERROR format)
        pytest_pattern = r'^(FAILED|ERROR)\s+([\w/_.]+\.py)::([\w:]+)\s*-\s*(.+)$'
        for line in lines:
            match = re.match(pytest_pattern, line)
            if match:
                status, file_path, test_path, error_msg = match.groups()

                # Extract just the test name (last part after ::)
                test_name = test_path.split('::')[-1]

                failures.append(FailingTest(
                    file_path=file_path,
                    test_name=test_name,
                    error_message=error_msg,
                    full_output=line
                ))

        # Parse Vitest failures (FAIL .test.ts format)
        current_fail = None
        error_buffer = []
        capturing_error = False

        for i, line in enumerate(lines):
            # Detect FAIL lines for frontend tests
            if ' FAIL ' in line and '.test.ts' in line:
                # Save previous failure if exists
                if current_fail and error_buffer:
                    current_fail.error_message = '\n'.join(error_buffer[:15])
                    failures.append(current_fail)
                    error_buffer = []

                # Parse new failure
                parts = line.split('>')
                if len(parts) >= 2:
                    file_path = parts[0].replace('FAIL', '').strip()
                    test_name = '>'.join(parts[1:]).strip()

                    current_fail = FailingTest(
                        file_path=file_path,
                        test_name=test_name,
                        error_message="",
                        full_output=line
                    )
                    capturing_error = True

            elif capturing_error and current_fail:
                # Capture error details
                if line.strip():
                    error_buffer.append(line)

                # Stop capturing after file location line
                if '❯' in line or (len(error_buffer) > 20):
                    capturing_error = False

        # Add last Vitest failure
        if current_fail and error_buffer:
            current_fail.error_message = '\n'.join(error_buffer[:15])
            failures.append(current_fail)

        return failures

    def identify_failures(self) -> List[FailingTest]:
        """Run tests and identify failures directly (no agent needed)."""
        console.print(Panel.fit(
            "[bold cyan]Step 1: Test Identification[/bold cyan]\n"
            "Running 'make test' to identify failing tests...",
            border_style="cyan"
        ))

        # Run tests directly
        output = self.run_tests()

        # Parse failures
        failures = self.parse_test_failures(output)

        return failures

    async def agent_fix_test(self, test: FailingTest, iteration: int) -> bool:
        """Agent: Fix a specific failing test."""
        console.print(Panel.fit(
            f"[bold green]Agent: Test Fixer (Iteration {iteration})[/bold green]\n"
            f"Fixing: {test.file_path}\n"
            f"Test: {test.test_name}",
            border_style="green"
        ))

        # Determine if it's a frontend or backend test
        is_frontend = test.file_path.startswith('src/') or test.file_path.startswith('archon-ui-main/')
        is_integration = test.file_path.startswith('tests/integration')

        # Build test command
        if is_frontend or is_integration:
            test_cmd = f"cd archon-ui-main && npm run test -- {test.file_path}"
        else:
            test_cmd = f"cd python && uv run pytest {test.file_path} -v"

        options = ClaudeAgentOptions(
            model="sonnet",
            permission_mode="acceptEdits",
            allowed_tools=[
                'Read',
                'Write',
                'Edit',
                'Grep',
                'Glob',
                'Bash',
            ],
        )

        success = False

        async with ClaudeSDKClient(options=options) as client:
            prompt = f"""Fix this specific failing test:

TEST INFORMATION:
File: {test.file_path}
Test Name: {test.test_name}

ERROR OUTPUT:
{test.error_message}

CRITICAL CONSTRAINTS:
1. NEVER use Supabase directly in fixes
2. If error is database-related, ONLY use the database repository interface
3. Make minimal, targeted changes to fix this specific test
4. DO NOT introduce new features or refactor unrelated code

WORKFLOW:
1. Read the test file: {test.file_path}
2. Understand what the test expects
3. Read the implementation file(s) being tested
4. Identify the mismatch between test expectations and implementation
5. Fix either the test or the implementation (use judgment):
   - If the test expects wrong behavior: Fix the test
   - If the implementation is broken: Fix the implementation
   - If it's a styling/className issue: Update test expectations to match actual classes
6. After making changes, validate with: {test_cmd}
7. Review the output - if the test passes, you're done

IMPORTANT:
- For className/styling tests: Match the actual rendered classes, not idealized ones
- For API tests: Ensure headers and responses match actual implementation
- For integration tests: Check for missing files or incorrect imports first

Start by reading the test file to understand what it's checking."""

            await client.query(prompt)

            output_lines = []
            test_passed = False

            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            output_lines.append(block.text)
                            # Look for success indicators
                            text_lower = block.text.lower()
                            if any(phrase in text_lower for phrase in [
                                'test passed',
                                'tests passed',
                                '1 passed',
                                'all tests passed',
                                'test fixed successfully'
                            ]):
                                test_passed = True

            # Check if agent indicated success
            success = test_passed

            # Print summary
            if output_lines:
                # Show last few lines
                summary = '\n'.join(output_lines[-3:])
                console.print(f"[dim]Agent output: {summary[:200]}...[/dim]")

        return success

    async def run(self):
        """Main orchestration loop."""
        console.print(Panel.fit(
            "[bold magenta]Automated Test Fixer[/bold magenta]\n"
            "Uses Claude agents to systematically fix failing tests\n"
            "Iterates until all tests pass or max iterations reached",
            border_style="magenta"
        ))

        iteration = 0
        initial_failure_count = 0

        while iteration < self.max_iterations:
            iteration += 1
            console.print(f"\n[bold yellow]{'='*70}[/bold yellow]")
            console.print(f"[bold yellow]Iteration {iteration}/{self.max_iterations}[/bold yellow]")
            console.print(f"[bold yellow]{'='*70}[/bold yellow]\n")

            # Identify failures directly (no agent needed for this)
            failures = self.identify_failures()

            if iteration == 1:
                initial_failure_count = len(failures)

            if not failures:
                console.print(Panel.fit(
                    f"[bold green]✓ All tests passing![/bold green]\n"
                    f"Fixed {initial_failure_count} test(s) in {iteration} iteration(s)",
                    border_style="green"
                ))
                break

            console.print(f"\n[bold red]Found {len(failures)} failing test(s)[/bold red]\n")

            # Create a table to display failures
            table = Table(title="Failing Tests", show_header=True, header_style="bold magenta")
            table.add_column("#", style="dim", width=4)
            table.add_column("File", style="cyan")
            table.add_column("Test", style="yellow")
            table.add_column("Error", style="red")

            for i, failure in enumerate(failures, 1):
                error_preview = failure.error_message[:80].replace('\n', ' ')
                table.add_row(
                    str(i),
                    failure.file_path,
                    failure.test_name[:50],
                    error_preview
                )

            console.print(table)
            console.print()

            # Fix each test with an agent
            fixes_attempted = 0
            fixes_successful = 0

            # Track currently failing tests (will be updated after each successful fix)
            current_failures_set = {f"{f.file_path}::{f.test_name}" for f in failures}

            for failure in failures:
                test_key = f"{failure.file_path}::{failure.test_name}"

                # Don't retry the same test in the same iteration
                if test_key in self.fixed_tests:
                    console.print(f"[dim]Skipping (already attempted): {test_key}[/dim]\n")
                    continue

                # Check if this test is still failing (may have been fixed as side effect)
                if test_key not in current_failures_set:
                    console.print(f"[blue]✓ Already fixed as side effect: {test_key}[/blue]\n")
                    continue

                fixes_attempted += 1
                success = await self.agent_fix_test(failure, iteration)
                self.fixed_tests.append(test_key)

                if success:
                    fixes_successful += 1
                    console.print(f"[green]✓ Successfully fixed: {test_key}[/green]\n")

                    # Re-run tests to get updated failure list
                    console.print("[cyan]Re-running tests to check for side-effect fixes...[/cyan]")
                    updated_failures = self.identify_failures()
                    current_failures_set = {f"{f.file_path}::{f.test_name}" for f in updated_failures}

                    side_effect_fixes = len(failures) - len(updated_failures) - fixes_successful
                    if side_effect_fixes > 0:
                        console.print(f"[blue]✓ {side_effect_fixes} additional test(s) fixed as side effect![/blue]\n")
                else:
                    console.print(f"[yellow]⚠ Fix attempted: {test_key}[/yellow]\n")

                # Pause between fixes
                await asyncio.sleep(1)

            # Summary for this iteration
            console.print(Panel.fit(
                f"Iteration {iteration} Summary:\n"
                f"Tests attempted: {fixes_attempted}\n"
                f"Fixes successful: {fixes_successful}\n"
                f"Remaining failures: {len(current_failures_set)}",
                border_style="blue"
            ))

            # If no fixes were attempted, break to avoid infinite loop
            if fixes_attempted == 0:
                console.print("[yellow]No new tests to fix. Exiting.[/yellow]")
                break

        if iteration >= self.max_iterations:
            console.print(Panel.fit(
                "[bold red]Maximum iterations reached[/bold red]\n"
                f"Started with: {initial_failure_count} failures\n"
                f"Remaining: {len(current_failures_set)} failures",
                border_style="red"
            ))

        # Final test run to confirm
        console.print("\n[bold cyan]Running final test verification...[/bold cyan]")
        final_output = self.run_tests()
        final_failures = self.parse_test_failures(final_output)

        if not final_failures:
            console.print(Panel.fit(
                "[bold green]🎉 SUCCESS! All tests are now passing![/bold green]",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                f"[bold yellow]⚠ {len(final_failures)} test(s) still failing[/bold yellow]\n"
                "Manual intervention may be required",
                border_style="yellow"
            ))


async def main():
    """Entry point."""
    orchestrator = TestFixerOrchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
