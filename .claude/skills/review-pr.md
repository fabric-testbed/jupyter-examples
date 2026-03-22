---
name: review-pr
description: Full PR review — validate notebooks, check standards compliance, verify metadata, and report findings
user_invocable: true
---

# /review-pr — Full Pull Request Review

Review the current branch's changes (or a specific PR) for readiness to merge.

## Input

- No arguments: review current branch changes vs main
- PR number: `review-pr 123` — review a specific GitHub PR

## Workflow

### 1. Identify Changes

Run `git diff main...HEAD --name-only` to find all changed/added files. Categorize:
- New notebooks
- Modified notebooks
- Metadata changes (artifacts.json, start_here.ipynb)
- Infrastructure changes (tests, docs, CI)

### 2. Dispatch Agents in Parallel

Launch these agents simultaneously using the `Agent` tool:

**Agent: test-runner**
- Run `python tests/run_all.py` on the full repo
- Run targeted validation on changed notebooks

**Agent: notebook-reviewer**
- Review each changed/new notebook against the project spec
- Check FABlib best practices, documentation quality

**Agent: site-auditor** (if notebooks have site references)
- Check changed notebooks for hardcoded sites

### 3. Check Metadata Sync

Verify:
- Every new notebook has an `artifacts.json` entry
- Every new notebook has a `start_here.ipynb` link
- No orphaned entries from deleted notebooks

### 4. Synthesize Review

Combine all agent results into a unified review:

```markdown
## PR Review: {branch_name}

### Overall: PASS / FAIL / NEEDS WORK

### Validation Results
- tests/validate_notebooks.py: PASS/FAIL
- tests/check_links.py: PASS/FAIL
- tests/check_artifacts.py: PASS/FAIL

### Notebook Reviews
For each changed notebook:
- Compliance: PASS/FAIL
- Issues: [list]

### Metadata
- artifacts.json: [in sync / missing entries]
- start_here.ipynb: [in sync / missing links]

### Blocking Issues (must fix before merge)
1. ...

### Suggestions (non-blocking)
1. ...

### Checklist
- [ ] All notebooks pass validation
- [ ] Outputs cleared
- [ ] artifacts.json updated
- [ ] start_here.ipynb updated
- [ ] No hardcoded sites (unless justified)
- [ ] Commits are GPG-signed
```

### 5. Offer to Fix

If issues are found, offer to dispatch the batch-fixer or fix-notebook skill to resolve them.
