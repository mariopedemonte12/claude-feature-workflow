# Workflow: SDD Direct

Use it when the intent is clear, the expected behavior is predictable, technical uncertainty is low and existing architecture gives a reasonable direction. ⛔ marks a human gate: stop this feature and wait for the programmer (other features keep moving).

This workflow runs **per feature**. For each delegation, the executor and standard model come from `SKILL.md` §4; the orchestrator chooses the actual model per task and logs it in `delegations.md`.

## Phase 1: Specification (orchestrator)

**1. Understand.** Feature intent; existing behavior in the area; requirements; constraints; invariants; ambiguities; contradictions; missing information. Delegate broad inspection to the Repository Analyst. Read `knowledge/specification-guide.md`.

**2. Specify.** Write `specification.md` from `templates/specification.md`. Keep it minimal but sufficient: no implementation details unless they are genuine external constraints, no invented requirements, and every open question marked blocking or non-blocking. Ask the programmer for the feature's **criticality** (Critical / Standard). It determines whether mutation testing and independent review are mandatory.

**3. ⛔ Review.** Present a summary of the spec and its blocking questions. Resolve blocking ambiguity. Once the programmer approves, set the spec status to `Approved (YYYY-MM-DD)`. An unapproved spec never feeds planning.

## Phase 2: Implementation

**4. Analyze.** Brief the Repository Analyst: architecture evidence, affected components, integration points, conventions, existing tests, build/test commands. Skip this if the orchestrator already holds enough evidence. Write the Specification → Planning handoff.

**5. Plan.** Brief the Planner (`roles/planner.md`). It returns implementation options, or a single option with the excluded alternatives when only one is viable.

**6. ⛔ Decide.**
- Check that the planner's output follows `protocols/neutral-decisions.md` (fix ordering or wording if needed) and present it.
- In the same gate, settle verification depth:
  - **Critical feature:** mutation testing and independent review are mandatory. State this; do not ask.
  - **Standard feature:** ask neutrally whether to run mutation testing and whether to run an independent review. For each, state what it adds (what it can detect) and what it costs (time, tooling, possible new dev dependency).
- Record the decision in `decisions/` (`templates/decision-record.md`).
- Write `implementation-plan.md` (`templates/implementation-plan.md`) for the approved approach only, with a one-line mention of each alternative not chosen and the decision reference.
- Write the Planning → Implementation handoff.

**7. Implement.** Brief the Implementer (`roles/implementer.md`). If it reports that the plan is invalid or that a deviation is needed, that is a new programmer decision: ⛔ present it neutrally, update `decisions/` and the plan, then resume. The implementer writes `reports/implementation-report.md` and the Implementation → Testing handoff.

## Phase 3: Testing and validation

**8–11. Test.** Brief the Tester (`roles/tester.md`). It writes `testing-plan.md`, then performs:
- functional testing (acceptance criteria, negative scenarios, error handling, integration, regression);
- evaluation of each black-box technique (Boundary Value Analysis, Fuzz, Symbolic/Concolic, Decision Table, Finite State Machine), with status Applied / Not applicable + justification / Blocked + explanation;
- mutation testing, if mandatory or decided at step 6;
- validation against the approved spec, in `reports/validation-report.md`, plus the Testing → Finalization handoff.

If independent review applies, brief the Reviewer (`roles/reviewer.md`) **in parallel** with testing. It writes `reports/review-report.md`.

**Defects and discrepancies.** ⛔ Present them to the programmer. Fix now / accept as a known limitation / change the spec are options under the neutral protocol. Fixes go back to the Implementer with a focused handoff, followed by a re-run of the affected tests (and re-review of the fix when review applies).

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
- [ ] Every black-box technique has a status with a justification.
- [ ] Mandatory or decided mutation testing and review performed.
- [ ] Regressions evaluated.
- [ ] Decisions documented; limitations and risks reported; no blocking issue concealed.
- [ ] Final report and handoff complete.

Code being written, or tests passing, does not by itself make a feature done.
