<!-- Resume state. When and by whom it is written: `protocols/context-handoff.md` §Resume state. Overwritten each time. In EVO as executor, and in DIRECT with a card, the card's *State* replaces it; DIRECT without a card has none. Omit any section that has no content. -->
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
| Agents | role → agent ID, model and last reported `subagent_tokens`, what `SKILL.md` §4, *Reusing agents*, needs (e.g. Implementer → a1b2… sonnet (183k), Tester → c3d4… sonnet (60k), Planner → e5f6… opus (not reported yet)); critics and verifiers are never listed |
| Agents at the stop | After a pause or a stop everything (`SKILL.md` §7, *Pause and stop everything*): finished → agent ID and where its result is recorded · interrupted → agent ID, role, task, what it left on disk (unverified) · to relaunch → the tasks |

## Open questions

EVO, which has no specification: ID · asked by · blocking? · Pending, Answered (S-n) or Deferred; for a question an agent is waiting on, its agent ID.
