#!/usr/bin/env python3
"""
Test Fix Orchestrator - Automated test fixing using Claude Agent SDK

This script orchestrates multiple specialized agents to automatically fix failing tests:
- Test Runner Agent: Identifies failing tests
- Test Analyzer Agent: Analyzes failure root causes
- Test Fixer Agent: Implements fixes
- Validator Agent: Validates fixes work

Features:
- State persistence (resume on interruption)
- Max 3 attempts per test
- 1-hour timeout protection
- Structured logging and progress tracking
- Rollback capability (file-based, no git)
- Summary report generation
"""

import asyncio
import json
import os
import shutil
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Literal
from enum import Enum

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from dotenv import load_dotenv

load_dotenv()


# ================================
# Configuration
# ================================

class Config:
    """Orchestrator configuration"""
    MAX_ATTEMPTS_PER_TEST = 3
    TIMEOUT_HOURS = 1
    STATE_FILE = "test_fix_state.json"
    LOG_FILE = "test_fix_log.jsonl"
    SUMMARY_FILE = "TEST_FIX_SUMMARY.md"
    BACKUP_DIR = ".test_fix_backups"
    TEST_COMMAND = "make test"
    MODEL = "sonnet"


# ================================
# Data Models
# ================================

class TestStatus(str, Enum):
    """Test status enumeration"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    FIXING = "fixing"
    VALIDATING = "validating"
    FIXED = "fixed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestAttempt:
    """Single attempt to fix a test"""
    attempt_number: int
    timestamp: str
    analysis: str
    changes_made: List[str]
    validation_result: bool
    error_message: Optional[str] = None


@dataclass
class TestRecord:
    """Record of a test's fix progress"""
    test_path: str
    status: TestStatus
    attempts: List[TestAttempt]
    current_attempt: int = 0
    error_output: str = ""
    fixed_at: Optional[str] = None
    skipped_reason: Optional[str] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "test_path": self.test_path,
            "status": self.status.value,
            "attempts": [asdict(a) for a in self.attempts],
            "current_attempt": self.current_attempt,
            "error_output": self.error_output,
            "fixed_at": self.fixed_at,
            "skipped_reason": self.skipped_reason,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        attempts = [TestAttempt(**a) for a in data.get("attempts", [])]
        return cls(
            test_path=data["test_path"],
            status=TestStatus(data["status"]),
            attempts=attempts,
            current_attempt=data.get("current_attempt", 0),
            error_output=data.get("error_output", ""),
            fixed_at=data.get("fixed_at"),
            skipped_reason=data.get("skipped_reason"),
        )


@dataclass
class OrchestratorState:
    """Overall orchestrator state"""
    started_at: str
    last_updated: str
    tests: Dict[str, TestRecord]
    total_tests: int = 0
    fixed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    is_complete: bool = False

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "started_at": self.started_at,
            "last_updated": self.last_updated,
            "tests": {k: v.to_dict() for k, v in self.tests.items()},
            "total_tests": self.total_tests,
            "fixed_count": self.fixed_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        tests = {k: TestRecord.from_dict(v) for k, v in data.get("tests", {}).items()}
        return cls(
            started_at=data["started_at"],
            last_updated=data["last_updated"],
            tests=tests,
            total_tests=data.get("total_tests", 0),
            fixed_count=data.get("fixed_count", 0),
            failed_count=data.get("failed_count", 0),
            skipped_count=data.get("skipped_count", 0),
            is_complete=data.get("is_complete", False),
        )


# ================================
# State Management
# ================================

