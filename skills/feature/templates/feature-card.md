# Feature: <name> · <EVO executor · DIRECT> · <status> · base `abc1234` · worktree <path or "checkout">

<!-- The single-file record of a feature: EVO in executor mode (every section), or DIRECT when the programmer asks for a record (Intent, Scope, Cases and Result only). Target 500 lines, never a cut: overflow goes to decisions/ or feature-appendix.md, linked by section. Omit the sections a feature does not use. -->

## Intent
The intent record, as `templates/intent.md` describes. The programmer's words are the source; everything else in this card is the current reading of them, not a closed contract.
- Original request: > verbatim, never edited.
- Consolidated intent: version, the gate where the programmer confirmed it, absorbed S-IDs, and a few lines, with the completion criteria.
- Statements since the last consolidation: verbatim, only those that change the intent: S-n · date · statement · prompted by (Q-n, D-n, gate, unprompted) · what it changes. Absorbed statements move to the card appendix, under the version that absorbed them.

## Scope
- Reach: for each broad statement of the programmer's words, the search run and the places found so far.
- Outside the intent: each item marked *programmer* (S-n) or *reading* (to confirm).

## Discoveries
Found after the first gate, in any step. Each one goes to the programmer: ID · found in (step) · what (evidence) · relation to the intent (covered by the programmer's words, quoted with the S-ID · implied by the intent · outside what was stated · contradicts) · decision (S-n), date.

## Nearest analog
The existing feature most like this one, `path:line`, and how it handles empty and invalid input, whitespace, exceptions from user objects, escaping, error messages.

## Increments
| # | Flow | Starts at commit | Edge cases deferred here from (D-ID) | Status (planned · in progress · done) |
| --- | --- | --- | --- | --- |

## Cases
The executable criteria: no other section restates what the feature must do.

| ID | Increment | Case (input or setup) | Type (positive · negative · error · security · worst case) | Expected result | Source (request · S-n · D-n · `path:line`) | Analog does | Status (planned · passed · failed · deferred to # · retired) |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Decisions
- Workflow and role of the session. Approach: … (alternatives, one line each). Answers to questions: Q-1 → … (date). Pending decisions live in `decisions/`.

## Skills
Skills that applied, by phase, with their location (library · programmer · repository · module `<path>`); specialists run and their phases.

## State
Increment # and step · next step · what blocks it.

## Result
Files changed · test commands with real results, per increment · testing technique statuses · specialists and their results · mutation testing · quality gate result · `shortcut:` markers · known limitations · accepted findings · deferred edge cases never covered.
