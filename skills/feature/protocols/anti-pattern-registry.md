# Anti-Pattern Registry Protocol

Each project keeps its own registry of anti-patterns: the mistakes that matter **in its architecture**, learned from its own features. Agents read it before writing code, check it after, and propose new entries when they find a mistake that is not registered. The programmer decides what enters the registry. Whatever can be detected mechanically becomes a lint rule, so the mistake is caught by a tool rather than by memory.

## Layout in the project

```
<registry>/
├── config.json          # limits, exclusions, allowed directives, project checks
├── anti-patterns.md     # the registry
└── rules/               # machine rules, one per automated entry, each with its tests
```

**Where the registry lives is the programmer's choice at bootstrap**, because committing it adds files to the project that its maintainers may not want (a contribution to someone else's repository, for example):

| Location | Path | What follows |
| --- | --- | --- |
| Local to this clone | `$(git rev-parse --git-common-dir)/quality/` | Never committed and never in a diff. Shared by every worktree of this clone, and lost if the clone is deleted. Other developers do not see it. |
| Project's existing lint configuration | the place the project already uses | Only what that tool can express; the rest stays local or versioned, as chosen |
| Versioned with the project | `<repo>/.quality/` | Committed. Changes are made in the feature worktree and travel on the feature branch, like any other file, and appear in the feature's diff and pull request. |

Everywhere in this workflow, `.quality/` names the registry wherever it lives. Agents and `scripts/quality_gate.py` look for `<repo>/.quality/` first and then for the local path, so a local registry needs no flag. A local registry is written directly at its path, not in the feature worktree, and is never staged.

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
- **Enforced by:** check · proven on csv-export@a1b2c3d (the original occurrence fails the rule)
- **Seen:** csv-export 2026-11-20 (reviewer) · invoices 2026-12-02 (gate)
```

`Detection` is `automated · <rule path>` or `manual · <what the reviewer looks for>`. `Enforced by` names the level that makes the mistake impossible or caught (§Enforcement levels) and where that was proven; an entry enforced only by the reviewer's attention says `review`. Statuses: **Active** or **Retired** (with date and decision reference). A rejected candidate is listed once under a final `## Rejected candidates` section with its reason, so it is not proposed again.

When the registry passes 400 lines, split it by area (`anti-patterns/<area>.md`) and keep `anti-patterns.md` as an index.

## Bootstrap (first feature in a project without a registry)

1. The Repository Analyst reports the architecture style, the folder organization, and the lint, format and architecture tools already installed.
2. The orchestrator selects the seed catalogs from `knowledge/anti-patterns/` that match that evidence: `general.md` always, plus whichever of `feature-folders.md`, `layered.md`, `frontend-ui.md`, `backend-api.md` and `tests.md` apply.
3. ⛔ Present to the programmer, following `protocols/neutral-decisions.md`:
   - the seed entries, so they choose which to adopt (all, some, none);
   - the limits in `config.json`, with the defaults stated as defaults, next to the repository's own figures (how many files already exceed each limit);
   - `allowDocstrings`, with the evidence of whether the project documents its public units with docstrings;
   - how detection is automated (options below);
   - **where the registry lives** (table above), with the facts of this repository: whether it is the programmer's own project or a contribution, and whether its `.gitignore` or contributing guide says anything about tool files.
4. Write the registry at the chosen location with only what was approved, and record the decision in `decisions/`. When it is versioned, write it in the feature worktree; otherwise never stage it.

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
| C-1 | … | … | the input or change that makes it hurt | new · AP-NNN | yes (how) · no | role · programmer (a correction) |

**The programmer's corrections are candidates too.** When the programmer corrects the agent's work in a way that would apply to other changes ("never call X from Y", "we always do Z"), it is written as a candidate with *Found by: programmer* and their words, even in executor mode and in DIRECT. A correction that repeats an Active entry is an occurrence of it, and, if that entry is enforced only by `review`, a reason to propose a higher level at the next gate.

A candidate needs a concrete case, as a review finding does. "Could be cleaner" is not a candidate.

