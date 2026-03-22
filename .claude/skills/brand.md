---
name: brand
description: Apply FABRIC official branding to notebooks — logo headers, brand colors, Montserrat typography, styled callouts, chart palettes
user_invocable: true
---

# /brand — Apply FABRIC Branding to Notebooks

Apply the official FABRIC testbed branding to one or more Jupyter notebooks.

## Input

- **Specific notebook**: `/brand fabric_examples/fablib_api/hello_fabric/hello_fabric.ipynb`
- **Directory**: `/brand fabric_examples/fablib_api/` — brand all notebooks in directory
- **All**: `/brand all` — brand everything (excluding legacy directories)

## What Gets Applied

1. **FABRIC logo header** — branded title cell with the FABRIC wave logo and Montserrat heading
2. **CSS injection** — a code cell that loads Montserrat font and sets brand colors for headings, links, and callout classes
3. **Styled callouts** — converts plain notes/warnings to `<div class="fabric-info/warning/success/danger">` blocks
4. **Section dividers** — gradient `<hr>` elements between major sections using the brand blue
5. **Chart palette** — matplotlib rcParams with FABRIC color cycle (only if notebook has plotting code)
6. **Branded footer** — FABRIC logo + links to portal, knowledge base, and API docs

## FABRIC Brand Colors

| Role | Hex |
|------|-----|
| Primary | `#5798bc` |
| Primary Dark | `#1f6a8c` |
| Primary Light | `#8ac9ef` |
| Dark (headings) | `#374955` |
| Success | `#008e7a` |
| Warning | `#ff8542` |
| Danger | `#b00020` |

**Font**: Montserrat for headings, system-ui for body.

## Workflow

1. Read the target notebook(s)
2. Dispatch the `brand-styler` agent with the notebook path and branding instructions
3. The agent applies branding using NotebookEdit
4. Report what was changed

## Directories to Brand

- `fabric_examples/fablib_api/` — all core examples
- `fabric_examples/complex_recipes/` — all complex recipes
- `fabric_examples/mflib/` — measurement framework examples
- `configure_and_validate/` — setup notebook

## Skip

- `fabric_examples/public_demos/` — legacy workshop materials
- `fabric_examples/acceptance_testing/` — internal test notebooks
- `fabric_examples/beta_functionality/` — beta previews
- `fabric_examples/testing_and_debugging/` — debug utilities

## Examples

```
/brand hello_fabric                    # brand the hello_fabric notebook
/brand fabric_examples/fablib_api/     # brand all fablib_api notebooks
/brand all                             # brand everything
```
