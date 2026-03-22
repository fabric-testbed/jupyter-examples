# Architecture

## System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                     FABRIC Testbed Ecosystem                     │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │ FABRIC Portal│   │  JupyterHub  │   │  FABRIC Sites (25+)  │ │
│  │  (Auth/Mgmt) │   │  (Notebooks) │   │  RENC, TACC, UCSD... │ │
│  └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘ │
│         │                  │                       │             │
│         │           ┌──────┴───────┐               │             │
│         │           │ THIS REPO:   │               │             │
│         └──────────►│ jupyter-     │◄──────────────┘             │
│                     │ examples     │                             │
│                     └──────┬───────┘                             │
│                            │                                     │
│                     ┌──────┴───────┐                             │
│                     │   FABlib     │                             │
│                     │ Python API   │                             │
│                     └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

This repository is the **tutorial layer** that sits between researchers and the FABRIC infrastructure. Researchers clone it into their JupyterHub environment (or local machine) and run notebooks that call FABlib to provision and manage testbed resources.

## Component Architecture

### 1. Entry Points

```
start_here.ipynb          ← Master index (links to all examples)
configure_and_validate/   ← First-time setup (tokens, keys, config)
artifact_manager.ipynb    ← Download pre-built experiment artifacts
```

**Data flow**: User lands on `start_here.ipynb` → runs `configure_and_validate` → picks an example category → runs notebooks.

### 2. Example Hierarchy

```
fabric_examples/
├── fablib_api/            # Tier 1: Single-feature examples
│   ├── hello_fabric/      #   Entry point — simplest possible slice
│   ├── create_slice/      #   Slice lifecycle operations
│   ├── create_l2network_*/   # L2 networking (3 variants each)
│   ├── create_l3network_*/   # L3 networking (3 variants each)
│   ├── fabric_all_gpus/      # GPU provisioning
│   ├── post_boot_tasks/      # Automation
│   └── ...                   # ~48 feature directories
│
├── complex_recipes/       # Tier 2: Multi-component compositions
│   ├── FRRouting/         #   Combines: nodes + networking + routing
│   ├── kubernetes/        #   Combines: nodes + networking + docker
│   ├── iPerf3/            #   Combines: nodes + networking + benchmarks
│   ├── owl/               #   Combines: nodes + networking + measurement
│   ├── p4_labs_bmv2/      #   Combines: nodes + P4 switches + labs
│   └── ...
│
├── mflib/                 # Tier 3: Measurement framework integration
├── public_demos/          # Workshop/conference materials
├── acceptance_testing/    # Release validation suites
├── beta_functionality/    # Pre-release feature previews
└── testing_and_debugging/ # Internal debug tools
```

**Design principle**: Tier 1 examples teach one feature. Tier 2 composes multiple features into realistic experiments. This separation keeps the learning curve manageable.

### 3. Notebook Internal Architecture

Every notebook follows a pipeline pattern:

```
┌─────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  Setup   │──►│ Topology │──►│ Submit  │──►│ Execute │──►│ Cleanup │
│  FABlib  │   │  Build   │   │ & Wait  │   │ Exper.  │   │ Delete  │
└─────────┘   └──────────┘   └─────────┘   └─────────┘   └─────────┘
```

Each stage maps to numbered step cells:

| Stage | Cells | Purpose |
|-------|-------|---------|
| Setup | 1-2 | Import FABlib, show config, optionally query resources |
| Topology | 3-4 | `new_slice()` → `add_node()` → `add_component()` → `add_network()` |
| Submit | 5 | `slice.submit()` — blocks until provisioned |
| Execute | 6+ | `node.execute()`, file transfers, configuration |
| Cleanup | Last | `slice.delete()` |

### 4. Network Variant Pattern

Networking examples follow a consistent variant system:

```
create_l2network_basic/
├── create_l2network_basic_manual.ipynb   # User sets all IPs explicitly
├── create_l2network_basic_auto.ipynb     # FABlib auto-assigns IPs
└── create_l2network_basic_config.ipynb   # User provides IP config dict
```

