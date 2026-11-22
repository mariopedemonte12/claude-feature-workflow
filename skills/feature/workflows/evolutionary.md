# Workflow: Evolutionary Development

Use it when requirements are incomplete or evolving, feasibility is uncertain, several approaches are plausible, or important discoveries are expected. The feature advances in small increments, main flows first, and what it must do is settled as the work goes, by the programmer, increment by increment. ⛔ marks a human gate: it stops this feature only, and other features keep moving.

**There is no specification document.** Three artifacts replace it, each with one owner:

| Artifact | Holds | Written by |
| --- | --- | --- |
| `intent.md` (`templates/intent.md`) | The programmer's words: original request, consolidated intent confirmed at each gate, statements since. Includes the completion criteria | Orchestrator |
| `decisions/` | Every choice the programmer made, with its options | Orchestrator |
| `testing-plan.md` | The executable criteria: every case with its expected result and the source it comes from (an S-ID, the consolidated intent version, a D-ID or repository evidence), including the edge, error, security and worst-case cases of each increment | Test Designer |

Hypotheses are the team's, not the programmer's, so they live in the plan's *Increments*, each with how an increment confirms or rejects it. Nothing else restates the requirements.

This workflow runs **per feature**, at Medium or High intensity (`protocols/intensity.md`). For each delegation, the executor and standard model come from `SKILL.md` §4; the orchestrator chooses the actual model per task and logs it in `delegations.md`. The Specification Writer does not run in this workflow.

**Hybrid mode:** when uncertainty is confined to one area, run SDD Direct (`workflows/sdd-direct.md`) for the feature. The specification marks that area *Under exploration* and points here; Phases 2–5 below run only for the area, with its cases tracing to the intent record and decisions, until it is resolved enough for the Specification Writer to specify it.

## Phase 1: Intent (orchestrator)

**1. Understand and explore.** Start the intent record with the request verbatim, as `workflows/sdd-direct.md` step 1 describes. Delegate broad inspection to the Repository Analyst: existing behavior of the area, the nearest analog of the feature in the project, constraints, test framework and E2E tooling. Separate known from unknown, product from technical uncertainties, and classify each uncertainty as *blocking now* or *investigable later*.

**2. Intent pass.** Without writing a specification, prepare the first gate from the request and the analyst's evidence:
- the reach of each broad statement, with the search run and the places found so far (`knowledge/specification-guide.md` §Process, step 2);
- the ambiguity checklist of `knowledge/specification-guide.md`, kept to what blocks the first increment;
- the main flows the feature has, as candidates for the first increments;
- the specialists whose signals match (`protocols/specialists.md`).

**3. ⛔ Intent gate.** In one message: the proposed consolidated intent, version 1; the blocking questions only, each with what the analog does as a fact; the main flows; the specialists; the feature's **criticality** (Critical / Standard); and the **completion criteria**: what "done" means, in the programmer's words, so the loop has an agreed exit. On the answers, consolidate the intent (`templates/intent.md`) and record choices in `decisions/`. Later questions are asked when an increment needs them, not now.

## Phase 2: Exploration and planning

**4. Analyze the solution space and design the first cases.** In parallel: brief the Test Designer (`roles/test-designer.md`, Evolutionary mode) with the Intent → Test design handoff, to design the cases of the first increment's flow; and the Planner (`roles/planner.md`) with the Intent → Planning handoff. Relay their questions (`protocols/agent-questions.md`); each answer that changes the intent becomes a statement. The Planner analyzes approaches, architectural alternatives, feasibility, integration challenges, dependencies and risks.

**5. Explore alternatives.** Each option includes reversibility and remaining uncertainty. Where reasoning alone cannot settle a question, the Planner describes a **disposable prototype or experiment** as an option: the question it answers, its cost, where it would live and how it would be discarded.

**6. ⛔ Exploration and decision.** Present the options following `protocols/neutral-decisions.md`, together with the first increment's cases and any proposed new consolidated intent. The programmer chooses among: continue exploring · validate a hypothesis · build a prototype · select an approach · change the intent · defer the decision. Record the choice in `decisions/`.
- Prototypes live outside production code paths (e.g. a `spikes/` folder or a separate branch). They are discarded, or promoted only by an explicit programmer decision.

