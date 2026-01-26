# Claude Code Deep Research

A comprehensive research workflow system for Claude Code that enables structured, multi-source research with both interactive and autonomous execution modes.

## Features

- **6 Slash Commands**: Complete research workflow from outline to final report
- **Autonomous Mode**: Run entire research pipeline without prompts using `--auto` flag
- **Parallel Execution**: Batch research with background agents
- **Resume Support**: Interrupted research can be resumed from where it stopped
- **Structured Output**: YAML outlines, JSON results, Markdown reports

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/samelhousseini/claude-code-deep-research.git
cd claude-code-deep-research

# Run installer
python install.py

# Or use shell script
./install.sh
```

### Verify Installation

```bash
python install.py --check
```

### Configure MCP Search Servers

The installer can automatically configure MCP search servers for you:

```bash
# Interactive configuration (will prompt for API keys)
python install.py --mcp

# Or provide API keys directly (non-interactive)
python install.py --tavily-key YOUR_TAVILY_KEY
python install.py --brave-key YOUR_BRAVE_KEY
python install.py --perplexity-key YOUR_PERPLEXITY_KEY
python install.py --firecrawl-key YOUR_FIRECRAWL_KEY

# Install everything with API keys in one command
python install.py --force --tavily-key YOUR_KEY
```

**Supported MCP Servers:**

| Server | Description | Get API Key |
|--------|-------------|-------------|
| Tavily | Recommended for web search | [tavily.com](https://tavily.com) |
| Brave Search | Alternative web search | [brave.com/search/api](https://brave.com/search/api/) |
| Perplexity | Deep synthesis and research | [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api) |
| Firecrawl | Web scraping and crawling | [firecrawl.dev](https://firecrawl.dev/) |

## Commands

| Command | Description |
|---------|-------------|
| `/research <topic>` | Generate research outline with items and fields |
| `/research-add-items` | Add more items to existing outline |
| `/research-add-fields` | Add more fields to collect |
| `/research-deep` | Execute deep research on all items |
| `/research-report` | Generate markdown report from results |
| `/research-auto <topic>` | Run complete workflow automatically |

### Autonomous Mode

Add `--auto` flag for unattended execution:

```
/research-auto "AI chip market 2024-2025" --auto
```

## Project Structure

```
~/.claude/
├── skills/
│   └── research/
│       ├── research/SKILL.md
│       ├── research-add-items/SKILL.md
│       ├── research-add-fields/SKILL.md
│       ├── research-deep/SKILL.md
│       ├── research-report/SKILL.md
│       ├── research-auto/SKILL.md
│       └── validate_json.py
└── agents/
    └── web-search-agent.md
```

## Output Structure

```
{topic-slug}/
├── outline.yaml      # Research items
├── fields.yaml       # Data fields to collect
├── results/          # JSON files per item
│   ├── item_1.json
│   └── item_2.json
├── generate_report.py
└── report.md         # Final markdown report
```

## Requirements

- Claude Code 2.1.0+
- Python 3.x with PyYAML
- At least one MCP search server (Tavily, Brave, or Perplexity)

## Documentation

See [docs/README.md](docs/README.md) for detailed documentation including:
- Complete command reference
- Configuration options
- Troubleshooting guide
- Use cases and examples

## Examples

The `examples/` directory contains sample files:
- `sample-outline.yaml` - Example research outline
- `sample-fields.yaml` - Example field definitions
- `sample-result.json` - Example research result

## Reference

- Deep Research Skill for Claude Code / OpenCode - ([link](https://github.com/Weizhena/Deep-Research-skills))


## License

MIT License