class StateManager:
    """Manages state persistence to JSON"""

    def __init__(self, state_file: str = Config.STATE_FILE):
        self.state_file = state_file
        self.state: Optional[OrchestratorState] = None

    def load_or_create(self) -> OrchestratorState:
        """Load existing state or create new"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.state = OrchestratorState.from_dict(data)
                return self.state
        else:
            now = datetime.now().isoformat()
            self.state = OrchestratorState(
                started_at=now,
                last_updated=now,
                tests={},
            )
            return self.state

    def save(self):
        """Save current state to file"""
        if self.state:
            self.state.last_updated = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)

    def add_test(self, test_path: str, error_output: str = ""):
        """Add a new test to track"""
        if test_path not in self.state.tests:
            self.state.tests[test_path] = TestRecord(
                test_path=test_path,
                status=TestStatus.PENDING,
                attempts=[],
                error_output=error_output,
            )
            self.state.total_tests += 1
            self.save()

    def update_test_status(self, test_path: str, status: TestStatus):
        """Update test status"""
        if test_path in self.state.tests:
            self.state.tests[test_path].status = status
            self.save()

    def add_attempt(self, test_path: str, attempt: TestAttempt):
        """Add an attempt record"""
        if test_path in self.state.tests:
            test = self.state.tests[test_path]
            test.attempts.append(attempt)
            test.current_attempt += 1
            self.save()

    def mark_fixed(self, test_path: str):
        """Mark test as fixed"""
        if test_path in self.state.tests:
            test = self.state.tests[test_path]
            test.status = TestStatus.FIXED
            test.fixed_at = datetime.now().isoformat()
            self.state.fixed_count += 1
            self.save()

    def mark_skipped(self, test_path: str, reason: str):
        """Mark test as skipped"""
        if test_path in self.state.tests:
            test = self.state.tests[test_path]
            test.status = TestStatus.SKIPPED
            test.skipped_reason = reason
            self.state.skipped_count += 1
            self.save()

    def mark_failed(self, test_path: str):
        """Mark test as failed"""
        if test_path in self.state.tests:
            test = self.state.tests[test_path]
            test.status = TestStatus.FAILED
            self.state.failed_count += 1
            self.save()


# ================================
# Logging
# ================================

class Logger:
    """Structured logging to JSONL"""

    def __init__(self, log_file: str = Config.LOG_FILE):
        self.log_file = log_file
        self.console = Console()

    def log(self, event_type: str, data: dict):
        """Log an event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            **data
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def info(self, message: str):
        """Log info message"""
        self.console.print(f"[cyan]ℹ️  {message}[/cyan]")
        self.log("info", {"message": message})

    def success(self, message: str):
        """Log success message"""
        self.console.print(f"[green]✅ {message}[/green]")
        self.log("success", {"message": message})

    def warning(self, message: str):
        """Log warning message"""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")
        self.log("warning", {"message": message})

    def error(self, message: str):
        """Log error message"""
        self.console.print(f"[red]❌ {message}[/red]")
        self.log("error", {"message": message})


# ================================
# Backup/Rollback Manager
# ================================

