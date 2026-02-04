---
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: Execute complete research lifecycle in one command - from topic to final report. Supports interactive and fully autonomous modes.
---

# Research Auto - Full Lifecycle Automation

## Trigger
`/research-auto <topic>` or `/research-auto <topic> --auto`

## Execution Modes

### Interactive Mode (Default)
- Asks 4 initial questions before starting
- Displays progress at each phase
- Produces final report with summary

### Autonomous Mode (`--auto`)
- Uses sensible defaults for all decisions
- No prompts or confirmations
- Optimized for batch processing and CI/CD pipelines
- Higher throughput with larger batch sizes

**Mode Comparison**:
| Setting | Interactive | Autonomous |
|---------|-------------|------------|
| Initial questions | 4 questions | Skip all |
| Time range | User specified | "last 2 years" |
| Batch size | 3 | 5 |
| Batch approval | N/A (auto) | N/A (auto) |
| TOC fields | Auto-select | Auto-select |
| Error handling | Log and continue | Log and continue |

## Workflow

### Step 0: Parse Arguments
Extract from user command:
- `{topic}`: Research topic (required)
- `{auto_mode}`: True if `--auto` flag present, False otherwise

Generate `{topic_slug}`:
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep alphanumeric and hyphens)
4. Truncate to 64 characters max

### Step 1: Initial Configuration (Interactive Only)

**Interactive Mode**: Use AskUserQuestion to ask 4 questions:

**Question 1 - Research Scope**:
```
What is the scope of this research?
- Comprehensive (thorough coverage of all major items)
- Focused (specific subset or recent developments only)
- Quick overview (top 5-10 most important items)
```

**Question 2 - Time Range**:
```
What time range should the research cover?
- Last 6 months (recent developments)
- Last 1 year
- Last 2 years (Recommended)
- All time (historical perspective)
```

**Question 3 - Research Depth**:
```
What level of detail do you need?
- Brief (key facts only, faster execution)
- Moderate (balanced detail and speed)
- Detailed (comprehensive data, slower execution)
```

**Question 4 - Domain Type** (for intelligent defaults):
```
What type of research is this?
- Technical (software, frameworks, APIs, benchmarks)
- Financial (stocks, companies, markets, valuations)
- Academic (papers, research, citations)
- General (products, services, comparisons)
```

Store responses as:
- `{scope}`: "comprehensive" | "focused" | "quick"
- `{time_range}`: "last 6 months" | "last 1 year" | "last 2 years" | "all time"
- `{depth}`: "brief" | "moderate" | "detailed"
- `{domain}`: "technical" | "financial" | "academic" | "general"

**Autonomous Mode**: Use defaults:
- `{scope}`: "comprehensive"
- `{time_range}`: "last 2 years"
- `{depth}`: "moderate"
- `{domain}`: Auto-detect from topic keywords (see Domain Detection)

### Step 2: Domain Detection (Autonomous Mode)

Auto-detect domain from topic keywords:

**Financial Keywords**: stock, company, market, valuation, investment, equity, earnings, financ, portfolio, dividend, revenue, profit
**Technical Keywords**: software, framework, library, api, benchmark, tool, code, programming, developer, tech, ai, ml, llm
**Academic Keywords**: paper, research, study, journal, citation, academic, science, review, literature

Detection logic:
1. Convert topic to lowercase
2. Check for keyword matches
3. If multiple domains match, use priority: financial > technical > academic > general
4. Default to "general" if no matches

### Step 3: Apply Domain-Specific Defaults

Based on detected/selected domain, configure research parameters:

**Technical Domain**:
```yaml
suggested_fields:
  - github_stars
  - release_date
  - license
  - programming_language
  - swe_bench_score
  - documentation_quality
batch_size: 5
items_per_agent: 1
```

**Financial Domain**:
```yaml
suggested_fields:
  - market_cap
  - pe_ratio
  - revenue
  - profit_margin
  - dividend_yield
  - analyst_rating
batch_size: 3  # Rate limit consideration for financial APIs
items_per_agent: 1
```

