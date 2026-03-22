---
name: sync-index
description: Synchronize start_here.ipynb and artifacts.json with the actual directory contents
user_invocable: true
---

# Synchronize Index Files

Ensure `start_here.ipynb` and `artifacts.json` are consistent with the actual notebook directories.

## Steps

### 1. Scan the repository

Find all example directories containing notebooks:
```
fabric_examples/fablib_api/*/
fabric_examples/complex_recipes/*/
fabric_examples/mflib/*/
configure_and_validate/
```

### 2. Check artifacts.json

For each example directory:
- Verify it has an entry in `artifacts.json`
- Verify the entry's `location` field matches the actual path
- Verify the `title` and `description_short` are populated
- Flag any artifacts.json entries pointing to non-existent directories

### 3. Check start_here.ipynb

For each example directory:
- Verify it has a link in `start_here.ipynb`
- Verify the link path is correct
- Flag any links pointing to non-existent notebooks

### 4. Report discrepancies

Present a table of:
- Directories missing from `artifacts.json`
- Directories missing from `start_here.ipynb`
- Orphaned entries (point to deleted directories)
- Mismatched paths

### 5. Apply fixes (with user confirmation)

- Add missing `artifacts.json` entries (prompt user for title/description)
- Add missing `start_here.ipynb` links in the appropriate section
- Remove orphaned entries
- Fix incorrect paths

### 6. Validate

Run `python tests/check_artifacts.py --strict` to confirm everything is in sync.
