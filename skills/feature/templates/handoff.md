<!-- Overwritten at each transition. Omit any section that has no content. -->
# Handoff: <from role> → <to role>

## Workflow state

| Field | Value |
| --- | --- |
| Feature | <slug> |
| Status | Active · Paused · Done |
| Workflow | SDD Direct · ESDD · Hybrid |
| Feature worktree | <absolute path to .claude/worktrees/<slug>> · branch <name> · base commit `abc1234` |
| Related features | <slug>: <relation, e.g. "both modify src/x.ts">, or "none" |
| Phase / step | … |
| Last gate passed | … (YYYY-MM-DD) |
| Pending decisions | D-NNN … |
| Git | commit `abc1234` · branch · dirty yes/no (or "not a git repo", with date/time) |
| Artifact versions | spec vN · plan <status> |

## Objective

What the next agent must accomplish.

## Current state

## Key findings

- [Confirmed] … (ref)
- [Hypothesis] …

## Approved decisions

- D-NNN: … (one line each)

## Constraints and invariants

IDs with references, e.g. `specification.md` §Invariants INV-1..3.

## Relevant references

- `path` §section / `file:line`: why it matters

## Open issues

## Expected next actions

1. …
