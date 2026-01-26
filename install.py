#!/usr/bin/env python3
"""
Deep Research System Installation Script

Installs research skills, agents, and MCP servers for Claude Code.

Usage:
    python install.py           # Install skills/agents with interactive prompts
    python install.py --force   # Overwrite existing files without prompting
    python install.py --check   # Check installation status only
    python install.py --mcp     # Configure MCP search servers interactively
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


# Installation paths
def get_claude_dir():
    """Get the .claude directory path."""
    return Path.home() / ".claude"


def get_skills_dir():
    """Get the skills installation directory."""
    return get_claude_dir() / "skills" / "research"


def get_agents_dir():
    """Get the agents installation directory."""
    return get_claude_dir() / "agents"


def get_settings_path():
    """Get the settings.json path."""
    return get_claude_dir() / "settings.json"


# Source paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
SRC_DIR = SCRIPT_DIR / "src"
SRC_SKILLS_DIR = SRC_DIR / "skills" / "research"
SRC_AGENTS_DIR = SRC_DIR / "agents"


# Files and directories to install
SKILL_DIRS = [
    "research",
    "research-add-items",
    "research-add-fields",
    "research-deep",
    "research-report",
    "research-auto",
]
SKILL_FILES = ["validate_json.py"]
AGENT_FILES = ["web-search-agent.md"]

# MCP Server configurations
MCP_SERVERS = {
    "tavily": {
        "name": "Tavily",
        "description": "Recommended for web search",
        "url": "https://tavily.com/",
        "env_var": "TAVILY_API_KEY",
        "config": {
            "command": "npx",
            "args": ["-y", "tavily-mcp@latest"],
            "env": {
                "TAVILY_API_KEY": ""
            }
        }
    },
    "brave-search": {
        "name": "Brave Search",
        "description": "Alternative web search",
        "url": "https://brave.com/search/api/",
        "env_var": "BRAVE_API_KEY",
        "config": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": ""
            }
        }
    },
    "perplexity": {
        "name": "Perplexity",
        "description": "Deep synthesis and research",
        "url": "https://www.perplexity.ai/settings/api",
        "env_var": "PERPLEXITY_API_KEY",
        "config": {
            "command": "npx",
            "args": ["-y", "perplexity-mcp@latest"],
            "env": {
                "PERPLEXITY_API_KEY": ""
            }
        }
    },
    "firecrawl": {
        "name": "Firecrawl",
        "description": "Web scraping and crawling",
        "url": "https://firecrawl.dev/",
        "env_var": "FIRECRAWL_API_KEY",
        "config": {
            "command": "npx",
            "args": ["-y", "firecrawl-mcp@latest"],
            "env": {
                "FIRECRAWL_API_KEY": ""
            }
        }
    }
}


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_status(status, text):
    """Print a status message."""
    symbols = {"ok": "✓", "warn": "!", "error": "✗", "info": "→"}
    symbol = symbols.get(status, "•")
    print(f"  [{symbol}] {text}")


def check_pyyaml():
    """Check if PyYAML is installed."""
    try:
        import yaml
        return True, yaml.__version__
    except ImportError:
        return False, None


def install_pyyaml():
    """Attempt to install PyYAML."""
    print_status("info", "Attempting to install PyYAML...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "PyYAML"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def copy_directory(src, dst, force=False):
    """Copy a directory, optionally overwriting."""
    if dst.exists():
        if force:
            shutil.rmtree(dst)
        else:
            return False, "exists"
    shutil.copytree(src, dst)
    return True, "installed"


def copy_file(src, dst, force=False):
    """Copy a file, optionally overwriting."""
    if dst.exists():
        if force:
            dst.unlink()
        else:
            return False, "exists"
    shutil.copy2(src, dst)
    return True, "installed"


def load_settings():
    """Load existing settings.json or return empty dict."""
    settings_path = get_settings_path()
    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_settings(settings):
    """Save settings to settings.json."""
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)


def check_mcp_servers():
    """Check which MCP servers are configured."""
    settings = load_settings()
    mcp_servers = settings.get("mcpServers", {})

    configured = []
    for server_id, server_info in MCP_SERVERS.items():
        if server_id in mcp_servers:
            env = mcp_servers[server_id].get("env", {})
            api_key = env.get(server_info["env_var"], "")
            if api_key and api_key != "your-api-key-here":
                configured.append((server_id, server_info["name"], True))
            else:
                configured.append((server_id, server_info["name"], False))

    return configured, mcp_servers


def configure_mcp_servers(api_keys=None):
    """Configure MCP servers interactively or with provided keys."""
    print_header("MCP Server Configuration")

    settings = load_settings()
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    # If api_keys provided (non-interactive), use those
    if api_keys:
        for server_id, api_key in api_keys.items():
            if server_id in MCP_SERVERS and api_key:
                server_info = MCP_SERVERS[server_id]
                config = server_info["config"].copy()
                config["env"] = {server_info["env_var"]: api_key}
                settings["mcpServers"][server_id] = config
                print_status("ok", f"Configured {server_info['name']}")
        save_settings(settings)
        return True

    # Interactive configuration
    print("\n  Available MCP search servers:\n")

    servers_list = list(MCP_SERVERS.items())
    for i, (server_id, server_info) in enumerate(servers_list, 1):
        existing = server_id in settings["mcpServers"]
        status = " (configured)" if existing else ""
        print(f"    {i}. {server_info['name']}: {server_info['description']}{status}")
        print(f"       Get API key: {server_info['url']}")
        print()

    print("    0. Skip MCP configuration")
    print()

    try:
        choice = input("  Select server to configure (0-4): ").strip()
        if choice == "0" or not choice:
            print_status("info", "Skipping MCP configuration")
            return False

        idx = int(choice) - 1
        if 0 <= idx < len(servers_list):
            server_id, server_info = servers_list[idx]

            print(f"\n  Configuring {server_info['name']}...")
            print(f"  Get your API key from: {server_info['url']}")
            print()

            api_key = input(f"  Enter {server_info['env_var']}: ").strip()

            if api_key:
                config = server_info["config"].copy()
                config["env"] = {server_info["env_var"]: api_key}
                settings["mcpServers"][server_id] = config
                save_settings(settings)
                print_status("ok", f"Configured {server_info['name']}")

                # Ask if user wants to configure more
                another = input("\n  Configure another server? (y/n): ").strip().lower()
                if another == 'y':
                    return configure_mcp_servers()
                return True
            else:
                print_status("warn", "No API key provided, skipping")
                return False
        else:
            print_status("error", "Invalid selection")
            return False

    except (ValueError, KeyboardInterrupt):
        print()
        print_status("info", "Configuration cancelled")
        return False


def check_installation():
    """Check current installation status."""
    print_header("Installation Status Check")

    skills_dir = get_skills_dir()
    agents_dir = get_agents_dir()
    settings_path = get_settings_path()

    print(f"\n  Skills directory: {skills_dir}")
    print(f"  Agents directory: {agents_dir}")
    print(f"  Settings file: {settings_path}")

    print("\n  Skills:")
    for skill in SKILL_DIRS:
        skill_path = skills_dir / skill / "SKILL.md"
        if skill_path.exists():
            print_status("ok", f"/{skill}")
        else:
            print_status("error", f"/{skill} (not installed)")

    for file in SKILL_FILES:
        file_path = skills_dir / file
        if file_path.exists():
            print_status("ok", file)
        else:
            print_status("error", f"{file} (not installed)")

    print("\n  Agents:")
    for agent in AGENT_FILES:
        agent_path = agents_dir / agent
        if agent_path.exists():
            print_status("ok", agent)
        else:
            print_status("error", f"{agent} (not installed)")

    print("\n  MCP Servers:")
    configured, mcp_servers = check_mcp_servers()
    if configured:
        for server_id, name, has_key in configured:
            if has_key:
                print_status("ok", f"{name}")
            else:
                print_status("warn", f"{name} (no API key)")

    # Check for servers not in our list but configured
    for server_id in mcp_servers:
        if server_id not in MCP_SERVERS:
            print_status("ok", f"{server_id} (custom)")

    if not mcp_servers:
        print_status("error", "No MCP servers configured")
        print_status("info", "Run: python install.py --mcp")

    print("\n  Dependencies:")
    yaml_ok, version = check_pyyaml()
    if yaml_ok:
        print_status("ok", f"PyYAML {version}")
    else:
        print_status("error", "PyYAML (not installed)")

    return yaml_ok


def install(force=False, skip_mcp=False):
    """Install all components."""
    print_header("Deep Research System Installer")

    print(f"\n  Platform: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version.split()[0]}")

    # Check source files exist
    if not SRC_DIR.exists():
        print_status("error", f"Source directory not found: {SRC_DIR}")
        print_status("info", "Please run this script from the project root directory.")
        return False

    skills_dir = get_skills_dir()
    agents_dir = get_agents_dir()

    print(f"\n  Installing to:")
    print(f"    Skills: {skills_dir}")
    print(f"    Agents: {agents_dir}")

    # Create directories
    print_header("Creating Directories")
    skills_dir.mkdir(parents=True, exist_ok=True)
    print_status("ok", f"Created {skills_dir}")
    agents_dir.mkdir(parents=True, exist_ok=True)
    print_status("ok", f"Created {agents_dir}")

    # Install skills
    print_header("Installing Skills")
    skills_installed = 0
    skills_skipped = 0

    for skill in SKILL_DIRS:
        src = SRC_SKILLS_DIR / skill
        dst = skills_dir / skill
        if src.exists():
            success, status = copy_directory(src, dst, force)
            if success:
                print_status("ok", f"/{skill}")
                skills_installed += 1
            else:
                if force:
                    print_status("error", f"/{skill} (failed)")
                else:
                    print_status("warn", f"/{skill} (already exists, use --force to overwrite)")
                    skills_skipped += 1
        else:
            print_status("error", f"/{skill} (source not found)")

    for file in SKILL_FILES:
        src = SRC_SKILLS_DIR / file
        dst = skills_dir / file
        if src.exists():
            success, status = copy_file(src, dst, force)
            if success:
                print_status("ok", file)
                skills_installed += 1
            else:
                if force:
                    print_status("error", f"{file} (failed)")
                else:
                    print_status("warn", f"{file} (already exists, use --force to overwrite)")
                    skills_skipped += 1
        else:
            print_status("error", f"{file} (source not found)")

    # Install agents
    print_header("Installing Agents")
    agents_installed = 0
    agents_skipped = 0

    for agent in AGENT_FILES:
        src = SRC_AGENTS_DIR / agent
        dst = agents_dir / agent
        if src.exists():
            success, status = copy_file(src, dst, force)
            if success:
                print_status("ok", agent)
                agents_installed += 1
            else:
                if force:
                    print_status("error", f"{agent} (failed)")
                else:
                    print_status("warn", f"{agent} (already exists, use --force to overwrite)")
                    agents_skipped += 1
        else:
            print_status("error", f"{agent} (source not found)")

    # Check/install PyYAML
    print_header("Checking Dependencies")
    yaml_ok, version = check_pyyaml()
    if yaml_ok:
        print_status("ok", f"PyYAML {version} (already installed)")
    else:
        if install_pyyaml():
            yaml_ok, version = check_pyyaml()
            if yaml_ok:
                print_status("ok", f"PyYAML {version} (installed)")
            else:
                print_status("error", "PyYAML installation verification failed")
        else:
            print_status("error", "PyYAML (please install manually: pip install PyYAML)")

    # Summary
    print_header("Installation Summary")
    total_installed = skills_installed + agents_installed
    total_skipped = skills_skipped + agents_skipped

    if total_installed > 0:
        print_status("ok", f"Installed: {total_installed} components")
    if total_skipped > 0:
        print_status("warn", f"Skipped: {total_skipped} components (already exist)")
    if yaml_ok:
        print_status("ok", "Dependencies: satisfied")
    else:
        print_status("error", "Dependencies: PyYAML missing")

    # Check MCP servers
    configured, mcp_servers = check_mcp_servers()
    has_valid_mcp = any(has_key for _, _, has_key in configured)

    if has_valid_mcp:
        print_status("ok", f"MCP Servers: {len([c for c in configured if c[2]])} configured")
    else:
        print_status("warn", "MCP Servers: none configured")

    # MCP server configuration
    if not skip_mcp and not has_valid_mcp:
        print_header("MCP Server Setup")
        print("""
  Web search requires at least one MCP search server.
  You can configure this now or later with: python install.py --mcp
