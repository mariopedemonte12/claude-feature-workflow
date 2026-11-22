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

**Leaner than the other workflows, on purpose:**
- **One gate per increment.** The intent gate opens the feature, an exploration gate runs only when the approach is in question, and each increment then has a single gate. Anything that does not block the work waits for it.
- **The Planner runs at the start and when the approach is in question.** You write each increment's entry in the plan yourself.
- **Mutation testing runs once,** at the end, over all the changed code.
- **`handoff.md` is written only to resume in another session:** when the session stops or the programmer pauses the feature. Resumed agents keep their context; a new agent's brief names the artifacts and sections it needs, from the transition checklists in `protocols/context-handoff.md`, instead of a handoff file.
- **The final report is short:** it points to the intent record, the cases and the decisions instead of summarizing them.

**Hybrid mode:** when uncertainty is confined to one area, run SDD Direct (`workflows/sdd-direct.md`) for the feature. The specification marks that area *Under exploration* and points here; Phases 2–4 below run only for the area, with its cases tracing to the intent record and decisions, until it is resolved enough for the Specification Writer to specify it.

## Phase 1: Intent (orchestrator)

**1. Understand and explore.** Start the intent record with the request verbatim, as `workflows/sdd-direct.md` step 1 describes. Delegate broad inspection to the Repository Analyst: existing behavior of the area, the nearest analog of the feature in the project, constraints, test framework and E2E tooling. Separate known from unknown, product from technical uncertainties, and classify each uncertainty as *blocking now* or *investigable later*.

**2. Intent pass.** Without writing a specification, prepare the first gate from the request and the analyst's evidence:
- the reach of each broad statement, with the search run and the places found so far (`knowledge/specification-guide.md` §Process, step 2);
- the ambiguity checklist of `knowledge/specification-guide.md`, kept to what blocks the first increment;
- the main flows the feature has, as candidates for the first increments;
- the specialists whose signals match (`protocols/specialists.md`).

**3. ⛔ Intent gate.** In one message: the proposed consolidated intent, version 1; the blocking questions only, each with what the analog does as a fact; the main flows; the specialists; the feature's **criticality** (Critical / Standard); and the **completion criteria**: what "done" means, in the programmer's words, so the loop has an agreed exit. On the answers, consolidate the intent (`templates/intent.md`) and record choices in `decisions/`. Later questions are asked when an increment needs them, not now.

## Phase 2: Approach

**4. Analyze the solution space and design the first cases.** In parallel: brief the Test Designer (`roles/test-designer.md`, Evolutionary mode) with the Intent → Test design checklist, to design the cases of the first increment's flow; and the Planner (`roles/planner.md`) with the Intent → Planning checklist. Relay their questions (`protocols/agent-questions.md`); each answer that changes the intent becomes a statement. The Planner maps approaches, architectural alternatives, feasibility, integration challenges, dependencies and risks. Each option includes reversibility and remaining uncertainty; where reasoning alone cannot settle a question, a **disposable prototype or experiment** is an option, with the question it answers, its cost, where it would live and how it would be discarded.

**5. ⛔ Approach gate.** Present the options following `protocols/neutral-decisions.md`, together with the first increment: its flow, its cases, and the edge cases of that flow it covers or defers. The programmer chooses among: continue exploring · validate a hypothesis · build a prototype · select an approach · change the intent · defer the decision. Settle at the same gate verification depth for the feature (mutation testing mandatory when Critical, otherwise a neutral question; the review level you recommend and the programmer validates), the specialists' plan-slot facts and the end-to-end harness, and bootstrap the anti-pattern registry if the project has none (`protocols/anti-pattern-registry.md`). Record the choices in `decisions/`.
- Prototypes live outside production code paths (e.g. a `spikes/` folder or a separate branch). They are discarded, or promoted only by an explicit programmer decision.
- This gate runs again only when the approach is in question. The Planner is resumed for it if it still exists.

