# Workflow: Evolutionary Spec-Driven Development (ESDD)

Use it when requirements are incomplete or evolving, feasibility is uncertain, several approaches are plausible, or important discoveries are expected. Specification, plan and implementation evolve together, in increments. ⛔ marks a human gate: it stops this feature only, and other features keep moving.

This workflow runs **per feature**, at Medium or High intensity (`protocols/intensity.md`). For each delegation, the executor and standard model come from `SKILL.md` §4; the orchestrator chooses the actual model per task and logs it in `delegations.md`.

**Hybrid mode:** when uncertainty is confined to one area, run SDD Direct (`workflows/sdd-direct.md`) for the feature, and apply Phases 2–5 below only to the uncertain area, until it is resolved enough to plan it directly.

## Phase 1: Initial specification (orchestrator)

**1. Understand and explore.** Write the programmer's request, verbatim, to `request.md`. Separate known from unknown requirements, product from technical uncertainties, and existing system constraints from candidate exploration areas. Classify each uncertainty as *blocking now* or *investigable later*. Delegate broad inspection to the Repository Analyst.

**2. Initial specification.** Brief the Specification Writer (`roles/spec-writer.md`), relaying its questions and resuming it until it returns `STATUS: DONE` (`protocols/agent-questions.md`). It writes `specification.md` with: intent, known requirements, constraints, invariants, initial acceptance criteria, open questions and hypotheses. Every item carries a status: Confirmed / Hypothesis / Under exploration / Rejected. Ask the programmer for the feature's **criticality** (Critical / Standard) and for the **completion criteria**: what "done" means for this feature, so the loop has an agreed exit.

**3. ⛔ Collaborative review.** Resolve blocking questions only. The initial spec does not need to anticipate future discoveries.

## Phase 2: Solution exploration and planning

**4. Analyze the solution space.** Brief the Planner (`roles/planner.md`) with the Specification → Planning handoff, relaying any questions it returns (`protocols/agent-questions.md`): possible approaches, architectural alternatives, feasibility, integration challenges, dependencies, risks.

**5. Explore alternatives.** Each option includes reversibility and remaining uncertainty. Where reasoning alone cannot settle a question, the planner describes a **disposable prototype or experiment** as an option: the question it answers, its cost, where it would live and how it would be discarded.

**6. ⛔ Collaborative exploration and decision.** Present the options following `protocols/neutral-decisions.md`. The programmer chooses among: continue exploring · validate a hypothesis · build a prototype · select an approach · modify requirements · defer the decision. Record the choice in `decisions/`.
- Prototypes live outside production code paths (e.g. a `spikes/` folder or a separate branch). They are discarded, or promoted only by an explicit programmer decision.

**7. Plan the next increment.** Write or update `implementation-plan.md`: the approved approach plus an **Increments** section (goal, hypothesis it validates if any, done criteria). Plan only the next increment in detail. At the first gate, also settle verification depth and the end-to-end harness as in SDD Direct step 6 (mutation testing and R2 mandatory when Critical; otherwise a neutral question for mutation testing and a recommended review level the programmer validates), and bootstrap the anti-pattern registry if the project has none (`protocols/anti-pattern-registry.md`). Write the Planning → Implementation handoff.

## Phase 3: Incremental implementation

**8. Implement a small, coherent increment.** Brief the Implementer (`roles/implementer.md`). It implements only justified behavior, follows the approved approach, keeps changes focused, adds no speculative functionality and records discoveries and invalidated assumptions.

**9. Reassess.** For each discovery, run a targeted impact analysis: does it affect requirements, constraints, architecture, implementation strategy, or testing strategy? Do not change everything automatically. If it affects a programmer decision → ⛔.

## Phase 4: Testing and discovery

**10. Functional and exploratory testing.** Brief the Tester (`roles/tester.md`). Testing both checks expected behavior and discovers missing requirements, wrong assumptions, ambiguous rules, unexpected behavior, architectural limits and integration constraints. End-to-end tests through the real entry point (`knowledge/e2e-testing.md`) cover each increment's user-facing criteria.

**11. Black-box techniques.** Each of BVA, Fuzz, Symbolic/Concolic, Decision Table and FSM gets a status: Applied / Not applicable + justification / Blocked + explanation.

**12. Mutation testing.** Mandatory if Critical or requested; otherwise only if decided at the gate. Report scope, score, surviving mutants and gaps. Run the review at the validated level (`protocols/review-cycle.md`), re-checking the level against each increment's real diff; the first critic runs in parallel with testing.

**13. ⛔ Collaborative validation.** Present the findings, separating observed facts from interpretations and hypotheses. Present the increment's anti-pattern candidates in the same gate (`protocols/anti-pattern-registry.md` §The learning loop).

## Phase 5: Evolution and iteration

**14. Classify each relevant discovery:** Confirmed (evidence or programmer approval) · Hypothesis · Under exploration · Rejected.

**15. ⛔ Evolve the specification.** The Specification Writer applies the approved changes. Requirements may be Added, Clarified, Modified, Replaced or Retired. Each change bumps the spec version and adds a change-log row with its rationale and approval. Prefer additive, traceable evolution, but move obsolete requirements to Retired rather than keeping contradictions active. The programmer approves every requirement change.

**16. Evolve the plan.** Update `implementation-plan.md` (plan change log). Keep spec and plan separate: a technical change does not imply a requirement change, while a functional change requires reassessing the plan and the tests.

**17. Impact analysis before any significant change:**
1. affected requirements;
2. affected components;
3. affected tests;
4. affected decisions;
5. estimated consequences;
6. identify the minimum change that would satisfy the need, and present it as *one* option among the viable ones, not as the default;
7. present the options neutrally;
8. ⛔ obtain approval.

**Loop:** go back to Phase 2 (if the approach is in question) or Phase 3 (next increment) until the completion criteria agreed in Phase 1 are met. Update `handoff.md` at every transition.

## Phase 6: Finalization

Write `reports/final-report.md` (`templates/final-report.md`), including: final spec state and its evolution, important discoveries, approved decisions, implemented increments, architecture and implementation changes, testing performed, validation results, **remaining hypotheses**, known limitations and outstanding risks. ⛔ The programmer decides final acceptance. Then apply the ⛔ integration and ⛔ cleanup gates exactly as in `workflows/sdd-direct.md`, steps 14–15.
