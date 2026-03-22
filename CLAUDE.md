# FABRIC Jupyter Examples — Claude Code Project Guide

## Project Overview

This is the **official FABRIC Testbed Jupyter examples repository** (`fabric-testbed/jupyter-examples`). It contains ~250 Jupyter notebooks that teach researchers how to use the FABRIC research infrastructure — a nationwide programmable network testbed for networking and distributed systems experiments.

**Repository**: `git@github.com:fabric-testbed/jupyter-examples.git`
**License**: MIT
**Primary language**: Jupyter Notebooks (Python) with supporting shell scripts, YAML configs, and P4 programs.

## What This Repo Is

- A **tutorial and reference library**, not a Python package
- Each notebook is a **self-contained, runnable example** demonstrating one FABRIC capability
- Notebooks are the **primary deliverable** — they are both documentation and executable code
- The audience is **researchers and students** using FABRIC for network experiments

## Repository Structure

```
jupyter-examples/
├── start_here.ipynb              # Master index of all examples
├── artifact_manager.ipynb        # Download reproducible experiments
├── artifacts.json                # Metadata registry for all examples
├── configure_and_validate/       # Environment setup notebook
├── fabric_examples/
│   ├── fablib_api/               # Core FABlib examples (~68 notebooks)
│   │   ├── hello_fabric/         # Entry point example
│   │   ├── create_slice/         # Slice lifecycle
│   │   ├── create_l2network_*/   # L2 networking variants
│   │   ├── create_l3network_*/   # L3 networking variants
│   │   ├── fabric_all_gpus/      # GPU provisioning
│   │   ├── fabric_fpgas/         # FPGA examples
│   │   ├── post_boot_tasks/      # Automated configuration
│   │   └── ...                   # ~40 more feature directories
│   ├── complex_recipes/          # Advanced multi-component examples
│   │   ├── FRRouting/            # OSPF routing
│   │   ├── kubernetes/           # K8s on FABRIC
│   │   ├── iPerf3/               # Performance testing
│   │   ├── owl/                  # One-way latency
│   │   ├── p4_labs_bmv2/         # P4 programmable switches
│   │   └── ...
│   ├── mflib/                    # Measurement Framework examples
│   ├── public_demos/             # Conference workshop materials
│   ├── acceptance_testing/       # Release acceptance tests
│   ├── beta_functionality/       # Beta feature previews
│   └── testing_and_debugging/    # Debug utilities
├── docker_containers/            # Docker compose configs for FABRIC nodes
├── fabric_ssh_tunnel_tools/      # SSH tunnel helper scripts
└── .github/workflows/checks.yml  # CI: GPG-signed commit enforcement
```

## Notebook Conventions

### Standard Structure (every notebook follows this)

1. **Title & Description** (markdown) — H1 title, purpose, FABlib API reference links
2. **Import FABlib** (code) — Always this exact pattern:
   ```python
   from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager
   fablib = fablib_manager()
   fablib.show_config();
   ```
3. **Query Resources** (optional code) — `fablib.list_sites();`
4. **Create Slice** (code) — Build topology, add nodes/networks/components, submit
5. **Run Experiment** (code) — Execute commands, configure, measure
6. **Cleanup** (code) — `slice.delete()`

### Naming Conventions

- **Directories**: `snake_case` matching the feature name (e.g., `create_l2network_basic/`)
- **Notebooks**: Same name as directory or descriptive variant (e.g., `create_l2network_basic_manual.ipynb`)
- **Figures**: Stored in `figs/` subdirectory within each example
- **Shell scripts**: Supporting config scripts alongside notebooks

### Markdown Patterns

- API references link to `https://fabric-fablib.readthedocs.io/en/latest/`
- Steps are numbered with `## Step N:` headers
- Images use relative paths: `<img src="./figs/Name.png" width="20%">`
- FABlib method references use `[method_name](readthedocs_url)` format

### Code Patterns

- Slice names are set as variables at the top: `slice_name = "MyExperiment"`
- `fablib.show_config();` — trailing semicolon suppresses Jupyter output
- Node commands use `node.execute('command')` returning `(stdout, stderr)`
- Network variants: `manual` (explicit IPs), `auto` (FABlib assigns), `config` (user-defined)
- Cleanup is always the final cell: `slice.delete()`

## Key Dependencies

```
fabrictestbed-extensions>=1.9.0   # FABlib — the main FABRIC Python API
fabrictestbed-mflib>=1.0.4        # Measurement Framework Library
ipython==8.12.0                    # Interactive Python (pinned)
python-dotenv                      # Environment variable loading
```

## FABlib API Quick Reference

```python
# Initialize
fablib = fablib_manager()

# Discover resources
fablib.list_sites(output='pandas')
fablib.get_random_site()

# Create experiment
slice = fablib.new_slice(name="name")
node = slice.add_node(name="node1", site="RENC", cores=4, ram=16, disk=100)
iface = node.add_component(model='NIC_Basic', name='nic1').get_interfaces()[0]
net = slice.add_l2network(name='net1', interfaces=[iface1, iface2])
slice.submit()

# Use experiment
slice = fablib.get_slice(name="name")
node = slice.get_node(name="node1")
stdout, stderr = node.execute("command")

# Cleanup
slice.delete()
```

### Component Models
- NICs: `NIC_Basic`, `NIC_ConnectX_5`, `NIC_ConnectX_6`
- GPUs: `GPU_RTX6000`, `GPU_TeslaT4`, `GPU_A30`, `GPU_A40`
- FPGAs: `FPGA_Xilinx_U280`
- Storage: `NVME_P4510`
- DPUs: `SmartNIC_ConnectX_6_DPU`, `SmartNIC_ConnectX_7_DPU`

### Network Types
- `slice.add_l2network()` — L2 Ethernet (local or wide-area)
- `slice.add_l3network(type='IPv4')` — FABnet L3
- `slice.add_facility_port()` — External facility connection

## CI/CD

- **GitHub Actions** (`.github/workflows/checks.yml`): Enforces GPG-signed commits on all PRs via `1Password/check-signed-commits-action`
- No automated notebook execution or linting in CI (yet)

## Working with This Repo

### Adding a New Example
1. Create a directory under the appropriate category in `fabric_examples/`
2. Follow the standard notebook structure (see above)
3. Add a `figs/` subdirectory for any images
4. Add the example to `start_here.ipynb` index
5. Add metadata to `artifacts.json`
6. Use GPG-signed commits

### Modifying Existing Notebooks
- Preserve the standard structure
- Keep FABlib import pattern identical across all notebooks
- Update `start_here.ipynb` if links or titles change
- Test that the notebook runs end-to-end on FABRIC JupyterHub

### Common Pitfalls
- Don't hardcode site names — use `fablib.get_random_site()` for portability
- Always include `slice.delete()` as the final cell
- Suppress output with trailing `;` on display calls
- Network examples need both `manual` and `auto` variants when possible
- Large output cells should be cleared before committing

## File Registry

`artifacts.json` is the metadata registry for all examples. Each entry has:
```json
{
  "key": {
    "title": "Human-readable title",
    "description_short": "One-line description",
    "location": "relative/path/to/directory",
    "tags": ["fabric", "example"],
    "visibility": "public",
    "authors": ["email@example.com"]
  }
}
```

Keep `artifacts.json` and `start_here.ipynb` in sync when adding/removing examples.
