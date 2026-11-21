# Feature Workflow for Claude Code

A Claude Code skill that turns a session into an orchestrated, multi-agent software engineering process (specification → planning → implementation → testing → validation) in which **the programmer makes every consequential decision**.

It loads **only when you call it** (`/feature`). In every other session it costs, at most, a one-line description (~70 tokens). The workflow itself (~4k tokens for the entry point) loads only on invocation.

## What you get

- **Two workflows, chosen per feature by uncertainty, not size.**
  - **SDD Direct:** for well-understood features.
  - **Evolutionary Spec-Driven Development (ESDD):** for features with open requirements or technical unknowns.
  - **Hybrid:** ESDD only for the uncertain part.
- **Specialized subagents.** Repository Analyst, Specification Writer, Planner, Implementer, Tester, Clean Code Critic and Finding Verifier, each driven by its own role file.
- **Agents ask you, through the orchestrator.** When an agent needs an answer only you can give, it stops instead of guessing and returns its questions (blocking or not, with evidence and neutral options). The orchestrator records them in the spec or in `decisions/`, puts them to you, and resumes the same agent with your answers and its context intact. This is what keeps specification and planning from building on invented requirements.
- **Per-task model selection.** Every role has a standard model, and the orchestrator picks the cheapest sufficient model for *each* delegation. That can be higher or lower than the standard, with floors so architecture and review are never downgraded. Every non-standard choice is announced, and every delegation is logged.
- **Neutral decision gates.** Options are never recommended or ranked: they are sorted alphabetically, given symmetric pros and cons, described with verifiable facts instead of adjectives, and excluded options are listed with the constraint they violate. The agent gives an opinion only if you explicitly insist on one.
- **One git worktree per feature.** Every feature, even a lone one, lives in its own worktree created with Claude Code's built-in worktree support (`.claude/worktrees/<slug>`, on its own branch). Its code and artifacts travel on that branch. How it is integrated (merge, pull request…) and whether the worktree is removed are your decisions.
- **Several features in parallel.** One orchestrator acts as the single intermediary between you and the agents of every feature. Each feature has its own workflow, gates, artifacts and agents. A gate in one feature does not block the others. Overlaps between features (files changed on several branches, shared test resources) are reported early.
- **Optional phased mode for large portfolios (experimental, never run).** By default the orchestrator runs every phase itself. With `--phased`, it keeps only what needs you (gates, questions, decisions, the portfolio) and hands each phase of a feature to a short-lived phase runner that orchestrates that phase's agents and stops at its first gate. Same gates and decisions; less visibility inside a phase; an orchestrator context that grows far more slowly. Estimated costs are in [`docs/cost-estimates.md`](docs/cost-estimates.md).
- **Several orchestrators, if you want them.** Three modes, none mandatory: a single orchestrator; independent orchestrators in separate sessions that see each other's features through shared claims; or a hierarchy, where a principal orchestrator (`/feature hub`) is your only channel and coordinates sub-orchestrators, one per group of features, each with its own context. The principal collects every sub-orchestrator's decision requests into one queue, ordered by how much work each one blocks, and routes your answers back. Sub-orchestrators can run as an agent team, as separate sessions with cross-session messaging, or as subagents: you choose.
- **Artifacts as source of truth.** Specification, plan, testing plan, decision records, reports and a handoff file per feature. Any feature can be resumed in a new session.
- **Three intensity levels per feature or group: Lite, Medium, High.** Lite runs one implementer that writes code and tests, a single spec-and-plan gate and a one-page feature card. Medium adds a tester, a clean critic and separate spec, plan and defects gates with size budgets. High runs every agent, gate and artifact, including the review cycle and mutation testing. Critical features always run at High.
- **Code quality standard for every agent that writes code.** The smallest complete change (reuse → standard library → installed dependency → minimum new code), no comments except `shortcut: <limit>, <when to upgrade>` markers and tool directives, files up to 400 lines and short functions as signals of mixed responsibilities, declarative names, single responsibility, feature folders where the project uses them, and classic design patterns only for problems present now. A dependency-free quality gate (`scripts/quality_gate.py`) checks the feature's changes; with `lizard` installed it also checks function size and complexity.
- **A per-project anti-pattern registry that learns.** Seeded from catalogs matching the project's architecture (general, feature folders, layered/hexagonal, component UIs, back ends, tests). Agents read it before coding and record new anti-patterns they find as candidates; you approve what enters it, and entries that can be detected mechanically become lint rules (ast-grep, Semgrep, import-rule tools or the stack's own linter: your choice).
- **End-to-end testing by the Tester.** Every user-facing acceptance criterion is exercised through the real entry point: Playwright for web UIs, real HTTP requests, CLI processes, mobile and desktop drivers, or a deterministic simulation harness when there is no interactive surface.
- **A lean pipeline: `/feature-lean`.** For one feature per session, without an orchestrator relay:
  - the session itself specifies the feature, with its edge, error, security and worst-case behavior;
  - one gate with your answers and the approach, where options carry their security consequence and their probed worst case;
  - code with tests and the quality gate;
  - one clean critic, whose every finding comes to you.
