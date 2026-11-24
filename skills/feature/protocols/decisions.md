# Decision Protocol

Applies to the orchestrator, to executor sessions and to every subagent that produces options. It covers every decision reserved to the programmer: product intent, requirements, scope, business rules, architecture, technologies and dependencies, implementation strategy, trade-offs, risk acceptance, changes to approved behavior, workflow choice, verification depth, prototype or explore decisions, and acceptance.

**Purpose:** the programmer decides with the facts and with the agent's view in the open. Presenting options neutrally is not possible: the agent already chooses which options to show, which facts to look up and which words to use. So the agent states its view explicitly, shows what it left out, and the programmer decides.

## Rules

1. **Recommend, labeled.** Every decision with options ends with a **Recommendation**: the option, the reasons tied to the evidence, the criteria it weighed (time, cost, risk, reversibility, maintenance, performance…), and the fact that would change it. When the evidence favors no option, write *No recommendation* and why: that is an answer too. The recommendation is never disguised as the only viable option or as a confirmation question.
2. **Show the selection.** Every viable option found is shown. When genuinely viable, these are options too: *defer*, *investigate further*, *build a disposable prototype*, *change the requirement*. Options considered and dropped go under **Not shown**, one line each with the reason; options that violate a confirmed constraint go under **Excluded**, naming the constraint (ID and reference), because the programmer may relax it. Do not manufacture options: if only one is viable, say so.
3. **Facts, not adjectives.** State consequences the programmer can verify: components and files affected, new dependencies, schema or data migrations, public API changes, what undoing it takes, test effort, performance with its evidence (`knowledge/measurement.md`). Replace "simple", "clean", "robust", "hacky", "future-proof" with the underlying fact.
4. **Evidence status on every claim.** *Confirmed* (with a reference: `path:line`, doc, measured result), *Hypothesis*, or *Unknown*. Estimates are ranges with their basis. The recommended option gets the same standard of evidence as the others, and its disadvantages are written as fully as theirs.
5. **An explicit question.** Ask *"Which option do you choose: A, B, C, or another?"*, naming every option. Never "Shall I proceed with B?": a yes-or-no question hides the other options.
6. **No de-facto choices.** Do not pre-implement, pre-write a detailed plan for, or pre-install anything for one option before the decision. The only exception is a disposable prototype the programmer approved.
7. **No default by inaction or silence.** If the programmer has not decided, do not proceed with any option; work independent of the decision may continue. Never phrase a gate item as "I will do X; say if you want Y". Conditional or standing approvals ("accept if all tests pass", "I accept your recommendation") are recorded with their scope, quoted each time they are applied, and listed in the final report.
8. **After the decision.** If the chosen option conflicts with a confirmed constraint or carries a risk not yet discussed, state it once, with evidence, then follow the decision. A recommendation that was not taken is not repeated at later gates unless a new fact changes the case; say which fact.
9. **Frame scope against the intent record, not the specification.** The specification is the current reading of the intent (`knowledge/specification-guide.md` §What a specification is), and the intent record (`intent.md`, or the card's *Intent* section) holds the programmer's own words: the original request, the confirmed consolidated intent and the statements since, the most recent winning. When a finding or a discovery touches scope, state its relation to the intent as a fact: *covered by the programmer's words* (quote them, citing the S-ID, the consolidated intent version or "original request"), *implied by the intent* (marked as reading), *outside what the programmer stated*, or *contradicts the original request or a statement*. "Not in the spec", "beyond the spec" or "requires a spec amendment" is never a disadvantage of an option: updating the specification is a routine consequence, stated in the option's effects.
10. **Relaying.** When the orchestrator relays a subagent's options, it keeps the subagent's recommendation attributed to it ("the Planner recommends B because…"), and adds its own, labeled, only when it differs or the subagent gave none.
11. **Workflow and review level** follow their own procedures: the workflow recommendation of `SKILL.md` §2.5, and the review level of `protocols/review-cycle.md`, which starts from the default (R1 for SDD and EVO, R2 for Critical; DIRECT runs no critic unless asked) and shows the default, the deviation if any, and its evidence. A standing acceptance of recommendations covers only review levels equal to the default; a deviation is asked every time. With the `depth` gate off, a re-check after implementation that raises the level by size applies and is reported; one that lowers it is asked.

## Presentation format

```markdown
### Decision D-<NNN>: <question>

**Context:** the problem in 2–4 lines.
**Why this is your decision:** <category from the list above>
**Relevant evidence:** facts with references.

#### A — <short name>
- **Approach:**
- **Advantages:**
- **Disadvantages:**
- **Effort (observable):** files and components touched, new concepts, migration…
- **Cost · Risks · Architectural impact · Reversibility · Maintenance · Remaining uncertainty:** one line each

#### B — <short name>
(same fields)

**Comparison**
| Aspect | A | B |
| --- | --- | --- |
| New dependencies | | |
| Files / components touched | | |
| Data migration | | |
| Public API change | | |
| Reversibility | | |

**Not shown:** <option>: <reason>. **Excluded:** <option> violates <constraint ID> (<reference>).

**Recommendation:** B, because <reasons with evidence>. Criteria weighed: <…>. It would change if <fact>.

**Decision required:** Which option do you choose: A, B, or another?
```

Drop fields or rows that apply to no option. A field that applies to some options stays for all, with "n/a" or "none". In a short gate item, the same content fits in a few lines: the options with their facts, the recommendation with its reason, the question.

## Self-check before presenting

- [ ] A labeled recommendation with its reasons and what would change it, or *No recommendation* with why.
- [ ] Every viable option shown; dropped ones under *Not shown*, excluded ones with their constraint.
- [ ] Every claim has a status; Confirmed claims have a reference.
- [ ] The recommended option's disadvantages are as complete as the others'.
- [ ] The question names every option.
- [ ] Nothing was implemented or prepared for one option ahead of the decision.
