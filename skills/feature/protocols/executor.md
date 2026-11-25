# Executor Mode

In executor mode the session **does the feature's work itself** instead of orchestrating agents. It follows the feature's workflow file step by step, playing every role the step names, with three exceptions that need a context the session does not have:

| Part | Why it is separate | Who runs it |
| --- | --- | --- |
| The clean critic, and its verifier when one runs | It must not have seen the code being written | A subagent the session launches (§The critic) |
| Specialist audits | Same reason | Subagents, launched with the critic (`protocols/skills.md` §Specialists) |
| The Test Designer, in SDD | It designs from the approved specification and must never see the plan | **A separate session the programmer opens** (§Sessions the programmer opens) |

Everything else the workflow file assigns to a role (Repository Analyst, Specification Writer, Planner, Implementer, Tester, and in EVO the Test Designer) is the session's own work. It reads the role file for its method and checklists, and skips what belongs to delegation: briefs, return formats, handoffs, `delegations.md`.

One feature per executor session. Several features at once means several sessions, each in its own worktree, or an orchestrator.

## Principles

Questions are always allowed: whatever the gate profile, ask the programmer directly when only they can answer and the work is blocked (`protocols/gates.md` §Questions).


The principles of `SKILL.md` §1 apply, except 9: the executor changes project code, because it is the one doing the work. Read `protocols/decisions.md` before the first decision and follow it, including rules 7 (no defaults by silence), 9 (scope framed against the intent record) and 10 (relaying).

## Worktree

- **Create and stay** (DIRECT: `workflows/direct.md` §Where the work happens decides whether a worktree is created; with none, the claim records the current checkout): call `EnterWorktree` with `name: "<slug>"` (load it with ToolSearch if deferred) and **stay in it**. Record its path, branch and base commit (`git rev-parse --short HEAD`).
- **On failure:** if it cannot be created, stop and present the situation to the programmer. Never work in the shared checkout on your own.
- **Claim:** write the feature's claim (`protocols/hierarchy.md` §Claims) with `orchestrator` set to this session and `mode: "executor"`, so orchestrators and other sessions see it.

## Artifacts

