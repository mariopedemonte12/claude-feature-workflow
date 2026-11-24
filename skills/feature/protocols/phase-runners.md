# Phase Runners (optional orchestration mode)

> **Experimental: never run.** Nothing in this mode has been measured, including whether a resumed runner can resume its own agents. Tell the programmer this when they choose it.

The orchestrator's cost grows with the square of its work: each call re-reads a context that every agent return, brief and verification makes longer. In **phased** mode, the orchestrator keeps only what needs the programmer and hands each **phase** of a feature to a **phase runner**: a subagent that orchestrates that phase's agents and ends at the phase's first ⛔ gate. Its context dies with the phase, so the orchestrator's own context grows several times more slowly.

**Direct** mode (the orchestrator runs every phase itself, as in `SKILL.md`) remains the default. Phased mode is chosen by the programmer, per feature or per group, with `--phased` or in their request ("run billing phased"), and can change at any gate. Features in the same portfolio may use different modes.

## What changes for the programmer

Facts to present when the programmer asks which mode to use:

| Aspect | Direct | Phased |
| --- | --- | --- |
| Decisions | Every ⛔ gate is the programmer's | Same gates. A runner cannot talk to the programmer, so it cannot pass a gate: it must stop and return it |
| What the programmer sees during a phase | Each agent's result, as it arrives | The phase's result at its gate; the runner's log in `delegations.md` on request |
| Stopping or redirecting mid-phase | Direct, agent by agent | Stop the whole runner (`TaskStop`), then relaunch the phase from its handoff |
| Agent questions | Agent → orchestrator → programmer | Agent → runner → orchestrator → programmer, and back |
| Who verifies agents' claims | The orchestrator the programmer talks to | The runner; the orchestrator adds a cheap consistency check at each gate |
| Orchestration cost | Measured once (3 features) | Not measured. A model in the skill repository's `docs/cost-estimates.md` gives estimates, built on assumed parameters |

## Phases

A runner handles one phase of one feature, from its first step to the first ⛔ it reaches:

| Workflow | Phase | Steps | Ends at |
| --- | --- | --- | --- |
| SDD | Specification | 1 (analyst) – 2 | ⛔ 3 spec gate |
| SDD | Planning | 4 – 5, and the plan gate's content | ⛔ 6 plan gate |
| SDD | Build | 7 – 11 and the review at the validated level | ⛔ defects and candidates gate (or a deviation gate) |
| SDD | Fixes | approved fixes, affected tests, new critic if R2 | ⛔ defects gate again, or step 12 then ⛔ 13 acceptance |
| EVO | Intent | 1 – 2 | ⛔ 3 |
| EVO | Approach | 4 | ⛔ 5 |
| EVO | Increment | 6 – 9 | ⛔ 10 increment gate |
| EVO | Evolution | 11 | ⛔ 10 of the next increment, or, after the last, finalization (12 – 13) and ⛔ acceptance |

Phased mode applies only to orchestrated SDD and EVO features. A DIRECT feature is one agent, so a runner would add a level without removing work.

## The orchestrator in phased mode

It keeps everything that needs the programmer or spans features:
- startup (`SKILL.md` §2): memory, claims, worktree creation, workflow recommendation, role;
- `intent.md`, and recording every answer and statement in it;
- gates: presenting, recording decisions, choosing what the next phase runs;
- relaying agent questions (`protocols/agent-questions.md`) between runners and the programmer;
- the portfolio, overlaps between features, project memory, integration and cleanup (SDD steps 14–15).

**At each runner return:**
1. Present the gate **from disk**: the Pending decision records and the spec's open questions the runner wrote, not its summary. The programmer sees exactly what was written.
2. **Consistency check**, one batched command per gate: `git -C <worktree> status --porcelain` and `git -C <worktree> diff --stat <base>`, plus the existence of the reports the phase must produce. Code changes before the plan is approved, or a missing report, are reported to the programmer as facts.
3. Gates of several features that are ready together are presented in one message, grouped by feature.

**Launching runners.** One runner per feature and phase, never reused for the next phase. Runners of different features launch together in one message. Within one feature, never two runners at once. Standard model `sonnet`; `opus` for Critical features; never `haiku`. Log each runner in `delegations.md` as role *Phase runner*.

**Runner brief:**

```
You are the phase runner for the <Phase> phase of feature "<slug>" in a multi-agent feature workflow.
You are not the orchestrator and you cannot talk to the programmer. Read and follow
<absolute path to protocols/phase-runners.md> §The phase runner.
Feature worktree: <path> (branch <branch>, base <commit>). Feature folder: <path>. Never call EnterWorktree.
Workflow file: <absolute path>, steps <from> – <to>. Criticality: <level>.
Decisions in force: <D-IDs, one line each>
Task: run the steps above until the first ⛔ gate, then return.
```

## The phase runner

You orchestrate one phase of one feature.

1. **Read**: `SKILL.md` §4 (roles, models, delegation practice, briefs, verification, escalation), the steps of the workflow file the brief names, `protocols/skills.md` §Loading, and `protocols/agent-questions.md`. Read the other protocols and templates only when a step in your range calls for them. You do not run startup, claims, memory or gates.
2. **Delegate** each step to its role exactly as `SKILL.md` §4 describes: model choice per delegation, logged in `delegations.md`; briefs in its format; parallel launches where independent. Roles never delegate further.
3. **Verify** what each agent returns against the artifacts and the diff before using it, keeping each agent's recommendation attributed to it.
4. **Agent questions.** Answer from evidence what you can. For the rest, stop: record them as `protocols/agent-questions.md` §For the orchestrator, steps 1–2, describes (including the agent's ID in `handoff.md`) and return with `QUESTIONS`. When resumed with the answers, record them and resume that agent with `SendMessage`; if it cannot be resumed, relaunch it with its work so far.
5. **Stop at the first ⛔** in your range, before doing anything that depends on its decision. Write every decision of that gate to `decisions/D-NNN-<topic>.md` with status **Pending** and the full option block in the decision format, so the orchestrator can present it from disk. The review level, at the plan gate, is written as a *Recommendation* with its evidence (`protocols/review-cycle.md`). Update `handoff.md`.
6. **Return**, and nothing else:

```
PHASE <name> [<slug>] ended at: GATE <step> | QUESTIONS | FAILED
Pending on disk: <D-IDs> · <Q-IDs> (paths)
Facts for the gate: <at most 150 words, observed facts only>
Produced: <files written or changed>
Agents waiting on answers: <agent ID> (<role>), or none
```

`FAILED`: a step could not be completed after the escalation rules of `SKILL.md` §4. State what failed, the evidence and what was tried.

## Limits

- **Reusing agents across phases.** `SKILL.md` §4 resumes the same Implementer or Tester when work returns to them. In phased mode, those agents were launched by an earlier runner that no longer exists. Whether a later runner can resume them with `SendMessage` is **untested**; if it cannot, it launches a new agent with the earlier agent's last report.

- **Nesting.** Orchestrator → runner → role uses 2 of the 3 subagent levels Claude Code allows by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). In the hierarchical mode with the *Subagents* transport (`protocols/hierarchy.md`), sub-orchestrator → runner → role reaches 3 of 3: it works only at the default limit or above. With the *Agent team* or *Separate sessions* transports, a sub-orchestrator is a full session and uses phased mode like any orchestrator.
- **Session end.** A runner lives only as long as the orchestrator's session. A phase interrupted by the end of the session is relaunched from `handoff.md`; work already written to disk is not redone.
