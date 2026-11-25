# Review Cycle Protocol

Code review is done by **clean agents**: a fresh subagent that never saw how the code was written reviews it from scratch, as critically as it can. In the full cycle, a second clean agent tries to refute each finding, confirmed findings are fixed, and a new clean critic reviews again.

## Review levels

| Level | What runs | Typical feature |
| --- | --- | --- |
| **R0 · Gate only** | The Implementer's quality gate and project lint. No review agent. | Mechanical change: rename, configuration, copy, dependency bump, a change that follows an existing pattern line by line |
| **R1 · Single critic** | One clean critic, in parallel with the Tester. Its findings go to the defects gate (unless it is off: `protocols/gates.md`). | Standard feature with new logic of moderate size |
| **R2 · Review cycle** | Clean critic (the first one in parallel with the Tester) → clean verifier → automatic fixes (after the Tester) → new clean critic, until the round cap (§R2 · The cycle). | Every Critical feature; Standard features that are large or complex |

**Critical features always use R2.** The orchestrator states it; it does not ask.

### Recommending the level

The recommendation goes in the plan gate (SDD step 6, EVO step 5; with the `depth` gate off, a level above the default by the size and risk criteria below applies and is reported, and a lower one is asked; the `depth` gate: `protocols/gates.md` §Profiles), labeled *Recommendation*, with the evidence behind it:

- **Size:** files and components the plan touches; estimated changed lines.
- **Complexity:** new branching logic, state machines, parsers, concurrency, money, security, data writes or migrations, public interfaces, changes across several features or layers.
- **Criticality.**

**Start from the default:** R1 for SDD and EVO; R2 for Critical (above). DIRECT: `workflows/direct.md` step 5. Recommend a different level only with evidence: lower to R0 only for a mechanical change with no new branching logic, none of the risk areas above and a small diff (on the order of 50 changed lines); raise to R2 for several risk areas or a large diff. The recommendation always states the default and why it deviates, if it does. A standing acceptance of recommendations covers only the default; a deviation is asked every time (standing approvals: `protocols/decisions.md` rule 7). The programmer validates or changes the level; record it in `decisions/` and in the plan's verification depth.

**Re-check after implementation.** Before review starts, compare the real diff (`git diff --shortstat <base>`, the files touched, the risk areas reached) with the estimate. If it crosses into another level, state the facts and recommend again; the programmer validates. With the `depth` gate off, a level above the one validated at plan time applies and is reported; a lower one is asked.

## Specialist audits

Specialists active in their `audit` phase (`protocols/skills.md`) are separate clean agents. They follow the critic's clean-context rules, run in parallel with it, and are never resumed. Their findings are never fixed automatically, at any level: they go to the defects gate, merged with the critic's; with that gate off, to acceptance, except a Blocker from a security audit, which is a hard stop (`protocols/gates.md` §Hard stops).

## Clean context

A critic's brief contains only: the feature worktree, the base commit, its role file, the output path and the programmer's own words: from the intent record: the original request, the confirmed consolidated intent and the statements since, verbatim. They let it check the reach of the intent (`roles/reviewer.md` §Method, step 4); they are what the programmer said, not how anyone read it. It does **not** receive, and must not open: the specification, the plan, decisions, handoffs, the implementation report, delegations, earlier review rounds, or anything else in the feature folder. It reads the code, `git diff <base>`, the project's own conventions (CLAUDE.md, lint configuration), the quality standard and the anti-pattern registry.

Each round launches a **new** critic. Never reuse a critic through SendMessage. Scope compliance against the spec is not the critic's job, but places the programmer's words reach and the diff does not are findings: the Tester validates the acceptance criteria and the orchestrator checks the implementation report against the plan.

## R2 · The cycle

```
round n:  Critic(n) ──► Verifier(n) ──► VALID behavior-preserving findings ──► Implementer fixes
              ▲                          everything else ──► defects gate        │
              └────────── tests + quality gate pass ◄────────────────────────────┘
```