## Phase 3: Increments

**6. Plan the increment.** You write its entry in `implementation-plan.md` (*Increments*): the flow it delivers, the hypotheses it confirms or rejects and how, its done criteria, and the edge cases of that flow it covers or defers. **A deferred edge case needs a programmer decision** (D-ID) naming the increment that will cover it; edge cases never accumulate silently. The first increment's entry is the one approved at the approach gate.

**7. Implement.** Brief the Implementer (`roles/implementer.md`); for later increments, resume the same Implementer (`SKILL.md` §4, *Reusing agents*). It writes production code only, for the increment's flow and the cases planned for it. It follows the approved approach, keeps changes focused, adds no speculative functionality and records discoveries and invalidated assumptions.

**8. Discoveries.** For each discovery, note its relation to the intent (`protocols/neutral-decisions.md` rule 15) and its impact: affected intent items (S-IDs, consolidated version), components, cases and tests, decisions, and the estimated consequences, with the minimum change that would satisfy the need as *one* option among the viable ones. **Only a discovery that blocks the work stops the increment** (⛔ at once); every other one goes to the increment gate.

**9. Test and review.** In parallel:
- **Tester** (`roles/tester.md`), resumed in later increments: implements the increment's designed cases as tests, then explores, to find missing behavior, wrong assumptions, ambiguous rules and integration limits. End-to-end tests through the real entry point (`knowledge/e2e-testing.md`) cover the increment's user-facing flow. Each black-box technique (BVA, Fuzz, Symbolic/Concolic, Decision Table, FSM) gets a status for the increment: Applied / Not applicable + justification / Blocked + explanation.
- **Review** at the validated level (`protocols/review-cycle.md`), on the increment's diff, re-checking the level against it; the first critic and the active specialist audits run with the Tester. Re-check the specialists' signals against the diff; a newly matching specialist is offered at the gate (`protocols/specialists.md`).

**10. ⛔ Increment gate.** The only gate of the increment. In one message:
- **Results:** tests, E2E, technique statuses, quality gate and review, separating observed facts from interpretations.
- **Findings and discoveries,** each with its relation to the intent and its impact (step 8), in the neutral format. Defect fixes follow `workflows/sdd-direct.md` §Defects, discrepancies and discoveries.
- **Hypotheses:** the proposed status of each one the increment touched (Confirmed with evidence · Under exploration · Rejected).
- **Deferred edge cases** still open, by increment.
- **Consolidated intent:** a proposed new version, when there are statements since the last gate.
- **Next:** the next increment's entry (flow, hypotheses, edge cases covered or deferred), or, if the completion criteria in the intent record are met, the move to finalization. If the approach is in question, the approach gate instead.
- **Anti-pattern candidates** of the increment (`protocols/anti-pattern-registry.md` §The learning loop).

**11. Evolve.** Apply what the programmer decided: consolidate the intent on their confirmation (`templates/intent.md`); record the hypotheses' statuses and the next increment's entry in the plan (with its change log); resume the Test Designer to update the affected cases and design the next increment's. A case whose source statement was superseded is retired, never left active, and keeps its ID. Then go to step 6.

## Phase 4: Finalization

**12. Mutation testing,** once, over all the code the feature changed, when the feature is Critical or the programmer chose it. Report scope, score, surviving mutants and the tests added for the gaps.

**13. Final report.** Write `reports/final-report.md` (`templates/final-report.md`), short: links to `intent.md` (final consolidated intent; its evolution in `intent-history.md`), `testing-plan.md` (the record of the behavior delivered) and `decisions/`, plus only what lives nowhere else: the increments delivered with their test results, the mutation testing result, **remaining hypotheses**, known limitations, accepted findings and outstanding risks. ⛔ The programmer decides final acceptance. Then apply the ⛔ integration and ⛔ cleanup gates exactly as in `workflows/sdd-direct.md`, steps 14–15.
