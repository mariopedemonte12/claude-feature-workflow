# Context Handoff Protocol

**Purpose:** let the next agent continue correctly without reconstructing the previous phase. Transfer knowledge, not conversation.

## Who writes it

The outgoing agent writes it. The Repository Analyst and the Planner are read-only, so they return their content and the orchestrator writes the handoff. The orchestrator also writes the Request → Specification handoff. The orchestrator checks every handoff before the next delegation.

`handoff.md` lives in the feature folder and is overwritten at each transition. History lives in the artifacts (specification change log, decisions, reports), not in old handoffs.

## Rules

- Reference canonical artifacts (path + section, or file:line) instead of copying them.
- Cite approved decisions by ID (D-NNN). Never present a pending option as decided, or a superseded decision as current.
- Mark findings Confirmed or Hypothesis explicitly.
- Write for the receiver: include what its responsibility needs (checklists below) and omit sections that would be empty.
- Keep it concise, normally one page. Correctness beats brevity: include anything whose absence could produce a wrong result.
- Never include full conversation histories, repeated explanations, irrelevant code details, superseded decisions shown as current, or speculation shown as fact.

Structure: `templates/handoff.md`.

## What each transition must carry

**Request → Specification**
`request.md` path · repository references (analyst report): existing behavior in the area, constraints it imposes · workflow · criticality if already known · intensity and its size budget.

**Specification → Planning**
Intent · confirmed FR/AC IDs · constraints · invariants · open questions (blocking ones flagged) · repository references (analyst report) · areas of technical uncertainty.

**Specification → Test design** (the Test Designer never reads the plan)
Approved spec version · confirmed FR/AC/INV IDs · out of scope · existing test framework, location, style and commands · E2E tooling · existing behavior of the area (analyst report).

**Planning → Implementation**
Approved approach (D ref) · alternatives not chosen, with the reason only when that prevents re-litigating · technical decisions · affected files and components · dependencies · implementation sequence · risks · `testing-plan.md` (the behaviors the code must handle; the Implementer writes no tests) · decisions still pending and what must not be touched until they are made · verification depth (mutation testing yes or no · review level R0 / R1 / R2) · end-to-end harness · registry entries (AP IDs) relevant to the change.

**Implementation → Testing** (critics and verifiers never read handoffs: `protocols/review-cycle.md` §Clean context)
Implemented functionality by FR/AC · agent IDs to resume (Implementer, Tester) · files modified · actual behavior implemented · deviations from the plan, with D refs · assumptions · known limitations · test commands · test data and setup · higher-risk areas · base commit for the diff · how to start the system for end-to-end tests · quality gate result · suggested testing focus.

**Testing → Specification / Evolution (ESDD)**
Tests executed, with results and evidence · failures · uncovered scenarios · discrepancies between spec and implementation · newly discovered requirements (as hypotheses) · invalidated assumptions · risks · possible spec or plan changes, phrased as options for the programmer rather than recommendations.

**Testing → Finalization**
Validation results · status of each acceptance criterion · end-to-end status and evidence · black-box technique statuses · mutation testing results · known defects · remaining risks · limitations.

## Incoming agent

1. Read the handoff and identify your own responsibility.
2. Open only the referenced artifacts and sections.
3. Check freshness (below).
4. Retrieve additional context only as needed.
5. Do not redo completed investigations.
6. Report inconsistencies or missing information instead of guessing. The handoff is a starting point and may be incomplete.

## Freshness

**When writing:** run these inside the feature worktree. Record `git rev-parse --short HEAD`, the branch, whether the working tree is dirty (`git status --porcelain` is non-empty), and the artifact versions (spec vN, plan status). If the project is not a git repository, record the date and time and the list of files touched.

**When receiving or resuming:** compare against the current state (`git log --oneline <recorded>..HEAD`, `git diff --stat <recorded>`). Re-read only the changed files that matter to your task. Re-verify a decision only if the changes touch what it depends on. A change does not automatically invalidate the handoff.

## A transition is complete when

- the phase deliverable exists;
- important decisions are recorded;
- unresolved issues are documented;
- the handoff is written and checked by the orchestrator;
- the next agent can start without reconstructing the previous phase.
