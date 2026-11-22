<!-- The intent record of one feature. Written only by whoever talks to the programmer: the orchestrator in /feature, the session in /feature-lean (as the card's Intent section). Omit any section that has no content. -->
# Intent: <Feature name>

## Original request

> The programmer's first request, verbatim. Never edited.

## Consolidated intent

Version <n> · confirmed by the programmer at <gate>, <date> · absorbs S-1 … S-<n>

What the programmer wants, in their terms: the behavior, the reach of each broad statement, and the boundaries they drew. A few lines to a short list. Written by the agent as a proposal and binding only once the programmer confirmed or corrected it; their correction is the text.

## Statements since the last consolidation

Verbatim, in the programmer's words. Only statements that change the intent: they add, remove or narrow scope, behavior or a boundary, asked or unprompted. Approvals ("approve", "B") stay in the gate records, and implementation choices in `decisions/`.

| ID | Date | Statement (verbatim) | Prompted by (Q-n · D-n · gate · unprompted) | Changes |
| --- | --- | --- | --- | --- |
| S-<n+1> | YYYY-MM-DD | "…" | Q-3 | … |

<!--
Rules:
- Precedence: a recent statement wins over the consolidated intent, and the consolidated intent wins over the original request where they differ.
- Consolidation, at each gate with new statements: propose the new consolidated text, showing what changed and which S-IDs it absorbs. On the programmer's confirmation or correction, bump the version, write the text, and move the absorbed statements, verbatim, to intent-history.md (in Lean, the card appendix), under the version that absorbed them. Never consolidate without that confirmation.
- intent-history.md is the archive: it is never edited and not read by default. Read it only to trace why the intent changed.
- Readers that need the programmer's words (the Specification Writer, the critic) receive the original request, the confirmed consolidated intent and the statements since; never an unconfirmed proposal.
-->
