# Anti-Pattern Registry Protocol

Each project keeps its own registry of anti-patterns: the mistakes that matter **in its architecture**, learned from its own features. Agents read it before writing code, check it after, and propose new entries when they find a mistake that is not registered. The programmer decides what enters the registry. Whatever can be detected mechanically becomes a lint rule, so the mistake is caught by a tool rather than by memory.

## Layout in the project

```
<repo>/.quality/
├── config.json          # limits, exclusions, allowed directives, project checks
├── anti-patterns.md     # the registry
└── rules/               # machine rules, one per automated entry, each with its tests
```

`.quality/` is versioned with the project. Changes to it are made in the feature worktree and travel on the feature branch, like any other file. If the project already has an equivalent place for lint configuration, the programmer may choose it instead at bootstrap.

### `config.json`

```json
{
  "limits": { "fileLines": 400, "functionLines": 30, "parameters": 4, "cyclomaticComplexity": 10 },
  "exclude": ["**/generated/**", "**/migrations/**", "**/vendor/**"],
  "allowedCommentPatterns": [],
  "checks": [
    { "name": "ast-grep rules", "command": "ast-grep scan", "covers": ["AP-003", "AP-007"] }
  ]
}
```

Every field is optional; `scripts/quality_gate.py` falls back to the defaults in `knowledge/code-quality.md`. `checks` are shell commands run from the repository root; a non-zero exit is a violation.

### Entry format (`anti-patterns.md`)

```markdown
### AP-007 · Cross-feature internal import
- **Status:** Active · since 2026-11-20 (csv-export, csv-export/D-004)
- **Scope:** src/features/**
- **Smell:** a feature imports a file inside another feature's folder.
- **Why it hurts here:** features change independently; internal imports couple their releases.
- **Instead:** import from the other feature's index; move code to shared/ once two features need it.
- **Example:** ✗ `import { rate } from '../billing/tax/rate'` · ✓ `import { rate } from '../billing'`
- **Detection:** automated · `.quality/rules/ap-007.yml` (covered by check "ast-grep rules")
- **Seen:** csv-export 2026-11-20 (reviewer) · invoices 2026-12-02 (gate)
```

`Detection` is `automated · <rule path>` or `manual · <what the reviewer looks for>`. Statuses: **Active** or **Retired** (with date and decision reference). A rejected candidate is listed once under a final `## Rejected candidates` section with its reason, so it is not proposed again.

When the registry passes 400 lines, split it by area (`anti-patterns/<area>.md`) and keep `anti-patterns.md` as an index.

## Bootstrap (first feature in a project without a registry)

1. The Repository Analyst reports the architecture style, the folder organization, and the lint, format and architecture tools already installed.
2. The orchestrator selects the seed catalogs from `knowledge/anti-patterns/` that match that evidence: `general.md` always, plus whichever of `feature-folders.md`, `layered.md`, `frontend-ui.md`, `backend-api.md` and `tests.md` apply.
3. ⛔ Present to the programmer, following `protocols/neutral-decisions.md`:
   - the seed entries, so they choose which to adopt (all, some, none);
   - the limits in `config.json`, with the defaults stated as defaults, next to the repository's own figures (how many files already exceed each limit);
   - `allowDocstrings`, with the evidence of whether the project documents its public units with docstrings;
   - how detection is automated (options below).
4. Write `.quality/` in the feature worktree with only what was approved, and record the decision in `decisions/`.

The bootstrap happens once per project. If another feature in progress also bootstraps or edits `.quality/`, report the overlap as described in `protocols/multi-feature.md`.

## Automation options (presented neutrally, in this order)

| Option | What it detects | Cost |
| --- | --- | --- |
| ast-grep | Structural code patterns in many languages (tree-sitter), YAML rules, `kind: comment` matching, rule tests with valid/invalid cases (`ast-grep test`) | One binary as a dev dependency. On Linux the short name `sg` may be another program: call `ast-grep` |
| Architecture / import rule tools | Layer and feature boundaries, forbidden imports, cycles: dependency-cruiser or eslint-plugin-boundaries (JS/TS), import-linter (Python), ArchUnit (JVM), depguard (Go) | One dev dependency per ecosystem; covers imports only |
| Manual only | Anything; the clean Critic checks the entries by reading the diff | No dependency; depends on critic attention, so it can miss cases |
| Native linter of the stack | What its built-in or plugin rules cover (ESLint, Ruff, golangci-lint, RuboCop, Detekt…) | No new dependency if the project already uses it; custom rules may need plugin code |
| Semgrep | Code patterns with metavariables and taint flows in many languages, YAML rules, rule tests (`semgrep --test`) | Larger install as a dev dependency |

`scripts/quality_gate.py` needs no dependency for file length and full-line comments. If `lizard` is installed, it also checks function length, parameters and complexity; otherwise it reports those as not checked.

## The learning loop

**1. Prevent.** The Planner and the Implementer read the active entries whose scope covers the paths they will touch, before planning or coding.

**2. Detect.**
- The Implementer runs `scripts/quality_gate.py`, which runs the limits, the comment check and every `checks` command.
- At review levels R1 and R2, the clean Critic re-runs the gate and checks the `manual` entries against the diff (`protocols/review-cycle.md`).
- The Implementer and the Tester write unregistered recurring mistakes as candidates in the feature's `reports/anti-pattern-candidates.md`. Critics and verifiers only mark findings `candidate`; the orchestrator copies them into that file.

Candidate format, one row per candidate:

| ID | Smell | Location (`path:line`) | Concrete case | Matches | Mechanizable | Found by |
| --- | --- | --- | --- | --- | --- | --- |
| C-1 | … | … | the input or change that makes it hurt | new · AP-NNN | yes (how) · no | role |

A candidate needs a concrete case, as a review finding does. "Could be cleaner" is not a candidate.

**3. Register.** ⛔ At the defects gate (or before final acceptance, if there are no defects), the orchestrator presents the candidates. For each one, the options are: add as a new entry · record as an occurrence of AP-NNN · reject (reason recorded). The programmer decides. The orchestrator then updates `anti-patterns.md`.

**4. Automate.** For an approved, mechanizable entry, the Implementer writes the rule in the approved tool with at least one invalid case (must match) and one valid case (must not match), runs the rule's tests, adds or updates the `checks` command in `config.json`, and sets the entry's `Detection` to `automated`. A manual entry seen in two or more features is proposed for automation at the next gate.

**5. Retire.** The programmer may retire an entry (status Retired, with a decision reference). Rules of retired entries are removed from `checks`.

Fixing existing occurrences elsewhere in the codebase is separate work. It is never done silently inside a feature.

## Shortcut ledger

`shortcut:` markers (`knowledge/code-quality.md` §2) are deliberate debt, not anti-patterns. `scripts/quality_gate.py` lists the markers added by the feature. The final report lists them, and markers without an upgrade trigger are violations.
