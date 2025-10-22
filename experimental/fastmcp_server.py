"""Experimental FastMCP server for Claude Code.

This module creates a small MCP server using :class:`mcp.server.fastmcp.FastMCP`
that exposes a handful of helpful tools for exploring the local workspace.
It is designed to be easy to run from the command line so Claude Code can
connect via the MCP (Model Context Protocol).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

from mcp.server.fastmcp import Context, FastMCP


logger = logging.getLogger("experimental.fastmcp_server")
WORKSPACE_ROOT = Path(os.getenv("ARCHON_WORKSPACE", Path.cwd())).resolve()


INSTRUCTIONS = """# Experimental FastMCP Server

Welcome to the experimental Archon MCP server. These tools help you explore the
local project workspace from Claude Code.

## Available tools
- `workspace_health`: Quick readiness and uptime check.
- `list_workspace`: List files under a relative path (default: project root).
- `read_text_file`: Read small UTF-8 text files from the repository.
- `search_workspace`: Perform a simple substring search across text files.

## Transports
- `stdio` (default): Best option when running locally with Claude Code.
- `sse`: Legacy streaming endpoint for backwards compatibility.
- `http`: Streamable HTTP transport suitable for HTTP-based MCP clients.

## Safety
- Paths are always resolved inside the repository to avoid accidental access to
  other parts of the filesystem.
- Searches limit the number of results to keep responses concise.

