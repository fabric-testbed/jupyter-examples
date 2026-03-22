# Testing Guide

How to validate your changes before submitting a pull request.

## Quick Start

Run all checks from the repository root:

```bash
python tests/run_all.py
```

For strict mode (warnings treated as failures):

```bash
python tests/run_all.py --strict
```

---

## Test Scripts Reference

### `tests/validate_notebooks.py` — Notebook Structure

Validates notebooks against the spec in `docs/NOTEBOOK_SPEC.md`.

```bash
# All notebooks (skips public_demos, acceptance_testing, native_api, testing_and_debugging)
python tests/validate_notebooks.py

# Specific notebook(s)
python tests/validate_notebooks.py fabric_examples/fablib_api/hello_fabric/hello_fabric.ipynb

# Strict mode — warnings become failures
python tests/validate_notebooks.py --strict
```

**What it checks:**

| Check | Severity | Description |
|-------|----------|-------------|
| Markdown title cell | ERROR | First cell must be markdown with `# Title` |
| Kernel language | ERROR | Must be Python |
| FABlib import pattern | WARNING | Must use exact `FablibManager as fablib_manager` pattern |
| Cleanup cell | WARNING | `slice.delete()` should exist and be the last code cell |
| Cleared outputs | WARNING | Code cells should have no execution output |
| Step numbering | WARNING | `## Step N:` headers should be sequential |
| Empty code cells | WARNING | No empty code cells |

### `tests/check_links.py` — Internal Link Validation

Validates that all relative links in markdown cells point to existing files.

```bash
# All notebooks
python tests/check_links.py

# Specific notebook(s)
python tests/check_links.py start_here.ipynb
```

**What it checks:**
- Markdown links: `[text](./relative/path.ipynb)`
- Image tags: `<img src="./figs/image.png">`
- Ignores external URLs (http, https, mailto)

### `tests/check_artifacts.py` — Metadata Consistency

Validates `artifacts.json` entries and cross-references with `start_here.ipynb`.

```bash
# Validate existing entries
python tests/check_artifacts.py

# Also flag example directories missing from artifacts.json
python tests/check_artifacts.py --strict
```

**What it checks:**

| Check | Severity | Description |
|-------|----------|-------------|
| Required fields | ERROR | `title`, `description_short`, `location`, `tags`, `visibility`, `authors` |
| Location exists | ERROR | `location` path must be a real directory |
| Duplicate locations | ERROR | No two entries can share the same `location` |
| Valid types | ERROR | `tags` and `authors` must be lists; `visibility` must be "public" or "private" |
| Coverage (strict) | WARNING | Every example directory should have an entry |
| start_here.ipynb links | WARNING | All links in start_here.ipynb should resolve |

### `tests/run_all.py` — Full Suite

Runs all three validators in sequence and reports a pass/fail summary.

```bash
python tests/run_all.py           # Normal mode
python tests/run_all.py --strict  # Strict mode
```

**Exit codes:** `0` = all checks pass, `1` = at least one check failed.

---

## Testing by Change Type

### Adding a New Notebook

Run all three checks — a new notebook needs structure validation, working links, and metadata entries:

```bash
# Validate the notebook structure
python tests/validate_notebooks.py fabric_examples/category/my_example/my_example.ipynb

# Check all links (including any you added to start_here.ipynb)
python tests/check_links.py fabric_examples/category/my_example/my_example.ipynb
python tests/check_links.py start_here.ipynb

# Confirm artifacts.json is valid and complete
python tests/check_artifacts.py --strict
```

**Checklist:**
- [ ] Notebook passes `validate_notebooks.py` with no errors
- [ ] All internal links resolve
- [ ] Entry added to `artifacts.json` with all required fields
- [ ] Link added to `start_here.ipynb` in the correct section
- [ ] Outputs cleared before committing

### Modifying an Existing Notebook

```bash
# Validate the changed notebook
python tests/validate_notebooks.py path/to/modified_notebook.ipynb

# Check links in case you changed any
python tests/check_links.py path/to/modified_notebook.ipynb
```

**Checklist:**
- [ ] Notebook still passes structure validation
- [ ] No new broken links introduced
- [ ] Outputs cleared before committing

### Updating `artifacts.json` or `start_here.ipynb`

```bash
# Validate metadata consistency
python tests/check_artifacts.py

# Check start_here.ipynb links
python tests/check_links.py start_here.ipynb
```

### Changing Test Infrastructure (`tests/`, `docs/`, `.github/`)

```bash
# Run the full suite to make sure nothing broke
python tests/run_all.py
```

---

## Understanding Results

### Errors vs Warnings

- **Errors** are hard failures — the notebook violates a requirement that must be fixed (invalid JSON, wrong kernel, missing title cell).
- **Warnings** are deviations from the spec that should be addressed but won't block existing notebooks. New notebooks should have zero warnings.

### Common Warnings and Fixes

| Warning | Fix |
|---------|-----|
| `Code cells with uncleared output` | Clear outputs: In Jupyter, *Kernel → Restart & Clear Output*, then save |
| `No slice.delete() found` | Add `slice.delete()` as the final code cell with a `## Step N: Delete the Slice` header |
| `slice.delete() should be in the last code cell` | Move the delete call to the very last code cell; remove any empty cells after it |
| `Non-standard FABlib import` | Replace with the exact pattern (see `docs/NOTEBOOK_SPEC.md` Cell 3) |
| `Step numbers not sequential` | Renumber `## Step N:` headers starting from 1 |
| `N empty code cell(s)` | Delete empty code cells (usually at the end of the notebook) |

### Exit Codes

All scripts return `0` on success and `1` on failure. In strict mode, warnings also cause failure.

---

## CI Checks

GitHub Actions (`.github/workflows/checks.yml`) currently runs on every PR:

| Check | Automated | Description |
|-------|-----------|-------------|
| GPG-signed commits | Yes (CI) | All commits must be GPG-signed. Enforced by `1Password/check-signed-commits-action` |
| Notebook structure | **No (local only)** | Run `python tests/validate_notebooks.py` locally |
| Link validation | **No (local only)** | Run `python tests/check_links.py` locally |
| Artifacts consistency | **No (local only)** | Run `python tests/check_artifacts.py` locally |

All test scripts must be run locally before pushing. The CI pipeline enforces commit signing only.

---

## Manual Verification

The automated tests check structure and metadata but cannot verify runtime behavior. For complete verification:

### Notebook Execution
- Run the notebook end-to-end on FABRIC JupyterHub (or a local FABlib environment)
- Confirm that slice creation, experiment execution, and cleanup all succeed
- Verify the notebook works on at least one FABRIC site

### API Reference Links
- Spot-check that `fabric-fablib.readthedocs.io` links in the title cell resolve to the correct documentation page
- API methods may have been renamed or moved between FABlib versions

### Visual Verification
- Open the notebook in Jupyter and confirm images in `figs/` render correctly
- Check that topology diagrams match the actual slice being created
- Verify markdown formatting renders properly (headers, links, code blocks)

### Cross-Reference
- If you added a new example, confirm it appears correctly in:
  - `start_here.ipynb` (link works when clicked in Jupyter)
  - `artifacts.json` (shows up in the artifact manager)