| Workflow | Artifacts |
| --- | --- |
| SDD | The folder of `SKILL.md` §6 (specialist runs: `protocols/skills.md` §Logging): `intent.md`, `specification.md`, `implementation-plan.md`, `testing-plan.md` (written by the Test Designer's session), `decisions/`, `reports/review/`. No `delegations.md` and no handoff file (`handoff.md` or `handoff-<role>.md`); `state.md` at every stop (a gate, a pending question, the end of the turn, a pause) |
| EVO | **One card**, `feature.md` (`templates/feature-card.md`), plus `decisions/` and appendices when it overflows. Its Intent section is the intent record, its Cases section replaces `testing-plan.md`, and its Increments section replaces the plan; in EVO the card's *State* plays the role of `state.md`, written at every stop |

The card has a target of 500 lines, never a cut: keep the card as the summary, move the overflow to `decisions/D-NNN-<topic>.md` or `feature-appendix.md`, linked by section, and report the total size at the next gate.

## EVO as executor

Follow `workflows/evo.md`, with these changes:

1. **Intent pass** (steps 1–2), in the card. *Intent*: the original request verbatim and a proposed consolidated intent, version 1 (or the one refinement confirmed, with its *Refinement* section), with the completion criteria. *Scope*: the reach of each broad statement, with the search run. *Nearest analog*, *Main flows*, and the *Cases* of every main flow, from `knowledge/edge-cases.md` §Before code. Cases of later flows may be revised when their increment starts.
2. **Gates 3 and 5 are one gate** (`[gate: intent, specialists, approach, depth, bootstrap]`), in one message, holding only the items whose gates are on in the feature's profile (`protocols/gates.md`); the items of gates that are off are decided by you and reported in the same message, each item in full: consolidated intent and readings to confirm; blocking questions with what the analog does; the approach (several viable: the decision format, each option with **Security consequence** and **Worst case**, probed or Unknown; one viable: it, with the excluded alternatives); **increments** as a question (one for the whole feature, one per main flow, or another grouping), with the cases in full; choices by convention, one line each; specialists; criticality and mutation testing; the review level you recommend; approve · change · reject. If `spec` or `plan` specialists run, bring their questions back in a short gate 1b before implementing.
3. **Each increment** (steps 6–11): you implement the flow and write a test for every case of the increment, with each technique of `knowledge/testing-techniques.md` given a status, fuzz or property tests on every input that crosses a trust boundary, and an end-to-end test when the flow is user-facing and the project has a harness. Run the tests, lint, type checks and `scripts/quality_gate.py`. Record in the card's *State* the commit where the increment started. Then the review at the validated level (`protocols/review-cycle.md`: R0 no critic; R1 one critic; R2 critic → verifier → fixes → new critic, up to 3 rounds; Critical is always R2) and the active audits on the increment's diff; check every finding (§Checking findings); then the ⛔ increment gate as `workflows/evo.md` step 10 describes (a report when `increment` is off).
4. **Fixes:** for each Blocker or Major that changes behavior, first a test that reproduces it, seen failing, then the fix (`knowledge/code-quality.md` §Test first for defects). At R1, a second critic on the fixes runs only if the programmer asks; at R2 the cycle runs it; a fixed audit finding (fixed only on the programmer's decision) gets a new auditor on the fix diff.
5. **Finalization** (steps 12–13): mutation testing once when chosen or Critical; the card's *Result*; then ⛔ acceptance, and the integration and cleanup hard stops.

## SDD as executor

Follow `workflows/sdd.md`, with these changes:

1. **Steps 1–3:** you explore and write `specification.md` yourself, following `roles/spec-writer.md` and `knowledge/specification-guide.md`. ⛔ Spec gate (`[gate: intent, specialists]`) as written.
2. **Step 5:** once the spec is approved, write the Test Designer's brief (§Sessions the programmer opens) and tell the programmer how to open its session. **Then plan**, following `roles/planner.md`, while that session works. You never read `testing-plan.md` while planning, and you never write it.
3. **Step 6 (⛔ plan gate, `[gate: approach, depth]`):** present the plan and the testing plan together, as written. If the Test Designer's session has not finished, present the plan and say the testing plan is pending; the gate closes when both are approved. With both gates off, you approve them yourself and report it, but you still wait for the Test Designer's `testing-plan.md`: that wait is a dependency, not a gate.
4. **Steps 7–11:** you implement, then implement the designed cases as tests and test, following `roles/implementer.md` (without its no-tests rule) and `roles/tester.md`. Then review at the validated level (§The critic).
5. **Defects, finalization:** as in `workflows/sdd.md`, with fixes made by you, test first.

## The critic

Launch one subagent in the background (`run_in_background: true` where the Agent tool offers it), `general-purpose`, model `opus`, with this brief and nothing else. Tell the programmer in one line that it started, and wait for its notification. Specialist auditors get the same brief, with `Read and follow your specialist file: <path> (section Slot: audit)` and their own output file. Never resume any of them: every round and every increment is a new agent.

```
You are the Clean Code Critic for a code change.
Feature worktree: <path> (branch <branch>). Start every shell command with `cd <worktree> &&`. First confirm `git -C <worktree> branch --show-current` prints <branch>; if not, stop and report. Never call EnterWorktree.
1. Read and follow your role file: <skill dir>/roles/reviewer.md
Skills for this phase: <absolute paths of the review guides that apply, protocols/skills.md>
Task: review `git diff <base, or the commit where this increment started; from round 2, the commit of the previous round>` (round <n>). Do not open <feature folder>.
Original request (verbatim): <from the intent record>
Consolidated intent (confirmed, version n): <from the intent record>
Statements since (verbatim; a statement wins over the consolidated intent): <each S-n; never an unconfirmed proposal>
Output: <feature folder>/reports/review/round-<n>-critic.md   (EVO: inc<k>-round-<n>-critic.md, and with a card <feature folder>/review/inc<k>-round-<n>-critic.md; `protocols/review-cycle.md` §Rounds in EVO)
Return: a summary of at most 150 words.
```

At R2 (`protocols/review-cycle.md`), the verifier is a second clean subagent (`sonnet`, `roles/verifier.md`) with the critic's report; with a card, its output is `<feature folder>/review/inc<k>-round-<n>-verification.md`.

## Checking findings

Check every finding of the critic and the specialists against the code, re-run their evidence, merge duplicates, and add your result next to each in its report: **Reproduced** with evidence · **Not reproduced** with what you tried · **Unclear**. Discard nothing: the programmer sees every finding, with its relation to the intent (`protocols/decisions.md` rule 9). When the programmer's words cover a finding, say so with the quote and its S-ID; updating the cases or the spec is an effect of the fix, never an argument against it.

## Sessions the programmer opens

When a part must run in a context of its own and is not a subagent, the executor:

1. writes its brief to `<feature folder>/briefs/<role>.md`, in the format of `SKILL.md` §4 *Briefing a subagent*, with `Programmer channel: you talk to the programmer directly` in place of the questions line;
2. tells the programmer the command, in one line: `/feature role <role> <slug>`, to run in a new Claude Code session opened in this repository;
3. keeps working on what does not depend on it, and when the programmer says it finished, reads its output and its *Questions* section.

**The role session** (`/feature role <role> <slug>`, `SKILL.md` §2) locates the worktree, reads the brief and the role file, and does that role's work only. It asks the programmer directly, never guessing, and records each question and answer in its output's *Questions* section (in `testing-plan.md`, its §Open questions), so the executor can append the ones that change the intent to the intent record. It never reads what its brief excludes (for the Test Designer: the plan) and ends by telling the programmer to return to the executor session.

The programmer may also choose to open a role session for any other role, instead of the executor doing that part; the same procedure applies.

## Resume

`/feature resume <slug>` in executor mode: locate `.claude/worktrees/<slug>` (`git worktree list`) and enter it with `EnterWorktree` (`path`), or, for DIRECT with a card kept in the checkout, the feature folder its claim records (DIRECT without a card is not resumable: say so); read the card's *State* (EVO, DIRECT) or `state.md` (SDD), and continue.
