---
name: specification-guide
kind: guide
summary: What a specification is, deepening the request, the reach of the intent, discoveries, ambiguity checklist, acceptance criteria
use-in: [intent, spec, test-design]
workflows: [sdd, evo]
---
# Specification Guide

A specification states the problem and the expected behavior: **what** and **why**. It does not state *how*, unless the how is a genuine external constraint (a regulation, an API contract that must be honored, a platform the programmer mandates).

## What a specification is

**A specification is the team's current reading of the programmer's intent, not a closed contract.** Its source is the **intent record** (`templates/intent.md`): `intent.md` in the feature folder, or the card's *Intent* section when the feature uses a card (EVO in executor mode). The record holds the original request, verbatim and never edited; a *consolidated intent* that the programmer confirmed at the last gate; and their statements since, verbatim, limited to those that change the intent. The request evolves as the programmer talks, and the record is where it evolves: a recent statement wins over the consolidated intent, which wins over the original request. At each gate the new statements are consolidated with the programmer's confirmation, and the absorbed ones move to an archive, so the record stays short. The specification is a working interpretation of the record, written before the code exists, and so it is always incomplete. Treat it this way:

- **Intent wins over wording.** When the specification and the intent record diverge, the record wins, and the divergence is a question. The consolidated intent counts as the programmer's words only once they confirmed it. The specification never narrows the request silently: a broad statement in the request ("everywhere that…", "all…", "consistently") stays broad, and the places it reaches are listed as found so far, not as the complete set.
- **Requirements are the current understanding.** They are testable statements, so the work can be checked, but they describe what is known today. The list grows and changes as the work finds new facts.
- **"Outside the intent" is a reading too.** Each boundary records who drew it: the programmer (with their words) or the agent's reading of the request, to be confirmed. Only the programmer's boundaries are settled.
- **Discoveries go to the programmer.** When any phase (planning, implementation, testing, review) finds something the specification did not foresee, such as another place the intent reaches, a case the programmer's words imply, a contradiction with existing behavior or an easier path, it is a *discovery*. It is recorded and presented to the programmer with its relation to the intent (see *Discoveries* below). Nobody, in any role, settles it alone: not by implementing it silently, and not by dismissing it as "not in the spec".
- **"Not in the specification" is never an argument.** A missing item means the specification did not foresee it, not that the programmer excluded it. An option is never presented as worse because it "goes beyond the spec".

## Discoveries

A discovery is recorded in the specification's *Discoveries* table (the card's, when the feature uses one) and presented at the next gate, or at once if it blocks the work. Each one states, as facts:

- **What was found,** with evidence (`path:line`, a probe, a failing case).
- **Relation to the intent:** *Covered by the programmer's words* (quote them, from the original request or a statement, with its S-ID), *Implied by the intent* (the reasoning, marked as reading), *Outside what the programmer stated*, or *Contradicts the original request or a statement*. Cite the latest statement on the point: it wins.
- **Options,** in the decision format: for example, change the code, change the specification, accept as a known limitation, or defer it to another feature. Each option states its effect on the work already done (files, tests, a later gate).

The programmer's decision updates the specification through its change log, like any other change. A discovery *covered by the programmer's words* that the specification missed is a specification defect: say so. The programmer's decision on a discovery is itself a statement: it is appended to the intent record before the specification changes.

## Deepen the request

Before writing the requirements (SDD step 2, EVO intent pass), make the reading of the request **deeper, not bigger**. Answer four questions, adapted from the `sharpen` skill of pstack (github.com/cursor/plugins, MIT):

1. **What would a top professional in this field do here that the request does not ask for?** Each answer is a reading or a question for the programmer, related to the intent as rule 9 of `protocols/decisions.md` describes. Nothing enters the scope without their word.
2. **What is the rawest material to start from,** instead of what has already been digested: real inputs, logs, data, the library's source rather than its docs, the standard or RFC rather than a summary of it, the existing behavior observed in a run.
3. **Which methods and tools** that discipline uses would settle the open points: a probe, a measurement (`knowledge/measurement.md`), a formal model, a reference implementation, a property test.
4. **What, other than the agent or the programmer, would show the result is right:** an external oracle such as a reference implementation, a test suite of the standard, recorded production inputs, a formal model, another tool's output on the same input.

