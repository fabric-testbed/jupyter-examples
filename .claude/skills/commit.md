---
name: commit
description: Create a GPG-signed git commit with a well-formed message following project conventions
user_invocable: true
---

# /commit — GPG-Signed Git Commit

Create a GPG-signed commit for the jupyter-examples repository. This ensures all commits pass the CI check for signed commits (`.github/workflows/checks.yml`).

## Signing Configuration

- **GPG Key**: `68D279E0BD93F510` (Paul Ruth <pruth@renci.org>)
- **git config**: `commit.gpgsign=true` is set globally, so `-S` is automatic
- **CI Requirement**: All PRs are checked via `1Password/check-signed-commits-action`

## Workflow

### 1. Review Changes

Run these in parallel:
```bash
git status
git diff --staged
git diff
```

If nothing is staged, identify which changed files should be included and stage them with `git add <file>...`. Prefer adding specific files over `git add -A`.

### 2. Analyze Changes

Categorize what changed:
- New notebooks added
- Existing notebooks modified
- Metadata updates (artifacts.json, start_here.ipynb)
- Infrastructure (tests, docs, .claude/)
- Other files

### 3. Draft Commit Message

Write a concise commit message:
- **First line**: imperative mood, under 72 chars, describes the "why" not the "what"
- **Body** (if needed): bullet points with details
- **Always include**: `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`

### 4. Create the Signed Commit

Use this exact pattern to ensure GPG signing and proper formatting:

```bash
git commit -S -m "$(cat <<'EOF'
Commit message here

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

The `-S` flag explicitly requests GPG signing (belt-and-suspenders with the global config).

### 5. Verify

After committing, run:
```bash
git log --show-signature -1
```

Confirm the output shows `Good signature from "Paul Ruth <pruth@renci.org>"`.

## Rules

- **NEVER** use `--no-gpg-sign` or `-c commit.gpgsign=false`
- **NEVER** use `--no-verify` to skip pre-commit hooks
- **NEVER** amend a previous commit unless explicitly asked
- **NEVER** use `git add -A` or `git add .` — always add specific files
- Do not commit files that look like secrets (`.env`, `id_token.json`, credentials)
- Do not commit notebook output cells — they should be cleared first
- If the GPG agent is not running or the key is locked, tell the user to run `gpg --sign --armor /dev/null` to unlock it

## Examples

```
/commit                          # commit all staged changes
/commit add the new CephFS example notebook
/commit fix broken links in start_here
```