**3. Register.** ⛔ At the defects gate (or before final acceptance, if there are no defects), the orchestrator presents the candidates. For each one, the options are: add as a new entry · record as an occurrence of AP-NNN · reject (reason recorded). The programmer decides. The orchestrator then updates `anti-patterns.md`.

**4. Enforce.** For each approved entry, the levels of §Enforcement levels are presented at the same gate, in their order and neutrally: the ones that can work for that entry with what each changes and costs, and the ones that cannot, with why. The programmer chooses. A level that changes project code (architecture, types, a test) is work in the feature's scope only when the programmer says so; otherwise it is proposed as its own change. For an entry enforced by a check, the Implementer writes the rule in the approved tool with at least one invalid case (must match) and one valid case (must not match), runs the rule's tests, adds or updates the `checks` command in `config.json`, and sets the entry's `Detection` to `automated`. **Prove every new check, type or test on a real past mistake:** it must fail on the occurrence recorded in *Seen* (check out that commit or reproduce the code in a scratch file) and pass on the fixed code; record where it was proven in *Enforced by*. A manual entry seen in two or more features is proposed for a higher level at the next gate.

**5. Retire.** The programmer may retire an entry (status Retired, with a decision reference). Rules of retired entries are removed from `checks`.

Fixing existing occurrences elsewhere in the codebase is separate work. It is never done silently inside a feature.

## Enforcement levels

From the level that removes the mistake to the one that only describes it. The order is the order of strength, stated as a fact; the programmer chooses the level per entry. Adapted from the `correct` skill of pstack (github.com/cursor/plugins, MIT).

| Level | What it does | What it costs |
| --- | --- | --- |
| 1. Architecture | Makes the wrong way not exist: one owner per piece of state, one supported way per task, internals hidden so the wrong import fails, one source of truth instead of hand-synced lists, old ways deleted | A project refactor, often across files; its own change |
| 2. Types | The bad state cannot be written: it does not compile or type-check | Type changes at the boundary and in callers |
| 3. Check | A lint or CI check fails, and its message names the file, type or function to use instead. If the pattern is already common, it fails only when a change adds more | A rule with its own tests, and its `checks` command |
| 4. Test | A behavior test fails when the mistake recurs. Tests that pass when the behavior breaks, or fail when only the internals change, are fixed or deleted | Test code |
| 5. Review | The critic checks the entry by reading the diff (`manual` detection) | Nothing fails when it is missed |

Assume every future contributor is an agent that sees only the files it opened, copies the nearest example and takes the shortest path that compiles: a change that looks right from one file should be right for the whole repository. Exceptions to a check go on the offending line with a reason, an expiry date and the programmer's approval. An entry whose mistake can no longer happen (level 1 or 2) may be retired, with that fact as its reason.

## Correction sweep (`/feature correct`)

The programmer may ask, outside any feature, for a sweep of the mistakes agents keep repeating in this repository:

1. **Find the mistake classes.** Read the recent commits, reverts, review comments of pull requests (`gh` when available), the registry's *Seen* lines and rejected candidates, the features' `reports/anti-pattern-candidates.md`, and the repository's agent instruction files. Group the mistakes into classes; a class counts once it has happened twice. Each class cites its occurrences (commit, `path:line`, review comment).
2. **⛔ Present** each class with its evidence, whether the registry already has it (and at which level), and the levels that can work and those that cannot, under `protocols/neutral-decisions.md`. The programmer chooses which classes to enforce, at which level, and where the work happens: a branch of its own (a worktree, `protocols/executor.md` §Worktree) or a feature.
3. **Enforce and prove,** one commit per class: write the architecture change, type, check or test; show it failing on a real past occurrence and passing on the current code; run the same command the CI runs. Update or add the registry entry, with *Enforced by*.
4. **Report** each class with its evidence, the level chosen, where it was proven, and why the higher levels were not used. Integration is a ⛔ gate as in any workflow.

## Shortcut ledger

`shortcut:` markers (`knowledge/code-quality.md` §2) are deliberate debt, not anti-patterns. `scripts/quality_gate.py` lists the markers added by the feature. The final report lists them, and markers without an upgrade trigger are violations.
