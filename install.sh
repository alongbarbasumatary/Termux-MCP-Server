#!/data/data/com.termux/files/usr/bin/bash

set -e

# ============================================================
# Termux MCP Server Installer
# GitHub: alongbarbasumatary/Termux-MCP-Server
# ============================================================

REPO_OWNER="alongbarbasumatary"
REPO_NAME="Termux-MCP-Server"
BRANCH="main"

INSTALL_DIR="$HOME/.termux-mcp"
BIN_DIR="$PREFIX/bin"

SERVER_URL="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/server.py"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       TERMUX MCP SERVER INSTALLER        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Termux environment
if [ -z "$PREFIX" ] || [ ! -d "$PREFIX" ]; then
    echo "❌ This installer must be run inside Termux."
    exit 1
fi

# Install curl if missing
if ! command -v curl >/dev/null 2>&1; then
    echo "📦 Installing curl..."
    pkg install -y curl
fi

echo "📦 Updating package information..."
pkg update -y

echo "🐍 Installing Python..."
pkg install -y python

echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

echo "⬇️ Downloading MCP server..."
curl -fL "$SERVER_URL" -o "$INSTALL_DIR/server.py"

echo "📚 Installing Python dependency..."
python -m pip install --upgrade aiohttp

echo "🔗 Creating mcp-server command..."

cat > "$BIN_DIR/mcp-server" <<EOF
#!/data/data/com.termux/files/usr/bin/bash

exec python "$INSTALL_DIR/server.py" "\$@"
EOF

chmod +x "$BIN_DIR/mcp-server"

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Start HTTP server:"
echo "   mcp-server http"
echo ""
echo "📡 Start SSE server:"
echo "   mcp-server sse"
echo ""
echo "🌐 HTTP endpoint:"
echo "   http://127.0.0.1:3000/mcp"
echo ""
echo "📡 SSE endpoint:"
echo "   http://127.0.0.1:3000/sse"
echo ""
echo "⚡ Termux MCP Server is ready!"
echo ""