Use concise prompts when invoking tools and prefer relative paths whenever
possible.
"""


def _resolve_workspace_path(relative_path: str) -> Path:
    """Resolve a user-supplied path string safely within the workspace."""

    candidate = (WORKSPACE_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError("Path escapes the workspace boundary") from exc

    return candidate


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, str]]:
    """Track basic lifecycle information for clients that connect."""

    start_time = datetime.utcnow().isoformat()
    logger.info("Starting experimental FastMCP server")
    try:
        yield {"started_at": start_time}
    finally:
        logger.info("Shutting down experimental FastMCP server")


mcp = FastMCP(
    "experimental-fastmcp",
    description="Lightweight MCP server for experimental Claude Code usage",
    instructions=INSTRUCTIONS,
    lifespan=lifespan,
)


@mcp.tool()
async def workspace_health(ctx: Context) -> str:
    """Return a small status payload indicating the server is ready."""

    lifespan_context = getattr(ctx.request_context, "lifespan_context", {}) or {}
    started_at = lifespan_context.get("started_at")
    uptime = None

    if started_at:
        try:
            started = datetime.fromisoformat(started_at)
            uptime_delta = datetime.utcnow() - started
            uptime = max(int(uptime_delta.total_seconds()), 0)
        except Exception:  # pragma: no cover - fallback for unexpected input
            uptime = None

    payload = {
        "status": "ready",
        "started_at": started_at,
        "uptime_seconds": uptime,
    }

    logger.debug("workspace_health -> %s", payload)
    return json.dumps(payload)


@mcp.tool()
async def list_workspace(ctx: Context, path: str | None = None, max_entries: int = 200) -> str:
    """
    List files beneath the provided workspace-relative ``path``.

    ``path`` defaults to the repository root. Results are truncated to the first
    ``max_entries`` items to keep responses compact.
    """

    relative_path = path or "."
    resolved = _resolve_workspace_path(relative_path)

    if not resolved.exists():
        return json.dumps(
            {
                "success": False,
                "error": f"Path '{relative_path}' does not exist inside the workspace.",
            }
        )

    if resolved.is_file():
        return json.dumps(
            {
                "success": True,
                "entries": [str(resolved.relative_to(WORKSPACE_ROOT))],
            }
        )

    entries: list[str] = []
    for idx, item in enumerate(sorted(resolved.glob("**/*"))):
        if idx >= max_entries:
            break
        try:
            entries.append(str(item.relative_to(WORKSPACE_ROOT)))
        except ValueError:
            # Fall back to a relative path from the provided directory for robustness
            entries.append(str(item.relative_to(resolved)))

    return json.dumps(
        {
            "success": True,
            "root": str(resolved.relative_to(WORKSPACE_ROOT)),
            "count": len(entries),
            "entries": entries,
            "truncated": resolved.is_dir() and len(entries) >= max_entries,
        }
    )


@mcp.tool()
async def read_text_file(ctx: Context, path: str, max_bytes: int = 16384) -> str:
    """
    Read a UTF-8 text file located within the workspace.

    Large files are truncated after ``max_bytes`` to prevent overwhelming the
    client response.
    """

    try:
        resolved = _resolve_workspace_path(path)
    except ValueError as exc:
        return json.dumps({"success": False, "error": str(exc)})

    if not resolved.exists() or not resolved.is_file():
        return json.dumps(
            {
                "success": False,
                "error": f"File '{path}' not found inside the workspace.",
            }
        )

    try:
        data = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return json.dumps(
            {
                "success": False,
                "error": "File is not valid UTF-8 text.",
            }
        )

    truncated = len(data.encode("utf-8")) > max_bytes
    if truncated:
        encoded = data.encode("utf-8")[:max_bytes]
        data = encoded.decode("utf-8", errors="ignore")

    return json.dumps(
        {
            "success": True,
            "path": str(resolved.relative_to(WORKSPACE_ROOT)),
            "truncated": truncated,
            "content": data,
        }
    )


@mcp.tool()
async def search_workspace(
    ctx: Context,
    query: str,
    path: str | None = None,
    max_results: int = 20,
    max_file_size: int = 200_000,
) -> str:
    """Perform a simple substring search across text files in the workspace."""

    if not query:
        return json.dumps({"success": False, "error": "Query cannot be empty."})

    base_dir = _resolve_workspace_path(path or ".")

    if not base_dir.exists():
        return json.dumps(
            {
                "success": False,
                "error": f"Path '{path}' does not exist inside the workspace.",
            }
        )

    results: list[dict[str, str | int]] = []
    for candidate in sorted(base_dir.rglob("*")):
        if not candidate.is_file():
            continue

        try:
            if candidate.stat().st_size > max_file_size:
                continue
            text = candidate.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if query.lower() in text.lower():
            snippet_start = text.lower().index(query.lower())
            snippet_end = min(len(text), snippet_start + 200)
            snippet = text[snippet_start:snippet_end]

            results.append(
                {
                    "path": str(candidate.relative_to(WORKSPACE_ROOT)),
                    "snippet": snippet.strip(),
                }
            )

            if len(results) >= max_results:
                break

    return json.dumps(
        {
            "success": True,
            "query": query,
            "results": results,
            "truncated": len(results) >= max_results,
        }
    )


def main() -> None:
    """Command-line entry point used by Claude Code MCP configuration."""

    parser = argparse.ArgumentParser(description="Run the experimental FastMCP server")
    parser.add_argument(
        "--transport",
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        choices=("stdio", "sse", "http"),
        help="Transport to use when exposing the MCP server.",
    )
    parser.add_argument("--host", default=os.getenv("MCP_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "8765")),
        help="Port used for SSE or HTTP transport (ignored for stdio).",
    )
    parser.add_argument(
        "--http-path",
        default=os.getenv("MCP_HTTP_PATH", "/mcp"),
        help="Base path for HTTP transport endpoints.",
    )

    args = parser.parse_args()

    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    mcp.settings.host = args.host
    mcp.settings.port = args.port

    http_path = args.http_path if args.http_path.startswith("/") else f"/{args.http_path}"
    mcp.settings.streamable_http_path = http_path

    if args.transport == "stdio":
        logger.info("Starting FastMCP server using stdio transport")
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        logger.info(
            "Starting FastMCP server using SSE transport",
            extra={"host": args.host, "port": args.port},
        )
        mcp.run(transport="sse")
    else:
        logger.info(
            "Starting FastMCP server using HTTP transport",
            extra={"host": args.host, "port": args.port, "path": http_path},
        )
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
