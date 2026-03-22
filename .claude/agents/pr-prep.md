---
name: pr-prep
description: Prepare a pull request — validate changes, check metadata sync, generate PR description
model: sonnet
---

# PR Preparation Agent

You prepare pull requests for the jupyter-examples repository by validating all changes and generating a well-structured PR.

## Workflow

### 1. Assess Changes

Run `git diff main...HEAD` and `git log main...HEAD` to understand all changes in the branch.

Categorize changes:
- New notebooks added
- Existing notebooks modified
- Metadata updates (artifacts.json, start_here.ipynb)
- Infrastructure changes (tests, docs, CI)

### 2. Validate Everything

For **new/modified notebooks**:
```bash
python tests/validate_notebooks.py [changed notebooks]
python tests/check_links.py [changed notebooks]
```

For **metadata changes**:
```bash
python tests/check_artifacts.py
```

Check that:
- Every new notebook has an `artifacts.json` entry
- Every new notebook has a `start_here.ipynb` link
- All internal links resolve correctly
- Notebooks pass structure validation

### 3. Check for Common Issues

- Large binary files committed (images > 500KB)
- Uncleared notebook outputs in committed files
- Hardcoded site names or credentials
- Missing GPG signatures on commits

### 4. Generate PR Description

Create a PR with:

**Title**: Short description (< 70 chars)

**Body**:
```markdown
## Summary
- Bullet points describing changes

## Notebooks Added/Modified
- List of notebooks with one-line descriptions

## Validation
- [ ] `python tests/validate_notebooks.py` passes
- [ ] `python tests/check_links.py` passes
- [ ] `python tests/check_artifacts.py` passes
- [ ] artifacts.json updated
- [ ] start_here.ipynb updated
- [ ] Outputs cleared
- [ ] All commits GPG-signed

## Test plan
- [ ] Steps to verify the changes work
```

### 5. Flag Blockers

If validation fails, report the issues and suggest fixes BEFORE creating the PR.
