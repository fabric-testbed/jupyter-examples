# Notebook Specification

This document defines the required structure, conventions, and quality standards for all Jupyter notebooks in this repository.

## Cell Structure

Every notebook MUST follow this cell ordering:

### Cell 1: Branded Title and Description (Markdown)

```html
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
<img src="https://www.dropbox.com/s/26lsgihw277bfgm/2019_NRIG_FABRIC%20logo%20Dark.png?raw=1" width="200" style="margin-right: 1.5rem;" />
<div>

# Title: Descriptive Name of the Example

Brief description of what this notebook demonstrates and why it's useful.

</div>
</div>

<hr class="fabric-divider" />

### FABlib API References

- [fablib.method_name](https://fabric-fablib.readthedocs.io/en/latest/...)
- [slice.method_name](https://fabric-fablib.readthedocs.io/en/latest/...)
```

**Requirements**:
- FABRIC logo header using the branded `<div>` layout shown above
- H1 header with descriptive title
- 1-3 sentence description of the notebook's purpose
- Brand divider (`<hr class="fabric-divider" />`) after the header block
- API References section linking to every FABlib method used in the notebook
- Links must use the format: `https://fabric-fablib.readthedocs.io/en/latest/{module}.html`

### Cell 2: Environment Setup Reference (Markdown)

```markdown
## Step 1: Configure the Environment

Before running this notebook, you will need to configure your environment using the
[Configure Environment](../../../configure_and_validate/configure_and_validate.ipynb) notebook.
```

**Requirements**:
- Reference to configure_and_validate notebook (relative path)
- Brief mention of JupyterHub auto-configuration

### Cell 3: FABlib Import (Code)

```python
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

fablib = fablib_manager()

fablib.show_config();
```

**Requirements**:
- MUST use exactly this import pattern — no variations
- MUST include `fablib.show_config();` with trailing semicolon
- Variable MUST be named `fablib`

### Cell 3b: FABRIC Brand Styling (Code)

```python
from IPython.display import HTML, display
display(HTML("""<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
h1, h2, h3, h4, h5, h6 { font-family: 'Montserrat', sans-serif; }
h1 { color: #374955; border-bottom: 3px solid #5798bc; padding-bottom: 0.5rem; }
h2 { color: #1f6a8c; }
h3, h4 { color: #477595; }
a { color: #1f6a8c; }
a:hover { color: #8ac9ef; }
.fabric-info { background: #e4f4f8; border-left: 4px solid #5798bc; padding: 1rem; margin: 1rem 0; border-radius: 4px; font-family: system-ui; }
.fabric-warning { background: #fff3e6; border-left: 4px solid #ff8542; padding: 1rem; margin: 1rem 0; border-radius: 4px; font-family: system-ui; }
.fabric-success { background: #e6f7f4; border-left: 4px solid #008e7a; padding: 1rem; margin: 1rem 0; border-radius: 4px; font-family: system-ui; }
.fabric-danger { background: #fde8ec; border-left: 4px solid #b00020; padding: 1rem; margin: 1rem 0; border-radius: 4px; font-family: system-ui; }
.fabric-divider { border: none; height: 2px; background: linear-gradient(to right, transparent, #5798bc, transparent); margin: 2rem 0; }
</style>"""))
```

**Requirements**:
- MUST appear immediately after the FABlib import cell
- MUST include all brand CSS classes (fabric-info, fabric-warning, fabric-success, fabric-danger, fabric-divider)
- Loads Montserrat font from Google Fonts for headings

### Cell 4+: Optional Resource Query (Code)

```python
fablib.list_sites();
```

**Requirements**:
- Trailing semicolon to suppress output
- Optional but recommended for examples that target specific sites

### Experiment Cells: Topology and Execution

**Slice name variable**:
```python
slice_name = "MyExperiment"
```

**Topology construction**:
```python
slice = fablib.new_slice(name=slice_name)
node = slice.add_node(name="Node1", site="RENC")
# ... add components, networks
slice.submit();
```

**Experiment execution**:
```python
slice = fablib.get_slice(name=slice_name)
node = slice.get_node(name="Node1")
stdout, stderr = node.execute("command")
```

**Requirements**:
- Each step has a markdown header cell above it: `## Step N: Description`
- Slice name defined as a variable, not hardcoded in `new_slice()`
- Use `fablib.get_random_site()` unless the example requires a specific site
- Retrieve slice by name before executing commands (allows running cells independently)

### Pre-Cleanup Cell: Branded Footer (Markdown)

