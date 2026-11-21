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
4. **Project knowledge first.** If the repository has `.quality/` (`config.json`, `anti-patterns.md`, `rules/`), its limits and registry override the library defaults whenever the `quality` module is active.

## Catalog

| Module | Load when | Read |
| --- | --- | --- |
| `explore` | mapping unfamiliar code, finding conventions, build and test commands | `roles/repository-analyst.md` |
| `spec` | the requirement is vague, contradictory or missing acceptance criteria | `knowledge/specification-guide.md`; the method of `roles/spec-writer.md` (every item traced to a source; gaps become questions to the programmer) |
| `plan` | choosing how to implement something with more than one viable approach | `roles/planner.md`, then `protocols/neutral-decisions.md` before presenting options |
| `decide` | any choice that belongs to the programmer | `protocols/neutral-decisions.md` |
| `quality` (alias `ponytail`) | writing or changing code | `knowledge/code-quality.md`, plus the project's `.quality/anti-patterns.md` if present |
| `patterns` | a design pattern is being considered or a structure feels forced | `knowledge/design-patterns.md` |
| `antipatterns` | creating or updating the project's anti-pattern registry or lint rules | `protocols/anti-pattern-registry.md` and the matching `knowledge/anti-patterns/*.md` |
| `test` | writing or evaluating tests | `knowledge/testing-techniques.md`; the method section of `roles/tester.md` |
| `e2e` | a change is user-facing and needs end-to-end evidence | `knowledge/e2e-testing.md` |
| `gate` | checking a change against the quality limits | run `python3 <library>/scripts/quality_gate.py --repo <repo> --base <ref>`; uses `.quality/config.json` when present |
| `review` | the programmer asks for a review | see below |
| `card` | the programmer wants a single-file record of the change (up to 500 lines) | `templates/feature-card.md` |

**`review`.** A reviewer that wrote the code is biased toward it (`protocols/review-cycle.md` §References). So for a review, spawn a clean subagent (model `opus`) briefed only with `roles/reviewer.md`, the repository path and the diff range: never the conversation, the plan or your own reasoning. If the programmer asks to verify its findings, spawn a second clean subagent (model `sonnet`) with `roles/verifier.md` and the findings. Present the verified findings; fix only what the programmer approves. For a quick self-check instead, the programmer must ask for it explicitly, and you say it is not a clean review.

## Commands

- **`/feature-kit`**: activate with no module loaded; reply with the module names in one line.
- **`/feature-kit <module…>`**: activate and load those modules now, e.g. `/feature-kit plan quality`.
- **`/feature-kit list`**: show the catalog table.
- **`/feature-kit off`**: stop applying the kit's modules for the rest of the session.

The kit stays active for the session. After a context compaction, the catalog may be lost: if you no longer have this table, say so and ask the programmer to run `/feature-kit` again.

**Escalating.** If the work grows into something that needs gates, parallel features or artifacts, you may tell the programmer that `/feature` exists, once. Never start it yourself.
