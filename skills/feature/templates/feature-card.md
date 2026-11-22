# Feature: <name> · Lite or Lean · <status> · base `abc1234` · worktree <path>

<!-- Lean works by increments: it uses Nearest analog, Increments and Cases, and no Requirements or Plan section. Lite uses Requirements and acceptance criteria and Plan. Omit the sections a mode does not use. -->

## Intent
The intent record, as `templates/intent.md` describes. The programmer's words are the source; everything else in this card is the current reading of them, not a closed contract.
- Original request: > verbatim, never edited.
- Consolidated intent: version, the gate where the programmer confirmed it, absorbed S-IDs, and a few lines.
- Statements since the last consolidation: verbatim, only those that change the intent: S-n · date · statement · prompted by (Q-n, D-n, gate, unprompted) · what it changes. Absorbed statements move to the card appendix, under the version that absorbed them.

## Scope
- Reach: for each broad statement of the programmer's words, the search run and the places found so far.
- Outside the intent: each item marked *programmer* (S-n) or *reading* (to confirm).

## Discoveries
Found after gate 1, in any step. Each one goes to the programmer: ID · found in (step) · what (evidence) · relation to the intent (covered by the programmer's words, quoted with the S-ID · implied by the intent · outside what was stated · contradicts) · decision (S-n), date.

## Nearest analog (Lean)
The existing feature most like this one, `path:line`, and how it handles empty and invalid input, whitespace, exceptions from user objects, escaping, error messages.

## Increments (Lean)
| # | Flow | Starts at commit | Edge cases deferred here from (D-ID) | Status (planned · in progress · done) |
| --- | --- | --- | --- | --- |

## Cases (Lean)
The executable criteria: no other section restates what the feature must do.

| ID | Increment | Case (input or setup) | Type (positive · negative · error · security · worst case) | Expected result | Source (request · S-n · D-n · `path:line`) | Analog does | Status (planned · passed · failed · deferred to # · retired) |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Requirements and acceptance criteria (Lite)
- AC-1: … (observable, testable)

## Decisions
- Approach: … (alternatives, one line each). Answers to questions: Q-1 → … (date). Pending decisions live in `decisions/`.

## Plan (Lite)
Files to touch · steps · tests to write (unit and end-to-end).

## State
Phase (Lean: increment # and step) · next step · what blocks it.

## Result
Files changed · test commands with real results (Lean: per increment) · testing technique statuses · quality gate result · `shortcut:` markers · known limitations · anti-pattern candidates.
