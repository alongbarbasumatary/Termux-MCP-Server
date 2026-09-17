Termux MCP Server

A lightweight Model Context Protocol (MCP) server for Android using Termux.

This server allows MCP-compatible AI clients to interact with your Termux environment through tools such as shell commands, file management, Termux API, and environment information.

Features

- Run shell commands in Termux
- Execute Termux API commands
- List files and directories
- Read files
- Write files
- View environment information
- HTTP transport support
- Server-Sent Events (SSE) transport support
- Configurable host and port
- Configurable MCP root directory
- Local-only access by default
- Optional remote access
- Optional long-running commands
- Simple installation using one command

Requirements

- Android device
- "Termux" (https://termux.dev/)
- Internet connection
- Python 3
- "curl"

«Recommended: Install Termux from "F-Droid" (https://f-droid.org/packages/com.termux/) or the official Termux source.»

Installation

Open Termux and run:

curl -fsSL https://raw.githubusercontent.com/alongbarbasumatary/Termux-MCP-Server/main/install.sh | bash

The installer will:

1. Install required packages
2. Install Python
3. Install "aiohttp"
4. Download the MCP server
5. Create the "mcp-server" command

Usage

Start HTTP Server

mcp-server http

Default HTTP endpoint:

http://127.0.0.1:3000/mcp

Start SSE Server

mcp-server sse

Default SSE endpoint:

http://127.0.0.1:3000/sse

Configuration

You can configure the server using environment variables.

Change Port

MCP_PORT=3001 mcp-server http

The server will then run at:

http://127.0.0.1:3001

Change Host

By default, the server only accepts local connections:

127.0.0.1

To bind to another host:

MCP_HOST=0.0.0.0 mcp-server http

«Binding to "0.0.0.0" alone does not enable remote access. Remote access must also be explicitly enabled.»

Enable Remote Access

Remote access is disabled by default.

To enable it:

MCP_ALLOW_REMOTE=1 mcp-server http

Example:

MCP_HOST=0.0.0.0 MCP_ALLOW_REMOTE=1 MCP_PORT=3000 mcp-server http

«Security warning: Remote access may expose your Termux environment to other devices. Only enable it on trusted networks and use additional authentication or network restrictions when exposing the server outside your device.»

Change MCP Root Directory

By default, the MCP root is the Termux home directory:

/data/data/com.termux/files/home

To use another directory:

MCP_ROOT=/sdcard mcp-server http

You may need to grant Termux storage access first:

termux-setup-storage

Configure Maximum Output

The default maximum command output is "100000" characters.

MCP_MAX_OUTPUT=20000 mcp-server http

Enable Long-Running Commands

Long-running commands are disabled by default.

To enable them:

MCP_ALLOW_LONG_RUNNING=1 mcp-server http

Available MCP Tools

The server provides the following tools:

Tool| Description
"shell"| Execute shell commands in Termux
"termux_api"| Execute Termux API commands
"list_files"| List files and directories
"read_file"| Read file contents
"write_file"| Write content to a file
"environment"| Get environment information

Example Commands

List Files

ls -la

Check Current Directory

pwd

Check Python Version

python --version

Check Termux Packages

pkg list-installed

Use Termux API

If Termux:API is installed:

termux-battery-status

You must have the Termux:API add-on installed to use Termux API commands.

Connect to an MCP Client

Use the appropriate endpoint in your MCP-compatible client.

HTTP

http://127.0.0.1:3000/mcp

SSE

http://127.0.0.1:3000/sse

If the MCP client runs on another device, configure the server for remote access and use your Android device's local IP address.

Example:

http://ANDROID_DEVICE_IP:3000/mcp

Troubleshooting

Port Already in Use

If you see:

OSError: [Errno 98] address already in use

Another process is already using port "3000".

Check the port:

ss -ltnp | grep ':3000'

Check running server processes:

ps -ef | grep '[s]erver.py'

Stop the installed MCP server process:

pkill -f '/.termux-mcp/server.py'

Then start the server again:

mcp-server http

Alternatively, use another port:

MCP_PORT=3001 mcp-server http

Check Whether the Server Is Running

curl http://127.0.0.1:3000/

Python Dependency Error

Reinstall "aiohttp":

python -m pip install --upgrade aiohttp

Stop the Server

Press:

CTRL + C

Or stop the process using:

pkill -f '/.termux-mcp/server.py'

Uninstall

Remove the installed server files:

rm -rf "$HOME/.termux-mcp"
rm -f "$PREFIX/bin/mcp-server"

Security

This server can execute commands and access files inside the configured MCP root.

Important security recommendations:

- Keep remote access disabled unless required
- Do not expose the server directly to the public internet
- Use trusted networks only
- Avoid sharing your endpoint publicly
- Review commands before allowing an AI client to execute them
- Do not run sensitive commands through untrusted clients
- Use firewall or VPN restrictions for remote access

Project Structure

Termux-MCP-Server/
├── server.py
├── install.sh
├── README.md
└── LICENSE

License

This project is licensed under the MIT License.

You may add a "LICENSE" file containing the MIT License text.

Author

Created by "Alongbar Basumatary" (https://github.com/alongbarbasumatary).

Repository

"Termux-MCP-Server" (https://github.com/alongbarbasumatary/Termux-MCP-Server)
