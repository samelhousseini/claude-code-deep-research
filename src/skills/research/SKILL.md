---
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: Conduct preliminary research on a topic and generate research outline. For academic research, benchmark research, technology selection, etc.
---

# Research Skill - Preliminary Research

## Trigger
`/research <topic>` or `/research <topic> --auto`

## Execution Modes

### Interactive Mode (Default)
- User prompted at each decision point
- Full control over items, fields, and time range
- Confirmation before proceeding

### Autonomous Mode (`--auto`)
- Skip all user prompts
- Use sensible defaults (see table below)
- Proceed directly to output

**Autonomous Defaults**:
| Decision | Default Value |
|----------|---------------|
| Items approval | Accept generated list |
| Field framework | Accept suggested framework |
| Time range | "last year" |
| Existing fields | None (skip) |
| batch_size | 5 |
| items_per_agent | 1 |

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{topic}`: Research topic (required)
- `{auto_mode}`: True if `--auto` flag present, False otherwise

### Step 1: Generate Initial Framework from Model Knowledge
Based on topic, use model's existing knowledge to generate:
- Main research objects/items list in this domain
- Suggested research field framework

Output `{step1_output}`:
```
### Items List
1. item_name: Brief description
2. item_name: Brief description
...

### Field Framework
- Category Name: field1, field2, field3
- Category Name: field1, field2
...
```

**Interactive Mode**: Use AskUserQuestion to confirm:
- Need to add/remove items?
- Does field framework meet requirements?

**Autonomous Mode**: Skip confirmation, proceed with generated framework.

### Step 2: Web Search Supplement

**Interactive Mode**: Use AskUserQuestion to ask for time range (e.g., "last 6 months", "since 2024", "unlimited").

**Autonomous Mode**: Use default time range "last year".

**Parameter Retrieval**:
- `{topic}`: User input research topic
- `{YYYY-MM-DD}`: Current date (retrieve using appropriate method)
- `{step1_output}`: Complete output from Step 1
- `{time_range}`: User specified or default time range

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

Launch 1 web-search-agent (background), **Prompt Template**:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
{step1_output}

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for {topic} related items within {time_range} and supplement
4. Supplement new fields

## Output Requirements
Return structured results directly (do not write files):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
"""
```

**One-shot Example** (assuming researching AI Coding History):
```
## Task
Research topic: AI Coding History
Current date: 2025-12-30

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
### Items List
1. GitHub Copilot: Developed by Microsoft/GitHub, first mainstream AI coding assistant
2. Cursor: AI-first IDE, based on VSCode
...

### Field Framework
- Basic Info: name, release_date, company
- Technical Features: underlying_model, context_window
...

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for AI Coding History related items within since 2024 and supplement
4. Supplement new fields

## Output Requirements
Return structured results directly (do not write files):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
```

### Step 3: Ask User for Existing Fields

**Interactive Mode**: Use AskUserQuestion to ask if user has existing field definition file, if so read and merge.

**Autonomous Mode**: Skip this step, use only generated fields.

### Step 4: Generate Outline Files
Merge `{step1_output}`, `{step2_output}` and user's existing fields (if any), generate two files:

**outline.yaml** (items + config):
```yaml
topic: "Research Topic Name"

items:
  - name: "Item 1"
    category: "Category A"
    description: "Brief description"
  - name: "Item 2"
    category: "Category B"
    description: "Brief description"

execution:
  batch_size: 3          # 5 in autonomous mode
  items_per_agent: 1
  output_dir: ./results
  auto_mode: false       # true if --auto flag used
```

**fields.yaml** (field definitions):
```yaml
field_categories:
  - category: "Basic Info"
    fields:
      - name: "name"
        description: "Official name"
        detail_level: "brief"
        required: true
      - name: "release_date"
        description: "Initial release date"
        detail_level: "brief"
        required: true
  - category: "Technical Features"
    fields:
      - name: "underlying_model"
        description: "Base AI model used"
        detail_level: "moderate"
        required: false
```

**Detail Level Hierarchy**: brief -> moderate -> detailed
- `brief`: Single value, short phrase (date, name, version)
- `moderate`: Paragraph, small list (key features, pricing tiers)
- `detailed`: Comprehensive content (full changelog, detailed analysis)

**Interactive Mode**: Use AskUserQuestion to confirm batch_size and items_per_agent values.

**Autonomous Mode**: Use defaults (batch_size: 5, items_per_agent: 1).

### Step 5: Output and Confirm
- Generate topic slug: lowercase, replace spaces with hyphens, remove special characters
- Create directory: `./{topic_slug}/`
- Save: `outline.yaml` and `fields.yaml`
- Display summary to user

**Interactive Mode**: Show files to user for final confirmation.

**Autonomous Mode**: Skip confirmation, display completion summary.

## Output Path
```
{current_working_directory}/{topic_slug}/
  ├── outline.yaml    # items list + execution config
  └── fields.yaml     # field definitions
```

## Slug Generation Rules

**Topic Slug** (for directory):
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)
4. Truncate to 64 characters max

Examples:
- "AI Agent Demo 2025" → `ai-agent-demo-2025`
- "LLM Comparison Study" → `llm-comparison-study`

## Follow-up Commands
- `/research-add-items` - Supplement items
- `/research-add-fields` - Supplement fields
- `/research-deep` - Start deep research
