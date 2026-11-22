---
name: feature-lean
description: Lean feature pipeline. This session keeps the programmer's intent, settles every case with them before code, delivers the feature in one increment or several (their choice), and gets a clean critic review of each increment, with no orchestrator relay. Manual invocation only.
argument-hint: "<feature description> [--with <specialist>,…] | resume <slug>"
disable-model-invocation: true
---

# Feature Lean

The programmer wants the pieces of the feature workflow that showed value at the lowest cost:
- an intent record of the programmer's own words, consolidated with them at each gate;
- every edge, error, security and worst-case case settled before the code, delivered in one increment or in several, main flows first, as the programmer chooses;
- code with tests and the quality gate;
- a review of each increment by a clean critic that never saw the code being written.

**You do the work yourself.** There is no orchestrator relay. The only subagent is the critic.

- **Request:** $ARGUMENTS
- **Command name:** `/feature-lean` standalone, `/feature-workflow:feature-lean` as a plugin.
- **Library:** `${CLAUDE_SKILL_DIR}/../feature`. Every path below is relative to it; read it by its absolute path.
- **Language:** the programmer's for conversation; the project's documentation language for the card.
- **One feature per session.** Several features in parallel means several sessions, each in its own worktree.

## Principles

1. **The programmer decides** scope, observable behavior, risk acceptance, dependencies and integration. Read `protocols/neutral-decisions.md` before presenting the first decision and follow it, including rules 13b (no defaults by silence), 15 (scope framed against the request) and 16.
2. **Ask, don't guess.** A question whose answer changes the output for a valid input is blocking (`protocols/agent-questions.md` §For the agent, "Blocking or not"). Never weaken an acceptance criterion to avoid asking.
3. **Evidence over assertion.** Report only what was run. A test not run is never "passed".
4. **No silent drift, in either direction.** The request evolves as the programmer talks: the card's *Intent* is the intent record (`templates/intent.md`), with the original request verbatim, a consolidated intent they confirmed at the last gate, and their statements since that change the intent (S-n, asked or not, verbatim). The cases are the current reading of that record, not a closed contract (`knowledge/specification-guide.md` §What a specification is). Any change of scope or behavior after a gate goes back to the programmer, and so does anything found later that their words seem to reach: it is a *discovery*, framed against the intent record (`protocols/neutral-decisions.md` rule 15), never dismissed as out of scope.

## Steps

**1. Worktree.**
- **Create and stay:** call `EnterWorktree` with `name: "<slug>"` (load it with ToolSearch if deferred) and **stay in it**: you are the one who works there. Record its path, branch and base commit (`git rev-parse --short HEAD`).
- **On failure:** if it cannot be created, stop and present the situation neutrally. Never work in the shared checkout on your own.
- **Card:** create `docs/features/<slug>/feature.md` from `templates/feature-card.md`, or use the project's docs convention. Write "Lean" in its title line, with a target of 500 lines. The target is never a cut: when the feature needs more, keep the card as the summary and move the overflow to `decisions/D-NNN-<topic>.md` or `feature-appendix.md` next to it, linked by section. Never leave out a requirement, case or decision because of size, and report the total size at the next gate.

**2. Read only what the feature needs:**
- CLAUDE.md, the code of the affected area, its tests, and the build, test and lint commands;
- the registry if it exists: `<repo>/.quality/`, or `$(git rev-parse --git-common-dir)/quality/` when it is local;
- `knowledge/code-quality.md`;
- `knowledge/specification-guide.md`, only §What a specification is and §Discoveries;
- `workflows/evolutionary.md`, only its opening section (the artifacts that replace the specification);
- the frontmatter only of every specialist file, and `protocols/specialists.md` when one matches or the request uses `--with`; the full specialist file only once it is active;
- `knowledge/testing-techniques.md`;
- `knowledge/design-patterns.md`, only when a design pattern is being considered.

Do not read the rest of the library.

