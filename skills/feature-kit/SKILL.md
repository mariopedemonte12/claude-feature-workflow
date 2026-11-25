---
name: feature-kit
description: Loads the feature workflow's engineering skills (planning, code quality, testing, review…) as an on-demand catalog for hand-driven work, without starting the workflow. Manual invocation only.
argument-hint: "[module…] | list | off"
disable-model-invocation: true
---

# Feature Kit: skills without the workflow

The programmer is working **by hand** and wants the workflow's knowledge available, not the workflow. You are **not** the orchestrator:

- No workflow selection, phases, gates, feature slugs, worktrees, artifacts, handoffs, memory files or claims.
- No subagents, except where a module below says so and the programmer asks for that module.
- The programmer drives. You do what they ask, the way you normally would, applying the loaded modules to your own work.

- **Request:** $ARGUMENTS
- **Command name:** `/feature-kit` standalone, `/feature-workflow:feature-kit` as a plugin. Use the form that applies wherever this file says `/feature-kit` or `/feature`.
- **Kit directory:** `${CLAUDE_SKILL_DIR}`. **Library:** `${CLAUDE_SKILL_DIR}/../feature`. Every module path below is relative to the library; read it by its absolute path.
- **Language:** the programmer's.

## How modules load

1. **Lazily.** Do not read any module now, except the ones named in the request. Read a module the first time the current task needs it, by the triggers below, or when the programmer names it ("plan this", "use ponytail", "test it").
2. **Announce it** in one line, e.g. `Loaded: test (testing-techniques.md)`. Do not re-read a module already loaded in this session unless the context was compacted.
3. **Take the method, drop the process.** Role files are written for subagents inside the workflow. From them, apply the method, the checklists and the quality rules; ignore what belongs to the workflow: worktree location checks, handoffs, report files, artifact paths, delegation logs and gates. Write a file only when the programmer asks for one.
4. **Your own skills too.** The skill index of the workflow (`protocols/skills.md` §Where skills come from) applies here: build it from the frontmatter the first time a module loads, and load a skill of the programmer (`~/.claude/feature-skills/`), the repository (`<repo>/.claude/feature-skills/`) or a module of it (`<module>/.claude/feature-skills/`, when you work on files under `<module>`) when its signals match or its `use-in` covers what you are doing. A more specific skill replaces the library's with the same name. Announce each one like a module.
5. **Project knowledge first.** If the repository has a registry, at `<repo>/.quality/` or locally at `$(git rev-parse --git-common-dir)/quality/` (`config.json`, `anti-patterns.md`, `rules/`), its limits and registry override the library defaults whenever the `quality` module is active.

## Catalog

| Module | Load when | Read |
| --- | --- | --- |
| `edge-cases` | before writing code for a request: reach of broad statements, nearest analog, cases per input | `knowledge/edge-cases.md` |
| `explore` | mapping unfamiliar code, finding conventions, build and test commands | `roles/repository-analyst.md` |
| `refine` | the programmer is not sure what they need, the request names a solution without its problem, or context is missing | `protocols/refinement.md` §Steps (no feature, no files; the confirmed intent stays in the conversation unless the programmer asks for a record) |
| `spec` | the requirement is vague, contradictory or missing acceptance criteria | `knowledge/specification-guide.md`; the method of `roles/spec-writer.md` (every item traced to a source; gaps become questions to the programmer) |
| `plan` | choosing how to implement something with more than one viable approach | `roles/planner.md`, then `protocols/decisions.md` before presenting options |
| `decide` | any choice that belongs to the programmer | `protocols/decisions.md`: the options with their facts, what you left out, and your labeled recommendation |
| `writing` | writing documentation, a README, a PR description, a commit message or a report | `knowledge/writing.md` |
| `quality` (alias `ponytail`) | writing or changing code, debugging, or shaping the types and modules of a change | `knowledge/code-quality.md` (including §Root causes and §10 Design principles), plus the project's `.quality/anti-patterns.md` if present |
| `patterns` | a design pattern is being considered or a structure feels forced | `knowledge/design-patterns.md` |
| `antipatterns` | creating or updating the project's anti-pattern registry or lint rules | `protocols/anti-pattern-registry.md` and the matching `knowledge/anti-patterns/*.md` |
| `test` | writing or evaluating tests | `knowledge/testing-techniques.md`; the method section of `roles/tester.md` |
| `e2e` | a change is user-facing and needs end-to-end evidence | `knowledge/e2e-testing.md` |
| `gate` | checking a change against the quality limits | run `python3 <library>/scripts/quality_gate.py --repo <repo> --base <ref>`; uses `.quality/config.json` when present |
| `review` | the programmer asks for a review | see below |
| `specialist <name>` | the work touches a specialist's domain (security, ux-ui, database, network, performance, observability, or the project's or programmer's own) | the specialist file, found as `protocols/skills.md` §Where skills come from describes. Apply its phase sections as checklists. Its `audit` phase runs as a clean subagent only if the programmer asks, like `review` |
| `measure` | reporting or deciding on a measured number: a speedup, a regression, a latency, an eval result | `knowledge/measurement.md` |
| `correct` | the programmer wants the mistakes agents repeat in this repository made impossible, or corrects you in a way that applies beyond this change | `protocols/anti-pattern-registry.md` §Enforcement levels and §Correction sweep (its ⛔ steps become questions to the programmer) |
| `verify-skill` | the programmer wants a scripted way for agents to drive the real app and capture evidence | `protocols/verification-skills.md` §Where the skill lives, §App verification |
| `formal-skill` | concurrency, retries, a state machine, a parser or unsafe code need more than tests; or a state machine should be shown as a statechart | `protocols/verification-skills.md` §Formal verification, §Statecharts |
| `card` | the programmer wants a single-file record of the change (target 500 lines, overflow to linked files) | `templates/feature-card.md` |

**`review`.** A reviewer that wrote the code is biased toward it. So for a review, spawn a clean subagent (model `opus`) briefed only with `roles/reviewer.md`, the repository path, the diff range and the programmer's own words about the change, verbatim (the request and, if refinement ran, the confirmed intent and later corrections): never the conversation, the plan or your own reasoning. If the programmer asks to verify its findings, spawn a second clean subagent (model `sonnet`) with `roles/verifier.md` and the findings. Present the verified findings; fix only what the programmer approves. For a quick self-check instead, the programmer must ask for it explicitly, and you say it is not a clean review.

## Commands

- **`/feature-kit`**: activate with no module loaded; reply with the module names in one line.
- **`/feature-kit <module…>`**: activate and load those modules now, e.g. `/feature-kit plan quality`.
- **`/feature-kit list`**: show the catalog table.
- **`/feature-kit off`**: stop applying the kit's modules for the rest of the session.

The kit stays active for the session. After a context compaction, the catalog may be lost: if you no longer have this table, say so and ask the programmer to run `/feature-kit` again.

**Escalating.** If the work grows into something that needs gates, parallel features or artifacts, you may tell the programmer once that `/feature` exists, with its DIRECT, SDD and EVO workflows, as orchestrator or executor. Never start it yourself.