**Academic Domain**:
```yaml
suggested_fields:
  - citation_count
  - publication_date
  - journal
  - authors
  - impact_factor
  - methodology
batch_size: 5
items_per_agent: 1
```

**General Domain**:
```yaml
suggested_fields:
  - name
  - release_date
  - company
  - key_features
  - pricing
  - user_rating
batch_size: 5
items_per_agent: 1
```

### Step 4: Phase 1 - Outline Generation

Display progress:
```
## Phase 1/3: Generating Research Outline
Topic: {topic}
Mode: {auto_mode ? "Autonomous" : "Interactive"}
Time Range: {time_range}
Domain: {domain}
```

Execute outline generation internally (equivalent to `/research {topic} --auto`):
1. Generate initial framework from model knowledge
2. Web search for recent items within `{time_range}`
3. Apply domain-specific field suggestions
4. Create `{topic_slug}/outline.yaml` and `{topic_slug}/fields.yaml`

**Outline Generation Process**:

**Parameter Retrieval**:
- `{topic}`: User input research topic
- `{YYYY-MM-DD}`: Current date (retrieve using appropriate method)
- `{time_range}`: From Step 1 configuration
- `{domain}`: From Step 1/2 configuration

**Generate Initial Framework** (Model Knowledge):
Based on topic, generate:
- Items list relevant to the domain
- Field framework using domain-specific suggestions

**Web Search Supplement**:
Launch 1 web-search-agent to supplement items and fields.

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

**Prompt Template**:
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
4. Supplement new fields relevant to {domain} research

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

**Create Output Files**:
Write `{topic_slug}/outline.yaml`:
```yaml
topic: "{topic}"

items:
  - name: "Item 1"
    category: "Category A"
    description: "Brief description"
  # ... more items

execution:
  batch_size: {batch_size}
  items_per_agent: 1
  output_dir: ./results
  auto_mode: true
```

Write `{topic_slug}/fields.yaml`:
```yaml
field_categories:
  - category: "Basic Info"
    fields:
      - name: "name"
        description: "Official name"
        detail_level: "{depth}"
        required: true
      # ... domain-specific fields
```

Log any errors to `{topic_slug}/errors.log` with timestamp.

Display completion:
```
Outline generated: {item_count} items, {field_count} fields
Files: {topic_slug}/outline.yaml, {topic_slug}/fields.yaml
```

### Step 5: Phase 2 - Deep Research Execution

Display progress:
```
## Phase 2/3: Executing Deep Research
Items to research: {item_count}
Batch size: {batch_size}
Estimated batches: {ceil(item_count / batch_size)}
```

Execute deep research internally (equivalent to `/research-deep --auto`):
1. Read outline.yaml and fields.yaml
2. Execute all batches without approval prompts
3. Run validation on each JSON output
4. Log errors but continue on failures

**Batch Execution Loop**:
For each batch of items:
1. Display batch progress: `Processing batch {n}/{total}: {item_names}`
2. Launch web-search-agent for each item in parallel (background)
3. Wait for batch completion
4. Run validation on outputs
5. Log any failures to `{topic_slug}/errors.log`

**Agent Prompt** (same as /research-deep):

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

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

Display batch completion:
```
Batch {n}/{total} complete: {success_count}/{batch_size} successful
```

After all batches:
```
Deep research complete: {completed}/{total} items
Failed items: {failed_count}
Results: {topic_slug}/results/
```

### Step 6: Phase 3 - Report Generation

Display progress:
```
## Phase 3/3: Generating Report
Aggregating {completed} research results...
```

Execute report generation internally (equivalent to `/research-report --auto`):
1. Scan JSON results for summary fields
2. Auto-select top 3-5 most populated metric fields for TOC
3. Generate Python conversion script
4. Execute script to produce report.md

**Auto-Selection Algorithm**:
1. Read all JSON files from results directory
2. For each field, calculate population rate (% with non-null, non-uncertain value)
3. Filter to numeric/metric fields (numbers, dates, scores, versions)
4. Sort by population rate descending
5. Select top 3-5 fields for TOC

**Generate and Execute Script**:
1. Write `{topic_slug}/generate_report.py`
2. Execute: `python {topic_slug}/generate_report.py`
3. Verify `{topic_slug}/report.md` exists and is non-empty

