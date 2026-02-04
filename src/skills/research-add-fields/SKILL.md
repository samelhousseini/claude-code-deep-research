---
user-invocable: true
description: Add field definitions to existing research outline.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Fields - Supplement Research Fields

## Trigger
`/research-add-fields` or `/research-add-fields --auto`

## Execution Modes

### Interactive Mode (Default)
- User provides field definitions manually and/or triggers web search
- User confirms which fields to add before saving
- User assigns category, detail_level, required status

### Autonomous Mode (`--auto`)
- Automatically trigger web search for common fields in the domain
- Add all discovered fields without confirmation
- Use intelligent defaults for category, detail_level, required

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{auto_mode}`: True if `--auto` flag present, False otherwise

### Step 1: Auto-locate Fields File

Use `Glob` tool to find `*/fields.yaml` file in current working directory.

Read the file to extract:
- `{topic}`: Research topic (inferred from directory or outline.yaml)
- `{existing_fields}`: Current field definitions list
- `{field_categories}`: Existing category structure

**Error Handling**: If no `fields.yaml` found, inform user:
> "No fields.yaml found. Please run `/research <topic>` first to create a research outline."

### Step 2: Get Supplement Sources

**Interactive Mode**: Simultaneously ask two questions using AskUserQuestion:

**A. Direct Input**:
- "What fields would you like to add? (Enter field names with descriptions, separated by semicolons, or leave empty)"
- Example format: "pricing: Product pricing tiers; user_count: Number of active users"

**B. Web Search**:
- "Would you like to search the web for common research fields related to '{topic}'?"
- Options: "Yes, search for more" / "No, just use my input"

**Autonomous Mode**: Skip user questions, proceed directly to web search.

### Step 3: Web Search (If Requested or Autonomous)

If user selected web search OR in autonomous mode, launch `web-search-agent`.

**Parameter Retrieval**:
- `{topic}`: Research topic from fields.yaml or outline.yaml
- `{YYYY-MM-DD}`: Current date (retrieve using appropriate method)
- `{existing_fields_list}`: Formatted list of existing field names

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

Launch 1 web-search-agent (background), **Prompt Template**:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}

Find additional research fields commonly used for analyzing this domain that are not in the existing list.

## Existing Fields
{existing_fields_list}

## Goals
1. Search for common research dimensions/metrics used to evaluate {topic}
2. Focus on fields that are widely documented and useful for comparison
3. Consider both quantitative (metrics, numbers) and qualitative (descriptions, features) fields
4. Prioritize fields that differentiate items in this domain

## Output Requirements
Return new fields only (not in existing list):

### New Fields
- field_name: Field description (why this dimension is useful)
  - Suggested category: [category name]
  - Detail level: [brief|moderate|detailed]
  - Required: [yes|no]
...

### Sources
- [Source1](url1)
- [Source2](url2)
"""
```

**One-shot Example** (assuming researching AI Coding Tools):
```
## Task
Research topic: AI Coding Tools
Current date: 2025-12-30

Find additional research fields commonly used for analyzing this domain that are not in the existing list.

## Existing Fields
1. name: Official name
2. release_date: Initial release date
3. company: Developing company
4. underlying_model: Base AI model used

## Goals
1. Search for common research dimensions/metrics used to evaluate AI Coding Tools
2. Focus on fields that are widely documented and useful for comparison
3. Consider both quantitative (metrics, numbers) and qualitative (descriptions, features) fields
4. Prioritize fields that differentiate items in this domain

## Output Requirements
Return new fields only (not in existing list):

### New Fields
- field_name: Field description (why this dimension is useful)
  - Suggested category: [category name]
  - Detail level: [brief|moderate|detailed]
  - Required: [yes|no]
...

### Sources
- [Source1](url1)
- [Source2](url2)
```

### Step 4: Merge and Deduplicate

Combine fields from:
1. User-provided fields (if any)
2. Web search results (if performed)

**Deduplication Logic**:
- Compare new field names against existing fields (case-insensitive)
- Normalize field names (snake_case, lowercase)
- Remove any duplicates
- Track which fields are new vs. duplicates

**Autonomous Default Assignments**:
If detail_level or required not specified:
- Fields with "date", "name", "version", "count" → detail_level: brief
- Fields with "features", "comparison", "analysis" → detail_level: moderate
- Fields with "history", "documentation", "changelog" → detail_level: detailed
- First 5 fields → required: true, rest → required: false

### Step 5: Confirm and Save

**Interactive Mode**:
Display the proposed additions using AskUserQuestion:

```
Found {n} new fields to add:

From your input:
1. {field_name}: {description}
   Category: {category}, Level: {detail_level}, Required: {required}
...

From web search:
1. {field_name}: {description}
   Category: {category}, Level: {detail_level}, Required: {required}
...

Skipped {m} duplicates.

Would you like to modify any field assignments?
```

Options:
- "Add all fields as shown" (default)
- "Modify field assignments"
- "Select specific fields"
- "Cancel"

If "Modify field assignments", allow user to change category, detail_level, or required for specific fields.

**Autonomous Mode**:
- Add all new fields automatically with intelligent defaults
- Display summary: "Added {n} fields, skipped {m} duplicates"

### Step 6: Update Fields File

- Add new fields to appropriate categories in `fields.yaml`
- Create new categories if necessary
- Preserve all existing fields and structure
- Write updated file back to same location

**YAML Format Example**:
```yaml
field_categories:
  # Existing category preserved
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
  # Fields added to existing category
  - category: "Technical Features"
    fields:
      - name: "underlying_model"
        description: "Base AI model used"
        detail_level: "moderate"
        required: false
      # New field appended
      - name: "context_window"
        description: "Maximum context window size"
        detail_level: "brief"
        required: false
  # New category created
  - category: "Pricing"
    fields:
      - name: "pricing_model"
        description: "Subscription, usage-based, or free"
        detail_level: "moderate"
        required: true
```

## Output

Updated `{topic_slug}/fields.yaml` file (in-place modification)

**Summary Output**:
```
Updated fields for "{topic}":
- Previous fields: {old_count}
- Added fields: {new_count}
- Total fields: {total_count}
- Duplicates skipped: {duplicate_count}
- New categories created: {new_categories}

File: {path}/fields.yaml
```

## Detail Level Guidelines

| Level | Description | Examples |
|-------|-------------|----------|
| brief | Single value, short phrase | date, name, version, count |
| moderate | Paragraph, small list | features list, pricing tiers, key capabilities |
| detailed | Comprehensive content | full changelog, detailed analysis, documentation |

## Error Handling

| Error | Message |
|-------|---------|
| No fields file found | "No fields.yaml found. Run `/research <topic>` first." |
| Invalid YAML | "Could not parse fields.yaml. Please check file format." |
| Web search fails | "Web search failed. Fields from user input will still be added." |
| All duplicates | "All proposed fields already exist in the field definitions." |

## Follow-up Commands
- `/research-add-items` - Add more research items
- `/research-deep` - Start deep research on all items
- `/research` - Create new research outline for different topic
