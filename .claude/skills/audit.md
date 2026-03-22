---
name: audit
description: Full repository audit — validation, site checks, coverage gaps, metadata consistency, and documentation quality
user_invocable: true
---

# /audit — Full Repository Audit

Run a comprehensive audit of the entire jupyter-examples repository.

## Input

- No arguments: audit everything
- Category: `/audit fablib_api` — audit only that category
- Specific check: `/audit sites` — run only site auditing

## Workflow

### 1. Dispatch Agents in Parallel

Launch all audit agents simultaneously using the `Agent` tool:

**Agent: test-runner**
- Run `python tests/run_all.py` for full validation
- Run `python tests/check_artifacts.py --strict` for strict metadata checks

**Agent: site-auditor**
- Scan all notebooks for hardcoded sites
- Check for stale site names
- Verify get_random_site() usage

**Agent: example-finder**
- Scan the full example inventory
- Identify coverage gaps (FABRIC features without examples)
- Check for outdated examples

### 2. Collect and Synthesize

Combine all agent results into a comprehensive audit report:

```markdown
## Repository Audit Report

### Executive Summary
- Total notebooks: N
- Passing validation: X / N
- Errors: E | Warnings: W
- Hardcoded sites: H
- Metadata gaps: M

### Validation Results
[From test-runner]
- Structure errors: ...
- Link errors: ...
- Artifact consistency: ...

### Site Audit
[From site-auditor]
- Notebooks with hardcoded sites: ...
- Stale site references: ...
- Missing get_random_site(): ...

### Coverage Analysis
[From example-finder]
- FABRIC features with examples: ...
- FABRIC features missing examples: ...
- Outdated examples: ...

### Metadata Consistency
- artifacts.json orphans: ...
- start_here.ipynb broken links: ...
- Missing entries: ...

### Top Issues (prioritized)
1. [Most impactful issue]
2. [Second most impactful]
...

### Recommended Actions
1. Run `/fix-notebook` to fix N structural issues
2. Run `/sync-index` to fix M metadata gaps
3. Update N notebooks to use get_random_site()
```

### 3. Offer Remediation

Based on findings, suggest which skills/agents to run:
- `/fix-notebook` for structural issues
- `/sync-index` for metadata gaps
- `batch-fixer` agent for bulk changes
- `site-auditor` recommendations for manual site fixes
