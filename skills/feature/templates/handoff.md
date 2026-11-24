<!-- Overwritten at each transition (in EVO, at each stop). Omit any section that has no content. -->
# Handoff: <from role> → <to role>

## Workflow state

| Field | Value |
| --- | --- |
| Feature | <slug> |
| Status | Active · Paused · Done |
| Workflow | DIRECT · SDD · EVO · Hybrid |
| Role of the session | Orchestrator · Executor |
| Gate profile | full · key · auto, with per-gate changes (`protocols/gates.md`) |
| Feature worktree | <absolute path to .claude/worktrees/<slug>> · branch <name> · base commit `abc1234` |
| Related features | <slug>: <relation, e.g. "both modify src/x.ts">, or "none" |
| Phase / step | … |
| Last gate passed | … (YYYY-MM-DD) |
| Pending decisions | D-NNN … |
| Git | commit `abc1234` · branch · dirty yes/no (or "not a git repo", with date/time) |
| Artifact versions | spec vN · plan <status> |
| Agents | role → agent ID, resumable (e.g. Implementer → a1b2…, Tester → c3d4…); critics and verifiers are never listed |

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
In EVO, which has no specification, this section also holds the open questions: ID · asked by · blocking? · Pending, Answered (S-n) or Deferred.

## Expected next actions

1. …
