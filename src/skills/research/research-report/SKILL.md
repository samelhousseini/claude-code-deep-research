---
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, AskUserQuestion
description: Generate markdown report from deep research JSON results. Supports TOC summary field selection and handles complex data structures.
---

# Research Report - Summary Report Generation

## Trigger
`/research-report` or `/research-report --auto`

## Execution Modes

### Interactive Mode (Default)
- User selects which fields appear in TOC summary
- Detailed feedback during generation

### Autonomous Mode (`--auto`)
- Automatically select top 3-5 most populated numeric/metric fields for TOC
- No user prompts

**Auto-Selection Algorithm**:
1. Scan all JSON results for field presence
2. Filter to numeric/short metric fields (numbers, dates, scores, versions)
3. Rank by population rate (% of items with non-null, non-uncertain value)
4. Select top 3-5 fields

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{auto_mode}`: True if `--auto` flag present, False otherwise

### Step 1: Locate Results Directory
Find `*/outline.yaml` in current working directory using Glob.

Read from outline.yaml:
- `{topic}`: Research topic
- `{items}`: List of research items
- `{output_dir}`: execution.output_dir (default: ./results)

Also locate `*/fields.yaml` for field definitions.

Scan `{output_dir}` for all JSON result files.

**Error Handling**: If outline.yaml not found:
```
Error: No outline.yaml found in current directory.
Please run /research <topic> first to generate the research outline.
```

If no JSON files found:
```
Error: No research results found in {output_dir}/.
Please run /research-deep first to execute deep research.
```

### Step 2: Scan for Summary Fields
Read all JSON results and identify fields suitable for TOC display:
- Numeric values (stars, scores, citations, counts)
- Short metrics (dates, versions, percentages)
- Key identifiers (company, type)

**Field Analysis**:
For each field across all JSON files:
1. Count how many items have this field
2. Identify if value is numeric/date/short metric
3. Calculate population rate (items with value / total items)

**Interactive Mode**: Use AskUserQuestion:
```
Which fields should appear in the TOC summary?
(Select 3-5 fields for best readability)

Available fields (sorted by population rate):
- github_stars (95% populated)
- release_date (90% populated)
- swe_bench_score (80% populated)
- company (100% populated)
- user_scale (70% populated)
```

Allow multi-select with header "TOC Fields".

**Autonomous Mode**: Auto-select top 3-5 fields by:
1. Filter to numeric/metric fields
2. Sort by population rate descending
3. Take top 3-5 (prefer 4-5 if many highly-populated fields)

### Step 3: Generate Python Conversion Script
Generate `generate_report.py` in `{topic_slug}/` directory.

**Script Requirements**:

1. **Read inputs**:
   - All JSON files from output_dir
   - fields.yaml for field structure

2. **Generate markdown report** with:
   - Title with topic name
   - Generation timestamp
   - Total items count
   - Table of Contents with anchor links and summary fields
   - Detailed sections for each item organized by category

3. **Save to** `{topic_slug}/report.md`

**TOC Format**:
```markdown
## Table of Contents

1. [GitHub Copilot](#github-copilot) - Stars: 10k | Score: 85%
2. [Cursor](#cursor) - Stars: 25k | Score: 92%
...
```

#### Script Technical Requirements (Must Follow)

**1. JSON Structure Compatibility**
Support two JSON structures:
- Flat structure: Fields directly at top level `{"name": "xxx", "release_date": "xxx"}`
- Nested structure: Fields in category sub-dict `{"basic_info": {"name": "xxx"}, "technical_features": {...}}`

Field lookup order: Top level -> category mapping key -> Traverse all nested dicts

**2. Category Multi-language Mapping**
fields.yaml category names and JSON keys can use different naming conventions. Establish bidirectional mapping:
```python
CATEGORY_MAPPING = {
    "Basic Info": ["basic_info", "Basic Info"],
    "Technical Features": ["technical_features", "technical_characteristics", "Technical Features"],
    "Performance Metrics": ["performance_metrics", "performance", "Performance Metrics"],
    "Milestone Significance": ["milestone_significance", "milestones", "Milestone Significance"],
    "Business Info": ["business_info", "commercial_info", "Business Info"],
    "Competition & Ecosystem": ["competition_ecosystem", "competition", "Competition & Ecosystem"],
    "History": ["history", "History"],
    "Market Positioning": ["market_positioning", "market", "Market Positioning"],
}
```

**3. Complex Value Formatting**
- **List of dicts** (e.g., key_events, funding_history): Format each dict as one line, separate kv with ` | `
- **Normal list**: Short lists joined with comma, long lists displayed with line breaks
- **Nested dict**: Recursive formatting, display with semicolon or line breaks
- **Long text strings** (over 100 chars): Add line breaks `<br>` or use blockquote format for readability

**4. Extra Fields Collection**
Collect fields that exist in JSON but not defined in fields.yaml, put in "Other Info" category.
Filter out internal fields:
- `_source_file`
- `uncertain`
- Top-level category keys: `basic_info`, `technical_features`, etc.

Display `uncertain` array contents: list each field name on separate line.

**5. Uncertain Value Skipping**
Skip field display if:
- Field value contains `[uncertain]` string
- Field name is in `uncertain` array
- Field value is None or empty string

**6. Anchor Link Generation**
Convert item name to anchor:
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)

Examples:
- "GitHub Copilot" -> `#github-copilot`
- "Claude 3.5 Sonnet" -> `#claude-35-sonnet`

### Step 4: Execute Script
Run: `python {topic_slug}/generate_report.py`

Verify:
- Script exits with code 0
- `{topic_slug}/report.md` exists
- Report file is non-empty

**Error Handling**:
- If script fails: Display error message, provide troubleshooting hints
- If report empty: Warn user, check JSON files for issues

### Step 5: Summary
Display completion message:
```
## Report Generated

Report saved to: {topic_slug}/report.md

Summary:
- Total items: {count}
- Items with data: {data_count}
- TOC summary fields: {field_list}

Next steps:
- Open report.md to review the research summary
- Run /research-add-items to add more items if needed
```

## Error Handling

| Scenario | Response |
|----------|----------|
| No outline.yaml | Error message, suggest running /research first |
| No fields.yaml | Error message, suggest running /research first |
| No JSON results | Error message, suggest running /research-deep first |
| Script generation fails | Display error, ask user to check permissions |
| Script execution fails | Display Python error, check YAML/JSON syntax |
| Empty report | Warn user, check JSON files for content |

## Output Artifacts

```
{topic_slug}/
  ├── outline.yaml        # Input (unchanged)
  ├── fields.yaml         # Input (unchanged)
  ├── results/            # Input (unchanged)
  │   └── *.json
  ├── generate_report.py  # Generated conversion script
  └── report.md           # Final markdown report
```

## Report Structure

```markdown
# {Topic} Research Report

Generated: {date}
Total Items: {count}

## Table of Contents

1. [Item 1](#item-1) - {summary_fields}
2. [Item 2](#item-2) - {summary_fields}
...

---

## Item 1

### Basic Info
- **Name**: Item 1
- **Release Date**: 2024-01-15
- **Company**: Example Corp

### Technical Features
- **Model**: GPT-4
- **Context Window**: 128k tokens

### Performance Metrics
- **Benchmark Score**: 92%

### Sources
- [Source 1](url1)
- [Source 2](url2)

### Other Info
- **Extra Field**: Value not in schema

---

## Item 2
...
```

## Follow-up Commands
- `/research-add-items` - Add more items and re-run research
- `/research-add-fields` - Add more fields and re-research
- `/research-auto` - Run full lifecycle again with new topic
