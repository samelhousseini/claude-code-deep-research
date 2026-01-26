#!/bin/bash
#
# Deep Research System Installation Script
#
# Usage:
#   ./install.sh                        # Install with interactive prompts
#   ./install.sh --force                # Overwrite existing files
#   ./install.sh --check                # Check installation status
#   ./install.sh --mcp                  # Configure MCP servers interactively
#   ./install.sh --tavily-key KEY       # Configure Tavily with API key
#   ./install.sh --brave-key KEY        # Configure Brave Search with API key
#   ./install.sh --perplexity-key KEY   # Configure Perplexity with API key
#   ./install.sh --firecrawl-key KEY    # Configure Firecrawl with API key
#   ./install.sh --skip-mcp             # Skip MCP configuration prompt
#
# Examples:
#   ./install.sh --force --tavily-key tvly-xxxxx
#   ./install.sh --mcp
#   ./install.sh --check
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Error: Python not found. Please install Python 3.x"
    exit 1
fi

# Run the Python installer
exec "$PYTHON" "$SCRIPT_DIR/install.py" "$@"
