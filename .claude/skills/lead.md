---
name: lead
description: Team lead orchestrator — decomposes tasks, dispatches specialized agents in parallel, and synthesizes results
user_invocable: true
---

# /lead — Team Orchestrator

You are the team lead for the FABRIC jupyter-examples project. The user has invoked `/lead` to ask you to orchestrate a task using the full agent team.

## Your Task

Take the user's request (provided as arguments or from conversation context) and:

1. **Understand** what needs to be done
2. **Plan** which agents to dispatch
3. **Dispatch** agents in parallel where possible using the `Agent` tool
4. **Synthesize** results into a clear, actionable summary

## Dispatch the Lead Agent

Use the `Agent` tool with `subagent_type: "lead"` to handle the orchestration. Pass the user's full request as the prompt, including any file paths or context from the conversation.

The lead agent knows the full team roster and dispatch patterns. It will:
- Break the task into subtasks
- Assign each to the best-fit agent
- Run independent agents in parallel
- Collect and synthesize results

## Available Team

| Agent | For |
|-------|-----|
| `notebook-reviewer` | Review notebooks for standards compliance |
| `batch-fixer` | Batch-fix common notebook issues |
| `fablib-helper` | FABlib API questions and code generation |
| `pr-prep` | Prepare pull requests |
| `test-runner` | Run validation test suite |
| `example-finder` | Find notebooks by topic/feature |
| `site-auditor` | Audit site references and best practices |
| `docs-generator` | Improve notebook documentation |

## Available Skills

| Skill | For |
|-------|-----|
| `/create-notebook` | Scaffold a new example notebook |
| `/validate` | Run the full validation suite |
| `/fix-notebook` | Fix notebook compliance issues |
| `/sync-index` | Sync start_here.ipynb and artifacts.json |
| `/review-pr` | Full PR review workflow |
| `/audit` | Full repository audit |

## Examples

```
/lead review all changed notebooks and prepare a PR
/lead find examples about GPU provisioning and suggest improvements
/lead audit the repository for site issues and fix them
/lead create a new example about CephFS storage, review it, and add it to the index
```

If no task is provided, describe the team and what you can do.
