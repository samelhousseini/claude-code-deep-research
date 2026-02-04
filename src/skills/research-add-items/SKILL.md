---
user-invocable: true
description: Add items (research objects) to existing research outline.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Items - Supplement Research Objects

## Trigger
`/research-add-items` or `/research-add-items --auto`

## Execution Modes

### Interactive Mode (Default)
- User provides items manually and/or triggers web search
- User confirms which items to add before saving

### Autonomous Mode (`--auto`)
- Automatically trigger web search for more items
- Add all discovered items without confirmation
- Skip duplicates automatically

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{auto_mode}`: True if `--auto` flag present, False otherwise

### Step 1: Auto-locate Outline

Use `Glob` tool to find `*/outline.yaml` file in current working directory.

Read the file to extract:
- `{topic}`: Research topic name
- `{existing_items}`: Current items list
- `{execution_config}`: Existing execution configuration

**Error Handling**: If no `outline.yaml` found, inform user:
> "No outline.yaml found. Please run `/research <topic>` first to create a research outline."

### Step 2: Get Supplement Sources

**Interactive Mode**: Simultaneously ask two questions using AskUserQuestion:

**A. Direct Input**:
- "What items would you like to add? (Enter item names, separated by commas, or leave empty)"

**B. Web Search**:
- "Would you like to search the web for more items related to '{topic}'?"
- Options: "Yes, search for more" / "No, just use my input"

**Autonomous Mode**: Skip user questions, proceed directly to web search.

### Step 3: Web Search (If Requested or Autonomous)

If user selected web search OR in autonomous mode, launch `web-search-agent`.

**Parameter Retrieval**:
- `{topic}`: Research topic from outline.yaml
- `{YYYY-MM-DD}`: Current date (retrieve using appropriate method)
- `{existing_items_list}`: Formatted list of existing item names

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

Launch 1 web-search-agent (background), **Prompt Template**:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}

Find additional items for this research that are not in the existing list.

## Existing Items
{existing_items_list}

## Goals
1. Search for items related to {topic} not already in the list
2. Focus on notable, well-documented items
3. Prioritize recent additions to the field

## Output Requirements
Return new items only (not in existing list):

### New Items
- item_name: Brief explanation (why it should be added)
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

Find additional items for this research that are not in the existing list.

## Existing Items
1. GitHub Copilot
2. Cursor
3. Cody
4. Tabnine

## Goals
1. Search for items related to AI Coding Tools not already in the list
2. Focus on notable, well-documented items
3. Prioritize recent additions to the field

## Output Requirements
Return new items only (not in existing list):

### New Items
- item_name: Brief explanation (why it should be added)
...

### Sources
- [Source1](url1)
- [Source2](url2)
```

### Step 4: Merge and Deduplicate

Combine items from:
1. User-provided items (if any)
2. Web search results (if performed)

**Deduplication Logic**:
- Compare new item names against existing items (case-insensitive)
- Remove any duplicates
- Track which items are new vs. duplicates

Format new items as objects:
```yaml
- name: "Item Name"
  category: "Uncategorized"  # Default, user can update later
  description: "Brief description"
```

### Step 5: Confirm and Save

**Interactive Mode**:
Display the proposed additions using AskUserQuestion:

```
Found {n} new items to add:

From your input:
1. {item_name}: {description}
...

From web search:
1. {item_name}: {description}
...

Skipped {m} duplicates.

Which items would you like to add?
```

Options:
- "Add all items" (default)
- "Select specific items"
- "Cancel"

If "Select specific items", present checkbox list of items.

**Autonomous Mode**:
- Add all new items automatically
- Display summary: "Added {n} items, skipped {m} duplicates"

### Step 6: Update Outline

- Append confirmed items to the `items` list in `outline.yaml`
- Preserve all existing fields (topic, execution config, etc.)
- Write updated file back to same location

**YAML Format Example**:
```yaml
topic: "Research Topic"

items:
  # Existing items preserved
  - name: "Existing Item 1"
    category: "Category A"
    description: "Description"
  # New items appended
  - name: "New Item 1"
    category: "Uncategorized"
    description: "Brief description from search"

execution:
  batch_size: 5
  items_per_agent: 1
  output_dir: ./results
```

## Output

Updated `{topic_slug}/outline.yaml` file (in-place modification)

**Summary Output**:
```
Updated outline for "{topic}":
- Previous items: {old_count}
- Added items: {new_count}
- Total items: {total_count}
- Duplicates skipped: {duplicate_count}

File: {path}/outline.yaml
```

## Error Handling

| Error | Message |
|-------|---------|
| No outline found | "No outline.yaml found. Run `/research <topic>` first." |
| Invalid YAML | "Could not parse outline.yaml. Please check file format." |
| Web search fails | "Web search failed. Items from user input will still be added." |
| All duplicates | "All proposed items already exist in the outline." |

## Follow-up Commands
- `/research-add-fields` - Add more research fields
- `/research-deep` - Start deep research on all items
- `/research` - Create new research outline for different topic
