<!-- Evidence only. Anything unverified is reported as unverified. Omit sections that do not apply. -->
# Final Report: <Feature name>

| Field | Value |
| --- | --- |
| Workflow | SDD · EVO · Hybrid (DIRECT reports in the conversation, `workflows/direct.md` step 6) |
| Role of the session | Orchestrator · Executor |
| Gate profile | full · key · auto, with per-gate changes; the programmer's words that set it |
| Spec | vN (`specification.md`), or in EVO: consolidated intent vN (`intent.md`) |
| Plan | `implementation-plan.md` (D-NNN) |
| Commits | base `abc1234` → final `def5678` |
| Date | YYYY-MM-DD |

## Implemented functionality

## Final specification state

For EVO, the report is short: link `intent.md` (its evolution is in `intent-history.md`), `testing-plan.md` and `decisions/` instead of restating them, and fill only the sections that live nowhere else (decided by the agent, increments with their test results, mutation testing, remaining hypotheses, known limitations, accepted findings, risks).

## Approved approach and important decisions

- D-NNN: …

## Decided by the agent

Every decision taken at a gate that was off (`protocols/gates.md`), grouped by gate: D-NNN · what was decided · the evidence · what reopening it would change. Discoveries recorded but not built are listed here too. "None" when every gate was on.

## Increments (EVO)

## Important discoveries (EVO)

| Discovery | Classification | Effect |
| --- | --- | --- |

## Files and components modified

## Tests executed

Commands, counts, results.

## Acceptance criteria

| AC | Status (Met · Not met · Not verified) | Evidence |
| --- | --- | --- |

## End-to-end

Harness · environment (real vs. faked) · scenarios by AC · flaky tests · evidence paths · status.

## Code quality

Quality gate result · remaining violations with decision references · `shortcut:` markers added (location, limit, upgrade trigger) · registry changes (AP entries added, occurrences recorded, rules automated, candidates rejected).

## Black-box techniques

| Technique | Status | Justification / result |
| --- | --- | --- |

## Mutation testing

Scope · tool · score · surviving mutants · gaps · limitations, or "Not performed (D-NNN)".

## Review

Level (R0 / R1 / R2, D-NNN) · rounds run and why the cycle stopped · the commits made after the last critic round, each with its hash, marked **unreviewed** (`protocols/review-cycle.md` §R2 · The cycle) · per round: findings raised, VALID / INVALID / AMBIGUOUS, fixed automatically, sent to the gate · how each remaining finding was resolved · Nits not applied · share of INVALID findings.

## Remaining hypotheses (EVO)

## Known limitations

## Remaining risks

## Outstanding work

## Acceptance

Pending the programmer's decision.
