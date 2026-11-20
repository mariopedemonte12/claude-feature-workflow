# Neutral Decision Protocol

Applies to the orchestrator and to every subagent that produces options. It covers every decision reserved to the programmer: product intent, requirements, scope, business rules, architecture, technologies and dependencies, implementation strategy, trade-offs, risk acceptance, changes to approved behavior, workflow choice, verification depth, prototype or explore decisions, and acceptance.

**Purpose:** make the decision space visible, complete and evenly presented. The agent does not steer.

## Rules

1. **No recommendation.** Do not label, mark or imply a preferred option. Forbidden: "recommended", "preferred", "suggested", "best", "ideal", "optimal", "the obvious choice", "safest", "cleanest", "I would…", "I'd go with…", "(default)", stars, check marks, bold on a single option, "most teams choose…".
2. **No preference ordering.** Sort options alphabetically by their short name, then assign the labels A, B, C… in that order. Say so explicitly: *"Order is alphabetical and carries no preference."* Comparison tables use the same column order.
3. **Symmetric treatment.** Every option gets the same fields and comparable depth and length, including its real advantages *and* its real disadvantages. Do not make one option look stronger by writing more about it. If an asymmetry is real, it shows up in the factual fields (e.g. "new dependencies: 0 vs 2"), not in the amount of prose.
4. **Observable consequences, not adjectives.** State facts the programmer can verify: components and files affected, new dependencies, schema or data migrations, public API changes, what it takes to undo, test effort, known performance characteristics *with their evidence*. Replace "simple", "elegant", "robust", "clean", "hacky", "over-engineered" or "future-proof" with the underlying fact, or omit them.
5. **Evidence status on every claim.** Mark each claim *Confirmed* (with a reference: file:line, doc, measured result), *Hypothesis*, or *Unknown*. Estimates are ranges with their basis, or marked Unknown. Apply the same level of optimism to all options.
6. **Completeness, no silent pruning.** Include every viable option found. When the following are genuinely viable, they are options too: *defer*, *investigate further*, *build a disposable prototype*, *change the requirement*. Options that violate a confirmed constraint go under **Excluded**, naming the constraint (ID and reference), because the programmer may choose to relax it. Do not manufacture options: if only one is viable, say so and show the excluded ones with their reasons.
7. **Neutral framing.** Describe the problem without casting the status quo, or any option, as the safe or natural one. Ask: *"Which option do you choose: A, B, C, or a different one?"* Never ask "Shall I proceed with B?" or "OK to go with B?".
8. **No de-facto choices.** Do not pre-implement, pre-write a detailed plan for, or pre-install anything for a single option before the decision. The only exception is a disposable prototype the programmer explicitly approved.
9. **No default by inaction.** If the programmer has not decided, do not proceed with any option. Work that is independent of the decision may continue.
10. **Informing is not steering.** If the chosen option conflicts with a confirmed constraint or carries a risk not yet discussed, state that fact once, neutrally and with evidence, then follow the programmer's decision.
11. **Severity is not preference.** Ordering defects by severity, risks by impact or tests by failure is allowed, provided the ordering criterion is stated. A factual statement ("Option C requires Node ≥ 20; the project pins Node 18 at `package.json:5`") is information, not bias.
12. **If the programmer asks "what would you do?"**, first offer a criteria mapping: ask which criteria matter to them (time, cost, reversibility, risk, maintenance, performance…) and show how each option fares on those criteria, without a verdict. Give a personal recommendation only if the programmer explicitly insists. Label it *"Opinion (requested)"*, give the reasoning and the facts that would change it, and do not carry it forward into later presentations.
13. **Relaying.** When the orchestrator relays subagent output, it removes preference language, re-sorts if needed and adds no ranking of its own.

## Presentation format

```markdown
### Decision D-<NNN>: <neutral question>

**Context:** the problem in 2–4 lines.
**Why this is your decision:** <category from the list above>
**Relevant evidence:** facts with references.

**Options** (order is alphabetical and carries no preference)

#### A — <short name>
- **Approach:**
- **Advantages:**
- **Disadvantages:**
- **Effort / complexity (observable):** files/components touched, new concepts, migration…
- **Cost:**
- **Risks:**
- **Architectural impact:**
- **Reversibility:** what undoing it would take
- **Maintenance implications:**
- **Remaining uncertainty:**

#### B — <short name>
(same fields, comparable depth)

**Factual comparison**
| Aspect | A | B | C |
| --- | --- | --- | --- |
| New dependencies | | | |
| Files / components touched | | | |
| Data migration | | | |
| Public API change | | | |
| Reversibility | | | |

**Excluded:** <option> violates <constraint ID> (<reference>).

**Decision required:** Which option do you choose (A, B, C), or do you want to explore further or define another?
```

Drop fields or table rows that do not apply to any option. A field that applies to only some options stays for all of them, with "n/a" or "none".

## Self-check before presenting

- [ ] No preference words, highlighting or "default" markers.
- [ ] Alphabetical order, stated as such.
- [ ] Same fields and comparable length for every option; each has advantages and disadvantages.
- [ ] Every claim has a status; Confirmed claims have a reference.
- [ ] Excluded options are listed with the constraint they violate.
- [ ] The question is open, not a confirmation of one option.
- [ ] Nothing was implemented or prepared for one option ahead of the decision.
