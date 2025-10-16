"""
Status Badge Implementation - Run All Phases
Executes all four phases in sequence with error handling and progress tracking

This script runs:
- Phase 1: Backend API Mapping
- Phase 2: Frontend Types
- Phase 3: Frontend Components
- Phase 4: Testing & Verification
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()


async def run_phase(phase_num: int, phase_name: str, script_path: Path, console: Console) -> tuple[bool, float]:
    """
    Run a single phase script and return success status and duration.

    Args:
        phase_num: Phase number (1-4)
        phase_name: Human-readable phase name
        script_path: Path to the phase script
        console: Rich console for output

    Returns:
        Tuple of (success: bool, duration: float)
    """
    import time
    from subprocess import run, PIPE, CalledProcessError

    start_time = time.time()

    console.print(f"\n[bold cyan]{'=' * 60}[/bold cyan]")
    console.print(f"[bold yellow]Phase {phase_num}: {phase_name}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 60}[/bold cyan]\n")

    try:
        # Run the phase script
        result = run(
            ["uv", "run", "python", str(script_path)],
            capture_output=False,  # Let output stream to console
            text=True,
            check=True,
            cwd=script_path.parent.parent  # Run from project root
        )

        duration = time.time() - start_time
        console.print(f"\n[bold green]✓ Phase {phase_num} completed in {duration:.1f}s[/bold green]\n")
        return True, duration

    except CalledProcessError as e:
        duration = time.time() - start_time
        console.print(f"\n[bold red]✗ Phase {phase_num} failed after {duration:.1f}s[/bold red]")
        console.print(f"[red]Error: {e}[/red]\n")
        return False, duration
    except Exception as e:
        duration = time.time() - start_time
        console.print(f"\n[bold red]✗ Phase {phase_num} encountered an error[/bold red]")
        console.print(f"[red]Error: {e}[/red]\n")
        return False, duration


async def main() -> int:
    """
    Main function that runs all phases.

    Returns:
        Exit code: 0 for success, 1 for failure
    """
    console = Console()

    console.print(Panel.fit(
        "[bold cyan]Status Badge Implementation - All Phases[/bold cyan]\n\n"
        "This will run all 4 phases sequentially:\n"
        "1. Backend API Mapping (~1 min)\n"
        "2. Frontend Types (~30 sec)\n"
        "3. Frontend Components (~1 min)\n"
        "4. Testing & Verification (~1 min)\n\n"
        "[yellow]Total estimated time: 3-4 minutes[/yellow]\n"
        "[yellow]Estimated cost: ~$0.38[/yellow]",
        border_style="cyan"
    ))

    # Confirm before starting
    console.print("\n[bold yellow]Press ENTER to start, or Ctrl+C to cancel...[/bold yellow]")
    try:
        input()
    except KeyboardInterrupt:
        console.print("\n[red]Cancelled by user[/red]")
        return 0

    # Define phases
    agents_dir = Path(__file__).parent
    phases = [
        (1, "Backend API Mapping", agents_dir / "implement_status_badge_phase1.py"),
        (2, "Frontend Types", agents_dir / "implement_status_badge_phase2.py"),
        (3, "Frontend Components", agents_dir / "implement_status_badge_phase3.py"),
        (4, "Testing & Verification", agents_dir / "implement_status_badge_phase4.py"),
    ]

    # Track results
    results = []
    total_start = asyncio.get_event_loop().time()

    # Run each phase
    for phase_num, phase_name, script_path in phases:
        success, duration = await run_phase(phase_num, phase_name, script_path, console)
        results.append((phase_num, phase_name, success, duration))

        # Stop on failure
        if not success:
            console.print(f"\n[bold red]Stopping due to Phase {phase_num} failure[/bold red]")
            console.print(f"[yellow]Please review the error and fix before continuing[/yellow]")
            break

    total_duration = asyncio.get_event_loop().time() - total_start

    # Summary table
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]EXECUTION SUMMARY[/bold cyan]")
    console.print("=" * 70 + "\n")

    summary_table = Table(title="Phase Results", show_header=True, title_style="bold cyan")
    summary_table.add_column("Phase", style="cyan", no_wrap=True)
    summary_table.add_column("Name", style="white")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Duration", justify="right", style="yellow")

    for phase_num, phase_name, success, duration in results:
        status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
        summary_table.add_row(
            f"Phase {phase_num}",
            phase_name,
            status,
            f"{duration:.1f}s"
        )

    console.print(summary_table)

    # Overall result
    all_success = all(result[2] for result in results)
    completed_phases = len(results)

    console.print(f"\n[bold]Total Duration:[/bold] {total_duration:.1f}s")
    console.print(f"[bold]Phases Completed:[/bold] {completed_phases}/4")

    if all_success and completed_phases == 4:
        console.print("\n" + "=" * 70)
        console.print("[bold green]🎉 ALL PHASES COMPLETED SUCCESSFULLY! 🎉[/bold green]")
        console.print("=" * 70 + "\n")

        console.print(Panel(
            "[cyan]Next Steps:[/cyan]\n\n"
            "1. Review automated changes:\n"
            "   git diff\n\n"
            "2. Manual UI Testing:\n"
            "   cd archon-ui-main && npm run dev\n"
            "   Open http://localhost:3737\n"
            "   Navigate to Knowledge page\n"
            "   Verify badges appear correctly\n\n"
            "3. Final checks:\n"
            "   - Test tooltips\n"
            "   - Check responsive design\n"
            "   - Verify dark mode\n\n"
            "4. Commit when ready:\n"
            "   git add .\n"
            "   git commit -m 'feat: add status badges to knowledge cards'",
            title="Implementation Complete",
            border_style="green"
        ))

        return 0
    else:
        console.print("\n[bold red]Implementation incomplete - please address errors above[/bold red]\n")
        return 1


if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        sys.exit(0)