This pattern repeats for: L2 basic, L2 wide-area, L3 FABnet IPv4, L3 FABnet IPv6.

### 5. Supporting Infrastructure

```
docker_containers/              # Docker compose files deployed TO FABRIC nodes
├── httpd/                      #   Apache web server
├── fabric_multitool/           #   Network debugging container
├── fabric_frrouting/           #   FRRouting service
├── monitoring/                 #   Grafana + Prometheus stack
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   └── grafana/provisioning/   #   Auto-provisioned dashboards
├── node_exporter/              #   Metrics collection
└── droppy/                     #   File sharing

fabric_ssh_tunnel_tools/        # Local scripts for SSH access
├── start_ssh_tunnel.sh
└── stop_ssh_tunnel.sh
```

These are **not** development infrastructure — they are resources that notebooks deploy onto FABRIC nodes.

### 6. Metadata Registry

```
artifacts.json
  ↓ referenced by
artifact_manager.ipynb
  ↓ indexed in
start_here.ipynb
```

`artifacts.json` is the single source of truth for example metadata. Each entry maps a key to title, description, location, tags, and authors. The `start_here.ipynb` notebook provides the human-readable index with links.

**Invariant**: Every example directory should have entries in both `artifacts.json` and `start_here.ipynb`.

## Dependency Graph

```
External Packages (PyPI)
│
├── fabrictestbed-extensions (>=1.9.0)
│   └── Provides: FablibManager, Slice, Node, Network, Component APIs
│
├── fabrictestbed-mflib (>=1.0.4)
│   └── Provides: MFLib measurement framework integration
│
├── ipython (==8.12.0)
│   └── Provides: Jupyter kernel runtime
│
└── python-dotenv
    └── Provides: .env file loading for configuration

FABRIC Services (Remote)
│
├── FABRIC Portal (portal.fabric-testbed.net)
│   └── Authentication, project management
│
├── FABRIC Orchestrator
│   └── Slice provisioning and lifecycle (called by FABlib)
│
├── FABRIC Bastion Host
│   └── SSH proxy jump to experiment VMs
│
└── FABRIC Sites (25+ distributed locations)
    └── Compute, network, storage resources
```

## CI/CD Pipeline

```
Developer Push/PR
       │
       ▼
GitHub Actions (.github/workflows/checks.yml)
       │
       ├── checkout (fetch-depth: 0)
       │
       └── Check GPG-signed commits
           (1Password/check-signed-commits-action)
           │
           ├── PASS → PR can be reviewed/merged
           └── FAIL → PR blocked with comment
```

**Current state**: CI only validates commit signatures. There is no automated notebook execution, linting, or link checking.

## Authentication Flow

```
User
 │
 ├── FABRIC Portal → Project ID, credentials
 │
 ├── configure_and_validate.ipynb
 │   ├── Sets project_id
 │   ├── Generates/validates bastion SSH keys
 │   ├── Generates slice SSH keys
 │   ├── Creates fabric_rc config file
 │   └── Creates ssh_config for bastion jumping
 │
 └── Notebook execution
     ├── fablib_manager() reads fabric_rc
     ├── API calls authenticated via OIDC tokens
     └── SSH access via bastion_key → slice_key chain
```

## Key Design Decisions

1. **Notebooks as documentation**: Executable examples > static docs. Every feature has a runnable notebook.

2. **Self-contained examples**: Each notebook stands alone. No shared utility imports between example directories (except `fablib_common/` for optional patterns).

3. **Variant system for networking**: Manual/Auto/Config variants let users learn at their comfort level without cluttering a single notebook.

4. **No Python package structure**: This is intentionally not a pip-installable package. It's a collection of notebooks meant to be cloned and run.

5. **Docker configs are deployable artifacts**: The `docker_containers/` directory contains configs meant to be uploaded to and run on FABRIC nodes, not for local development.

6. **GPG-signed commits enforced**: All contributions must be signed, enforced by CI. This is a FABRIC project-wide security policy.
