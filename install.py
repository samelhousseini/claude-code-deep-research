#!/usr/bin/env python3
"""
Deep Research System Installation Script

Installs research skills and agents for Claude Code.

Usage:
    python install.py           # Install with interactive prompts
    python install.py --force   # Overwrite existing files without prompting
    python install.py --check   # Check installation status only
"""

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


def check_installation():
    """Check current installation status."""
    print_header("Installation Status Check")

    skills_dir = get_skills_dir()
    agents_dir = get_agents_dir()

    print(f"\n  Skills directory: {skills_dir}")
    print(f"  Agents directory: {agents_dir}")

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

    print("\n  Dependencies:")
    yaml_ok, version = check_pyyaml()
    if yaml_ok:
        print_status("ok", f"PyYAML {version}")
    else:
        print_status("error", "PyYAML (not installed)")

    return yaml_ok


def install(force=False):
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

    # MCP server instructions
    print_header("MCP Server Setup (Optional)")
    print("""
  For web search capabilities, configure at least one MCP search server.

  Recommended: Tavily
  ──────────────────────────────────────────────────────────────────
  1. Get API key from: https://tavily.com/
  2. Add to ~/.claude/settings.json:

     {
       "mcpServers": {
         "tavily": {
           "command": "npx",
           "args": ["-y", "tavily-mcp@latest"],
           "env": {
             "TAVILY_API_KEY": "your-api-key"
           }
         }
       }
     }

  Alternative: Brave Search
  ──────────────────────────────────────────────────────────────────
  1. Get API key from: https://brave.com/search/api/
  2. Add to ~/.claude/settings.json:

     {
       "mcpServers": {
         "brave-search": {
           "command": "npx",
           "args": ["-y", "@anthropics/brave-search-mcp"],
           "env": {
             "BRAVE_API_KEY": "your-api-key"
           }
         }
       }
     }

  Alternative: Perplexity (for deep synthesis)
  ──────────────────────────────────────────────────────────────────
  1. Get API key from: https://www.perplexity.ai/settings/api
  2. Configure using Perplexity MCP server
""")

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
  python install.py           # Install with prompts for existing files
  python install.py --force   # Overwrite existing files
  python install.py --check   # Check installation status
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

    args = parser.parse_args()

    if args.check:
        check_installation()
    else:
        success = install(force=args.force)
        if not success:
            sys.exit(1)
        print("\n  Installation complete!\n")


if __name__ == "__main__":
    main()
