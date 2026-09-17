<div align="center">

# Termux MCP Server

### Give AI assistants powerful, controlled access to your Android device through Termux.

A lightweight, extensible **Model Context Protocol (MCP) server** for Termux, built with Python and `aiohttp`.

<p>
  <a href="https://github.com/alongbarbasumatary/Termux-MCP-Server">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub Repository">
  </a>
  <a href="https://github.com/alongbarbasumatary/Termux-MCP-Server/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/alongbarbasumatary/Termux-MCP-Server?style=for-the-badge" alt="License">
  </a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Platform-Termux-000000?style=for-the-badge&logo=android" alt="Termux">
</p>

</div>

---

## Overview

**Termux MCP Server** connects MCP-compatible AI clients to a Termux environment. It allows an AI assistant or automation client to interact with your Android device through a simple HTTP or Server-Sent Events (SSE) interface.

Use it to execute shell commands, access Termux APIs, inspect files, read and write data, retrieve device location, and view environment information.

> **Security note:** This server can expose powerful device capabilities. Run it locally unless remote access is explicitly required, and never expose an unauthenticated instance to the public internet.

## Features

- **HTTP MCP transport** for modern MCP clients
- **SSE transport** for clients that require Server-Sent Events
- **Shell execution** through Termux
- **Termux:API integration**
- **Device location access**
- **File management** within a configurable root directory
- **Environment inspection**
- **Configurable host, port, output limits, and permissions**
- **Local-first defaults**
- **Simple command-line startup**

## Available MCP Tools

| Tool | Description |
|---|---|
| `shell` | Execute shell commands in Termux |
| `termux_api` | Run supported Termux:API commands |
| `location` | Retrieve the Android device's current location using Termux:API |
| `list_files` | List files and directories |
| `read_file` | Read a file from the configured root |
| `write_file` | Create or overwrite a file in the configured root |
| `environment` | Inspect selected environment and runtime information |

### Location Tool

The `location` tool uses Termux:API to request the device's location.

Before using it, install the Termux:API companion application and grant the required Android location permissions.

The underlying Termux command is:

```bash
termux-location
```

Depending on the Android version and device settings, location availability may require:

- Location services to be enabled
- Termux:API to be installed
- Location permission to be granted
- A working GPS, Wi-Fi, or mobile network connection

## Requirements

- Android device
- [Termux](https://github.com/termux/termux-app)
- Python 3.9 or newer
- Optional: [Termux:API](https://github.com/termux/termux-api) for device APIs and location access

### Install Termux

Install Termux from the official project repository:

**[Download Termux](https://github.com/termux/termux-app)**

### Install Termux:API

Install the Termux:API companion application if you want to use device features such as location, battery information, sensors, and other Android APIs:

**[Download and view Termux:API](https://github.com/termux/termux-api)**

After installing Termux:API, also install the Termux:API package inside Termux:

```bash
pkg update
pkg install termux-api
```

## Installation

### Automatic Installation

Run this command directly in Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/alongbarbasumatary/Termux-MCP-Server/main/scripts/install.sh | bash
```

The installer sets up the required files and makes the `mcp-server` command available.

### Manual Installation

Clone the repository:

```bash
git clone https://github.com/alongbarbasumatary/Termux-MCP-Server.git
cd Termux-MCP-Server
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If the project does not include a requirements file in your checkout, install the runtime dependency manually:

```bash
pip install aiohttp
```

Make the launcher executable if required:

```bash
chmod +x mcp-server
```

## Usage

Start the server using one of the supported transports.

### HTTP

```bash
mcp-server http
```

Endpoint:

```text
http://127.0.0.1:3000/mcp
```

### SSE

```bash
mcp-server sse
```

Endpoint:

```text
http://127.0.0.1:3000/sse
```

### Custom Port

Set a different port with `MCP_PORT`:

```bash
MCP_PORT=8080 mcp-server http
```

## Configuration

The server is designed to be local-only by default.

| Variable | Default | Description |
|---|---|---|
| `MCP_HOST` | `127.0.0.1` | Network interface to bind to |
| `MCP_PORT` | `3000` | Server port |
| `MCP_ROOT` | Current project directory | Root directory for file operations |
| `MCP_MAX_OUTPUT` | Application default | Maximum shell output size |
| `MCP_ALLOW_LONG_RUNNING` | Application default | Allow long-running commands |
| `MCP_ALLOW_REMOTE` | `0` | Allow non-local binding when enabled |

### Local Access

The recommended configuration is local-only:

```bash
mcp-server http
```

### Remote Access

Remote access is optional and should only be enabled when you understand the network and security implications:

```bash
MCP_HOST=0.0.0.0 MCP_ALLOW_REMOTE=1 mcp-server http
```

**Important:** Do not expose the server directly to the public internet without adding authentication, encryption, firewall restrictions, and other appropriate security controls.

## Connecting an MCP Client

Configure your MCP-compatible client to use the appropriate endpoint.

### HTTP Transport

```text
http://127.0.0.1:3000/mcp
```

### SSE Transport

```text
http://127.0.0.1:3000/sse
```

The exact configuration format depends on the MCP client you use.

## Example Capabilities

Once connected, an MCP client may be able to:

- Run Termux shell commands
- Call Termux:API commands
- Retrieve device location
- Browse files inside the configured root
- Read and write files
- Inspect the Termux environment
- Automate Android workflows through supported commands

## Troubleshooting

### `mcp-server: command not found`

Restart Termux or ensure the installation directory is included in your `PATH`.

### Location does not work

Check the following:

1. Install the Termux:API application.
2. Install the Termux package:

   ```bash
   pkg install termux-api
   ```

3. Enable Android Location Services.
4. Grant location permission to Termux and Termux:API.
5. Test directly:

   ```bash
   termux-location
   ```

### Port already in use

Use another port:

```bash
MCP_PORT=8080 mcp-server http
```

### Termux API command fails

Make sure the corresponding Termux:API companion application is installed and that the requested Android permission has been granted.

## Security Recommendations

- Keep the server bound to `127.0.0.1` whenever possible.
- Do not share the server endpoint publicly without authentication.
- Avoid running untrusted commands.
- Use a restricted `MCP_ROOT` for file access.
- Review commands before allowing an AI client to execute them.
- Do not store secrets in files accessible to the server.
- Use firewall or VPN controls for remote access.

## Project Structure

```text
Termux-MCP-Server/
├── scripts/
│   └── install.sh
├── server.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions, bug reports, feature requests, and improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the server in Termux.
5. Open a pull request.

## License

This project is distributed under the license included in the repository.

---

<div align="center">

Made for Termux, Android automation, and MCP-compatible AI clients.

**[View the repository](https://github.com/alongbarbasumatary/Termux-MCP-Server)**

</div>
