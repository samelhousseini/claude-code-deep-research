# Deep Research Skills for Claude Code

A structured research workflow system for Claude Code enabling comprehensive, multi-source research with both human-in-the-loop and autonomous execution modes.

## Overview

Deep Research Skills provides six slash commands that work together to:
1. Generate research outlines from topics
2. Supplement items and fields iteratively
3. Execute deep research with parallel agents
4. Generate formatted markdown reports

The system supports two execution modes:
- **Interactive Mode**: Human-in-the-loop control at every stage
- **Autonomous Mode** (`--auto`): Fully automated execution with sensible defaults

## Installation

### Quick Install

```bash
# Run the installation script
python install.py

# Or use the shell wrapper
./install.sh
```

### Manual Install

```bash
# Copy skills to Claude Code skills directory
cp -r src/skills/research/* ~/.claude/skills/research/

# Copy agent to Claude Code agents directory
cp src/agents/web-search-agent.md ~/.claude/agents/

# Install Python dependency
pip install pyyaml
```

### Verify Installation

```bash
python install.py --check
```

## Commands Reference

### /research

Generate a research outline with items and field definitions.

```bash
# Interactive mode - prompts for customization
/research AI Coding Tools 2024

# Autonomous mode - uses defaults, no prompts
/research AI Coding Tools 2024 --auto
```

**Output**: Creates `{topic-slug}/outline.yaml` and `{topic-slug}/fields.yaml`

### /research-add-items

Supplement the research outline with additional items.

```bash
# Interactive mode
/research-add-items

# Autonomous mode - auto-searches for more items
/research-add-items --auto
```

**Requirement**: Must have existing `*/outline.yaml` in current directory.

### /research-add-fields

Supplement field definitions with additional fields.

```bash
# Interactive mode
/research-add-fields

# Autonomous mode - auto-searches for recommended fields
/research-add-fields --auto
```

**Requirement**: Must have existing `*/fields.yaml` in current directory.

### /research-deep

Execute deep research by launching parallel agents for each item.

```bash
# Interactive mode - approves each batch
/research-deep

# Autonomous mode - runs all batches continuously
/research-deep --auto
```

**Features**:
- Resume capability (skips completed items)
- Batch execution with configurable size
- JSON validation after each agent completes
- Progress reporting and error handling

**Output**: Creates `{topic-slug}/results/*.json` files

### /research-report

Generate a formatted markdown report from JSON results.

```bash
# Interactive mode - choose TOC summary fields
/research-report

# Autonomous mode - auto-selects top metric fields
/research-report --auto
```

**Features**:
- Table of contents with anchor links
- User-selectable summary fields for TOC
- Category-organized detailed sections
- Handles complex nested data structures
- Skips uncertain values

**Output**: Creates `{topic-slug}/report.md`

### /research-auto

Run the complete research lifecycle in one command.

```bash
# Interactive mode - 4 initial questions, then mostly automated
/research-auto AI Coding Tools 2024

# Fully autonomous mode - no prompts, sensible defaults
/research-auto AI Coding Tools 2024 --auto
```

**Features**:
- Domain auto-detection (technical, financial, academic, general)
- Domain-specific defaults for depth and focus
- Error logging to `{topic-slug}/errors.log`
- Progress display throughout all phases

## Workflow Example

### Step 1: Generate Outline

```bash
/research AI Agent Demo 2025
```

Creates:
- `ai-agent-demo-2025/outline.yaml` - List of 15-20 AI agents to research
- `ai-agent-demo-2025/fields.yaml` - Field definitions (name, company, features, etc.)

### Step 2: (Optional) Add More Items or Fields

```bash
/research-add-items   # Add more agents to research
/research-add-fields  # Add more data fields to collect
```

### Step 3: Execute Deep Research

```bash
/research-deep
```

Launches parallel agents to research each item. Creates:
- `ai-agent-demo-2025/results/chatgpt_agent.json`
- `ai-agent-demo-2025/results/claude_computer_use.json`
- ... (one JSON per item)