1. **Critic** (`roles/reviewer.md`) writes `reports/review/round-<n>-critic.md` (in EVO, `inc<k>-round-<n>-critic.md`: §Rounds in EVO).
2. **Verifier** (`roles/verifier.md`), also clean, receives that report and tries to refute each finding against the code. Verdicts: VALID, INVALID, AMBIGUOUS. It classifies each VALID finding's fix as **behavior-preserving** (rename, extract, split by responsibility, remove duplication, remove code that this change itself left unused, simplify control flow, move to the right folder, without changing observable behavior or public interfaces; tests pass before and after) or **behavior-changing** (anything that changes outputs, errors, interfaces, the spec or the plan). It writes `reports/review/round-<n>-verification.md` (in EVO, `inc<k>-round-<n>-verification.md`).
3. **Fixes.** VALID behavior-preserving findings of severity Blocker, Major or Minor go to the Implementer without a gate, once the Tester has finished: the Implementer, resumed or replaced as `SKILL.md` §4, *Reusing agents* decides. It fixes them, runs the affected tests and the quality gate, and records what it changed per finding ID. Behavior-changing findings, AMBIGUOUS findings and every Blocker that touches correctness or security go to the ⛔ defects gate. Nits are collected for the final report, not fixed in the loop.
4. **Next round** with a new critic on the **diff since the previous round** (the fixes); what a later round reports: `roles/reviewer.md` §Rules. Round 1 is the only one that reviews the whole diff from the base (in EVO, the increment's diff: §Rounds in EVO).

**Stop when:**
- a round produces no new Blocker or Major finding; or
- the feature (in EVO, the increment) has had 3 critic rounds in total, counting every path (R1, R2 and the critics after defect fixes); or
- the loop oscillates: a finding asks to undo an earlier fix, or the same location is flagged again for the same problem after being fixed. Present the oscillation at the ⛔ defects gate.

**Cap reached with a Blocker or Major open.** When the loop stops at the cap, check every Blocker and Major finding of every round of the feature (in EVO, of the increment). A finding is **open** unless it was fixed and a later critic round reviewed the fix, the verifier refuted it (INVALID), or the programmer accepted it; a finding fixed after the last round is still open, because nobody reviewed its fix. With one or more open, the feature stops (a hard stop: `protocols/gates.md` §Hard stops) and asks the programmer how to proceed, in the decision format (`protocols/decisions.md`), listing each open finding with its ID, round, severity, location and why it is still open. With the `defects` gate on, this is presented at that gate. With none open, the loop stops and the feature continues as the rest of its workflow says. This applies on every path that runs a critic: SDD, EVO and Hybrid (per increment), both executor modes, and DIRECT when the programmer asks for a critic.

**Unreviewed commits.** A commit made after the last critic round of the feature (in EVO, of the increment), the fixes of that round included, was not reviewed, unless the programmer chose another round and it reviewed it. Before acceptance, list every such commit with its hash as **unreviewed** in the final report (§Review; with a card, its *Result*; in DIRECT, the report of `workflows/direct.md` step 6) and in the message that presents acceptance (in DIRECT, integration). It is never presented as reviewed.

**Rounds in EVO** count per increment: each increment's review starts at round 1 and has its own cap (*Stop when* above), since every increment's diff is reviewed (`workflows/evo.md` step 9). Reports are `reports/review/inc<k>-round-<n>-critic.md` and `inc<k>-round-<n>-verification.md`, and specialist audits `reports/review/inc<k>-<name>.md`; with a card, the same names under the card's `review/`. A DIRECT card has no increments: `review/round-<n>-critic.md`. `rounds.md` adds the increment to each row (§Round log and feedback).

After the loop, the Tester re-runs the regression suite and the E2E scenarios affected by the fixes.

## R1 · Single critic

The critic runs once, in parallel with the Tester, with the same clean context. It double-checks each finding itself before reporting. All findings go to the ⛔ defects gate. **At R1 nothing is fixed automatically**, not even behavior-preserving findings, unless the `defects` gate is off, with the limits of its row in `protocols/gates.md` (Blocker and Major the programmer's words cover). The orchestrator checks the validated level before routing any fix.

## Automatic fixes are visible

At R2, every automatic fix is listed at the next gate: finding ID, files and hunks changed, and a revert option. The orchestrator never originates a fix itself: a problem it notices in the diff becomes a finding like any other.

## Round log and feedback

The orchestrator keeps `reports/review/rounds.md`, one row per round: (EVO: increment ·) round · critic model · findings raised (Blocker/Major/Minor/Nit) · VALID / INVALID / AMBIGUOUS · fixed automatically · sent to the gate.

Feedback beyond the feature:
- A VALID finding that is likely to recur, or that appeared in more than one round, becomes an anti-pattern candidate (`protocols/anti-pattern-registry.md`). The verifier marks them; the orchestrator writes them to `reports/anti-pattern-candidates.md`.
- A VALID finding that matches an `automated` registry entry means its rule missed a case: record it as a candidate to fix the rule.
- The share of INVALID findings across features shows how noisy the critic is. Report it in the final report.
