#!/bin/bash

# Setup AWS Data Processing MCP Server for querying SageMaker Lakehouse

echo "🚀 Setting up AWS Data Processing MCP Server"
echo "============================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install Python 3.10+ if needed
echo "Ensuring Python 3.10+ is available..."
uv python install 3.11

# Install the MCP server
echo "Installing AWS Data Processing MCP Server..."
uvx awslabs.aws-dataprocessing-mcp-server@latest --help > /dev/null 2>&1

# Create MCP configuration directory
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"

# Copy configuration
cp mcp-dataprocessing-config.json "$MCP_CONFIG_DIR/aws-dataprocessing.json"

echo
echo "✅ MCP Server setup complete!"
echo
echo "Configuration saved to: $MCP_CONFIG_DIR/aws-dataprocessing.json"
echo
echo "To use the MCP server:"
echo "1. Make sure AWS credentials are configured"
echo "2. The server will be available to AI agents that support MCP"
echo "3. Use with Claude Desktop, Continue.dev, or other MCP-compatible tools"
echo
echo "Example usage:"
echo "  uvx awslabs.aws-dataprocessing-mcp-server@latest --allow-write"