class BackupManager:
    """Manages file backups for rollback"""

    def __init__(self, backup_dir: str = Config.BACKUP_DIR):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def backup_file(self, file_path: str, test_name: str, attempt: int) -> str:
        """Create backup of a file"""
        src = Path(file_path)
        if not src.exists():
            return ""

        # Create backup with test name and attempt number
        backup_name = f"{test_name.replace('/', '_')}_attempt_{attempt}_{src.name}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(src, backup_path)
        return str(backup_path)

    def restore_file(self, backup_path: str, original_path: str):
        """Restore file from backup"""
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, original_path)
            return True
        return False

    def get_file_diff(self, file_path: str, backup_path: str) -> str:
        """Get diff between current and backup"""
        if not os.path.exists(backup_path):
            return "No backup available"

        try:
            import subprocess
            result = subprocess.run(
                ["diff", "-u", backup_path, file_path],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error generating diff: {e}"


# ================================
# Agent Orchestrator
# ================================

class TestFixOrchestrator:
    """Main orchestrator for test fixing workflow"""

    def __init__(self):
        self.console = Console()
        self.logger = Logger()
        self.state_manager = StateManager()
        self.backup_manager = BackupManager()
        self.start_time = time.time()
        self.timeout_seconds = Config.TIMEOUT_HOURS * 3600

    def check_timeout(self) -> bool:
        """Check if we've exceeded timeout"""
        elapsed = time.time() - self.start_time
        return elapsed > self.timeout_seconds

    async def run_test_suite(self) -> tuple[bool, List[str], str]:
        """Run full test suite and extract failing tests"""
        self.logger.info(f"Running test suite: {Config.TEST_COMMAND}")

        process = await asyncio.create_subprocess_shell(
            Config.TEST_COMMAND,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.getcwd()
        )

        stdout, _ = await process.communicate()
        output = stdout.decode()

        # Parse pytest output for failing tests
        failing_tests = self.parse_failing_tests(output)

        success = process.returncode == 0
        return success, failing_tests, output

    def parse_failing_tests(self, pytest_output: str) -> List[str]:
        """Parse pytest output to extract failing test paths"""
        failing_tests = []
        lines = pytest_output.split('\n')

        for line in lines:
            # Look for ERROR or FAILED lines
            if line.startswith('ERROR ') or line.startswith('FAILED '):
                # Extract test path
                parts = line.split()
                if len(parts) > 1:
                    test_path = parts[1].split('::')[0]  # Get file path before ::
                    if test_path not in failing_tests:
                        failing_tests.append(test_path)

        return failing_tests

    async def run_single_test(self, test_path: str) -> tuple[bool, str]:
        """Run a single test file"""
        self.logger.info(f"Running test: {test_path}")

        process = await asyncio.create_subprocess_shell(
            f"cd python && uv run pytest {test_path} -v",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        stdout, _ = await process.communicate()
        output = stdout.decode()

        success = process.returncode == 0
        return success, output

    def create_agent_options(self) -> ClaudeAgentOptions:
        """Create agent options with specialized agents"""
        return ClaudeAgentOptions(
            model=Config.MODEL,
            permission_mode="acceptEdits",
            setting_sources=["project"],
            allowed_tools=[
                'Read',
                'Write',
                'Edit',
                'Grep',
                'Glob',
                'Bash',
                'Task',
                'TodoWrite',
            ],
            agents={
                "test-runner": AgentDefinition(
                    description="Specialized agent for running tests and parsing output",
                    prompt="""You are a test runner specialist. Your job is to:
1. Run the full test suite using 'make test'
2. Parse the pytest output to identify ALL failing tests
3. Extract the exact test file paths (e.g., 'tests/integration/test_foo.py')
4. Return a structured list of failing test paths

Be precise and thorough. Return your findings as a JSON list of test paths.""",
                    model=Config.MODEL,
                    tools=['Bash', 'Read', 'Write'],
                ),
                "test-analyzer": AgentDefinition(
                    description="Analyzes test failures to understand root causes",
                    prompt="""You are a test failure analysis expert. Your job is to:
1. Read the failing test file
2. Analyze the error output from pytest
3. Identify the ROOT CAUSE of the failure (not just symptoms)
4. Check for:
   - Import errors
   - Missing dependencies
   - Configuration issues
   - Database/fixture problems
   - Code logic errors
   - API changes that broke tests
5. Provide a detailed analysis with specific recommendations

Return your analysis as a structured report with:
- Root cause summary
- Evidence from the code/error
- Recommended fix approach""",
                    model=Config.MODEL,
                    tools=['Read', 'Grep', 'Glob', 'Write'],
                ),
                "test-fixer": AgentDefinition(
                    description="Fixes failing tests based on analysis",
                    prompt="""You are a test fixing specialist. Your job is to:
1. Read the test failure analysis
2. Read the failing test file
3. Implement the recommended fixes
4. IMPORTANT: You may need to fix production code, not just the test
5. Make minimal, targeted changes
6. Preserve test intent and coverage
7. Follow the codebase conventions

After making changes:
- List all files modified
- Explain what you changed and why
- Ensure changes are backwards compatible

DO NOT:
- Skip or disable tests
- Remove assertions
- Make tests pass by removing functionality""",
                    model=Config.MODEL,
                    tools=['Read', 'Write', 'Edit', 'Grep', 'Glob', 'Bash'],
                ),
                "validator": AgentDefinition(
                    description="Validates that test fixes work correctly",
                    prompt="""You are a test validation specialist. Your job is to:
1. Run the specific test that was fixed
2. Verify it passes
3. Run the full test suite to check for regressions
4. Analyze any new failures

Report:
- Did the specific test pass? (YES/NO)
- Did any other tests break? (List them)
- Overall verdict: PASS, FAIL, or REGRESSION

If REGRESSION: Recommend rollback and alternative fix approach.""",
                    model=Config.MODEL,
                    tools=['Bash', 'Read', 'Write'],
                ),
            }
        )

    async def fix_test(self, test_path: str, attempt_number: int) -> TestAttempt:
        """Attempt to fix a single test"""
        self.logger.info(f"Fixing test {test_path} (attempt {attempt_number}/{Config.MAX_ATTEMPTS_PER_TEST})")

        # Backup the test file
        backup_path = self.backup_manager.backup_file(test_path, test_path, attempt_number)

        options = self.create_agent_options()
        attempt = TestAttempt(
            attempt_number=attempt_number,
            timestamp=datetime.now().isoformat(),
            analysis="",
            changes_made=[],
            validation_result=False,
        )

        try:
            async with ClaudeSDKClient(options=options) as client:
                # Step 1: Analyze the test failure
                self.state_manager.update_test_status(test_path, TestStatus.ANALYZING)
                test_record = self.state_manager.state.tests[test_path]

                analyze_prompt = f"""Analyze this failing test:

Test file: {test_path}
Error output:
{test_record.error_output}

Use the test-analyzer agent to perform a deep analysis."""

                await client.query(analyze_prompt)
                analysis_result = []
                async for message in client.receive_response():
                    # Collect analysis
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                analysis_result.append(block.text)

                attempt.analysis = '\n'.join(analysis_result)
                self.logger.log("analysis_complete", {"test": test_path, "analysis": attempt.analysis})

                # Step 2: Fix the test
                self.state_manager.update_test_status(test_path, TestStatus.FIXING)

                fix_prompt = f"""Fix this failing test based on the analysis:

Test file: {test_path}
Analysis:
{attempt.analysis}

Use the test-fixer agent to implement the fix. Remember: you may need to fix production code, not just the test file."""

                await client.query(fix_prompt)
                fix_result = []
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                fix_result.append(block.text)

                fix_summary = '\n'.join(fix_result)
                attempt.changes_made.append(fix_summary)
                self.logger.log("fix_applied", {"test": test_path, "changes": fix_summary})

                # Step 3: Validate the fix
                self.state_manager.update_test_status(test_path, TestStatus.VALIDATING)

                validate_prompt = f"""Validate the fix for this test:

Test file: {test_path}

Use the validator agent to:
1. Run the specific test
2. Check for regressions in the full suite"""

                await client.query(validate_prompt)
                validation_result = []
                async for message in client.receive_response():
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                validation_result.append(block.text)

                validation_text = '\n'.join(validation_result)

                # Parse validation result
                if "PASS" in validation_text and "REGRESSION" not in validation_text:
                    attempt.validation_result = True
                    self.logger.success(f"Test {test_path} fixed successfully!")
                elif "REGRESSION" in validation_text:
                    attempt.validation_result = False
                    attempt.error_message = "Fix caused regressions"
                    self.logger.warning(f"Fix caused regressions, rolling back...")
                    # Rollback
                    if backup_path:
                        self.backup_manager.restore_file(backup_path, test_path)
                else:
                    attempt.validation_result = False
                    attempt.error_message = "Test still failing after fix"

        except Exception as e:
            attempt.validation_result = False
            attempt.error_message = str(e)
            self.logger.error(f"Error fixing test {test_path}: {e}")

        return attempt

    def get_next_test_to_process(self, failing_tests: List[str]) -> Optional[str]:
        """Get the next test to process, prioritizing tests with fewer attempts

        Args:
            failing_tests: List of currently failing test paths

        Returns:
            Test path to process next, or None if no valid tests
        """
        state = self.state_manager.state
        valid_tests = []

        for test_path in failing_tests:
            if test_path not in state.tests:
                continue

            test_record = state.tests[test_path]

            # Skip already processed tests
            if test_record.status in [TestStatus.FIXED, TestStatus.SKIPPED]:
                continue

            # Skip tests that have exceeded max attempts
            if test_record.current_attempt >= Config.MAX_ATTEMPTS_PER_TEST:
                continue

            valid_tests.append((test_path, test_record.current_attempt))

        if not valid_tests:
            return None

        # Sort by attempt count (ascending) to process tests with fewer attempts first
        valid_tests.sort(key=lambda x: x[1])
        return valid_tests[0][0]

    async def refresh_failing_tests(self) -> tuple[bool, List[str], str]:
        """Re-run test suite and return current failing tests"""
        self.logger.info("Re-running full test suite to get fresh failing test list...")
        success, current_failing, output = await self.run_test_suite()

        if success:
            self.logger.success("All tests now passing!")
            return True, [], output

        # Detect cascading fixes (tests that were failing but are now passing)
        state = self.state_manager.state
        previously_failing = set(state.tests.keys())
        currently_failing = set(current_failing)

        cascading_fixes = previously_failing - currently_failing
        for test_path in cascading_fixes:
            if test_path in state.tests and state.tests[test_path].status not in [TestStatus.FIXED, TestStatus.SKIPPED]:
                self.logger.success(f"Cascading fix detected: {test_path} now passing!")
                self.state_manager.mark_fixed(test_path)

        # Detect new failures (regressions)
        new_failures = currently_failing - previously_failing
        for test_path in new_failures:
            self.logger.warning(f"New failure detected (possible regression): {test_path}")
            self.state_manager.add_test(test_path, error_output=output)

        return False, list(currently_failing), output

    async def process_test(self, test_path: str) -> bool:
        """Process a single test through the full fix cycle

        Returns:
            bool: True if test was fixed, False otherwise
        """
        test_record = self.state_manager.state.tests[test_path]

        for attempt_num in range(1, Config.MAX_ATTEMPTS_PER_TEST + 1):
            if self.check_timeout():
                self.logger.warning("Timeout reached, stopping test processing")
                break

            attempt = await self.fix_test(test_path, attempt_num)
            self.state_manager.add_attempt(test_path, attempt)

            if attempt.validation_result:
                self.state_manager.mark_fixed(test_path)
                self.logger.success(f"Successfully fixed {test_path}!")
                return True

        # If we exhausted attempts, mark as skipped
        self.state_manager.mark_skipped(
            test_path,
            f"Failed to fix after {Config.MAX_ATTEMPTS_PER_TEST} attempts"
        )
        return False

    def generate_summary_report(self):
        """Generate markdown summary report"""
        state = self.state_manager.state
        report = f"""# Test Fix Summary Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Started:** {state.started_at}
**Duration:** {self.get_elapsed_time()}

## Overview

- **Total Tests:** {state.total_tests}
- **Fixed:** {state.fixed_count} ✅
- **Failed:** {state.failed_count} ❌
- **Skipped:** {state.skipped_count} ⏭️

## Detailed Results

"""

        for test_path, test in state.tests.items():
            report += f"### {test_path}\n\n"
            report += f"**Status:** {test.status.value}\n"
            report += f"**Attempts:** {len(test.attempts)}\n\n"

            if test.status == TestStatus.FIXED:
                report += f"**Fixed at:** {test.fixed_at}\n\n"

            if test.status == TestStatus.SKIPPED:
                report += f"**Skipped reason:** {test.skipped_reason}\n\n"

            if test.attempts:
                report += "#### Attempts:\n\n"
                for attempt in test.attempts:
                    report += f"**Attempt {attempt.attempt_number}** ({attempt.timestamp}):\n"
                    report += f"- **Result:** {'✅ PASS' if attempt.validation_result else '❌ FAIL'}\n"
                    if attempt.error_message:
                        report += f"- **Error:** {attempt.error_message}\n"
                    report += "\n"

            report += "---\n\n"

        # Save report
        with open(Config.SUMMARY_FILE, 'w') as f:
            f.write(report)

        self.logger.success(f"Summary report saved to {Config.SUMMARY_FILE}")

    def get_elapsed_time(self) -> str:
        """Get elapsed time as formatted string"""
        elapsed = time.time() - self.start_time
        return str(timedelta(seconds=int(elapsed)))

    def display_progress(self):
        """Display current progress"""
        state = self.state_manager.state
        table = Table(title="Test Fix Progress")

        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="yellow")

        table.add_row("Total Tests", str(state.total_tests))
        table.add_row("Fixed", f"[green]{state.fixed_count}[/green]")
        table.add_row("Failed", f"[red]{state.failed_count}[/red]")
        table.add_row("Skipped", f"[yellow]{state.skipped_count}[/yellow]")
        table.add_row("Elapsed", self.get_elapsed_time())

        self.console.print(table)

    async def run(self):
        """Main orchestration loop"""
        self.console.print(Panel.fit(
            "[bold cyan]Test Fix Orchestrator[/bold cyan]\n"
            f"Max attempts per test: {Config.MAX_ATTEMPTS_PER_TEST}\n"
            f"Timeout: {Config.TIMEOUT_HOURS} hour(s)",
            border_style="cyan"
        ))

        # Load or create state
        state = self.state_manager.load_or_create()

        if state.is_complete:
            self.logger.info("Previous run was complete. Starting fresh...")
            state = OrchestratorState(
                started_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                tests={},
            )
            self.state_manager.state = state
            self.state_manager.save()

        # Step 1: Run test suite to identify failing tests
        self.logger.info("Step 1: Identifying failing tests...")
        success, failing_tests, output = await self.run_test_suite()

        if success:
            self.logger.success("All tests passing! Nothing to fix.")
            return

        # Add new failing tests to state
        for test_path in failing_tests:
            self.state_manager.add_test(test_path, error_output=output)

        self.logger.info(f"Found {len(failing_tests)} failing tests")
        self.display_progress()

        # Step 2: Process failing tests with dynamic refresh
        processed_in_cycle = 0
        max_cycles = len(failing_tests) * Config.MAX_ATTEMPTS_PER_TEST  # Safety limit

        while failing_tests and processed_in_cycle < max_cycles:
            if self.check_timeout():
                self.logger.warning("⏱️  Timeout reached! Stopping orchestrator.")
                break

            # Get next test to process (prioritize tests with fewer attempts)
            test_path = self.get_next_test_to_process(failing_tests)
            if not test_path:
                break

            test_record = state.tests[test_path]

            # Skip if already fixed or skipped
            if test_record.status in [TestStatus.FIXED, TestStatus.SKIPPED]:
                failing_tests.remove(test_path)
                continue

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing: {test_path} (attempt {test_record.current_attempt + 1})")
            self.logger.info(f"{'='*60}")

            was_fixed = await self.process_test(test_path)
            processed_in_cycle += 1

            if was_fixed:
                # Re-run test suite to get fresh list and detect cascading fixes/regressions
                all_passing, current_failing, output = await self.refresh_failing_tests()

                if all_passing:
                    self.logger.success("🎉 All tests passing after this fix!")
                    break

                # Update our working list with current failures
                failing_tests = current_failing

                # Update error output for any tests still failing
                for fp in failing_tests:
                    if fp in state.tests:
                        state.tests[fp].error_output = output

            self.display_progress()

        # Step 3: Final validation
        self.logger.info("\nStep 3: Running final validation...")
        final_success, final_failing, final_output = await self.run_test_suite()

        if final_success:
            self.logger.success("🎉 All tests passing!")
        else:
            self.logger.warning(f"Still have {len(final_failing)} failing tests")

        # Mark as complete
        state.is_complete = True
        self.state_manager.save()

        # Generate summary report
        self.generate_summary_report()
        self.display_progress()

        self.console.print(Panel.fit(
            f"[bold green]Orchestrator Complete![/bold green]\n"
            f"Fixed: {state.fixed_count} | Skipped: {state.skipped_count}\n"
            f"See {Config.SUMMARY_FILE} for details",
            border_style="green"
        ))


# ================================
# Main Entry Point
# ================================

async def main():
    """Main entry point"""
    orchestrator = TestFixOrchestrator()
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        orchestrator.logger.warning("\n⚠️  Interrupted by user. State saved. Run again to resume.")
    except Exception as e:
        orchestrator.logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())
