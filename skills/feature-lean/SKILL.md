---
name: feature-lean
description: Lean feature pipeline. This session specifies the feature and its edge cases, asks the programmer, implements with tests, and gets one clean critic review, with no orchestrator relay. Manual invocation only.
argument-hint: "<feature description> | resume <slug>"
disable-model-invocation: true
---

# Feature Lean

The programmer wants the pieces of the feature workflow that showed value at the lowest cost:
- a specification pass that enumerates edge, error, security and worst-case behavior;
- their answers before any code;
- code with tests and the quality gate;
- one review by a clean critic that never saw the code being written.

**You do the work yourself.** There is no orchestrator relay. The only subagent is the critic.

- **Request:** $ARGUMENTS
- **Command name:** `/feature-lean` standalone, `/feature-workflow:feature-lean` as a plugin.
- **Library:** `${CLAUDE_SKILL_DIR}/../feature`. Every path below is relative to it; read it by its absolute path.
- **Language:** the programmer's for conversation; the project's documentation language for the card.
- **One feature per session.** Several features in parallel means several sessions, each in its own worktree.

## Principles

1. **The programmer decides** scope, observable behavior, risk acceptance, dependencies and integration. Read `protocols/neutral-decisions.md` before presenting the first decision and follow it, including rules 13b (no defaults by silence) and 14.
2. **Ask, don't guess.** A question whose answer changes the output for a valid input is blocking (`protocols/agent-questions.md` §For the agent, "Blocking or not"). Never weaken an acceptance criterion to avoid asking.
3. **Evidence over assertion.** Report only what was run. A test not run is never "passed".
4. **No silent drift.** Any change of scope or behavior after a gate goes back to the programmer.

## Steps

**1. Worktree.**
- **Create and stay:** call `EnterWorktree` with `name: "<slug>"` (load it with ToolSearch if deferred) and **stay in it**: you are the one who works there. Record its path, branch and base commit (`git rev-parse --short HEAD`).
- **On failure:** if it cannot be created, stop and present the situation neutrally. Never work in the shared checkout on your own.
- **Card:** create `docs/features/<slug>/feature.md` from `templates/feature-card.md`, or use the project's docs convention. Write "Lean" in its title line, with a target of 500 lines. The target is never a cut: when the feature needs more, keep the card as the summary and move the overflow to `decisions/D-NNN-<topic>.md` or `feature-appendix.md` next to it, linked by section. Never leave out a requirement, case or decision because of size, and report the total size at the next gate.

**2. Read only what the feature needs:**
- CLAUDE.md, the code of the affected area, its tests, and the build, test and lint commands;
- `.quality/` if it exists;
- `knowledge/code-quality.md`;
- `knowledge/testing-techniques.md`;
- `knowledge/design-patterns.md`, only when a design pattern is being considered.

Do not read the rest of the library.

**3. Specification pass.** In the card's *Requirements and acceptance criteria*:
- **Request:** quote the request verbatim.
- **Nearest analog:** the existing feature of the project most like this one (a template tag for a tag, a form field for a field, a filter for a filter), with its `path:line`. Read how it handles each case listed below: empty and invalid input, whitespace, exceptions raised by user-supplied objects, escaping and safe-marking, error messages. If there is no analog, say so.
- **Behavior:** testable statements, each traced to the request or to `path:line` evidence.
- **Edge and error cases:** each case states what the analog does with it, as a fact (e.g. "`CharField` strips surrounding whitespace by default, `django/forms/fields.py:…`"). Enumerate, for each input:
  - boundaries, empty and missing values;
  - invalid values and encodings;
  - error paths, with their message and exit or status;
  - duplicates and ordering;
  - concurrency, if any.
- **Security:** escaping, injection, safe-marking, authorization and trust boundaries the feature touches.
- **Worst case:** the input size or shape that costs the most time or memory, and the bound expected.
- **Acceptance criteria:** Given/When/Then, each covering a behavior or a case.

**4. ⛔ Gate 1: behavior and approach.** In one message, each item shown in full:
- **Blocking questions**, each with why it matters, its options if closed, and what the analog does. The analog is a fact attached to the question, never a recommendation: an option that matches it and one that departs from it are presented alike.
- **Approach.**
  - If more than one approach is viable, present them in the neutral format. Each option carries two fields: **Security consequence**, and **Worst case**, probed or Unknown.
  - For options involving parsers, regular expressions, escaping or safe-marking, run a quick probe before the gate: a timing loop that doubles the input size, and an injection string. Report what it printed.
  - If only one approach is viable, state it with the excluded alternatives and the constraint each violates.