**3. Intent pass.** Lean follows `workflows/evolutionary.md` without its separate agents, and how many increments the feature has is the programmer's choice: there is no specification; the card's intent record, decisions and cases carry what the feature must do. In the card:
- **Intent:** the original request verbatim, and a proposed consolidated intent, version 1, to confirm at gate 1, including the **completion criteria**: what "done" means, in the programmer's words. From here on, append every statement of the programmer that changes the intent as an S-ID; at each gate with new statements, propose the next version and consolidate on their confirmation (`templates/intent.md`).
- **Scope:** the reach of each broad statement in the programmer's words ("everywhere that…", "all…", "consistently"), with the search you ran and the places it found so far, including subclasses, overrides and copies of the same list or rule; and what a reader might assume is included and the request does not say, each item your reading, to confirm at gate 1.
- **Nearest analog:** the existing feature of the project most like this one (a template tag for a tag, a form field for a field, a filter for a filter), with its `path:line`. Read how it handles: empty and invalid input, whitespace, exceptions raised by user-supplied objects, escaping and safe-marking, error messages. If there is no analog, say so.
- **Main flows:** the feature's main flows, in order, as the possible split into increments.
- **Cases,** in the card's *Cases*, for every main flow: every case with its expected result and its source (the request, an S-ID, a D-ID, or `path:line` for existing behavior to keep), stating what the analog does as a fact. Enumerate, for each input of the flow:
  - boundaries, empty and missing values;
  - invalid values and encodings;
  - error paths, with their message and exit or status;
  - duplicates and ordering;
  - concurrency, if any;
  - security: escaping, injection, safe-marking, authorization and trust boundaries;
  - worst case: the input size or shape that costs the most time or memory, and the bound expected.

  Cases of later flows may be revised when their increment starts.

**4. ⛔ Gate 1: intent, approach and first increment.** In one message, each item shown in full:
- **Consolidated intent**, proposed, with the completion criteria, to confirm or correct, and the **readings to confirm:** the reach found so far and each item you read as outside the intent.
- **Blocking questions**, each with why it matters, its options if closed, and what the analog does. The analog is a fact attached to the question, never a recommendation: an option that matches it and one that departs from it are presented alike. Questions that only later increments need wait for them.
- **Approach.**
  - If more than one approach is viable, present them in the neutral format. Each option carries two fields: **Security consequence**, and **Worst case**, probed or Unknown.
  - For options involving parsers, regular expressions, escaping or safe-marking, run a quick probe before the gate: a timing loop that doubles the input size, and an injection string. Report what it printed.
  - If only one approach is viable, state it with the excluded alternatives and the constraint each violates.
- **Increments,** a neutral question with the facts of each option: one increment for the whole feature (one critic and one increment gate), one per main flow (a critic and a gate per flow, with feedback before the next flow starts), or another grouping the programmer names. With the cases, in full. Each edge case the programmer wants to defer needs their decision naming the increment that will cover it.
- **Choices by convention.** Implementation details you will settle by following the project's existing conventions, one line each. The programmer may override any of them.
- **Specialists** (`protocols/specialists.md`): build the index and check signals against the request and the intent pass. Present the matching ones as facts (signals, slots, cost) and ask which run in which slots. Those with `mandatory-when: critical`, such as `security`, run on a Critical feature: state it. `--with <name>` in the request activates them directly. If `spec` or `plan` slots are chosen, run them right after this gate and bring back their questions and facts in a short **gate 1b** before implementing; `test-design` specialists add cases to each increment.
- **Criticality:** ask whether the feature is Critical or Standard. Critical makes mutation testing **mandatory**, once at the end: state that, do not ask whether to run it. For a Standard feature, ask neutrally whether to run it, stating what it can detect and what it costs. When it will run and the project has no mutation tool, present installing one (a new dev dependency) and leaving it *Blocked* with its residual risk as neutral options.
- **Approval:** end with approve · change (what) · reject.

Record every answer in the card's *Decisions*, with the date, and, when it changes the intent, append it to the intent record as a statement.

Steps 5 to 9 run once per increment: once in total when the programmer chose a single increment. Record in the card's *State* the commit where each increment starts.

**5. Implement the increment.**
- **Code:** follow `knowledge/code-quality.md` and the registry. Do only the increment's flow and its cases.
- **Tests:**
  - a test for every case of the increment;
  - each technique of `knowledge/testing-techniques.md` (Boundary Value Analysis, Fuzz/property-based, Decision Table, Finite State Machine, Symbolic/Concolic) gets one status for the increment in the card's *Result*: Applied (what was tested) or Not applicable + the reason;
  - fuzz or property-based tests on every input of the flow that crosses a trust boundary or receives user-supplied objects, including objects whose comparison, conversion or iteration raises, with the expected behavior taken from the cases;
  - an end-to-end test through the real entry point when the flow is user-facing and the project has a harness (`knowledge/e2e-testing.md`);
  - when the project has no harness, a note in the card, without installing anything unapproved.
- **Checks:** run the tests, the project's lint and type checks, and `python3 <library>/scripts/quality_gate.py --repo <worktree> --base <base>`. Fix what you wrote.
- **Discoveries:** anything found that the gates did not settle, such as another place the programmer's words reach or a case they imply, goes to the card's *Discoveries* with its relation to the intent. Only one that blocks the work is a ⛔ question at once; the rest go to the increment gate.

