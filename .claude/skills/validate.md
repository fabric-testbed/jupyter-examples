---
name: validate
description: Run all validation checks on notebooks — structure, links, and artifacts consistency
user_invocable: true
---

# Validate Notebooks

Run the full validation suite for the jupyter-examples repository.

## Steps

### 1. Run all validators

Execute the test suite:

```bash
python tests/run_all.py
```

### 2. If specific notebooks are mentioned

Run targeted validation:
```bash
python tests/validate_notebooks.py path/to/notebook.ipynb
python tests/check_links.py path/to/notebook.ipynb
```

### 3. Interpret results

- **Errors** are violations that must be fixed (missing title cell, invalid JSON, wrong kernel)
- **Warnings** are spec deviations that should be addressed (uncleared outputs, missing cleanup cell, non-sequential steps)

### 4. Summarize findings

Group issues by category:
- Structure issues (cell ordering, missing sections)
- Link issues (broken internal links, missing images)
- Metadata issues (artifacts.json gaps, start_here.ipynb mismatches)

For each issue, suggest the specific fix needed.

### 5. Optional: strict mode

If the user wants strict validation:
```bash
python tests/run_all.py --strict
```
This treats warnings as failures.