- **Choices by convention.** Implementation details you will settle by following the project's existing conventions, one line each. The programmer may override any of them.
- **Criticality:** ask whether the feature is Critical or Standard. Critical makes mutation testing **mandatory**: state that, do not ask whether to run it. For a Standard feature, ask neutrally whether to run it, stating what it can detect and what it costs. When it will run and the project has no mutation tool, present installing one (a new dev dependency) and leaving it *Blocked* with its residual risk as neutral options.
- **Approval:** end with approve · change (what) · reject.

Record every answer in the card's *Decisions*, with the date.

**5. Implement.**
- **Code:** follow `knowledge/code-quality.md` and the registry. Do only the approved scope.
- **Tests:**
  - a unit test for every acceptance criterion, and for every edge, error, security and worst-case item;
  - each technique of `knowledge/testing-techniques.md` (Boundary Value Analysis, Fuzz/property-based, Decision Table, Finite State Machine, Symbolic/Concolic) gets one status in the card's *Result*: Applied (what was tested) or Not applicable + the reason;
  - fuzz or property-based tests on every input that crosses a trust boundary or receives user-supplied objects, including objects whose comparison, conversion or iteration raises, with the expected behavior taken from the approved spec;
  - an end-to-end test through the real entry point when the feature is user-facing and the project has a harness (`knowledge/e2e-testing.md`);
  - when the project has no harness, a note in the card, without installing anything unapproved.
- **Mutation testing**, when the feature is Critical or the programmer chose it, after the tests pass. Follow `knowledge/testing-techniques.md` §Mutation Testing:
  - scope it to the changed code;
  - classify every surviving mutant as test gap, equivalent or out of scope;
  - add or strengthen tests for the test gaps;
  - report the scope, tool, totals, score and survivors in the card's *Result*.

  If the tool was not approved, its status is *Blocked*, with the residual risk.
- **Checks:** run the tests, the project's lint and type checks, and `python3 <library>/scripts/quality_gate.py --repo <worktree> --base <base>`. Fix what you wrote.
- **New questions:** a discovery that changes approved behavior is a new ⛔ question.

**6. Clean critic.** Launch one subagent in the background (`run_in_background: true` where the Agent tool offers it), `general-purpose`, model `opus`, with this brief and nothing else (no summary of the feature, no card). Tell the programmer in one line that it started, and wait for its notification. If the programmer asks for a second critic later, launch a **new** one: critics are never resumed.

```
You are the Clean Code Critic for a code change.
Feature worktree: <path> (branch <branch>). Start every shell command with `cd <worktree> &&`. First confirm `git -C <worktree> branch --show-current` prints <branch>; if not, stop and report. Never call EnterWorktree.
1. Read and follow your role file: <library>/roles/reviewer.md
Task: review `git diff <base>` (round 1). Do not open <worktree>/docs/features/<slug>/.
Output: <worktree>/docs/features/<slug>/review.md
Return: a summary of at most 150 words.
```

**7. Check every finding** against the code, and add your result to `review.md` next to it:
- **Reproduced**, with evidence;
- **Not reproduced**, with what you tried;
- **Unclear**.

Discard nothing: the programmer sees every finding.

**8. ⛔ Gate 2: findings and results.** In one message:
- **Test and gate results:** commands and real output, summarized, including the mutation score and the surviving mutants when mutation testing ran.
- **Findings:** every one, with severity, concrete case and your check result. Options for each: fix · accept as a known limitation · change the behavior. Accepting a reproduced Blocker requires the programmer's stated reason, recorded in the card and repeated at acceptance.
- **Unresolved items:** anything you could not settle.

**9. Fix** what the programmer chose. For each Blocker or Major that changes behavior, first write a test that reproduces it and run it to see it fail; then fix and see it pass (`knowledge/code-quality.md` §1, *Test first for defects*). Run the tests and the gate again. A second critic runs only if the programmer asks: same brief, task "review `git diff <commit before fixes>` (later round)".

**10. ⛔ Acceptance, integration and cleanup.**
- **Card:** write its *Result*: files changed, test commands with real results, testing technique statuses, mutation testing results (or *not run*, with the reason), gate result, `shortcut:` markers, known limitations, accepted findings.
- **Acceptance:** the programmer decides.
- **Integration:** present it neutrally: merge, rebase then merge, pull request, or leave the branch unmerged. Include the facts: uncommitted changes, commits ahead and behind, and files also changed on the target since the base.
- **Cleanup:** then ask whether to remove the worktree and branch. Execute only what is chosen. Commit the work on its branch only as part of the chosen integration.

## Resume

`resume <slug>`: locate `.claude/worktrees/<slug>` (`git worktree list`), enter it with `EnterWorktree` (`path`), read its card, and continue from its *State*.

## When Lean is not enough

If the feature needs exploration with prototypes, several features coordinated together, separate test design and testing agents, or the full review cycle, you may tell the programmer once that `/feature` provides it. Never start it yourself.