```html
<hr class="fabric-divider" />

<div style="display: flex; align-items: center; padding: 1rem 0; color: #838385; font-family: system-ui; font-size: 0.9rem;">
<img src="https://www.dropbox.com/s/26lsgihw277bfgm/2019_NRIG_FABRIC%20logo%20Dark.png?raw=1" width="120" style="margin-right: 1rem; opacity: 0.7;" />
<div>
This notebook is part of the <a href="https://github.com/fabric-testbed/jupyter-examples" style="color: #1f6a8c;">FABRIC Jupyter Examples</a> collection.<br/>
Learn more at <a href="https://fabric-testbed.net" style="color: #1f6a8c;">fabric-testbed.net</a> |
<a href="https://learn.fabric-testbed.net" style="color: #1f6a8c;">Knowledge Base</a> |
<a href="https://fabric-fablib.readthedocs.io" style="color: #1f6a8c;">FABlib API Docs</a>
</div>
</div>
```

**Requirements**:
- MUST appear before the cleanup cell
- Includes FABRIC logo (small, dimmed), links to portal, knowledge base, and API docs
- Uses brand divider to separate from experiment content

### Final Cell: Cleanup (Code)

```python
slice.delete()
```

**Requirements**:
- MUST be the last code cell
- MUST have a markdown header: `## Step N: Delete the Slice`
- Include reminder text: "Please delete your slice when you are done with your experiment."

## Markdown Standards

### Headers
- `#` H1: Notebook title only (one per notebook)
- `##` H2: Major steps (`## Step 1: Configure the Environment`)
- `###` H3: Sub-sections within steps

### Links
- API references: `[method_name](https://fabric-fablib.readthedocs.io/en/latest/{module}.html#full.path.to.method)`
- Cross-references to other notebooks: Relative paths (`../other_example/notebook.ipynb`)
- External links: Full URLs with descriptive text

### Images
```markdown
<img src="./figs/DiagramName.png" width="20%"><br>
```
- Store in `figs/` subdirectory
- Use `<img>` tag with `width` attribute (not markdown `![]()`)
- Common widths: `20%` for topology diagrams, `50%` for screenshots

### Notes and Warnings

Use branded callout blocks with the appropriate CSS class:

```html
<div class="fabric-info"><strong>Note:</strong> Important information about this step.</div>
<div class="fabric-warning"><strong>Warning:</strong> This action may take several minutes.</div>
<div class="fabric-success"><strong>Success:</strong> Your slice is now ready.</div>
<div class="fabric-danger"><strong>Error:</strong> If this step fails, check your configuration.</div>
```

| Class | Color | Use For |
|-------|-------|---------|
| `fabric-info` | Blue (`#5798bc`) | General notes, tips, references |
| `fabric-warning` | Orange (`#ff8542`) | Cautions, long-running operations |
| `fabric-success` | Green (`#008e7a`) | Confirmations, expected outcomes |
| `fabric-danger` | Red (`#b00020`) | Errors, destructive actions, critical warnings |

## FABRIC Branding

