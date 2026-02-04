---
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: Execute deep research by launching parallel agents for each item in the outline. Supports batch execution with resume capability.
---

# Research Deep - Deep Research Execution

## Trigger
`/research-deep` or `/research-deep --auto`

## Execution Modes

### Interactive Mode (Default)
- User approval required before each batch
- Can skip or re-order items
- Detailed progress reporting
- Pause on errors for user decision

### Autonomous Mode (`--auto`)
- No batch approval prompts
- Execute all batches continuously
- Higher default batch size (5 vs 3)
- Errors logged but don't halt execution

**Mode Comparison**:
| Setting | Interactive | Autonomous |
|---------|-------------|------------|
| Batch size | 3 | 5 |
| Batch approval | Required | Skipped |
| On error | Ask user | Log and continue |
| Progress display | Detailed | Summary |

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{auto_mode}`: True if `--auto` flag present, False otherwise

### Step 1: Auto-locate Outline
Find `*/outline.yaml` file in current working directory using Glob.

Read from outline.yaml:
- `{topic}`: Research topic
- `{items}`: List of research items
- `{batch_size}`: execution.batch_size (default: 3 interactive, 5 autonomous)
- `{items_per_agent}`: execution.items_per_agent (default: 1)
- `{output_dir}`: execution.output_dir (default: ./results)

Also locate `*/fields.yaml` for field definitions.

**Error Handling**: If outline.yaml not found, inform user:
```
Error: No outline.yaml found in current directory.
Please run /research <topic> first to generate the research outline.
```

### Step 2: Resume Check
- Scan `{output_dir}` for existing JSON files
- Match filenames to item names (slugified: replace spaces with `_`, remove special chars)
- Build list of completed items vs remaining items
- Report: "Found X completed items, Y remaining to research"

**If all items completed**: Display summary and exit.

### Step 3: Batch Execution
Group remaining items into batches of `{batch_size}`.

For each batch:

**Interactive Mode**: Use AskUserQuestion to show items in batch and ask for approval:
```
Ready to research batch N of M:
1. Item Name 1 (Category)
2. Item Name 2 (Category)
...

Proceed with this batch?
- Yes, start research
- Skip this batch
- Modify batch (specify items to skip)
```

**Autonomous Mode**: Skip approval, launch immediately.

**Launch Agents**: For each item in batch, launch `web-search-agent` in background.

**Parameter Retrieval**:
- `{topic}`: topic field from outline.yaml
- `{item_name}`: item's name field
- `{item_related_info}`: item's complete yaml content (name + category + description etc.)
- `{output_dir}`: execution.output_dir from outline.yaml (default: ./results)
- `{fields_path}`: absolute path to {topic_slug}/fields.yaml
- `{output_path}`: absolute path to {output_dir}/{item_name_slug}.json

**Item Name Slug Rules**:
1. Replace spaces with underscores
2. Remove special characters (keep alphanumeric and underscores)
3. Convert to lowercase

Examples:
- "GitHub Copilot" -> `github_copilot.json`
- "Claude 3.5 Sonnet" -> `claude_35_sonnet.json`

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

**Prompt Template**:
```python
prompt = f"""## Task
Research {item_related_info}, output structured JSON to {output_path}

## Field Definitions
Read {fields_path} to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
{output_path}

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
Task is complete only after validation passes.
"""
```

**One-shot Example** (assuming researching GitHub Copilot):
```
## Task
Research name: GitHub Copilot
category: International Product
description: Developed by Microsoft/GitHub, first mainstream AI coding assistant, ~40% market share, output structured JSON to /home/user/ai-coding/results/github_copilot.json

## Field Definitions
Read /home/user/ai-coding/fields.yaml to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
/home/user/ai-coding/results/github_copilot.json

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f /home/user/ai-coding/fields.yaml -j /home/user/ai-coding/results/github_copilot.json
Task is complete only after validation passes.
```

**Agent Launch Configuration**:
- Subagent type: `web-search-agent`
- Run in background: Yes
- Task output display: Disabled (agent writes to explicit output file)

### Step 4: Wait and Monitor
- Wait for current batch agents to complete
- Check each agent's output file exists
- Run validation on completed JSON files
- Display progress: "Batch N complete: X/Y items successful"

**Error Handling**:
- If agent fails: Log error, mark item as failed, continue with batch
- If validation fails: Log validation errors, continue with batch
- **Interactive Mode**: Ask user whether to retry failed items
- **Autonomous Mode**: Log failures, proceed to next batch

### Step 5: Launch Next Batch
Repeat Steps 3-4 for remaining batches until all items processed.

### Step 6: Summary Report
After all items complete, output summary:

```
## Deep Research Complete

### Results
- Total items: {total}
- Completed: {completed}
- Failed: {failed}
- With uncertain values: {uncertain_count}

### Failed Items (if any)
- Item Name: Error reason
...

### Items with Uncertain Fields (if any)
- Item Name: [field1, field2, ...]
...

### Output Location
Results saved to: {output_dir}/

### Next Steps
Run /research-report to generate the final markdown report.
```

## Error Handling

| Scenario | Interactive Response | Autonomous Response |
|----------|---------------------|---------------------|
| No outline.yaml | Error message, exit | Error message, exit |
| No fields.yaml | Error message, exit | Error message, exit |
| Agent failure | Ask retry/skip | Log, continue |
| Validation failure | Show errors, ask retry | Log, continue |
| Network timeout | Retry with backoff | Retry with backoff |
| User interrupt | Save progress, exit | Save progress, exit |

## Agent Configuration

| Setting | Value |
|---------|-------|
| Background execution | Yes |
| Task Output display | Disabled |
| Resume support | Yes |
| Timeout | 5 minutes per agent |

## Output Artifacts

```
{topic_slug}/
  ├── outline.yaml      # Input (items list)
  ├── fields.yaml       # Input (field definitions)
  └── results/          # Output directory
      ├── item_1.json
      ├── item_2.json
      └── ...
```

## JSON Output Format

Each agent produces a JSON file following fields.yaml schema:

```json
{
  "basic_info": {
    "name": "Item Name",
    "release_date": "2024-01-15",
    "company": "Company Name"
  },
  "technical_features": {
    "underlying_model": "GPT-4",
    "context_window": "128k tokens"
  },
  "performance_metrics": {
    "benchmark_score": "[uncertain]"
  },
  "uncertain": ["benchmark_score", "monthly_active_users"]
}
```

## Follow-up Commands
- `/research-report` - Generate markdown report from JSON results
- `/research-add-items` - Add more items and re-run deep research