""")
        try:
            setup_now = input("  Configure MCP server now? (y/n): ").strip().lower()
            if setup_now == 'y':
                configure_mcp_servers()
        except (KeyboardInterrupt, EOFError):
            print()
            print_status("info", "Skipping MCP configuration")

    # Usage instructions
    print_header("Usage")
    print("""
  Available commands:

    /research <topic>           Generate research outline
    /research-add-items         Add items to existing outline
    /research-add-fields        Add fields to existing definitions
    /research-deep              Execute deep research on outline
    /research-report            Generate markdown report from results
    /research-auto <topic>      Run complete research workflow

  Autonomous mode (no prompts):

    /research <topic> --auto
    /research-auto <topic> --auto

  Example:

    /research-auto "AI chip market 2024-2025" --auto
""")

    return yaml_ok and total_installed > 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install Deep Research System for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py           # Install skills and agents
  python install.py --force   # Overwrite existing files
  python install.py --check   # Check installation status
  python install.py --mcp     # Configure MCP search servers

  # Configure specific MCP servers non-interactively:
  python install.py --tavily-key YOUR_KEY
  python install.py --brave-key YOUR_KEY
  python install.py --perplexity-key YOUR_KEY
        """
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing files without prompting"
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Check installation status only"
    )
    parser.add_argument(
        "--mcp", "-m",
        action="store_true",
        help="Configure MCP search servers interactively"
    )
    parser.add_argument(
        "--tavily-key",
        metavar="KEY",
        help="Tavily API key (non-interactive)"
    )
    parser.add_argument(
        "--brave-key",
        metavar="KEY",
        help="Brave Search API key (non-interactive)"
    )
    parser.add_argument(
        "--perplexity-key",
        metavar="KEY",
        help="Perplexity API key (non-interactive)"
    )
    parser.add_argument(
        "--firecrawl-key",
        metavar="KEY",
        help="Firecrawl API key (non-interactive)"
    )
    parser.add_argument(
        "--skip-mcp",
        action="store_true",
        help="Skip MCP server configuration prompt"
    )

    args = parser.parse_args()

    # Collect API keys from arguments
    api_keys = {}
    if args.tavily_key:
        api_keys["tavily"] = args.tavily_key
    if args.brave_key:
        api_keys["brave-search"] = args.brave_key
    if args.perplexity_key:
        api_keys["perplexity"] = args.perplexity_key
    if args.firecrawl_key:
        api_keys["firecrawl"] = args.firecrawl_key

    if args.check:
        check_installation()
    elif args.mcp:
        if api_keys:
            configure_mcp_servers(api_keys)
        else:
            configure_mcp_servers()
    elif api_keys:
        # If API keys provided, install everything including MCP
        success = install(force=args.force, skip_mcp=True)
        if success:
            configure_mcp_servers(api_keys)
        if not success:
            sys.exit(1)
        print("\n  Installation complete!\n")
    else:
        success = install(force=args.force, skip_mcp=args.skip_mcp)
        if not success:
            sys.exit(1)
        print("\n  Installation complete!\n")


if __name__ == "__main__":
    main()
