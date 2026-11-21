# Code Quality Standard

Binding for every line of code an agent writes in this workflow: production code, tests, E2E suites, scripts and rules. The Implementer applies it, the Planner designs for it, the clean Critic checks it and the Tester follows it in test code.

The order of priority is: **correct → safe → holds under the expected load → tested → readable → lean.** No rule below justifies cutting the first four.

Part of this standard adapts the "smallest complete change" discipline of Ponytail (github.com/DietrichGebert/ponytail, MIT). It is stricter than Ponytail on comments (no "why" comments; only `shortcut:` markers and tool directives): the rules here win.

## 1. The smallest complete change

Before writing, read the task and the code it touches. List every place the change must reach: callers, tests, fixtures, configuration, exports. That is the scope. Extra features are not.

Then take the first rung that fully works:

1. **Does it need to exist?** Only what the approved spec and plan require. Anything else is named in the report, not built.
2. **Already in this codebase?** A helper, component, service or pattern. Use it the way the surrounding code does.
3. **Standard library or platform feature?** Use it, unless the project has its own equivalent.
4. **An installed dependency?** Use it. A new dependency is a programmer decision, never a shortcut for a few lines.
5. **Otherwise:** the minimum code that works, written to the rules below.

- Be lazy about the solution, never about the change: finish every caller, test and fixture the change breaks.
- No abstraction, wrapper, option, configuration or "for later" code that the spec or plan does not need.
- Code you move or merge keeps its error handling and validation.
- Bug fix: find every caller of the function you touch and fix the root cause once, in the shared code.
- Between options of equal size, take the one that is correct on edge cases.

**Never cut:** validation at trust boundaries, error handling that prevents data loss, security, accessibility, anything the spec requires.

## 2. No comments in code

New and modified code contains **no comments**: no line comments, block comments, docstrings, commented-out code or TODO/FIXME notes.

What replaces a comment:

| A comment would say… | Write instead |
| --- | --- |
| what a block does | extract it into a function whose name says it |
| what a value means | a named constant or a small type |
| why a decision was made | the decision record (`decisions/`), the implementation report or the commit message |
| how to use an API | a test that shows the usage |
| a known limitation or shortcut | a `shortcut:` marker (below) |
| a TODO | a `shortcut:` marker if it is a deliberate limit, otherwise an open issue in the implementation report |

**Exceptions, and the only ones:**

1. **Shortcut markers.** A deliberate shortcut with a known limit gets exactly one line in the form `shortcut: <the limit>, <when to upgrade>`, using the language's comment syntax. Example: `# shortcut: loads the whole file in memory, stream it when imports exceed 50 MB`. A marker without an upgrade trigger is not allowed. Every marker is listed in the implementation report; the shortcut ledger is built by searching for them.
2. **Tool directives** that a tool requires in comment syntax: a shebang, `eslint-disable-next-line`, `@ts-expect-error`, `# noqa`, `# type: ignore`, `// nolint`, encoding or SPDX license headers when the project requires them. Each directive is listed in the implementation report with its reason.

Existing comments in code you do not otherwise change stay as they are: removing them is unrelated refactoring.

## 3. Size limits

Defaults; the project may override them in `.quality/config.json`:

| Unit | Limit |
| --- | --- |
| File | 400 lines |
| Function or method | 30 lines |
| Parameters per function | 4 |
| Cyclomatic complexity per function | 10 |
| Nesting depth | 3 |

The limits are **signals of mixed responsibilities**, not targets. When a unit crosses one, split it **by responsibility**, never by line count, and never into helpers that exist only to make a function shorter. A cohesive 35-line function beats three fragments that must be read together.

A file that already exceeded a limit before the feature must not grow. If the change needs to grow it, splitting it is a refactor outside the approved scope: report it as a decision for the programmer.

## 4. Names

- Declarative names: they say **what** something is or does, in the domain's words. `overdueInvoices`, `calculateShippingCost`, `isEligibleForRefund`.
- Functions are verbs, values are nouns, booleans read as questions (`is`, `has`, `can`, `should`).
- No abbreviations a newcomer would have to decode, no type suffixes (`userList`, `dataObj`), no meaningless names (`data`, `info`, `manager`, `helper`, `utils`, `handle`, `process`, `tmp`) unless the domain uses the word.
- One name per concept across the codebase. If the project already calls it `customer`, do not introduce `client`.
- The length of a name grows with its scope: a loop index may be `i`, a module-level export may not.

## 5. Single Responsibility

- A module, class or function has **one reason to change**: one actor or one concern.
- Test: describe the unit in one sentence without "and" or "or". If you cannot, it has more than one responsibility.
- Separate decisions from effects: pure logic (rules, calculations, transformations) lives apart from I/O (network, storage, UI, clock, randomness). This also makes the logic testable without doubles.
- A function works at one level of abstraction: either it orchestrates named steps, or it does one low-level step, not both.
- Commands change state, queries return data; avoid functions that do both, except where the platform idiom demands it.

## 6. Feature folders

Code is organized **by feature** (vertical slices), not by technical type. A feature folder holds everything that changes together for that capability: UI, handlers, domain logic, data access, tests.

```
src/
  features/
    invoices/
      invoice-list.tsx
      invoice-list.test.tsx
      overdue-invoices.ts
      overdue-invoices.test.ts
      invoices-api.ts
    checkout/
      …
  shared/            # only code used by at least two features
```

- **Grow organically.** Start a feature as a few files. Add a sub-folder only when the feature holds several files of one kind that change together. Never create empty layers in advance.
- **Shared is earned.** Code moves to `shared/` only when a second feature actually needs it. A `shared/` that grows faster than the features is an anti-pattern.
- **Boundaries.** A feature uses another feature only through that feature's public entry point (e.g. its `index`), never through its internals.
- Tests sit next to the code they test, or in the project's existing test location if it has one.
- **Existing projects: the existing structure wins.** Feature folders apply to new projects and to projects already organized by feature. In a project organized by technical layer (`controllers/`, `services/`, `models/`…), new code follows those layers and its conventions. Moving to feature folders happens only through an explicit migration the programmer approves as its own work. Never reorganize existing code on your own.

## 7. Design patterns

Know the classic catalog (`knowledge/design-patterns.md`) and use a pattern **only when the problem it solves is present in the code now**, not because it might appear. Name the pattern in the implementation report so the reviewer can check it fits. A pattern with one implementation and no second one in the approved plan is speculative.

## 8. Project anti-patterns

Before writing, read the project's anti-pattern registry (`.quality/anti-patterns.md`), at least the active entries whose scope covers the paths you will touch. Avoiding them is part of this standard. When you notice an anti-pattern that is not registered, record it as a candidate (`protocols/anti-pattern-registry.md`); do not fix unrelated code.

## 9. Quality gate

Before reporting, run `python3 <skill dir>/scripts/quality_gate.py --repo <worktree> --base <base commit>` and the project's own lint and format commands. Fix every violation in code you wrote. Report the output verbatim in the implementation report, including the checks it says were skipped.