**7. Plan the next increment.** Write or update `implementation-plan.md`: the approved approach plus its *Increments* section (`templates/implementation-plan.md`). Plan only the next increment in detail: the flow it delivers, the hypotheses it confirms or rejects and how, its done criteria, and the edge cases of that flow it covers or defers. **A deferred edge case needs a programmer decision** (D-ID) naming the increment that will cover it; edge cases never accumulate silently for later. At the first increment, also settle verification depth, the specialists' plan-slot facts and the end-to-end harness as in SDD Direct step 6 (mutation testing and R2 mandatory when Critical; otherwise a neutral question for mutation testing and a recommended review level the programmer validates), and bootstrap the anti-pattern registry if the project has none (`protocols/anti-pattern-registry.md`). Write the Planning → Implementation handoff.

## Phase 3: Incremental implementation

**8. Implement a small, coherent increment.** Brief the Implementer (`roles/implementer.md`); for later increments, resume the same Implementer (`SKILL.md` §4, *Reusing agents*). It writes production code only, for the increment's flow and the cases planned for it. It follows the approved approach, keeps changes focused, adds no speculative functionality and records discoveries and invalidated assumptions.

**9. Reassess.** For each discovery, run a targeted impact analysis: does it affect the intent, the cases, the architecture, the implementation strategy or the testing strategy? Do not change everything automatically. If it affects the intent or a programmer decision → ⛔.

## Phase 4: Testing and discovery

**10. Functional and exploratory testing.** Brief the Tester (`roles/tester.md`), or resume the same one in later increments. It implements the increment's designed cases as tests, then explores. Testing both checks expected behavior and discovers missing behavior, wrong assumptions, ambiguous rules, unexpected behavior, architectural limits and integration constraints. End-to-end tests through the real entry point (`knowledge/e2e-testing.md`) cover each increment's user-facing flow.

**11. Black-box techniques.** Each of BVA, Fuzz, Symbolic/Concolic, Decision Table and FSM gets a status for the increment: Applied / Not applicable + justification / Blocked + explanation.

**12. Mutation testing and review.** Mutation testing is mandatory if Critical or requested; otherwise only if decided at the gate. Report scope, score, surviving mutants and gaps. Run the review at the validated level (`protocols/review-cycle.md`), re-checking the level against each increment's real diff; the first critic and the active specialist audits run in parallel with testing. Re-check the specialists' signals against each increment's diff; a newly matching specialist is offered again (`protocols/specialists.md`).

**13. ⛔ Increment validation.** Present the results and findings, separating observed facts from interpretations and hypotheses, and every discovery with its relation to the intent (`protocols/neutral-decisions.md` rule 15). Include the deferred edge cases still open, by increment, and the proposed new consolidated intent if there are statements since the last gate. Present the increment's anti-pattern candidates in the same gate (`protocols/anti-pattern-registry.md` §The learning loop).

## Phase 5: Evolution and iteration

**14. Classify each hypothesis** in the plan's *Increments*: Confirmed (evidence or programmer approval) · Under exploration · Rejected, with the evidence.

**15. Evolve the intent and the cases.** The programmer's decisions at the gate are statements; consolidate the intent on their confirmation (`templates/intent.md`). Then resume the Test Designer to update the affected cases and design the next increment's: a case whose source statement was superseded is retired, never left active, and keeps its ID.

**16. Evolve the plan.** Update `implementation-plan.md` (plan change log). A technical change does not imply an intent change, while a change of intent requires reassessing the plan and the cases.

**17. Impact analysis before any significant change:**
1. affected intent items (S-IDs, consolidated version);
2. affected components;
3. affected cases and tests;
4. affected decisions;
5. estimated consequences;
6. identify the minimum change that would satisfy the need, and present it as *one* option among the viable ones, not as the default;
7. present the options neutrally;
8. ⛔ obtain approval.

**Loop:** go back to Phase 2 (if the approach is in question) or to step 7 (next increment) until the completion criteria in the intent record are met. Update `handoff.md` at every transition.

## Phase 6: Finalization

Write `reports/final-report.md` (`templates/final-report.md`), including: the final consolidated intent and how it evolved (`intent-history.md`), important discoveries, approved decisions, implemented increments, the cases as the record of the behavior delivered, architecture and implementation changes, testing performed, validation results, **remaining hypotheses**, known limitations and outstanding risks. ⛔ The programmer decides final acceptance. Then apply the ⛔ integration and ⛔ cleanup gates exactly as in `workflows/sdd-direct.md`, steps 14–15.