- **The skills without the workflow: `/feature-kit`.** When you work on a feature by hand, `/feature-kit` makes the workflow's knowledge available as a catalog of modules (explore, spec, plan, decide, quality/ponytail, patterns, anti-patterns, test, e2e, gate, review, card) that the agent loads only when the task needs one, or when you name it. No phases, gates, artifacts, worktrees or subagents, except a clean critic when you ask for a review.
- **Testing discipline.** Boundary value analysis, fuzz/property-based, symbolic/concolic, decision tables and state machines, each reported as *Applied*, *Not applicable* (with a reason) or *Blocked* (with an explanation). Mutation testing is mandatory for features you mark as critical.

## Install

**Option A: plugin** (inside Claude Code)

```
/plugin marketplace add mariopedemonte12/claude-feature-workflow
/plugin install feature-workflow@feature-workflow
```

When installed as a plugin, the commands are namespaced: `/feature-workflow:feature`, `/feature-workflow:feature-lean` and `/feature-workflow:feature-kit`.

**Option B: script** (standalone skill, invoked as `/feature`)

```bash
git clone https://github.com/mariopedemonte12/claude-feature-workflow.git
cd claude-feature-workflow
./install.sh              # all your projects   -> ~/.claude/skills/{feature,feature-kit}
./install.sh --project    # current project only -> ./.claude/skills/{feature,feature-kit}
```

**Option C: manual.** Copy `skills/feature/`, `skills/feature-kit/` and `skills/feature-lean/` side by side into `~/.claude/skills/` (or `<project>/.claude/skills/`). The kit and the lean pipeline read from `../feature`.

Then start a new Claude Code session.

## Usage

```
/feature add CSV export to the reports page       # new feature; you choose the workflow after an uncertainty assessment
/feature migrate auth to OAuth --esdd             # choose the workflow up front (--sdd | --esdd)
/feature add audit log --high --phased            # intensity, and phased mode instead of direct
/feature status                                   # board of every feature in progress
/feature resume csv-export                        # continue a feature (or several) from its handoff
/feature hub                                      # become the principal orchestrator of several groups
/feature join main-hub billing                    # in another session: run the "billing" group for hub "main-hub"
/feature-lean add CSV export                      # lean pipeline: one session, two gates, one clean critic
/feature-kit                                      # work by hand; the agent loads modules on demand
/feature-kit plan quality                         # same, loading the plan and quality modules now
/feature-kit off                                  # stop applying the kit
```

A typical SDD Direct run:

1. **Workflow selection.** The orchestrator assesses uncertainty per dimension, with evidence, and you choose the workflow.
2. **Specification.** The Specification Writer turns your request (kept verbatim in `request.md`) into intent, requirements, constraints, invariants and acceptance criteria, each traced to its source. Its questions come to you through the orchestrator. You approve it and set the criticality.
3. **Planning.** The Planner subagent maps the viable approaches, which are presented neutrally. You choose, and you decide mutation testing; the orchestrator recommends a review level (R0 gate only · R1 single critic · R2 review cycle) and you validate it.
4. **Implementation.** The Implementer follows the approved plan. Any deviation comes back to you as a decision.
5. **Testing and review.** The Tester and a clean critic run in parallel. At R2, a verifier refutes false findings, behavior-preserving fixes are applied automatically and listed at the next gate with a revert option, and a new clean critic reviews only those fixes (3 critic rounds per feature at most, across every path). At R1, every finding goes to you. Defects come back to you as decisions.
6. **Final report.** Built only from evidence. You decide acceptance.
7. **Integration and cleanup.** You choose how the feature branch is integrated and whether its worktree is removed.

ESDD adds exploration, disposable prototypes, increments, discovery classification (Confirmed / Hypothesis / Under exploration / Rejected) and a traceable spec change log.

## How it stays out of your context

