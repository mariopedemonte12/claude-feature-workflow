<!-- Resume state. Written at every stop (a gate, a pending question, the end of the turn, a pause) by whoever drives the session: the orchestrator, a phase runner, or the SDD executor (`protocols/context-handoff.md` §Resume state). Overwritten each time. In EVO as executor, and in DIRECT with a card, the card's *State* replaces it; DIRECT without a card has none. Omit any section that has no content. -->
# State: <slug>

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

## Open questions

EVO, which has no specification: ID · asked by · blocking? · Pending, Answered (S-n) or Deferred; for a question an agent is waiting on, its agent ID.
