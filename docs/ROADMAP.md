# Development Roadmap

## Phase 1: Quality & Consistency (Foundation)

### 1.1 Notebook Standardization
- [ ] Audit all 248 notebooks against the notebook spec (see `NOTEBOOK_SPEC.md`)
- [ ] Ensure consistent FABlib import pattern across all notebooks
- [ ] Add missing `slice.delete()` cleanup cells where absent
- [ ] Standardize step numbering (`## Step N:` headers)
- [ ] Ensure all code cells suppress unnecessary output with trailing `;`
- [ ] Clear large output cells before committing

### 1.2 Metadata Consistency
- [ ] Reconcile `artifacts.json` with actual directory contents (find orphans and missing entries)
- [ ] Reconcile `start_here.ipynb` links with actual notebook paths (fix broken links)
- [ ] Ensure every example directory has entries in both `artifacts.json` and `start_here.ipynb`
- [ ] Add `description_long` fields to `artifacts.json` entries that are missing them
- [ ] Standardize tags in `artifacts.json` (establish a controlled vocabulary)

### 1.3 Documentation Gaps
- [ ] Add README.md to each `complex_recipes/` subdirectory explaining prerequisites
- [ ] Document the network variant pattern (manual/auto/config) in a central location
- [ ] Add troubleshooting sections to notebooks that commonly fail (resource contention, timeout)
- [ ] Document the docker_containers/ directory purpose and usage patterns

## Phase 2: Testing Infrastructure

### 2.1 Static Validation (runs without FABRIC access)
- [ ] Notebook structure linter — validates cell ordering, required sections, cleanup cell
- [ ] Link checker — validates all markdown links in notebooks and `start_here.ipynb`
- [ ] Import checker — validates FABlib import pattern consistency
- [ ] `artifacts.json` schema validator
- [ ] `start_here.ipynb` ↔ `artifacts.json` cross-reference checker
- [ ] Notebook metadata validator (kernel spec, language info)

### 2.2 CI/CD Enhancement
- [ ] Add notebook linting to GitHub Actions pipeline
- [ ] Add link checking to CI
- [ ] Add `artifacts.json` validation to CI
- [ ] Consider pre-commit hooks for notebook output stripping
- [ ] Add PR template with checklist for notebook contributions

### 2.3 Integration Testing (requires FABRIC access)
- [ ] Identify a subset of "smoke test" notebooks that can run end-to-end
- [ ] Create a test runner that executes notebooks via `nbconvert` or `papermill`
- [ ] Implement timeout and resource cleanup for failed test runs
- [ ] Schedule periodic integration test runs (weekly/monthly)

## Phase 3: Content Expansion

### 3.1 Missing Example Categories
- [ ] **IPv4/IPv6 dual-stack networking**: Combined IPv4+IPv6 examples
- [ ] **Multi-site topologies**: Examples with 3+ sites, complex routing
- [ ] **Slice modification patterns**: More examples of adding/removing resources to running slices
- [ ] **Error handling and recovery**: Examples showing retry logic, error recovery, slice healing
- [ ] **Data pipeline examples**: Moving data between FABRIC and external storage (S3, GCS)
- [ ] **CI/CD on FABRIC**: Using FABRIC for automated testing of network software

### 3.2 Complex Recipe Expansion
- [ ] **Ansible on FABRIC**: Configuration management across slice nodes
- [ ] **Terraform provider example**: Infrastructure-as-code for FABRIC
- [ ] **Multi-facility stitching**: Updated examples for Chameleon, CloudLab, ESnet connections
- [ ] **ML training on FABRIC GPUs**: Distributed training across GPU nodes
- [ ] **Network digital twin**: Recreating production topologies for testing

### 3.3 Learning Path Improvements
- [ ] Create difficulty tags (beginner/intermediate/advanced) for all examples
- [ ] Build guided learning paths: "Networking 101", "GPU Computing", "Advanced Routing"
- [ ] Add "Next Steps" sections at the end of each notebook linking to related examples
- [ ] Create a visual topology gallery showing what each example builds

## Phase 4: Automation & Tooling

### 4.1 Notebook Generation
- [ ] Template system for generating new example notebooks with standard boilerplate
- [ ] Auto-generation of `start_here.ipynb` from `artifacts.json`
- [ ] Script to scaffold a new example directory with notebook, figs/, and artifacts.json entry

### 4.2 Maintenance Automation
- [ ] Auto-detect FABlib API changes and flag affected notebooks
- [ ] Stale notebook detector (notebooks not updated in 6+ months)
- [ ] Output cell cleaner (strip outputs before commit)
- [ ] Image optimization for `figs/` directories

### 4.3 Developer Experience
- [ ] Claude Code skills for common development tasks (see `.claude/skills/`)
- [ ] Claude Code agents for validation and review (see `.claude/agents/`)
- [ ] Local development setup script (venv, FABlib, Jupyter kernel)
- [ ] VS Code / JupyterLab recommended extensions list

## Phase 5: Community & Contribution

### 5.1 Contribution Pipeline
- [ ] PR template requiring: notebook spec compliance, artifacts.json update, start_here.ipynb update
- [ ] Automated PR review checklist via GitHub Actions
- [ ] Contributor guide with video walkthrough
- [ ] Example contribution: step-by-step guide for adding a new recipe

### 5.2 Community Examples
- [ ] Separate `community_examples/` directory for user-contributed notebooks
- [ ] Submission review process and quality bar
- [ ] Featured example rotation on FABRIC portal
- [ ] Annual "best experiment" showcase

## Priority Matrix

| Item | Impact | Effort | Priority |
|------|--------|--------|----------|
| Notebook linting in CI | High | Low | **P0** |
| artifacts.json reconciliation | High | Low | **P0** |
| Broken link checker | High | Low | **P0** |
| Notebook structure standardization | High | Medium | **P1** |
| PR template + checklist | Medium | Low | **P1** |
| New example scaffolding tool | Medium | Low | **P1** |
| Integration test runner | High | High | **P2** |
| Learning paths | Medium | Medium | **P2** |
| Community examples pipeline | Medium | High | **P3** |