- `disable-model-invocation: true` in the skill frontmatter: Claude never loads the skill on its own; only you can, by typing the command. Per Claude Code's documentation, such a skill's description is not offered to the model. `claude plugin details` estimates ~70 always-on tokens as an upper bound; its estimate is the same with or without the flag.
- **Progressive disclosure.** On invocation, only `SKILL.md` (the orchestrator) loads. Workflows, protocols, guides and templates are read when a phase needs them.
- **Roles are files, not global agents.** Agents defined in `~/.claude/agents/` have their descriptions injected into every session. Here, the orchestrator spawns Claude Code's built-in subagents (`Explore`, `Plan`, `general-purpose`) with a model override and points each one at its role file.

## Repository layout

```
.claude-plugin/          plugin + marketplace manifests
install.sh               standalone installer
skills/feature-lean/
└── SKILL.md             lean pipeline: spec + edge cases, one gate, code and tests, one clean critic
skills/feature-kit/
└── SKILL.md             module catalog for hand-driven work (reads from skills/feature)
skills/feature/
├── SKILL.md             orchestrator: principles, startup, roles & model selection, gates
├── workflows/           sdd-direct.md · esdd.md (incl. hybrid)
├── protocols/           neutral-decisions.md · agent-questions.md · context-handoff.md · multi-feature.md · …
├── roles/               repository-analyst · spec-writer · planner · implementer · tester · reviewer (critic) · verifier
├── knowledge/           specification-guide · testing-techniques · code-quality · design-patterns · e2e-testing · anti-patterns/
├── scripts/             quality_gate.py
└── templates/           specification · implementation-plan · testing-plan · decision-record · handoff · final-report · feature-card
```

Artifacts created per feature in your project (default `docs/features/<slug>/`, or your project's own convention):

```
request.md  specification.md  implementation-plan.md  testing-plan.md
decisions/D-NNN-*.md  reports/*.md  delegations.md  handoff.md
```

And once per project, after your approval: `.quality/` (`config.json` with limits and checks, `anti-patterns.md`, `rules/`).

## Customizing

| What | Where |
| --- | --- |
| Standard model per role, deviations and floors | `skills/feature/SKILL.md` §4 |
| Default feature folder | `SKILL.md` §2.3 |
| Neutrality rules, e.g. never giving an opinion even when asked | `protocols/neutral-decisions.md` rule 12 |
| Add engineering knowledge (security review, refactoring…) | new `knowledge/<topic>.md`, plus a row in `SKILL.md` §3 or a reference in the role that uses it |
| Code quality rules and default limits | `knowledge/code-quality.md`; per project in `.quality/config.json` |
| Anti-pattern seed catalogs | `knowledge/anti-patterns/*.md` |
| Rename the command | rename the `skills/feature` folder and the `name:` field |

## Design background

A detailed description of the current architecture, with diagrams of every flow and the responsibilities of each agent, is in [`docs/architecture.md`](docs/architecture.md).

The workflow was derived from a longer design document, included as [`docs/master-prompt.md`](docs/master-prompt.md). Its header lists where the skill deliberately departs from it: neutrality instead of recommendations, per-delegation model selection, multi-feature orchestration and a consolidated skills library.

Part of the code quality standard and of the review checklist adapts [Ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert (MIT): the smallest-complete-change ladder, `shortcut:` markers, splitting by responsibility rather than line count, and findings that require a concrete case. This workflow is stricter on comments and does not install Ponytail's hooks.

The review cycle (clean critics, a refuting verifier, a limit of three rounds) draws on research on self-attribution and self-preference bias in LLM evaluators, adversarial multi-agent review and iterative repair loops. The papers are cited where each piece is justified, in [`protocols/review-cycle.md` §References](skills/feature/protocols/review-cycle.md#references). Most are recent arXiv preprints.

## Requirements and status

- Claude Code with skills and subagents. Built against Claude Code 2.1.319; `claude plugin validate` passes.
- A git repository (or `WorktreeCreate`/`WorktreeRemove` hooks), because every feature runs in its own worktree.
  - The orchestrator creates each worktree with `EnterWorktree` and leaves it immediately with `ExitWorktree` (keep).
  - Subagents run without isolation and work through absolute paths into their feature's worktree.
  - New worktrees branch from `origin/<default-branch>` by default. To branch from your local HEAD instead, set `"worktree": { "baseRef": "head" }` in your Claude Code settings.
- Uses the built-in subagent types `Explore`, `Plan` and `general-purpose`, and the model aliases `haiku`, `sonnet` and `opus`.
- Early version: the structure is validated, but the workflow has not yet been exercised across many real projects. Issues and pull requests are welcome.

## License

[MIT](LICENSE)
