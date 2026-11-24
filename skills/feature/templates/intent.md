<!-- The intent record of one feature. Written only by whoever talks to the programmer: the orchestrator, or the executor session (in a card, as its Intent section). DIRECT keeps no intent record. Omit any section that has no content. -->
# Intent: <Feature name>

## Original request

> The programmer's first request, verbatim. Never edited.

## Consolidated intent

Version <n> · confirmed by the programmer at <gate>, <date> · absorbs S-1 … S-<n>

What the programmer wants, in their terms: the behavior, the reach of each broad statement, and the boundaries they drew. A few lines to a short list. Written by the agent as a proposal and binding only once the programmer confirmed or corrected it; their correction is the text.

## Refinement

Only when refinement ran (`protocols/refinement.md`). Confirmed by the programmer with version 1.

- **Problem:** who has it, what happens today, the signal that it is solved, why now.
- **Readings:** the one chosen, and the ones rejected with the reason in the programmer's words.
- **Context gaps still open:** each with who answers it (the programmer, or a named third party).
- **Readiness verdict:** ready (the evidence for the workflow and the gate profile) or blocked (on whom, what to ask).

## Statements since the last consolidation

Verbatim, in the programmer's words. Only statements that change the intent: they add, remove or narrow scope, behavior or a boundary, asked or unprompted. Approvals ("approve", "B") stay in the gate records, and implementation choices in `decisions/`.

| ID | Date | Statement (verbatim) | Prompted by (Q-n · D-n · gate · unprompted) | Changes |
| --- | --- | --- | --- | --- |
| S-<n+1> | YYYY-MM-DD | "…" | Q-3 | … |

<!--
Rules:
- Precedence: a recent statement wins over the consolidated intent, and the consolidated intent wins over the original request where they differ.
- Consolidation, at each gate with new statements: propose the new consolidated text, showing what changed and which S-IDs it absorbs. On the programmer's confirmation or correction, bump the version, write the text, and move the absorbed statements, verbatim, to intent-history.md (with a card, the card appendix), under the version that absorbed them. Never consolidate without that confirmation.
- intent-history.md is the archive: it is never edited and not read by default. Read it only to trace why the intent changed.
- Readers that need the programmer's words (the Specification Writer, the critic) receive the original request, the confirmed consolidated intent and the statements since; never an unconfirmed proposal.
-->
