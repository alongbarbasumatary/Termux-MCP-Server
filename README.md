# Termux MCP Server

<div align="center">

### Give AI clients access to your Android terminal.

A lightweight, configurable Model Context Protocol server for Termux, built with Python and `aiohttp`.

[![Platform](https://img.shields.io/badge/platform-Android-green?style=for-the-badge&logo=android)](https://termux.dev/)
[![Python](https://img.shields.io/badge/built%20with-Python-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/github/license/alongbarbasumatary/Termux-MCP-Server?style=for-the-badge)](LICENSE)

</div>

---

## Overview

Termux MCP Server connects MCP-compatible AI applications to your Termux environment.

It provides tools for executing shell commands, managing files, accessing environment information, and running Termux API commands.

> Local access is enabled by default. Remote access must be explicitly enabled.

## Features

- Shell command execution
- File listing, reading, and writing
- Termux API command support
- HTTP and SSE transport
- Configurable host, port, root directory, and output limits
- Local-first security defaults
- One-command installation

## Installation

### Automatic Installation

Run this command inside Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/alongbarbasumatary/Termux-MCP-Server/main/scripts/install.sh | bash
```

### Manual Installation

```bash
git clone https://github.com/alongbarbasumatary/Termux-MCP-Server.git
cd Termux-MCP-Server
```

Install dependencies:

```bash
pkg update -y
pkg install -y python curl
python -m pip install --upgrade aiohttp
```

Start manually:

```bash
python server.py http
```

Or:

```bash
python server.py sse
```

## Usage

### HTTP Mode

```bash
mcp-server http
```

Endpoint:

```text
http://127.0.0.1:3000/mcp
```

### SSE Mode

```bash
mcp-server sse
```

Endpoint:

```text
http://127.0.0.1:3000/sse
```

Stop the server with `CTRL + C`.

## Configuration

### Change Port

```bash
MCP_PORT=3001 mcp-server http
```

### Enable Remote Access

Remote access is disabled by default.

```bash
MCP_HOST=0.0.0.0 MCP_ALLOW_REMOTE=1 mcp-server http
```

Connect from another device using:

```text
http://ANDROID_DEVICE_IP:3000/mcp
```

> **Security warning:** Enable remote access only on trusted networks. This server can execute commands and access files.

### Change MCP Root

```bash
termux-setup-storage
MCP_ROOT=/sdcard mcp-server http
```

### Configure Output Limit

```bash
MCP_MAX_OUTPUT=20000 mcp-server http
```

### Enable Long-Running Commands

```bash
MCP_ALLOW_LONG_RUNNING=1 mcp-server http
```

## Available Tools

| Tool | Description |
|---|---|
| `shell` | Execute shell commands |
| `termux_api` | Run Termux API commands |
| `list_files` | List files and directories |
| `read_file` | Read file contents |
| `write_file` | Write content to files |
| `environment` | Retrieve environment information |

## Termux API Support

Install the Termux API package:

```bash
pkg install termux-api
```

You also need the **Termux:API Android add-on** installed on your device.

Official Termux:API repository:

[Download and view Termux:API](https://github.com/termux/termux-api)

## Requirements

- Android device
- Termux
- Python 3
- Internet connection during installation
- Termux:API add-on for API features

### Download Termux

Install Termux from the official GitHub repository:

[Download Termux](https://github.com/termux/termux-app)

## Troubleshooting

### Port Already in Use

```bash
ss -ltnp | grep ':3000'
```

Or use another port:

```bash
MCP_PORT=3001 mcp-server http
```

### Check Running Processes

```bash
ps -ef | grep '[s]erver.py'
```

### Stop an Existing Instance

```bash
pkill -f '/.termux-mcp/server.py'
```

## Uninstallation

```bash
rm -rf "$HOME/.termux-mcp"
rm -f "$PREFIX/bin/mcp-server"
```

## Project Structure

```text
Termux-MCP-Server/
├── server.py
├── scripts/
│   └── install.sh
├── README.md
└── LICENSE
```

## Security

- Keep the server bound to `127.0.0.1` when possible
- Enable remote access only when necessary
- Use trusted networks
- Avoid exposing port `3000` publicly
- Do not connect untrusted AI clients
- Review commands before allowing sensitive operations
- Avoid using the server with confidential files

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Created and maintained by [alongbarbasumatary](https://github.com/alongbarbasumatary).

---

<div align="center">

If this project is useful, consider giving it a ⭐ on GitHub.

</div>
