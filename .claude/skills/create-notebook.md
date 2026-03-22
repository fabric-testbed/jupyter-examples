---
name: create-notebook
description: Scaffold a new FABRIC example notebook with standard structure, artifacts.json entry, and start_here.ipynb link
user_invocable: true
---

# Create a New FABRIC Example Notebook

You are creating a new Jupyter notebook example for the FABRIC testbed jupyter-examples repository.

## Input

The user will provide:
- **Topic**: What FABRIC feature to demonstrate (e.g., "GPU provisioning", "L2 networking", "CephFS storage")
- **Category**: Where it belongs — `fablib_api` (single-feature) or `complex_recipes` (multi-component)
- **Variant**: Optional — `manual`, `auto`, `config` for networking examples

If not provided, ask for the topic. Infer the category from the topic complexity.

## Steps

### 1. Determine directory and naming

- Directory: `fabric_examples/{category}/{topic_snake_case}/`
- Notebook: `{topic_snake_case}.ipynb` (or `{topic_snake_case}_{variant}.ipynb` for variants)
- Create `figs/` subdirectory if the user mentions diagrams

### 2. Create the notebook

Follow the spec in `docs/NOTEBOOK_SPEC.md` exactly. The notebook MUST have these cells in order:

**Cell 1 (markdown)**: Title, description, FABlib API References section with links to `https://fabric-fablib.readthedocs.io/en/latest/`

**Cell 2 (markdown)**: `## Step 1: Configure the Environment` with link to configure_and_validate notebook

**Cell 3 (code)**: FABlib import — use EXACTLY:
```python
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

fablib = fablib_manager()

fablib.show_config();
```

**Cell 4 (markdown + code)**: `## Step 2: Query Resources` with `fablib.list_sites();`

**Cell 5+ (markdown + code)**: Experiment steps — create slice, add nodes/networks/components, submit, execute

**Final cells (markdown + code)**: `## Step N: Delete the Slice` with `slice.delete()`

### 3. Set the slice name as a variable

```python
slice_name = "MyTopicName"
```

Use `fablib.get_random_site()` unless the example requires a specific site/resource.

### 4. Update artifacts.json

Add an entry:
```json
{
    "topic_key": {
        "title": "Human-Readable Title",
        "description_short": "One-line description.",
        "description_long": "",
        "location": "fabric_examples/category/topic_snake_case",
        "tags": ["fabric", "example"],
        "visibility": "public",
        "authors": ["pruth@email.unc.edu"]
    }
}
```

### 5. Update start_here.ipynb

Add a markdown link in the appropriate section of start_here.ipynb:
```markdown
- [Title](./fabric_examples/category/topic/notebook.ipynb): Short description.
```

### 6. Run validation

Run `python tests/validate_notebooks.py` on the new notebook to confirm it passes.

## Key Patterns to Follow

Look at existing examples for reference:
- Simple example: `fabric_examples/fablib_api/hello_fabric/hello_fabric.ipynb`
- Networking: `fabric_examples/fablib_api/create_l2network_basic/create_l2network_basic_auto.ipynb`
- Complex recipe: `fabric_examples/complex_recipes/kubernetes/kubernetes_simple.ipynb`

## Output

Report what was created:
1. Notebook file path
2. artifacts.json entry added
3. start_here.ipynb link added
4. Validation result
