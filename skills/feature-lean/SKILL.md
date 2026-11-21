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
- **Card:** create `docs/features/<slug>/feature.md` from `templates/feature-card.md`, or use the project's docs convention. Write "Lean" in its title line, and keep the card within 80 lines.

**2. Read only what the feature needs:**
- CLAUDE.md, the code of the affected area, its tests, and the build, test and lint commands;
- `.quality/` if it exists;
- `knowledge/code-quality.md`.

Do not read the rest of the library.

**3. Specification pass.** In the card's *Requirements and acceptance criteria*:
- **Request:** quote the request verbatim.
- **Behavior:** testable statements, each traced to the request or to `path:line` evidence.
- **Edge and error cases:** enumerate, for each input:
  - boundaries, empty and missing values;
  - invalid values and encodings;
  - error paths, with their message and exit or status;
  - duplicates and ordering;
  - concurrency, if any.
- **Security:** escaping, injection, safe-marking, authorization and trust boundaries the feature touches.
- **Worst case:** the input size or shape that costs the most time or memory, and the bound expected.
- **Acceptance criteria:** Given/When/Then, each covering a behavior or a case.

**4. ⛔ Gate 1: behavior and approach.** In one message, each item shown in full:
- **Blocking questions**, each with why it matters and its options, if closed.
- **Approach.**
  - If more than one approach is viable, present them in the neutral format. Each option carries two fields: **Security consequence**, and **Worst case**, probed or Unknown.
  - For options involving parsers, regular expressions, escaping or safe-marking, run a quick probe before the gate: a timing loop that doubles the input size, and an injection string. Report what it printed.
  - If only one approach is viable, state it with the excluded alternatives and the constraint each violates.
- **Choices by convention.** Implementation details you will settle by following the project's existing conventions, one line each. The programmer may override any of them.
- **Approval:** end with approve · change (what) · reject.

Record every answer in the card's *Decisions*, with the date.

**5. Implement.**
- **Code:** follow `knowledge/code-quality.md` and the registry. Do only the approved scope.
- **Tests:**
  - a unit test for every acceptance criterion, and for every edge, error, security and worst-case item;
  - an end-to-end test through the real entry point when the feature is user-facing and the project has a harness (`knowledge/e2e-testing.md`);
  - when the project has no harness, a note in the card, without installing anything unapproved.
- **Checks:** run the tests, the project's lint and type checks, and `python3 <library>/scripts/quality_gate.py --repo <worktree> --base <base>`. Fix what you wrote.
- **New questions:** a discovery that changes approved behavior is a new ⛔ question.

**6. Clean critic.** Launch one subagent, `general-purpose`, model `opus`, with this brief and nothing else (no summary of the feature, no card):

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
- **Test and gate results:** commands and real output, summarized.
- **Findings:** every one, with severity, concrete case and your check result. Options for each: fix · accept as a known limitation · change the behavior. Accepting a reproduced Blocker requires the programmer's stated reason, recorded in the card and repeated at acceptance.
- **Unresolved items:** anything you could not settle.

**9. Fix** what the programmer chose, then run the tests and the gate again. A second critic runs only if the programmer asks: same brief, task "review `git diff <commit before fixes>` (later round)".

**10. ⛔ Acceptance, integration and cleanup.**
- **Card:** write its *Result*: files changed, test commands with real results, gate result, `shortcut:` markers, known limitations, accepted findings.
- **Acceptance:** the programmer decides.
- **Integration:** present it neutrally: merge, rebase then merge, pull request, or leave the branch unmerged. Include the facts: uncommitted changes, commits ahead and behind, and files also changed on the target since the base.
- **Cleanup:** then ask whether to remove the worktree and branch. Execute only what is chosen. Commit the work on its branch only as part of the chosen integration.

## Resume

`resume <slug>`: locate `.claude/worktrees/<slug>` (`git worktree list`), enter it with `EnterWorktree` (`path`), read its card, and continue from its *State*.

## When Lean is not enough

If the feature needs exploration with prototypes, several features coordinated together, mutation testing or the full review cycle, you may tell the programmer once that `/feature` provides it. Never start it yourself.
