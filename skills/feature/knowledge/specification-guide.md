# Specification Guide

A specification states the problem and the expected behavior: **what** and **why**. It does not state *how*, unless the how is a genuine external constraint (a regulation, an API contract that must be honored, a platform the programmer mandates).

## What a specification is

**A specification is the team's current reading of the programmer's intent, not a closed contract.** The programmer's request, quoted verbatim, is the source; the specification is a working interpretation of it, written before the code exists, and so it is always incomplete. Treat it this way:

- **Intent wins over wording.** When the specification and the request diverge, the request and the programmer's answers win, and the divergence is a question. The specification never narrows the request silently: a broad statement in the request ("everywhere that…", "all…", "consistently") stays broad, and the places it reaches are listed as found so far, not as the complete set.
- **Requirements are the current understanding.** They are testable statements, so the work can be checked, but they describe what is known today. The list grows and changes as the work finds new facts.
- **"Outside the intent" is a reading too.** Each boundary records who drew it: the programmer (with their words) or the agent's reading of the request, to be confirmed. Only the programmer's boundaries are settled.
- **Discoveries go to the programmer.** When any phase (planning, implementation, testing, review) finds something the specification did not foresee, such as another place the intent reaches, a case the request implies, a contradiction with existing behavior or an easier path, it is a *discovery*. It is recorded and presented to the programmer with its relation to the request (see *Discoveries* below). Nobody, in any role, settles it alone: not by implementing it silently, and not by dismissing it as "not in the spec".
- **"Not in the specification" is never an argument.** A missing item means the specification did not foresee it, not that the programmer excluded it. An option is never presented as worse because it "goes beyond the spec".

## Discoveries

A discovery is recorded in the specification's *Discoveries* table (the card's, in Lean) and presented at the next gate, or at once if it blocks the work. Each one states, as facts:

- **What was found,** with evidence (`path:line`, a probe, a failing case).
- **Relation to the request:** *Covered by the request's words* (quote them), *Implied by the intent* (the reasoning, marked as reading), *Outside what the programmer stated*, or *Contradicts the request or an answer*.
- **Options,** in the neutral format: for example, change the code, change the specification, accept as a known limitation, or defer it to another feature. Each option states its effect on the work already done (files, tests, a later gate).

The programmer's decision updates the specification through its change log, like any other change. A discovery *covered by the request's words* that the specification missed is a specification defect: say so.

## Process

1. **Intent:** quote the request verbatim, then state who needs what outcome, and why. If you cannot state it in a few sentences, the intent is not clear yet: ask.
2. **Reach of the intent:** for every broad statement in the request ("everywhere that…", "all…", "any…", "consistently", "like X does"), search the repository and list the places it reaches, with the search you ran (the command or query) and its results. Record the list as *found so far*, so a later phase that finds another place compares it with this search.
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

## Evolutionary specifications (ESDD)

- **Item status:** Confirmed · Hypothesis · Under exploration · Rejected. Requirements that are no longer valid become Retired.
- **Change types:** Added · Clarified · Modified · Replaced · Retired. Each change bumps the spec version and adds a change-log row with its rationale and approval.
- **Prefer additive, traceable change,** but move obsolete requirements out of the active list (to Retired) rather than keeping contradictions alive for the sake of history.
- **Spec vs. plan:** a technical change in the plan does not imply a spec change. A functional change implies reassessing the plan and the tests (impact analysis).
