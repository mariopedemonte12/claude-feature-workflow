# Workflow: SDD Direct

Use it when the intent is clear, the expected behavior is predictable, technical uncertainty is low and existing architecture gives a reasonable direction. ⛔ marks a human gate: stop this feature and wait for the programmer (other features keep moving).

This workflow runs **per feature**, at the feature's intensity: `protocols/intensity.md` says which steps, agents, gates and artifacts apply at Lite, Medium and High. For each delegation, the executor and standard model come from `SKILL.md` §4; the orchestrator chooses the actual model per task and logs it in `delegations.md`.

## Phase 1: Specification (orchestrator)

**1. Understand.** Write the programmer's request, verbatim, to `request.md` in the feature folder. Delegate broad inspection of the affected area to the Repository Analyst (existing behavior, constraints, conventions).

**2. Specify.** Brief the Specification Writer (`roles/spec-writer.md`) with the Request → Specification handoff. Relay its questions as `protocols/agent-questions.md` describes, append every answer to `request.md`, and resume the same agent until it returns `STATUS: DONE`. Then check the draft against `knowledge/specification-guide.md`: every item has a source, no implementation details unless they are genuine external constraints, no invented requirements, every open question marked blocking or non-blocking. Ask the programmer for the feature's **criticality** (Critical / Standard). It determines whether mutation testing and the R2 review cycle are mandatory.

**3. ⛔ Review.** Present a summary of the spec and its blocking questions. Resolve blocking ambiguity. Once the programmer approves, set the spec status to `Approved (YYYY-MM-DD)`. An unapproved spec never feeds planning.

## Phase 2: Implementation

**4. Analyze.** Brief the Repository Analyst: architecture evidence, folder organization, affected components, integration points, conventions, existing tests, E2E tooling, quality tooling, build/test commands. Skip this if the orchestrator already holds enough evidence. If the project has no `.quality/` registry, run the bootstrap in `protocols/anti-pattern-registry.md` (⛔ its own gate; it may share the step 6 gate). Write the Specification → Planning handoff.

**5. Plan.** Brief the Planner (`roles/planner.md`). It returns implementation options, or a single option with the excluded alternatives when only one is viable. If it returns questions (a spec gap, a constraint only the programmer knows), relay them and resume it as `protocols/agent-questions.md` describes before presenting options; an answer that changes the approved spec goes back to the Specification Writer as a spec change.

**6. ⛔ Decide.**
- Check that the planner's output follows `protocols/neutral-decisions.md` (fix ordering or wording if needed) and present it.
- In the same gate, settle verification depth:
  - **Critical feature:** mutation testing and the R2 review cycle are mandatory. State this; do not ask.
  - **Standard feature:** ask neutrally whether to run mutation testing, stating what it adds (what it can detect) and what it costs (time, tooling, possible new dev dependency). For review, **recommend** a level (R0 / R1 / R2) starting from the intensity default, with its evidence, as `protocols/review-cycle.md` §Recommending the level describes; the programmer validates or changes it.
- In the same gate, settle the **end-to-end harness** when the project has none for this surface: present what installing it involves (packages, browser downloads, containers) and the alternatives (a simulation harness, Blocked with its residual risk) as neutral options. End-to-end testing itself is not optional for user-facing features; only how it runs is decided here.
- Record the decision in `decisions/` (`templates/decision-record.md`).
- Write `implementation-plan.md` (`templates/implementation-plan.md`) for the approved approach only, with a one-line mention of each alternative not chosen and the decision reference.
- Write the Planning → Implementation handoff.

**7. Implement.** Brief the Implementer (`roles/implementer.md`). If it reports that the plan is invalid or that a deviation is needed, that is a new programmer decision: ⛔ present it neutrally, update `decisions/` and the plan, then resume. The implementer writes `reports/implementation-report.md` and the Implementation → Testing handoff.

## Phase 3: Testing and validation

**8–11. Test.** Brief the Tester (`roles/tester.md`). It writes `testing-plan.md`, then performs:
- functional testing (acceptance criteria, negative scenarios, error handling, integration, regression);
- end-to-end testing through the real entry point (`knowledge/e2e-testing.md`), with status Applied / Not applicable + justification / Blocked + explanation;
- evaluation of each black-box technique (Boundary Value Analysis, Fuzz, Symbolic/Concolic, Decision Table, Finite State Machine), with status Applied / Not applicable + justification / Blocked + explanation;
- mutation testing, if mandatory or decided at step 6;
- validation against the approved spec, in `reports/validation-report.md`, plus the Testing → Finalization handoff.

**Review**, at the validated level (`protocols/review-cycle.md`). First re-check the level against the real diff. R1: one clean critic (`roles/reviewer.md`) **in parallel** with testing. R2: the first critic runs in parallel with testing, then the verify → fix → new-critic cycle; after it ends, the Tester re-runs the regression and E2E scenarios the fixes affect. R0: no review agent.

**Defects and discrepancies.** ⛔ Present them to the programmer, including review findings that the cycle does not fix automatically. Fix now / accept as a known limitation / change the spec are options under the neutral protocol. Fixes go back to the Implementer with a focused handoff, followed by a re-run of the affected tests, and, when the level is R1 or R2, a new clean critic on the fix diff within the feature's cap of 3 critic rounds (`protocols/review-cycle.md`).

**Anti-pattern candidates.** ⛔ In the same gate (or before acceptance if there were no defects), present `reports/anti-pattern-candidates.md` as described in `protocols/anti-pattern-registry.md` §The learning loop, steps 3–4. Update the registry with what the programmer approves; approved rule automation goes to the Implementer.

## Phase 4: Finalization

**12.** Write `reports/final-report.md` from `templates/final-report.md`, using only evidence from the reports. Unverified items are reported as unverified. If the reports are large, a subagent may compile a draft (model chosen per `SKILL.md` §4); verify it before presenting.

**13. ⛔ Acceptance.** The programmer decides final acceptance.

**14. ⛔ Integration.** The feature's code and artifacts live on its worktree branch. Present how to integrate it as a neutral decision, for example: merge into the target branch, rebase then merge, open a pull request, or leave the branch unmerged for now. Include the facts:
- uncommitted changes in the worktree;
- commits ahead of and behind the target;
- files changed by this feature that also changed on the target since the base (intersect `git diff --name-only <base>` run in the worktree with `git diff --name-only <base> <target>`);
- files that other in-progress features also change.

Execute only what the programmer chooses. Committing the feature's work on its branch is part of carrying out the chosen integration, never something done before the choice.

**15. ⛔ Cleanup.** After integration, or if the feature is abandoned, ask whether to remove the worktree and its branch. Removal destroys local state: do it only with the programmer's confirmation.

## Definition of done (ready for acceptance)

- [ ] Spec approved; plan approved.
- [ ] Implementation matches the approved scope; deviations recorded and approved.
- [ ] Relevant tests executed; every acceptance criterion evaluated with evidence.
- [ ] End-to-end testing has a status; every user-facing acceptance criterion has E2E evidence or a stated reason.
- [ ] Every black-box technique has a status with a justification.
- [ ] Quality gate passes on the feature's changes, or each remaining violation is reported with a decision reference.
- [ ] Anti-pattern candidates presented and the registry updated with the approved ones.
- [ ] Mandatory or decided mutation testing performed; review run at the validated level, with its round log.
- [ ] Regressions evaluated.
- [ ] Decisions documented; limitations and risks reported; no blocking issue concealed.
- [ ] Final report and handoff complete.

Code being written, or tests passing, does not by itself make a feature done.
