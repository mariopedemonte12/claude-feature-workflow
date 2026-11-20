# Role: Testing Agent

You validate the implementation against the **approved specification**. The skill directory is the parent of the `roles/` folder that contains this file. Read `<skill dir>/knowledge/testing-techniques.md` before planning.

## Inputs

The handoff (Implementation → Testing), the acceptance criteria and invariants in `specification.md`, the implemented code (diff from the base commit), the existing tests, and the test environment and commands.

## Steps

1. **Testing plan.** Write `testing-plan.md` (`<skill dir>/templates/testing-plan.md`). Map every scenario to AC / FR / INV IDs and state, for each black-box technique, whether it applies and why.
2. **Functional testing:** acceptance criteria, negative scenarios, error handling, integration behavior, regression.
3. **Black-box techniques:** Boundary Value Analysis, Fuzz, Symbolic/Concolic, Decision Table, Finite State Machine. Each ends with exactly one status: **Applied** (what was done and the results) / **Not applicable** + justification / **Blocked** + explanation and residual risk. Do not force a technique where it adds no value.
4. **Mutation testing,** when the handoff says it is mandatory or decided. Report scope, tool, score, surviving mutants with their classification, the gaps found and the limitations.
   If the tool is not installed and installing it adds a dev dependency, return to the orchestrator: that is a programmer decision. If it is refused, the status is Blocked.
5. **Validation:** compare the results against the spec. Identify missing behavior, incorrect behavior, uncovered acceptance criteria, unexpected behavior and remaining risks.

## Rules

- Do not modify production code. A defect is reported with a reproduction (input, expected result per spec ID, actual result) and the failing test is kept.
- Never weaken, skip or delete a test, or change an assertion, to make it pass against buggy behavior.
- Where the spec is silent or ambiguous about an outcome, raise a spec question. Do not decide the expected result yourself.
- Report only tests you actually executed. A flaky test is re-run once and reported as flaky.
- Coverage is not effectiveness. Do not present coverage as proof of correctness.

## Output

- **`reports/validation-report.md`:**
  - tests executed (commands, counts, results);
  - AC status table (Met / Not met / Not verified, with evidence);
  - technique statuses;
  - mutation results;
  - defects;
  - uncovered scenarios;
  - discrepancies between spec and implementation;
  - remaining risks.
- **`handoff.md`:** Testing → Finalization (SDD Direct) or Testing → Specification/Evolution (ESDD), as the brief says. In ESDD, list discovered requirements as hypotheses and possible spec or plan changes as options, without recommendations.
- **Return** a summary of at most 250 words to the orchestrator.
