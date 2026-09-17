#!/usr/bin/env python3

import asyncio
import json
import os
import shlex
import signal
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from aiohttp import web


HOST = os.getenv("MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("MCP_PORT", "3000"))

# Set MCP_ROOT to restrict filesystem operations to a directory.
# Default: Termux home directory.
MCP_ROOT = Path(
    os.getenv("MCP_ROOT", str(Path.home()))
).expanduser().resolve()

# Maximum output returned by shell/API tools.
MAX_OUTPUT = int(os.getenv("MCP_MAX_OUTPUT", "100000"))

# Optional remote access. Keep false for local-only operation.
ALLOW_REMOTE = os.getenv("MCP_ALLOW_REMOTE", "0") == "1"

# Long-running commands can be enabled explicitly.
ALLOW_LONG_RUNNING = os.getenv("MCP_ALLOW_LONG_RUNNING", "0") == "1"


def output_limit(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text
    return text[:MAX_OUTPUT] + "\n...[output truncated]"


def resolve_path(path: str) -> Path:
    """Resolve a path and prevent escaping MCP_ROOT."""
    p = Path(path).expanduser()

    if not p.is_absolute():
        p = MCP_ROOT / p

    p = p.resolve()

    try:
        p.relative_to(MCP_ROOT)
    except ValueError:
        raise ValueError(f"Path is outside MCP_ROOT: {MCP_ROOT}")

    return p


def run_command(
    command: str,
    timeout: int = 60,
    cwd: str | None = None,
) -> dict[str, Any]:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty string")

    if timeout < 1:
        timeout = 1

    if not ALLOW_LONG_RUNNING:
        timeout = min(timeout, 120)

    workdir = MCP_ROOT if cwd is None else resolve_path(cwd)

    if not workdir.exists() or not workdir.is_dir():
        raise ValueError(f"Invalid working directory: {workdir}")

    try:
        result = subprocess.run(
            ["bash", "-lc", command],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )

        return {
            "exit_code": result.returncode,
            "stdout": output_limit(result.stdout),
            "stderr": output_limit(result.stderr),
            "cwd": str(workdir),
        }

    except subprocess.TimeoutExpired as e:
        return {
            "exit_code": -1,
            "stdout": output_limit(e.stdout or ""),
            "stderr": output_limit(e.stderr or ""),
            "error": f"Command timed out after {timeout} seconds",
        }


def find_root_helper() -> str | None:
    """Return an available root helper, preferring tsu over su."""
    for helper in ("tsu", "su"):
        if shutil.which(helper):
            return helper
    return None


def root_status() -> dict[str, Any]:
    """Detect whether a root-capable helper is installed and usable."""
    helper = find_root_helper()
    if not helper:
        return {
            "available": False,
            "helper": None,
            "uid": os.getuid(),
            "is_root": os.getuid() == 0,
            "message": "Neither tsu nor su was found in PATH.",
        }

    try:
        result = subprocess.run(
            [helper, "-c", "id"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {
            "available": result.returncode == 0,
            "helper": helper,
            "is_root": os.getuid() == 0,
            "exit_code": result.returncode,
            "stdout": output_limit(result.stdout),
            "stderr": output_limit(result.stderr),
        }
    except (subprocess.TimeoutExpired, OSError) as e:
        return {
            "available": False,
            "helper": helper,
            "is_root": os.getuid() == 0,
            "error": str(e),
        }


def run_root_command(
    command: str,
    timeout: int = 60,
    cwd: str | None = None,
) -> dict[str, Any]:
    """Run a command through tsu or su when available."""
    if not isinstance(command, str) or not command.strip():
        raise ValueError("command must be a non-empty string")

    helper = find_root_helper()
    if not helper:
        return {
            "error": "No root helper found. Install/configure tsu or su, and grant root access.",
            "available_helpers": [],
        }

    if timeout < 1:
        timeout = 1
    if not ALLOW_LONG_RUNNING:
        timeout = min(timeout, 120)

    workdir = MCP_ROOT if cwd is None else resolve_path(cwd)
    if not workdir.exists() or not workdir.is_dir():
        raise ValueError(f"Invalid working directory: {workdir}")

    # Use a login shell so Termux commands and environment are available.
    wrapped = f"cd {shlex.quote(str(workdir))} && {command}"
    try:
        result = subprocess.run(
            [helper, "-c", f"bash -lc {shlex.quote(wrapped)}"],
            cwd=str(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
        return {
            "helper": helper,
            "exit_code": result.returncode,
            "stdout": output_limit(result.stdout),
            "stderr": output_limit(result.stderr),
            "cwd": str(workdir),
        }
    except subprocess.TimeoutExpired as e:
        return {
            "helper": helper,
            "exit_code": -1,
            "stdout": output_limit(e.stdout or ""),
            "stderr": output_limit(e.stderr or ""),
            "error": f"Root command timed out after {timeout} seconds",
        }


def termux_api(
    api: str,
    args: list[str] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """
    Run an installed termux-* command.

    Example:
      api = "battery-status"
      args = []
    """
    if not api or "/" in api or "\\" in api:
        raise ValueError("Invalid Termux API command")

    if not api.replace("-", "").isalnum():
        raise ValueError("Invalid Termux API command name")

    executable = f"termux-{api}"

    if subprocess.run(
        ["bash", "-lc", f"command -v {shlex.quote(executable)}"],
        capture_output=True,
        text=True,
    ).returncode != 0:
        return {
            "error": f"{executable} is not installed or unavailable"
        }

    try:
        result = subprocess.run(
            [executable] + (args or []),
            capture_output=True,
            text=True,
            timeout=min(max(timeout, 1), 120),
        )

        return {
            "exit_code": result.returncode,
            "stdout": output_limit(result.stdout),
            "stderr": output_limit(result.stderr),
        }

    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "error": f"{executable} timed out",
        }


def list_files(path: str = ".") -> list[dict[str, Any]]:
    p = resolve_path(path)

    if not p.exists():
        raise FileNotFoundError(str(p))

    if not p.is_dir():
        raise ValueError("Path is not a directory")

    result = []

    for item in sorted(p.iterdir(), key=lambda x: x.name.lower()):
        try:
            result.append({
                "name": item.name,
                "path": str(item.relative_to(MCP_ROOT)),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
            })
        except OSError:
            pass

    return result


def read_file(path: str) -> dict[str, Any]:
    p = resolve_path(path)

    if not p.is_file():
        raise ValueError("Not a file")

    data = p.read_text(errors="replace")

    return {
        "path": str(p.relative_to(MCP_ROOT)),
        "content": output_limit(data),
        "size": p.stat().st_size,
    }


def write_file(path: str, content: str) -> dict[str, Any]:
    p = resolve_path(path)

    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

    return {
        "success": True,
        "path": str(p.relative_to(MCP_ROOT)),
        "size": p.stat().st_size,
    }


def get_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "shell",
            "description": (
                "Execute a shell command in the Termux environment. "
                "Returns stdout, stderr, exit code, and working directory."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {
                        "type": "integer",
                        "default": 60,
                    },
                    "cwd": {"type": "string"},
                },
                "required": ["command"],
            },
        },
        {
            "name": "termux_api",
            "description": (
                "Run an installed Termux:API command, such as "
                "battery-status, wifi-connectioninfo, clipboard-get, "
                "toast, notification, or sensor."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "api": {"type": "string"},
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60,
                    },
                },
                "required": ["api"],
            },
        },
        {
            "name": "get_location",
            "description": (
                "Get the device's current location using Termux:API "
                "(termux-location). Requires the Termux:API app and permission."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["gps", "network", "passive"],
                        "default": "gps",
                    },
                    "request": {
                        "type": "string",
                        "enum": ["once", "last", "updates"],
                        "default": "once",
                    },
                },
            },
        },
        {
            "name": "root_status",
            "description": "Detect tsu/su and test whether root execution is available.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "root_shell",
            "description": (
                "Execute a shell command with root privileges through tsu or su "
                "if available and authorized on the device."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "default": 60},
                    "cwd": {"type": "string"},
                },
                "required": ["command"],
            },
        },
        {
            "name": "list_files",
            "description": "List files and directories inside MCP_ROOT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "default": ".",
                    },
                },
            },
        },
        {
            "name": "read_file",
            "description": "Read a text file inside MCP_ROOT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": "Write text to a file inside MCP_ROOT.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "environment",
            "description": "Return Termux server environment information.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name == "shell":
        return run_command(
            arguments.get("command", ""),
            arguments.get("timeout", 60),
            arguments.get("cwd"),
        )

    if name == "termux_api":
        return termux_api(
            arguments.get("api", ""),
            arguments.get("args", []),
            arguments.get("timeout", 60),
        )

    if name == "get_location":
        provider = arguments.get("provider", "gps")
        request = arguments.get("request", "once")
        return termux_api(
            "location",
            ["-p", provider, "-r", request],
            arguments.get("timeout", 60),
        )

    if name == "root_status":
        return root_status()

    if name == "root_shell":
        return run_root_command(
            arguments.get("command", ""),
            arguments.get("timeout", 60),
            arguments.get("cwd"),
        )

    if name == "list_files":
        return list_files(arguments.get("path", "."))

    if name == "read_file":
        return read_file(arguments["path"])

    if name == "write_file":
        return write_file(
            arguments["path"],
            arguments["content"],
        )

    if name == "environment":
        return {
            "termux_home": str(Path.home()),
            "mcp_root": str(MCP_ROOT),
            "android_root": os.getenv("ANDROID_ROOT"),
            "prefix": os.getenv("PREFIX"),
            "shell": os.getenv("SHELL"),
            "python": sys.version,
            "pid": os.getpid(),
        }

    raise ValueError(f"Unknown tool: {name}")


def jsonrpc_error(request_id, code: int, message: str):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def handle_jsonrpc(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    # Notifications do not require a response.
    if request_id is None and method == "notifications/initialized":
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "termux-mcp-server",
                    "version": "1.0.0",
                },
            },
        }

    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {},
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": get_tools(),
            },
        }

    if method == "tools/call":
        try:
            name = params["name"]
            arguments = params.get("arguments") or {}
            result = call_tool(name, arguments)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                result,
                                indent=2,
                                ensure_ascii=False,
                            ),
                        }
                    ],
                    "isError": False,
                },
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "error": str(e)
                            }),
                        }
                    ],
                    "isError": True,
                },
            }

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": [],
            },
        }

    if method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": [],
            },
        }

    return jsonrpc_error(
        request_id,
        -32601,
        f"Method not found: {method}",
    )


