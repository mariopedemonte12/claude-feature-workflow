# Gates Protocol

Every human gate (⛔) of a workflow has a **name**. Whether a gate stops the feature depends on the feature's **gate profile**, chosen at startup with the workflow and the role. A gate that is off does not disappear: the agent decides what the gate would have asked, records it, and reports it. Some events are **hard stops** instead (§Hard stops).

## The gates

| Name | Where | What it settles |
| --- | --- | --- |
| `intent` | SDD 3 (spec approval), EVO 3 (intent gate); executor EVO: the merged gate | The consolidated intent, the blocking questions, the criticality, the completion criteria or the approved spec |
| `specialists` | SDD 3, EVO 3; re-offered when signals change | Which specialists run in which phases |
| `bootstrap` | SDD 4, EVO 5 (`protocols/anti-pattern-registry.md` §Bootstrap) | The project's anti-pattern registry: seeds, limits, location |
| `approach` | SDD 6, EVO 5; again when the approach is in question; SDD 7 when the plan is invalid | The implementation approach, the increments (EVO), a deviation from the plan |
| `depth` | SDD 6, EVO 5 | The testing plan, mutation testing, the review level, the end-to-end harness |
| `increment` | EVO 10 | The increment's results and the next increment |
| `defects` | SDD defects gate, EVO 10 | Review, test and audit findings: fix now, accept, change the spec |
| `discoveries` | SDD defects gate, EVO 8 and 10, any phase | Something the intent may reach that nobody foresaw |
| `candidates` | SDD defects gate or before acceptance, EVO 10 | Anti-pattern candidates for the registry |
| `acceptance` | SDD 13, EVO 13 | Final acceptance of the feature |

Integration and cleanup are hard stops, not gates (§Hard stops).

## Profiles

| Gate | `full` | `key` (default) | `auto` |
| --- | --- | --- | --- |
| `intent` | stops | stops | off |
| `specialists` | stops | off: the mandatory ones and those named with `--with` run; the others are listed with their signals | off, as in `key` |
| `bootstrap` | stops | stops | off: a registry **local to the clone** with the `general` seeds and the default limits; nothing versioned |
| `approach` | stops | stops only when more than one viable option has different observable consequences (a public API, data or schema, a dependency, a structure other features will follow); otherwise off | off |
| `depth` | stops | off: the defaults (review level: `protocols/review-cycle.md` §Recommending the level, which says what applies with this gate off; mutation testing only when Critical, the testing plan as designed, an existing end-to-end harness or the status Blocked) | off, as in `key` |
| `increment` | stops | off: the increment's results go to the programmer as a report, and the work continues, unless another gate that is on or a hard stop (§Hard stops) stops it | off, as in `key` |
| `defects` | stops | off: the Implementer (resumed) fixes the Blocker and Major findings of the critic and the Tester that the programmer's words cover, at any review level, test first when the fix changes behavior (the Tester, resumed, writes the reproducing test, then the Implementer fixes); at R2 the cycle's automatic fixes of behavior-preserving VALID findings still run; the rest, and every specialist audit finding except a security Blocker (a hard stop: §Hard stops), go to acceptance, except the Blocker and Major findings still open when the round cap is reached, which stop the feature (`protocols/review-cycle.md` §R2 · The cycle) | off, as in `key` |
| `discoveries` | stops | stops for a discovery *outside what the programmer stated* or that *contradicts* their words; one *covered by* their words is fixed | off: covered ones are fixed; those outside the programmer's words are **not built**, only recorded for acceptance; one that **contradicts** them is a hard stop (§Hard stops) |
| `candidates` | stops | off: presented together at `acceptance` | off: listed in the final report, not registered |
| `acceptance` | stops | stops, together with integration | stops, together with integration |

A profile is a starting point. The programmer may switch any gate on or off for one feature: `--gates key,+increment,-intent`. They may also change the profile mid-feature; the change applies from the next gate on.

**DIRECT** has no gates before integration, in every profile.

## Recommending the profile

At startup, in the same message as the workflow recommendation (`SKILL.md` §2.5), recommend a profile, labeled, with its evidence:
- **`full`** when the feature is likely Critical: money, security, authorization, personal data, data writes or migrations, a public interface others depend on.
- **`key`** for SDD and EVO otherwise. It is the default.
- **`auto`** for DIRECT.

**Criticality decided later.** When a feature in `key` or `auto` turns out Critical (at the intent gate, or from the agent's own assessment when that gate is off), stop once and propose `full`, with the evidence. This is a hard stop (§Hard stops).

## When a gate is off

1. **Decide as the gate would have asked:** take the recommendation you would have presented (`protocols/decisions.md`), the default named in the table above, or, for a question, the reading the evidence supports best: the programmer's words first, then the nearest analog, then the project's conventions.
2. **Record it** in `decisions/` (or the card's *Decisions*) with status **Decided by agent**, the gate it replaced, the options and the evidence, exactly as a gate would have shown them.
3. **Tell the programmer in one line** in the next message (`[slug] decided by agent: <what> (gate <name> off), see D-NNN`), and continue. The programmer may reopen any such decision at any time; reopening it is a new decision, with its effects on the work already done.
4. **At acceptance**, the final report lists every decision taken by the agent, grouped by gate, so the programmer can review them before integrating.

Choosing a profile is a standing approval with a defined scope (`protocols/decisions.md` rule 7): quote it when applying it, and list it in the final report.

## Hard stops

These stop the feature in every profile, because they are hard to undo or leave the programmer's machine:
- **integration:** a merge, a rebase onto a shared branch, a push, a pull request (`workflows/sdd.md` step 14);
- **cleanup:** removing a worktree or a branch (`workflows/sdd.md` step 15);
- **installing** a dependency, a tool, a browser or a container image the project does not already have;
- a **migration** that touches data other than test data;
- **breaking a public interface** the programmer did not ask to change;
- a discovery that **contradicts** the programmer's words;
- a **Blocker** found by a security audit (the `security` specialist's `audit` phase);
- the **criticality** check above.
- the critic-round **cap reached with a Blocker or Major open** (`protocols/review-cycle.md` §R2 · The cycle);

## Questions

In every profile, an agent asks the programmer when an answer only they can give blocks the work (`protocols/agent-questions.md`); an executor session asks directly. A gate being off changes what is presented at fixed points, not whether questions are allowed; DIRECT's blocking questions (`workflows/direct.md` step 3) are asked in every profile. Refinement of a request that is not ready (`protocols/refinement.md`) runs in every profile; in `auto`, one round at most. In `auto`, except for DIRECT's blocking questions, ask only when the evidence does not support one reading and a wrong reading would be expensive to undo; otherwise decide as §When a gate is off describes and record it.