All notebooks MUST use the official FABRIC testbed branding. The brand spec is derived from the [FABRIC Portal branding page](https://portal.fabric-testbed.net/branding) and portal source code.

### Brand Colors

| Name | Hex | Usage |
|------|-----|-------|
| Primary | `#5798bc` | H1 border, accents, primary actions |
| Primary Dark | `#1f6a8c` | H2 headings, link text |
| Primary Light | `#8ac9ef` | Hover states, light backgrounds |
| Dark | `#374955` | H1 headings, body text |
| Secondary | `#838385` | Muted text, footer text |
| Success | `#008e7a` | Success callouts, active states |
| Warning | `#ff8542` | Warning callouts, attention |
| Danger | `#b00020` | Error callouts, critical warnings |
| Info | `#a8c9dc` | Info badges, soft accents |

### Chart Color Palette

For matplotlib/plotting, use this ordered palette:

```python
FABRIC_PALETTE = ['#5798bc', '#1f6a8c', '#008e7a', '#ff8542', '#8ac9ef', '#a8c9dc', '#374955', '#838385']
```

### Typography

- **Headings**: [Montserrat](https://fonts.google.com/specimen/Montserrat) (loaded via Google Fonts in the CSS injection cell)
- **Body**: system-ui (system font stack)

### Dark and Light Mode Compatibility

All branding and styling MUST look good in both Jupyter's light and dark themes. Guidelines:

- **Do NOT hardcode background colors** on the page body or large containers — let the Jupyter theme handle it
- **Use semi-transparent backgrounds** for callout blocks so they adapt to both modes:
  - Prefer `rgba()` over opaque hex for callout backgrounds
- **Avoid pure black (`#000`) or pure white (`#fff`)** for text — use the brand dark (`#374955`) or secondary (`#838385`) instead
- **Brand colors are chosen to work on both light and dark backgrounds** — the primary blue (`#5798bc`) and accent colors have sufficient contrast in both modes
- **Logo**: Use the light-background (dark text) logo variant by default; the CSS injection cell should include a `@media (prefers-color-scheme: dark)` rule to swap to the light variant
- **Links**: Brand link color (`#1f6a8c`) works on light backgrounds; for dark mode, the lighter `#8ac9ef` provides better contrast
- **Test callouts** in both modes — the left-border + light-tinted-background pattern works well in both

### Required Brand Elements

Every notebook must include:

1. **Branded logo header** (Cell 1) — FABRIC wave logo with title
2. **CSS injection cell** (Cell 3b) — loads Montserrat font, sets brand colors for headings/links/callouts, supports dark mode
3. **Styled callouts** — use `fabric-info`, `fabric-warning`, `fabric-success`, `fabric-danger` classes
4. **Section dividers** — `<hr class="fabric-divider" />` between major sections
5. **Branded footer** — FABRIC logo + links before the cleanup cell

### Applying Branding

Use the `/brand` skill to apply branding to notebooks:
```
/brand path/to/notebook.ipynb     # Single notebook
/brand all                        # All notebooks
```

## Code Standards

### Output Suppression
```python
fablib.show_config();     # Semicolon suppresses Jupyter output
fablib.list_sites();      # Same pattern for list/show methods
slice.submit();           # And for submit
```

### Error Handling
- Cleanup cells should not use try/except (let errors surface)
- Long-running operations should show progress: `slice.submit(wait=True, progress=True)`
- Network configuration failures should include diagnostic commands

### Variable Naming
```python
slice_name = "MyExperiment"    # String variable for slice name
slice = fablib.new_slice(...)  # Slice object
node = slice.add_node(...)     # Node object
node1, node2 = ...             # Numbered for multi-node
iface = node.add_component(...).get_interfaces()[0]  # Interface
net = slice.add_l2network(...) # Network object
```

### IP Address Handling
```python
from ipaddress import IPv4Network, IPv6Network, ip_address

subnet = IPv4Network("192.168.1.0/24")
# Assign from subnet
iface.ip_addr_add(addr="192.168.1.1", subnet=subnet)
```

## Directory Structure

Each example MUST have:
```
example_name/
├── example_name.ipynb          # Primary notebook
├── figs/                       # Topology diagrams and screenshots (if any)
│   └── DiagramName.png
└── supporting_script.sh        # Helper scripts (if needed)
```

For examples with variants:
```
example_name/
├── example_name_manual.ipynb   # Manual IP configuration
├── example_name_auto.ipynb     # Auto IP assignment
├── example_name_config.ipynb   # User-defined config dict
└── figs/
    └── Topology.png
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Directory | `snake_case` | `create_l2network_basic/` |
| Notebook | `snake_case.ipynb` | `create_l2network_basic_manual.ipynb` |
| Figures | `PascalCase.png` | `L2NetworkTopology.png` |
| Shell scripts | `snake_case.sh` | `config_script.sh` |
| Slice names | `PascalCase` | `"MyL2Network"` |
| Node names | `PascalCase` | `"Node1"`, `"Router1"` |
| Network names | `PascalCase` | `"Net1"`, `"WideAreaLink"` |

## Metadata Requirements

Every new example must be registered in two places:

### 1. `artifacts.json`
```json
{
    "example_key": {
        "title": "Human-Readable Title",
        "description_short": "One-line description.",
        "description_long": "",
        "location": "fabric_examples/category/example_name",
        "tags": ["fabric", "example", "networking"],
        "visibility": "public",
        "authors": ["author@email.com"]
    }
}
```

### 2. `start_here.ipynb`
Add a markdown link in the appropriate section:
```markdown
- [Example Title](./fabric_examples/category/example_name/notebook.ipynb): One-line description.
```

## Quality Checklist

Before submitting a notebook PR, verify:

- [ ] Follows standard cell structure (title → setup → import → experiment → cleanup)
- [ ] Uses exact FABlib import pattern
- [ ] Has `slice.delete()` as final code cell
- [ ] All markdown links are valid
- [ ] API reference links point to correct readthedocs pages
- [ ] Step headers are numbered sequentially
- [ ] Slice name uses a variable, not hardcoded string
- [ ] Output cells are cleared (no stale execution output)
- [ ] Images are in `figs/` subdirectory with reasonable file sizes
- [ ] Entry added to `artifacts.json`
- [ ] Link added to `start_here.ipynb`
- [ ] Commit is GPG-signed
