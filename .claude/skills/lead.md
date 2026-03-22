---
name: lead
description: Team lead orchestrator — decomposes tasks, dispatches specialized agents in parallel, and synthesizes results
user_invocable: true
---

# /lead — Team Orchestrator

Dispatch the **lead** agent to handle this task. The lead coordinates a team of 9 specialist agents, dispatching them in parallel where possible and synthesizing their results.

## How to Invoke

Use the `Agent` tool with `subagent_type: "lead"`. Pass the user's full request — including any file paths, notebook names, or context from the conversation — as the prompt.

```
Agent(subagent_type="lead", prompt="<user's request with full context>")
```

The lead agent will:
1. **Plan** — break the task into subtasks and assign to specialists
2. **Dispatch** — launch agents in parallel where tasks are independent
3. **Synthesize** — merge results into a unified report with next steps

## The Team

| Agent | Handles |
|-------|---------|
| `notebook-reviewer` | Single-notebook review against project spec |
| `batch-fixer` | Bulk structural fixes (imports, cleanup, outputs, numbering) |
| `docs-generator` | Documentation cells, API links, step explanations |
| `brand-styler` | FABRIC visual branding (CSS, logos, callouts, palettes) |
| `site-auditor` | Hardcoded sites, stale references, `get_random_site()` usage |
| `test-runner` | Validation suite execution and result interpretation |
| `example-finder` | Find notebooks by topic, feature, component, or use case |
| `fablib-helper` | FABlib API expertise, code snippets, debugging |
| `pr-prep` | Validate branch changes, generate PR description |

## Example Invocations

```
/lead audit the repo for site issues and prepare fixes
/lead review all notebooks changed in this branch
/lead create a new example about GPU provisioning, review it, and add to the index
/lead find examples about L2 networking and improve their documentation
/lead prepare a PR for the current branch
/lead what notebooks cover SmartNIC usage?
```

## When to Use /lead vs. Individual Agents

- **Use /lead** when the task spans multiple concerns or you want the full team's perspective
- **Use an individual agent directly** when you know exactly which specialist you need and the task is narrowly scoped

If no task is provided, the lead will describe the team's capabilities and ask what you'd like to do.
