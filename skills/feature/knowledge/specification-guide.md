# Specification Guide

A specification states the problem and the expected behavior: **what** and **why**. It does not state *how*, unless the how is a genuine external constraint (a regulation, an API contract that must be honored, a platform the programmer mandates).

## Process

1. **Intent:** who needs what outcome, and why. If you cannot state it in a few sentences, the intent is not clear yet: ask.
2. **Existing behavior:** what the system does today in this area, with evidence (`path:line` or an observed run).
3. **Requirements:** record each one with its source (programmer message, ticket, existing behavior, regulation). Without a source, it is not a requirement; it is a question or a hypothesis.
4. **Constraints vs. invariants:**
   - *Constraint:* an external limit on the solution space ("must not change public API v1", "p95 < 200 ms", "must run on the existing Postgres").
   - *Invariant:* a property that must always hold in the system ("a balance is never negative", "each order has exactly one owner").
5. **Acceptance criteria:** observable, testable and unambiguous, in Given / When / Then form. Every FR is covered by at least one AC. Include negative and error criteria.
6. **Non-functional requirements:** only when relevant, and measurable (latency, throughput, availability, security, accessibility, compatibility). A vague NFR ("fast") becomes a question asking for a number, unless the programmer accepts it as qualitative.
7. **Ambiguity sweep:** go through the checklist below.
8. **Open questions:** mark each one **Blocking** (planning or implementation cannot proceed correctly without it) or **Non-blocking** (can be resolved later). A non-blocking question gets no invented default answer.

## Ambiguity checklist

- Undefined terms, or terms used inconsistently.
- Boundaries: inclusive or exclusive, empty, zero, maximum, duplicates.
- Error behavior: invalid input, partial failure, timeout, conflict, retry.
- Actors and permissions: who can do it, and what others see.
- Data and state: existing data, migration, concurrent modification.
- Interacting rules: combinations of conditions.
- Scope edges: what is explicitly out of scope.
- Contradictions with existing behavior or with other requirements.

## Do not

- Fill a gap with a plausible guess and call it a requirement.
- Prescribe classes, functions, schemas, frameworks, algorithms, file layout or patterns.
- Over-specify details nobody knows yet. Leave them as open questions or hypotheses.
- Mark something Confirmed without the programmer's approval or evidence.

## IDs

`FR-n`, `NFR-n`, `C-n`, `INV-n`, `AC-n`, `Q-n`, `H-n`. IDs are never reused. A retired item keeps its ID, with status Retired.

## Evolutionary specifications (ESDD)

- **Item status:** Confirmed · Hypothesis · Under exploration · Rejected. Requirements that are no longer valid become Retired.
- **Change types:** Added · Clarified · Modified · Replaced · Retired. Each change bumps the spec version and adds a change-log row with its rationale and approval.
- **Prefer additive, traceable change,** but move obsolete requirements out of the active list (to Retired) rather than keeping contradictions alive for the sake of history.
- **Spec vs. plan:** a technical change in the plan does not imply a spec change. A functional change implies reassessing the plan and the tests (impact analysis).