Display completion:
```
Report generated: {topic_slug}/report.md
```

### Step 7: Completion Summary

Display final summary:

```
## Research Complete

### Topic
{topic}

### Execution Mode
{auto_mode ? "Autonomous" : "Interactive"}

### Configuration
- Domain: {domain}
- Time Range: {time_range}
- Depth: {depth}
- Batch Size: {batch_size}

### Results
- Total items researched: {total_items}
- Successful: {completed}
- Failed: {failed}
- Items with uncertain values: {uncertain_count}

### Output Files
- Outline: {topic_slug}/outline.yaml
- Fields: {topic_slug}/fields.yaml
- Results: {topic_slug}/results/ ({json_count} JSON files)
- Report: {topic_slug}/report.md
- Errors: {topic_slug}/errors.log (if any)

### Failed Items (if any)
- Item Name: Error reason
...

### Next Steps
- Review report: cat {topic_slug}/report.md
- Add more items: /research-add-items
- Add more fields: /research-add-fields
- Re-run deep research: /research-deep
```

## Error Handling

All errors are logged to `{topic_slug}/errors.log` with format:
```
[YYYY-MM-DD HH:MM:SS] [PHASE] [SEVERITY] Error message
Item: {item_name} (if applicable)
Details: {error_details}
---
```

**Error Severity Levels**:
- `ERROR`: Task failed but workflow continues
- `FATAL`: Workflow must stop

| Scenario | Severity | Response |
|----------|----------|----------|
| Invalid topic | FATAL | Display error, exit |
| Web search fails | ERROR | Use model knowledge only, continue |
| Agent failure | ERROR | Log, mark item failed, continue |
| Validation failure | ERROR | Log, continue with warnings |
| Script generation fails | ERROR | Log, skip report generation |
| Script execution fails | ERROR | Log, display partial results |
| All items fail | FATAL | Display error summary, exit |

## Domain Detection Keywords

```python
DOMAIN_KEYWORDS = {
    "financial": [
        "stock", "company", "market", "valuation", "investment",
        "equity", "earnings", "financ", "portfolio", "dividend",
        "revenue", "profit", "nasdaq", "nyse", "s&p", "fund",
        "bond", "etf", "ipo", "merger", "acquisition"
    ],
    "technical": [
        "software", "framework", "library", "api", "benchmark",
        "tool", "code", "programming", "developer", "tech",
        "ai", "ml", "llm", "agent", "model", "algorithm",
        "database", "cloud", "devops", "kubernetes", "docker"
    ],
    "academic": [
        "paper", "research", "study", "journal", "citation",
        "academic", "science", "review", "literature", "thesis",
        "dissertation", "arxiv", "peer-review", "methodology"
    ]
}
```

## Output Artifacts

```
{topic_slug}/
  ├── outline.yaml        # Research items and config
  ├── fields.yaml         # Field definitions
  ├── results/            # JSON research results
  │   ├── item_1.json
  │   ├── item_2.json
  │   └── ...
  ├── generate_report.py  # Report generation script
  ├── report.md           # Final markdown report
  └── errors.log          # Error log (if any errors)
```

## Examples

### Interactive Mode
```
> /research-auto AI Coding Assistants

## Initial Configuration

What is the scope of this research?
> Comprehensive

What time range should the research cover?
> Last 2 years

What level of detail do you need?
> Moderate

What type of research is this?
> Technical

## Phase 1/3: Generating Research Outline
...
```

### Autonomous Mode
```
> /research-auto AI Coding Assistants --auto

## Phase 1/3: Generating Research Outline
Topic: AI Coding Assistants
Mode: Autonomous
Time Range: last 2 years
Domain: technical (auto-detected)

Outline generated: 15 items, 12 fields
...

## Phase 2/3: Executing Deep Research
...

## Phase 3/3: Generating Report
...

## Research Complete
...
```

## Related Commands
- `/research` - Generate outline only
- `/research-add-items` - Add items to existing outline
- `/research-add-fields` - Add fields to existing definition
- `/research-deep` - Execute deep research only
- `/research-report` - Generate report only
