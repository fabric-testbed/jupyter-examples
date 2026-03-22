---
name: fix-notebook
description: Fix a notebook to comply with the project notebook specification
user_invocable: true
---

# Fix Notebook Compliance

Fix one or more notebooks to comply with the project's notebook specification (`docs/NOTEBOOK_SPEC.md`).

## Input

The user provides either:
- A specific notebook path to fix
- A category to fix (e.g., "all fablib_api notebooks")
- "all" to fix everything

## Steps

### 1. Run validation to identify issues

```bash
python tests/validate_notebooks.py [path]
```

### 2. Read the notebook(s) with issues

Use the Read tool to examine each notebook that has errors or warnings.

### 3. Apply fixes

Common fixes to apply:

**Missing H1 title**: Add a markdown cell at the top with `# Title` and description.

**Non-standard FABlib import**: Replace the import cell with the exact standard pattern:
```python
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

fablib = fablib_manager()

fablib.show_config();
```

**Missing slice.delete()**: Add a final markdown cell (`## Step N: Delete the Slice`) and code cell (`slice.delete()`) at the end.

**Uncleared outputs**: Clear all cell outputs. In notebook JSON, set `"outputs": []` and remove `"execution_count"`.

**Non-sequential steps**: Renumber `## Step N:` headers to be sequential starting from 1.

**Empty code cells**: Remove empty code cells at the end of notebooks.

### 4. Re-validate

Run validation again to confirm all issues are resolved.

### 5. Report changes

List every file modified and what was changed.

## Important

- Preserve all existing code logic — only fix structural/formatting issues
- Do not change the notebook's behavior or experiment code
- Keep all existing markdown content, just restructure if needed
- Use NotebookEdit for cell-level changes when possible
