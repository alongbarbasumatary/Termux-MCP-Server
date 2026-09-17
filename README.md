<div align="center">

# Termux MCP Server

### Give AI clients access to your Android terminal.

A lightweight, configurable **Model Context Protocol server** for Termux, built with Python and `aiohttp`.

<p>
  <a href="https://github.com/alongbarbasumatary/Termux-MCP-Server">
    <img src="https://img.shields.io/github/stars/alongbarbasumatary/Termux-MCP-Server?style=for-the-badge&logo=github" alt="GitHub Stars">
  </a>
  <a href="https://github.com/alongbarbasumatary/Termux-MCP-Server">
    <img src="https://img.shields.io/github/license/alongbarbasumatary/Termux-MCP-Server?style=for-the-badge" alt="License">
  </a>
  <img src="https://img.shields.io/badge/platform-Android-green?style=for-the-badge&logo=android" alt="Platform">
  <img src="https://img.shields.io/badge/built%20with-Python-blue?style=for-the-badge&logo=python" alt="Python">
</p>

</div>

---

## Overview

**Termux MCP Server** connects MCP-compatible AI applications to your Termux environment.

It allows AI clients to interact with your Android device through tools for executing commands, managing files, accessing environment information, and running Termux API commands.

> Designed for local use, with remote access available when explicitly enabled.

## Features

| Feature | Description |
|---|---|
| ⚡ Shell Execution | Run commands directly inside Termux |
| 📁 File Management | List, read, and write files |
| 📱 Termux API | Execute supported Termux API commands |
| 🌐 HTTP Transport | Connect through an HTTP MCP endpoint |
| 📡 SSE Transport | Connect through Server-Sent Events |
| ⚙️ Configuration | Customize host, port, root directory, and limits |
| 🔒 Local-First | Local access is enabled by default |
| 🚀 Simple Setup | Install and start with minimal commands |

---

## Installation

### Automatic Installation

Run the following command inside **Termux**:

```bash
curl -fsSL https://raw.githubusercontent.com/alongbarbasumatary/Termux-MCP-Server/main/scripts/install.sh | bash
```

The installer automatically:

- Installs Python
- Installs required dependencies
- Downloads the MCP server
- Creates the `mcp-server` command

### Manual Installation

Clone the repository:

```bash
git clone https://github.com/alongbarbasumatary/Termux-MCP-Server.git
```

Enter the project directory:

```bash
cd Termux-MCP-Server
```

Install the required packages:

```bash
pkg update -y
pkg install -y python curl
```

Install the Python dependency:

```bash
python -m pip install --upgrade aiohttp
```

Run the server manually:

```bash
python server.py http
```

Or start SSE mode:

```bash
python server.py sse
```

> If you want to use the `mcp-server` command, use the automatic installer.

---

## Quick Start

### Start HTTP Mode

```bash
mcp-server http
```

MCP endpoint:

```text
http://127.0.0.1:3000/mcp
```

### Start SSE Mode

```bash
mcp-server sse
```

SSE endpoint:

```text
http://127.0.0.1:3000/sse
```

### Stop the Server

Press:

```text
CTRL + C
```

---

## Configuration

The server can be configured using environment variables.

### Custom Port

```bash
MCP_PORT=3001 mcp-server http
```

### Custom Host

```bash
MCP_HOST=127.0.0.1 mcp-server http
```

### Enable Remote Access

Remote access is disabled by default.

```bash
MCP_HOST=0.0.0.0 MCP_ALLOW_REMOTE=1 mcp-server http
```

The server can then be accessed using your Android device's local IP address:

```text
http://ANDROID_DEVICE_IP:3000/mcp
```

> **Security notice:** Remote access allows other devices on the network to interact with the server. Only enable it on trusted networks. Do not expose the server directly to the public internet without proper security controls.

### Change MCP Root Directory

By default, the server uses the Termux home directory.

To use shared Android storage:

```bash
termux-setup-storage
```

Then start the server with:

```bash
MCP_ROOT=/sdcard mcp-server http
```

### Configure Output Limit

```bash
MCP_MAX_OUTPUT=20000 mcp-server http
```

### Enable Long-Running Commands

Long-running commands are disabled by default.

```bash
MCP_ALLOW_LONG_RUNNING=1 mcp-server http
```

---

## Available Tools

The server exposes the following MCP tools:

| Tool | Description |
|---|---|
| `shell` | Execute shell commands |
| `termux_api` | Run Termux API commands |
| `list_files` | List files and directories |
| `read_file` | Read file contents |
| `write_file` | Write content to files |
| `environment` | Retrieve environment information |

---

## Termux API Support

To use Termux API functionality, install the Termux API package:

```bash
pkg install termux-api
```

You also need the **Termux:API Android add-on** installed on your device.

Example:

```bash
termux-battery-status
```

---

## Requirements

- Android device
- Termux
- Python 3
- Internet connection during installation
- Termux:API add-on for API-related features

---

## Troubleshooting

### Port Already in Use

If you see:

```text
OSError: [Errno 98] address already in use
```

Another process is already using port `3000`.

Check the port:

```bash
ss -ltnp | grep ':3000'
```

Or use another port:

```bash
MCP_PORT=3001 mcp-server http
```

### Check Running Server Processes

```bash
ps -ef | grep '[s]erver.py'
```

### Stop an Existing Installed Instance

```bash
pkill -f '/.termux-mcp/server.py'
```

Then start the server again:

```bash
mcp-server http
```

### Reinstall the Python Dependency

```bash
python -m pip install --upgrade aiohttp
```

---

## Uninstallation

Remove the installed server and command:

```bash
rm -rf "$HOME/.termux-mcp"
rm -f "$PREFIX/bin/mcp-server"
```

---

## Project Structure

```text
Termux-MCP-Server/
├── server.py
├── scripts/
│   └── install.sh
├── README.md
└── LICENSE
```

---

## Security

This server can execute commands and access files within its configured root directory.

Recommendations:

- Keep the server bound to `127.0.0.1` when possible
- Enable remote access only when necessary
- Use trusted networks
- Avoid exposing port `3000` publicly
- Do not connect untrusted AI clients
- Review commands before allowing sensitive operations
- Avoid using the server with confidential files

---

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Created and maintained by **[alongbarbasumatary](https://github.com/alongbarbasumatary)**.

## Repository

[View the project on GitHub](https://github.com/alongbarbasumatary/Termux-MCP-Server)

---

<div align="center">

If this project is useful to you, consider giving it a ⭐ on GitHub.

</div>
