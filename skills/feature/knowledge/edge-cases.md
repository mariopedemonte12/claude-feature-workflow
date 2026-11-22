---
name: edge-cases
kind: guide
summary: The edge-case checklist: reach of broad statements, nearest analog, cases per input, self-review
use-in: [general]
---
# Edge-Case Checklist

The checklist every workflow runs before code, whoever runs it. In DIRECT it is the whole method; in SDD and EVO it is what the specification, the intent pass and test design enumerate. It is the one skill `--no-skills` leaves on.

## Before code

1. **Reach of every broad statement.** For each phrase like "everywhere that…", "all…", "any…", "consistently", "wherever", search the codebase for every place it reaches, including subclasses, overrides and copies of the same list or rule. Write down the search you ran and what it found. A place you are unsure about is a question for the programmer, not something you silently include or leave out.
2. **Nearest analog.** Find the existing feature of the project most like this one (a template tag for a tag, a form field for a field, a filter for a filter), with its `path:line`. Read how it handles empty and invalid input, whitespace, exceptions raised by user-supplied objects, escaping and safe-marking, and error messages. Matching it is the default reading of an unstated detail; departing from it is a question. If there is no analog, say so.
3. **Cases, for each input of each main flow**, each with its expected result and its source (the request, the programmer's later words, a decision, or `path:line` for existing behavior to keep):
   - boundaries, empty and missing values;
   - invalid values and encodings;
   - error paths, with their message and exit or status;
   - duplicates and ordering;
   - concurrency, if any;
   - security: escaping, injection, safe-marking, authorization and trust boundaries;
   - worst case: the input size or shape that costs the most time or memory, and the bound expected.
4. **Blocking questions.** A case whose expected result changes the output for a valid input, and that neither the request nor the analog settles, is asked before code. Never weaken a case to avoid asking.

## Probes

For a change involving parsers, regular expressions, escaping or safe-marking, run a quick probe before settling the approach: a timing loop that doubles the input size, and an injection string. Report what it printed.

## After code

5. **Tests for every case,** run with the project's test command, plus the relevant existing test modules to catch regressions. A test not run is never "passed".
6. **Self-review.** Read your own diff once as a strict reviewer would, against the cases and `knowledge/code-quality.md` when it is active, and fix what you find. A self-review is not a clean review: say so when you report it.