async def index(request: web.Request):
    return web.json_response({
        "name": "termux-mcp-server",
        "version": "1.0.0",
        "transport": "streamable-http",
        "endpoints": {
            "http": "/mcp",
            "sse": "/sse",
        },
        "tools": [x["name"] for x in get_tools()],
    })


async def http_mcp(request: web.Request):
    try:
        message = await request.json()
    except Exception:
        return web.json_response(
            {"error": "Expected JSON-RPC JSON body"},
            status=400,
        )

    response = handle_jsonrpc(message)

    if response is None:
        return web.Response(status=202)

    return web.json_response(response)


async def sse_handler(request: web.Request):
    """
    Basic SSE transport.

    Connect:
      GET /sse

    Send JSON-RPC messages:
      POST /message?session_id=<id>
    """
    session_id = str(uuid.uuid4())

    response = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

    await response.prepare(request)

    # Initial endpoint event.
    endpoint = f"/message?session_id={session_id}"
    await response.write(
        f"event: endpoint\ndata: {endpoint}\n\n".encode()
    )

    request.app["sse_sessions"][session_id] = response

    try:
        while True:
            await asyncio.sleep(15)
            await response.write(b": keepalive\n\n")
    except (asyncio.CancelledError, ConnectionResetError):
        pass
    finally:
        request.app["sse_sessions"].pop(session_id, None)

    return response


