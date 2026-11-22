---
name: testing-techniques
kind: guide
summary: Black-box techniques (BVA, fuzz, decision table, FSM, symbolic/concolic) and mutation testing
use-in: [test-design, test]
---
# Testing Techniques Guide

Testing must show behavior, not just that code runs. Prioritize by risk: critical business rules, boundaries, invalid inputs, error handling, state transitions, integrations, security-sensitive behavior, regressions.

Every black-box technique ends with exactly one status:

- **Applied:** what was done, how many cases, the results.
- **Not applicable:** why the technique adds no meaningful value here (e.g. "no ordered input domain").
- **Blocked:** what prevented it (missing tool, environment, a declined dependency) and the residual risk.

Never force a technique just to complete a checklist. Never mark something Applied that was not executed.

Tool availability: use what the project already has. Adding a dev dependency is a programmer decision, so return it to the orchestrator.

---

## Boundary Value Analysis

**Applicable when** inputs, outputs or state have ordered domains or limits: numeric ranges, lengths, sizes, dates, counts, pagination, quotas, timeouts, thresholds in business rules.

**How:**
1. List the equivalence partitions from the spec, both valid and invalid.
2. For a range `[min, max]`, test `min−1, min, min+1, max−1, max, max+1`, using the smallest step of the domain. Add type and representation limits where relevant: 0, empty, maximum integer, maximum length, Unicode character length vs. byte length.
3. Map each case to FR/AC IDs. If a boundary is ambiguous (inclusive or exclusive not stated), raise a spec question instead of guessing.

**Not applicable** for unordered enums or identifiers without limits. Use equivalence classes or decision tables there.

## Fuzz Testing (including property-based)

**Applicable to** parsers, deserializers, input validation, public APIs, file and format handling, any consumer of untrusted input, and pure logic with invariants.

**How:**
- **Property-based:** derive properties from the invariants (round-trip, idempotence, monotonicity, no crash, output within bounds).
- **Coverage-guided fuzzing:** for parsers and binary formats, when tooling exists.
- **Time-box every run.** Record the seed and duration. Minimize each crashing input and keep it as a regression test.

**Tools by ecosystem:**

| Ecosystem | Tools |
| --- | --- |
| Python | Hypothesis, Atheris |
| JS/TS | fast-check |
| JVM | jqwik, Jazzer |
| Go | `go test -fuzz` |
| Rust | proptest, cargo-fuzz |
| C/C++ | libFuzzer, AFL++ |
| .NET | FsCheck, SharpFuzz |

**Report:** properties, generators, runs and duration, failures found (with minimized inputs).

## Symbolic and Concolic Testing

**Applicable to** functions with complex path conditions (nested branches, arithmetic constraints, parsing logic), where hand-picked inputs would likely miss paths.

**How:**
- **With tooling** (e.g. KLEE for C/LLVM, CrossHair for Python, Symbolic PathFinder for Java): run it bounded, on the narrowest unit. Record the paths explored, the inputs generated and any counterexamples.
- **Without tooling:** do a manual path-condition analysis. Enumerate the branches of the target function, write the condition for each feasible path, derive one concrete input per path and turn each into a test. Report it as "Applied (manual path analysis, no solver)" and state that limitation.
- **Blocked:** when a solver is necessary and manual analysis is infeasible (path explosion, environment). State the residual risk.

**Not applicable** to straight-line code, glue code, UI wiring or thin wrappers.

## Decision Table Testing

**Applicable when** behavior depends on combinations of conditions: business rules, permissions, pricing, feature flags, combined validations.

**How:**
1. Extract the conditions and actions from the spec.
2. Build the combination table and collapse don't-care entries. Combinations the spec does not define become spec questions; do not invent their outcome.
3. Write one test per rule (column). Include impossible combinations when it matters to verify that they are rejected.

**Not applicable** to single-condition logic.

## Finite State Machine Testing

**Applicable to** entities with a lifecycle (orders, sessions, workflows, connections, UI flows, retries) and to protocols.

**How:**
1. Extract the states, events, guards and transitions from the spec and the code.
2. Cover:
   - every valid transition;
   - invalid events in each state (rejected or ignored, as the spec says);
   - guard boundaries;
   - initial and terminal states;
   - round-trips;
   - restart or persistence mid-state, and concurrent events, when relevant.
3. Transitions the spec does not define become spec questions.

**Not applicable** to stateless logic.

---

## Mutation Testing

**Mandatory** when the feature's criticality is Critical or the programmer requested it. Otherwise, run it only if the programmer decided so at the plan gate.

**How:**
- Scope it to the changed or added code (diff-based where the tool supports it).
- **Tools:**

  | Ecosystem | Tools |
  | --- | --- |
  | JS/TS, C#, Scala | Stryker |
  | Java | PIT |
  | Python | mutmut, cosmic-ray |
  | Rust | cargo-mutants |
  | Go | Gremlins |
  | PHP | Infection |
  | Ruby | mutant |

- **Classify each surviving mutant:**
  - *test gap*: add or strengthen a test;
  - *equivalent mutant*: explain why;
  - *out of scope*.

**Report:** scope; tool and configuration; totals (killed / survived / timeout / no coverage); score; surviving mutants with their classification; tests added; limitations.

High line coverage with surviving mutants means weak assertions. Coverage is not effectiveness.

## Regression Testing

Always run the existing suites that touch the affected components, and the full suite when feasible. Report the commands, counts, failures and flaky tests (re-run a flaky test once and report it as flaky; never hide it).

## Functional testing checklist

- Every AC has at least one test, positive and negative where meaningful.
- Every documented error path is triggered and produces the specified behavior.
- Integration points are exercised, either for real or with faithful test doubles; state which.
- Security-sensitive behavior (authorization, input validation, data isolation) is tested when in scope.