**6. Clean critic, and the active specialist audits,** on the increment's diff. Launch them together, all in the background, all clean. A specialist auditor gets the same brief as the critic below, except: `Read and follow your specialist file: <path> (section Slot: audit)` and output `<worktree>/docs/features/<slug>/<name>-<increment>.md`. Never resume any of them; every increment and every later round is a new agent.

The critic: launch one subagent in the background (`run_in_background: true` where the Agent tool offers it), `general-purpose`, model `opus`, with this brief and nothing else (no summary of the feature, no card). Tell the programmer in one line that it started, and wait for its notification.

```
You are the Clean Code Critic for a code change.
Feature worktree: <path> (branch <branch>). Start every shell command with `cd <worktree> &&`. First confirm `git -C <worktree> branch --show-current` prints <branch>; if not, stop and report. Never call EnterWorktree.
1. Read and follow your role file: <library>/roles/reviewer.md
Task: review `git diff <commit where this increment started>` (round 1). Do not open <worktree>/docs/features/<slug>/.
Original request (verbatim): <from the card's Intent>
Consolidated intent (confirmed, version n): <from the card's Intent>
Statements since (verbatim; a statement wins over the consolidated intent): <each S-n; never an unconfirmed proposal>
Output: <worktree>/docs/features/<slug>/review-<increment>.md
Return: a summary of at most 150 words.
```

**7. Check every finding** of the critic and the specialists against the code, and add your result next to it in its report. Re-run each specialist's evidence (exploit, query plan, timing, screenshot steps). Merge findings that describe the same problem:
- **Reproduced**, with evidence;
- **Not reproduced**, with what you tried;
- **Unclear**.

Discard nothing: the programmer sees every finding.

**8. ⛔ Increment gate.** The only gate of the increment. In one message:
- **Test and gate results:** commands and real output, summarized.
- **Findings and discoveries:** every finding of the critic and the specialists, and every new entry of the card's *Discoveries*, grouped by domain, with severity, concrete case or evidence, your check result and its relation to the intent (`protocols/neutral-decisions.md` rule 15). Specialist findings are never fixed without the programmer's choice. Options for each: fix · accept as a known limitation · change the behavior. When the programmer's words cover a finding, say so, with the quote and its S-ID; updating the cases is an effect of the fix, never an argument against it. Accepting a reproduced Blocker requires the programmer's stated reason, recorded in the card and repeated at acceptance.
- **Deferred edge cases** still open, with the increment each is planned for.
- **Consolidated intent:** a proposed new version, when there are statements since the last gate.
- **Next:** the next increment's flow and cases (each edge case covered or *to defer*), or, when the completion criteria are met, the move to acceptance. The programmer may also regroup the remaining increments: merge them into one, split one, reorder them.
- **Unresolved items:** anything you could not settle.

**9. Fix and evolve.** Fix what the programmer chose: for each Blocker or Major that changes behavior, first write a test that reproduces it and run it to see it fail; then fix and see it pass (`knowledge/code-quality.md` §1, *Test first for defects*). After a specialist's finding is fixed, launch a **new** auditor of that specialist on the fix diff only. Run the tests and the gate again; a second critic on the fixes runs only if the programmer asks. Then consolidate the intent if they confirmed a new version, retire the cases whose source statement was superseded (they keep their IDs), and continue with the next increment at step 5.

**10. ⛔ Finalization: mutation testing, acceptance, integration and cleanup.**
- **Mutation testing**, once, over all the code the feature changed, when the feature is Critical or the programmer chose it. Follow `knowledge/testing-techniques.md` §Mutation Testing: classify every surviving mutant as test gap, equivalent or out of scope; add or strengthen tests for the test gaps; report scope, tool, totals, score and survivors. If the tool was not approved, its status is *Blocked*, with the residual risk.
- **Card:** write its *Result*: the increments delivered with their test commands and real results, testing technique statuses, specialists run and their results (or *not run*, with the decision), mutation testing results (or *not run*, with the reason), gate result, `shortcut:` markers, known limitations, accepted findings, deferred edge cases never covered (each with its decision).
- **Acceptance:** the programmer decides.
- **Integration:** present it neutrally: merge, rebase then merge, pull request, or leave the branch unmerged. Include the facts: uncommitted changes, commits ahead and behind, and files also changed on the target since the base.
- **Cleanup:** then ask whether to remove the worktree and branch. Execute only what is chosen. Commit the work on its branch only as part of the chosen integration.

## Resume

`resume <slug>`: locate `.claude/worktrees/<slug>` (`git worktree list`), enter it with `EnterWorktree` (`path`), read its card, and continue from its *State*.

## When Lean is not enough

If the feature needs exploration with prototypes, a separate Planner, several features coordinated together, separate test design and testing agents, or the full review cycle, you may tell the programmer once that `/feature` provides it. Never start it yourself.