async def sse_message(request: web.Request):
    session_id = request.query.get("session_id")
    response = request.app["sse_sessions"].get(session_id)

    if response is None:
        return web.json_response(
            {"error": "Invalid or expired session"},
            status=404,
        )

    try:
        message = await request.json()
    except Exception:
        return web.json_response(
            {"error": "Expected JSON-RPC JSON body"},
            status=400,
        )

    result = handle_jsonrpc(message)

    if result is not None:
        payload = json.dumps(result, ensure_ascii=False)
        await response.write(
            f"event: message\ndata: {payload}\n\n".encode()
        )

    return web.Response(status=202)


def create_app() -> web.Application:
    app = web.Application()
    app["sse_sessions"] = {}

    app.router.add_get("/", index)
    app.router.add_post("/mcp", http_mcp)
    app.router.add_get("/sse", sse_handler)
    app.router.add_post("/message", sse_message)

    return app


def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "http"

    if mode not in {"http", "sse"}:
        print("Usage: mcp-server [http|sse]")
        sys.exit(1)

    bind_host = "0.0.0.0" if ALLOW_REMOTE else HOST

    print("╔══════════════════════════════════════╗")
    print("║       TERMUX MCP SERVER ☠️           ║")
    print("╚══════════════════════════════════════╝")
    print(f"Mode: {mode}")
    print(f"Address: http://{bind_host}:{PORT}")
    print(f"MCP Root: {MCP_ROOT}")
    print(f"Remote access: {ALLOW_REMOTE}")
    print()
    print("HTTP endpoint: /mcp")
    print("SSE endpoint:  /sse")
    print()

    web.run_app(
        create_app(),
        host=bind_host,
        port=PORT,
    )


if __name__ == "__main__":
    main()
