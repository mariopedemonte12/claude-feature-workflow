# Orchestrator Memory and Stateless Sessions

The orchestrator's cost grows with every call it makes, because each call re-reads its whole context. To keep that context small, the orchestrator does not rely on its conversation: everything it needs to continue lives in a small **project memory** file plus each feature's `state.md`, so any session can stop at a gate and a **fresh** session can pick up from there.

## The project memory file

```
$(git rev-parse --git-common-dir)/feature-workflow/memory.md
```

Shared by every worktree of the repository and never committed. **Hard limit: 80 lines.** It is an index, not a log: it holds the current state and pointers, never history or content that lives in artifacts.

```markdown
# Feature workflow memory · updated <ISO time> · HEAD <short sha> (<branch>)

## Project
- Stack: <language, framework, versions> (evidence: path)
- Commands: build `<…>` · test `<…>` · lint `<…>` · run `<…>`
- Architecture and folders: <style> (evidence: path)
- Quality: `.quality/` yes/no · lizard yes/no · E2E harness <…>
- Skill directory: <absolute path>

## Standing instructions from the programmer
- <one line each, only what the programmer stated, with the date>

## Portfolio
| Feature | Role | Workflow | Phase / step | Waiting on | Worktree | Feature folder |
| --- | --- | --- | --- | --- | --- | --- |

## Pending questions to the programmer
- <slug>/<id>: <one line> (full text: <artifact path §section>)

## Notes for the next session
- <only what a fresh session needs and the artifacts do not already say>
```

Rules:
- Facts about the project carry evidence (a path or a command), like the analyst report.
- Each feature gets one row. Its details stay in its own artifacts.
- Remove a feature's row once it is Done and its cleanup gate has passed.
- Never store decisions here. They live in `decisions/`; the memory points to the feature.

## Session lifecycle

**At the start of every session** (any `/feature` invocation):
1. Read `memory.md` if it exists. Trust its Project section instead of exploring the repository again. Check freshness: if `HEAD` differs from the recorded commit, run `git diff --stat <recorded>..HEAD` and refresh only the facts the changes touch.
2. Read the workflow file of each feature you will act on in this session, and `protocols/decisions.md` before presenting a decision. Do not preload other protocols.
3. Read the `state.md` only of the features the programmer's message concerns.

**At every stop** (a gate, a pending question, the end of the turn):
1. Write every decision you are about to present to the feature's `decisions/D-NNN-<topic>.md` with status **Pending**, including the full option block with its labels (A, B, T1…), exactly as presented. An answer such as "B" must be resolvable from disk. Open questions go to the artifact that owns them (spec §Open questions; in EVO, `state.md` §Open questions) with their labels. Questions an agent is waiting on also record the agent's ID in `state.md` (`protocols/agent-questions.md`).
2. Update each touched feature's `state.md` (`protocols/context-handoff.md` §Resume state).
3. Rewrite `memory.md` within its limit: portfolio rows, pending questions and decisions with pointers to their files, standing instructions.
4. Then present the gate. Everything needed to continue is now on disk.

## Continuing in a fresh session

`/feature continue <message>` starts from the memory and each feature's `state.md`, not from conversation history:
1. Read `memory.md`.
2. Map the message to the pending questions: by `slug/id` when given, or by unambiguous content. Ask when the mapping is ambiguous.
3. Read only the `state.md` of the features the message touches, record the answers in their artifacts, and continue those features.

The programmer chooses when to continue in a fresh session: in an interactive session, `/clear` followed by `/feature continue <answer>`; in a scripted session, a new invocation instead of a resumed one. Continuing in the same session also works; the memory then costs only its upkeep.

**Lost context is a defect of the artifacts.** If a fresh session cannot continue without something that was only in the conversation, record that fact in the feature's `state.md` and tell the programmer, so the gap is visible.
