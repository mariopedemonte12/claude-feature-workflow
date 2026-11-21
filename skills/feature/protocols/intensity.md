# Intensity Levels

Every feature runs at one of three intensities: **Lite**, **Medium** or **High**. The intensity sets how many agents, gates and artifacts the feature uses. It is set **per feature**; features in the same portfolio may run at different intensities.

## Choosing the level

- The programmer sets it per feature or **per group of features**, with a flag (`--lite`, `--medium`, `--high`) or in their request: "these three at Lite", "group billing at Medium". A group level applies to each member; a feature-level setting overrides it. In the hierarchical mode (`protocols/hierarchy.md`), a group's level is the default for every feature its sub-orchestrator runs.
- If it is not set, ask at the first gate, as a neutral decision (`protocols/neutral-decisions.md`), with the facts that bear on it: estimated size, files and components touched, risk areas (security, money, data writes, concurrency, public interfaces), criticality.
- **Critical features always run at High.** State it; do not ask.
- The level can change at any later gate, by the programmer's decision, recorded in `decisions/`. Raising it adds the missing steps from the current point; lowering it never removes evidence already produced.
- Record the level in the feature's handoff and in the project memory portfolio.

## What each level runs

| Aspect | Lite | Medium | High |
| --- | --- | --- | --- |
| Workflow | SDD Direct only | SDD Direct, ESDD or Hybrid | SDD Direct, ESDD or Hybrid |
| Repository Analyst | no; the orchestrator reads what it needs, or uses the project memory | only if the memory lacks the evidence | yes |
| Specification Writer | no; the orchestrator writes the card's specification section | yes | yes |
| Planner | no; the orchestrator writes one approach and lists alternatives in a line each | yes, briefed for the main decision only | yes, full solution space |
| Test Designer | no | yes, from the approved spec, in parallel with the Planner | yes, every technique evaluated |
| Implementer | writes the code **and** its tests (unit and end-to-end) | writes the code only, no tests | same as Medium |
| Tester | no; the Implementer's tests are the evidence | implements and runs the designed cases, including end-to-end | same, plus every black-box technique and mutation testing |
| Review level: the default the recommendation starts from (`protocols/review-cycle.md`) | R0 | R1 | R2 |
| Mutation testing | no | asked at the plan gate | yes |
| Gates | one **spec + plan** gate, then acceptance (defects go into the acceptance gate) | spec gate, plan gate, defects gate, acceptance | every gate in the workflow |
| Spec questions | blocking ones only; the rest are written as out of scope | blocking and those that change observable behavior | all |
| Agent questions (`protocols/agent-questions.md`) | yes | yes | yes |
| Artifacts | one `feature.md` card (`templates/feature-card.md`), target 500 lines, plus `decisions/` | spec, plan, handoff and reports, each within the size budget below | the full set |
| Anti-pattern registry | read and respected; candidates only listed in the card | full loop | full loop |

**Size budgets at Medium:** specification and plan, target 500 lines each; handoff, target 30 lines; each report, target 60. The Lite and Lean card has a target of 500 lines.

**Size budgets are targets, never cuts.** Each budget is the size a document should normally fit. When the content needs more, do not drop or compress anything that matters:
1. keep the main document within the target, as a readable summary;
2. move the overflow to linked files next to it: design decisions to `decisions/D-NNN-<topic>.md`, long case tables, option analyses and evidence to an appendix such as `feature-appendix.md` or `spec-appendix.md`;
3. link each moved part from the place it belongs, by section;
4. report the total size as a fact at the next gate, for example "spec 420 lines + appendix 310".

A requirement, case, decision or risk is never left out to stay within a budget, and work is never stopped because of size. At High, the templates apply without a budget.

## Efficiency rules for every level

- Launch every agent of a phase in one message, across features.
- Write the artifacts of several features in one command when their content is ready.
- Never wait with `sleep`: background agents notify when they finish.
- Verify an agent's claims with one batched check (for example, one command that runs every feature's tests), not one call per claim.
- Keep subagent returns within their word limits; do not re-read what a report already states unless you are verifying it.