### Step 4: Generate Report

```bash
/research-report
```

Creates `ai-agent-demo-2025/report.md` with:
- Table of contents with summary metrics
- Detailed sections for each agent
- Sources and references

## File Structure

After a complete research cycle:

```
ai-agent-demo-2025/
├── outline.yaml      # Research items + execution config
├── fields.yaml       # Field definitions
├── results/          # JSON research results
│   ├── chatgpt_agent.json
│   ├── claude_computer_use.json
│   └── ...
├── report.md         # Generated markdown report
├── generate_report.py # Report generation script
└── errors.log        # (if any errors occurred)
```

## Configuration

### outline.yaml Structure

```yaml
topic: "Research Topic Name"

items:
  - name: "Item Name"
    category: "Category"
    description: "Brief description"

execution:
  batch_size: 3          # Items per parallel batch
  items_per_agent: 1     # Items assigned to each agent
  output_dir: ./results  # JSON output directory
  auto_mode: false       # Autonomous execution flag
```

### fields.yaml Structure

```yaml
field_categories:
  - category: "Basic Info"
    fields:
      - name: "field_name"
        description: "What this field captures"
        detail_level: "brief"    # brief | moderate | detailed
        required: true           # Required for validation
```

### Detail Levels

| Level | Description | Examples |
|-------|-------------|----------|
| `brief` | Single value, short phrase | Dates, names, versions |
| `moderate` | Paragraph, small list | Features, pricing tiers |
| `detailed` | Comprehensive content | Full analysis, extensive lists |

## MCP Server Setup

Deep Research Skills work best with MCP search servers for enhanced web search capabilities.

### Recommended: Tavily

```json
{
  "mcpServers": {
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"],
      "env": {
        "TAVILY_API_KEY": "your-api-key"
      }
    }
  }
}
```

Get API key: https://tavily.com

### Alternative: Brave Search

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/brave-search-mcp"],
      "env": {
        "BRAVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

Get API key: https://brave.com/search/api/

### Optional: Perplexity (Deep Synthesis)

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "perplexity-mcp"],
      "env": {
        "PERPLEXITY_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Note**: Without MCP servers, the skills fall back to Claude Code's built-in WebSearch tool.

## Validation Script

The `validate_json.py` script checks JSON results against field definitions:

```bash
# Validate single file
python ~/.claude/skills/research/validate_json.py \
  -f fields.yaml \
  -j results/github_copilot.json

# Validate all results in directory
python ~/.claude/skills/research/validate_json.py \
  -f fields.yaml \
  -d results/
```

**Output**:
- Coverage percentage
- Missing required fields (ERROR)
- Missing optional fields (WARN)
- Extra fields not in schema (INFO)

## Troubleshooting

### "No outline.yaml found"

Run `/research <topic>` first to generate the research outline.

### "No fields.yaml found"

The `/research` command should create both files. Check you're in the correct directory.

### Agent fails or times out

- Check MCP server configuration
- Verify API keys are valid
- Try reducing `batch_size` in outline.yaml
- Use `--auto` mode for better error recovery

### Validation fails

- Check `fields.yaml` syntax is valid YAML
- Ensure required fields are populated
- Review `uncertain` array in JSON for fields that couldn't be determined

### WebSearch not working

- Ensure at least one MCP search server is configured
- Falls back to built-in WebSearch if no MCP servers available
- Check Claude Code is version 2.1.0+

## Requirements

- Claude Code 2.1.0+
- Python 3.x with PyYAML
- At least one MCP search server (recommended)

## Use Cases

- **Academic Research**: Literature reviews, benchmark analysis, paper surveys
- **Technical Research**: Technology comparison, framework evaluation, tool selection
- **Market Research**: Competitor analysis, industry trends, product comparison
- **Due Diligence**: Company research, investment analysis, risk assessment

## License

MIT