**Empirical forks** (behavior, timing, which approach works) are settled by a probe or a disposable prototype, and what was observed is reported as facts in the options' fields. Choices of product or preference, which no experiment settles, are the programmer's. Neither gets a recommendation: `protocols/decisions.md` applies.

Write the answers in the intent pass or the specification's context, a few lines each; an answer that adds nothing is written as "none found".

## Process

1. **Intent:** read the intent record, then state who needs what outcome, and why, citing the consolidated intent version and the statements (S-n) each part rests on. If you cannot state it in a few sentences, the intent is not clear yet: ask.
2. **Reach of the intent:** for every broad statement in the original request or a statement ("everywhere that…", "all…", "any…", "consistently", "like X does"), search the repository and list the places it reaches, with the search you ran (the command or query) and its results. Record the list as *found so far*, so a later phase that finds another place compares it with this search.
3. **Existing behavior:** what the system does today in this area, with evidence (`path:line` or an observed run).
4. **Requirements:** record each one with its source (programmer message, ticket, existing behavior, regulation). Without a source, it is not a requirement; it is a question or a hypothesis.
5. **Constraints vs. invariants:**
   - *Constraint:* an external limit on the solution space ("must not change public API v1", "p95 < 200 ms", "must run on the existing Postgres").
   - *Invariant:* a property that must always hold in the system ("a balance is never negative", "each order has exactly one owner").
6. **Acceptance criteria:** observable, testable and unambiguous, in Given / When / Then form. Every FR is covered by at least one AC. Include negative and error criteria.
7. **Non-functional requirements:** only when relevant, and measurable (latency, throughput, availability, security, accessibility, compatibility). A vague NFR ("fast") becomes a question asking for a number, unless the programmer accepts it as qualitative.
8. **Ambiguity sweep:** go through the checklist below.
9. **Open questions:** mark each one **Blocking** (planning or implementation cannot proceed correctly without it) or **Non-blocking** (can be resolved later). A non-blocking question gets no invented default answer.

## Ambiguity checklist

- Undefined terms, or terms used inconsistently.
- Boundaries: inclusive or exclusive, empty, zero, maximum, duplicates.
- Error behavior: invalid input, partial failure, timeout, conflict, retry.
- Actors and permissions: who can do it, and what others see.
- Data and state: existing data, migration, concurrent modification.
- Interacting rules: combinations of conditions.
- Scope edges: what the programmer has said is outside the intent, and what is only the agent's reading.
- Contradictions with existing behavior or with other requirements.

## Do not

- Fill a gap with a plausible guess and call it a requirement.
- Prescribe classes, functions, schemas, frameworks, algorithms, file layout or patterns.
- Over-specify details nobody knows yet. Leave them as open questions or hypotheses.
- Mark something Confirmed without the programmer's approval or evidence.
- Turn a broad statement of the request into a closed list. List what the search found, as found so far.
- Declare something outside the intent on your own reading without marking it as a reading to confirm.

## IDs

`FR-n`, `NFR-n`, `C-n`, `INV-n`, `AC-n`, `Q-n`, `H-n`. IDs are never reused. A retired item keeps its ID, with status Retired.

## Evolving specifications (Hybrid)

In Hybrid mode, the specification evolves while one area runs the evolutionary loop. EVO itself has no specification: the intent record, the decisions and the cases replace it (`workflows/evo.md`).


- **Item status:** Confirmed · Hypothesis · Under exploration · Rejected. Requirements that are no longer valid become Retired.
- **Change types:** Added · Clarified · Modified · Replaced · Retired. Each change bumps the spec version and adds a change-log row with its rationale and approval.
- **Prefer additive, traceable change,** but move obsolete requirements out of the active list (to Retired) rather than keeping contradictions alive for the sake of history.
- **Spec vs. plan:** a technical change in the plan does not imply a spec change. A functional change implies reassessing the plan and the tests (impact analysis).
