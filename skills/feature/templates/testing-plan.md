# Testing Plan: <Feature name>

Designed by the Test Designer before implementation, from the approved specification (spec vN), or in EVO from the intent record (consolidated intent vN, statements up to S-n) and `decisions/`, one increment at a time. In EVO these cases are the executable criteria of the feature. Implemented and run by the Tester. Cases the Tester adds during exploratory testing are marked *added* with their reason.

## Scope

In scope: … Out of scope: …

## Environment and commands

## Functional scenarios

| ID | Increment (EVO) | Scenario | Type (positive · negative · error · security · worst case · integration · regression) | Technique | Covers (AC/FR/INV) or source (S-n · intent vN · D-n · `path:line`) | Input or setup | Expected result (from the source) | Status (planned · implemented · passed · failed · retired) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## End-to-end

Status (Applied · Not applicable · Blocked) and basis. Harness and version · how the system is started · what is real and what is faked · evidence location (`reports/e2e/`).

| ID | User path | Covers (AC) | Expected observable result |
| --- | --- | --- | --- |

## Traceability

Every AC (in EVO: every part of the consolidated intent and every behavior-settling decision) with its case IDs; what has no case, and why. EVO: deferred edge cases, each with the D-ID that deferred it and the increment that will cover it.

## Black-box technique applicability

| Technique | Planned status | Justification |
| --- | --- | --- |
| Boundary Value Analysis | | |
| Fuzz / property-based | | |
| Symbolic / concolic | | |
| Decision table | | |
| Finite state machine | | |

## Mutation testing

Required: yes/no (basis: criticality, programmer decision). Scope · tool · agreed threshold, if any.

## Regression strategy

## Validation criteria

What counts as "validated" for this feature.
