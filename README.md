# Feature Workflow for Claude Code

Claude Code skills for building features with the programmer in control of every consequential decision. They come in three entry points, all **manual-only**: each loads only when you type its command.

| Command | What it is | Measured cost (one Django case, 3 large features) |
| --- | --- | --- |
| **`/feature-lean`** | **The main mode.** One session per feature, with no orchestrator relay. It runs a specification pass (edge, error, security and worst-case behavior, each compared with the nearest existing analog), one gate for your answers and the approach, code with tests and the quality gate, and one clean critic whose every finding comes to you. | **5× a plain session** (USD 5.6) |
| `/feature` | The full multi-agent workflow: SDD Direct or Evolutionary Development, specialized subagents, every gate and artifact, review cycle, several features and orchestrators. Opt-in, for when you want its process and can afford it. | 13.5× a plain session (USD 15.2) at High |
| `/feature-kit` | No pipeline: the workflow's knowledge (planning, quality, testing, review…) as modules the agent loads on demand while you work by hand. | not measured; close to a plain session, plus the modules it reads |

In every other session each skill costs, at most, a one-line description (~70 tokens).

## Evidence so far

| | Plain session | `/feature-lean` | `/feature` High |
| --- | --- | --- | --- |
| Hidden tests (Django, 3 large features) | 41/43 | 42/43 | 42/43 |
| Cost | USD 1.1 | USD 5.6 | USD 15.2 |
| Input-equivalent tokens | 0.6M | 2.7M | 8.2M |

- **Real feature, maintainers' tests** (Django HTTP QUERY, #37232): plain 47/48 for USD 0.52, a checklist prompt 48/48 for USD 1.06, `/feature-lean` 47/48 for USD 2.61, `/feature` High 47/48 for USD 8.28; no regressions in any arm. The miss was the same everywhere (`RedirectView`). `/feature`'s critic found it, but the gate framed the fix as beyond the spec and the simulated programmer declined it. That led to treating the spec as the current reading of the intent (below).
- **Smaller cases:** across four experiments (a toy project, Python-Markdown, two Django runs), the full workflow passed 120/121 hidden tests against the plain session's 114/121, at about 12× the cost.
- **What helped quality was cheap:** enumerating edge cases before coding, one clean critic, and comparing with the nearest analog. Those are what `/feature-lean` keeps. The full workflow's extra machinery (orchestrator relay, verifier, extra review rounds) showed no proportional gain.
- **Limits of this evidence.** Each configuration ran once (n=1). The hidden tests were written by the same people who designed the workflow, the programmer was simulated, and none of this is real day-to-day use. Treat it as a direction, not a result. Details: [`docs/cost-estimates.md`](docs/cost-estimates.md).
- **Usage budgets.** The full workflow spends millions of tokens per feature group. On plans with a usage limit, such as Pro, it can exhaust the limit within one run; `/feature-lean` fits far better.

## `/feature-lean`

How it works, step by step, with examples and the measured cost: [`docs/lean.md`](docs/lean.md). The behavior itself is defined in [`skills/feature-lean/SKILL.md`](skills/feature-lean/SKILL.md). One feature per session, in its own git worktree; several features means several sessions, which can run in parallel. The only artifacts are a card (target 500 lines; overflow goes to linked files, never cut) and the critic's review. Gate 1 settles behavior and approach, gate 2 the critic's findings, then acceptance, integration and cleanup.

## `/feature-kit`

When you work on a feature by hand, `/feature-kit` makes the workflow's knowledge available as a catalog of modules (explore, spec, plan, decide, quality/ponytail, patterns, anti-patterns, test, e2e, gate, review, card) that the agent loads only when the task needs one, or when you name it. No phases, gates, artifacts, worktrees or subagents, except a clean critic when you ask for a review.

## `/feature`: the full workflow


- **The spec is a reading of your intent, not a closed contract.** Your request evolves as you talk: every statement of yours that changes the intent goes, verbatim, to an intent record that is consolidated with your confirmation at each gate, and that the spec cites as its source. The spec maps where the broad statements in your words reach, and marks which boundaries you drew and which are the agent's reading. Anything a later phase finds that it did not foresee comes back to you as a discovery, framed against your own words, never dismissed as "not in the spec".
- **Two workflows, chosen per feature by uncertainty, not size.**
  - **SDD Direct:** for well-understood features.
  - **Evolutionary Development:** for features with open requirements or technical unknowns. No specification: your intent record, your decisions and the designed test cases carry what the feature must do, increment by increment, main flows first.
  - **Hybrid:** SDD Direct with a specification, and the evolutionary loop only for the uncertain part.
- **Specialized subagents.** Repository Analyst, Specification Writer, Planner, Test Designer, Implementer, Tester, Clean Code Critic and Finding Verifier, each driven by its own role file.
  - **Tests:** the Test Designer derives the test cases from the approved spec, in parallel with the Planner and without seeing the plan. Only the Tester writes tests. The Implementer writes production code to the quality standard and reviews its own diff against the critic's checklist first, so review finds little to rework.
  - **Headless:** agents run in the background. You see one line when an agent starts or finishes, and the full content at gates.
  - **Reuse:** when work goes back to a role (fixes, re-tests, spec changes), the same agent is resumed with its context. Critics and verifiers are always new.
- **Specialists you can extend.** Domain experts join the phases they are useful in: `spec` (questions), `plan` (facts per option), `test-design` (cases) and `audit` (a clean review with executed evidence).
  - **Built in:** `security`, `ux-ui`, `database`, `network`, `performance` and `observability`.
  - **Your own:** add them in `~/.claude/feature-specialists/` (all your projects) or `<repo>/.claude/feature-specialists/` (one project, versioned). For the same name, the project's file wins over yours, and yours over the built-in one.
  - **Activation:** the orchestrator or Lean session detects which specialists match the feature (paths, spec terms, trust boundaries) and presents them as facts; you confirm which run. `--with database,ux-ui` activates them directly. `security` is mandatory for Critical features it matches.
  - **Cost:** only an index of one line per specialist is loaded until one is activated. Available in `/feature`, `/feature-lean` and `/feature-kit`.
- **Agents ask you, through the orchestrator.** When an agent needs an answer only you can give, it stops instead of guessing and returns its questions (blocking or not, with evidence and neutral options). The orchestrator records them in the spec or in `decisions/`, puts them to you, and resumes the same agent with your answers and its context intact. This is what keeps specification and planning from building on invented requirements.
- **Per-task model selection.** Every role has a standard model, and the orchestrator picks the cheapest sufficient model for *each* delegation. That can be higher or lower than the standard, with floors so architecture and review are never downgraded. Every non-standard choice is announced, and every delegation is logged.
- **Neutral decision gates.** Options are never recommended or ranked: they are sorted alphabetically, given symmetric pros and cons, described with verifiable facts instead of adjectives, and excluded options are listed with the constraint they violate. The agent gives an opinion only if you explicitly insist on one.
- **One git worktree per feature.** Every feature, even a lone one, lives in its own worktree created with Claude Code's built-in worktree support (`.claude/worktrees/<slug>`, on its own branch). Its code and artifacts travel on that branch. How it is integrated (merge, pull request…) and whether the worktree is removed are your decisions.
- **Several features in parallel.** One orchestrator acts as the single intermediary between you and the agents of every feature. Each feature has its own workflow, gates, artifacts and agents. A gate in one feature does not block the others. Overlaps between features (files changed on several branches, shared test resources) are reported early.
- **Optional phased mode for large portfolios (experimental, never run).** By default the orchestrator runs every phase itself. With `--phased`, it keeps only what needs you (gates, questions, decisions, the portfolio) and hands each phase of a feature to a short-lived phase runner that orchestrates that phase's agents and stops at its first gate. Same gates and decisions; less visibility inside a phase; an orchestrator context that grows far more slowly. Estimated costs are in [`docs/cost-estimates.md`](docs/cost-estimates.md).
- **Several orchestrators, if you want them.** Three modes, none mandatory: a single orchestrator; independent orchestrators in separate sessions that see each other's features through shared claims; or a hierarchy, where a principal orchestrator (`/feature hub`) is your only channel and coordinates sub-orchestrators, one per group of features, each with its own context. The principal collects every sub-orchestrator's decision requests into one queue, ordered by how much work each one blocks, and routes your answers back. Sub-orchestrators can run as an agent team, as separate sessions with cross-session messaging, or as subagents: you choose.
- **Artifacts as source of truth.** Specification, plan, testing plan, decision records, reports and a handoff file per feature. Any feature can be resumed in a new session.
- **Three intensity levels per feature or group: Lite, Medium, High.** Lite runs one implementer that writes code and tests, a single spec-and-plan gate and a feature card (target 500 lines; overflow goes to linked files, never cut). Medium adds a tester, a clean critic and separate spec, plan and defects gates with size budgets. High runs every agent, gate and artifact, including the review cycle and mutation testing. Critical features always run at High.
- **Code quality standard for every agent that writes code.** The smallest complete change (reuse → standard library → installed dependency → minimum new code), no comments except `shortcut: <limit>, <when to upgrade>` markers and tool directives, files up to 400 lines and short functions as signals of mixed responsibilities, declarative names, single responsibility, feature folders where the project uses them, and classic design patterns only for problems present now. A dependency-free quality gate (`scripts/quality_gate.py`) checks the feature's changes; with `lizard` installed it also checks function size and complexity.
- **A per-project anti-pattern registry that learns.** Seeded from catalogs matching the project's architecture (general, feature folders, layered/hexagonal, component UIs, back ends, tests). Agents read it before coding and record new anti-patterns they find as candidates; you approve what enters it, and entries that can be detected mechanically become lint rules (ast-grep, Semgrep, import-rule tools or the stack's own linter: your choice).
- **End-to-end testing by the Tester.** Every user-facing acceptance criterion is exercised through the real entry point: Playwright for web UIs, real HTTP requests, CLI processes, mobile and desktop drivers, or a deterministic simulation harness when there is no interactive surface.
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
/feature-lean add CSV export                      # main mode: one session, two gates, one clean critic
/feature-lean resume csv-export                   # continue it in a new session
/feature-lean add bulk import --with database,performance   # activate specialists up front
/feature add CSV export to the reports page       # new feature; you choose the workflow after an uncertainty assessment
/feature migrate auth to OAuth --evo              # choose the workflow up front (--sdd | --evo)
/feature add audit log --high --phased            # intensity, and phased mode instead of direct
/feature status                                   # board of every feature in progress
/feature resume csv-export                        # continue a feature (or several) from its handoff
/feature hub                                      # become the principal orchestrator of several groups
/feature join main-hub billing                    # in another session: run the "billing" group for hub "main-hub"
/feature-kit                                      # work by hand; the agent loads modules on demand
/feature-kit plan quality                         # same, loading the plan and quality modules now
/feature-kit off                                  # stop applying the kit
```

A typical SDD Direct run:

1. **Workflow selection.** The orchestrator assesses uncertainty per dimension, with evidence, and you choose the workflow.
2. **Specification.** The Specification Writer turns your request (kept in `intent.md`, the intent record: your original request, a consolidated intent you confirm at each gate, and your statements since, verbatim) into intent, requirements, constraints, invariants and acceptance criteria, each traced to its source. Its questions come to you through the orchestrator. You approve it and set the criticality.
3. **Planning and test design.** In parallel, the Planner maps the viable approaches and the Test Designer derives the test cases from the spec. Both are presented at the same gate: you choose an approach, approve the testing plan, and decide mutation testing; the orchestrator recommends a review level (R0 gate only · R1 single critic · R2 review cycle) and you validate it.
4. **Implementation.** The Implementer writes production code for the approved plan, without tests. Any deviation comes back to you as a decision.
5. **Testing and review.** The Tester implements the designed cases and runs them, and a clean critic reviews in parallel. Fixes go back to the same Implementer, which makes the Tester's failing tests pass. At R2, a verifier refutes false findings, behavior-preserving fixes are applied automatically and listed at the next gate with a revert option, and a new clean critic reviews only those fixes (3 critic rounds per feature at most, across every path). At R1, every finding goes to you. Defects come back to you as decisions.
6. **Final report.** Built only from evidence. You decide acceptance.
7. **Integration and cleanup.** You choose how the feature branch is integrated and whether its worktree is removed.

Evolutionary Development replaces the specification with the intent record and the cases, and adds exploration, disposable prototypes, increments that deliver one flow at a time, hypotheses with their status, and edge cases that are covered or explicitly deferred in each increment.

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
├── workflows/           sdd-direct.md · evolutionary.md (incl. hybrid)
├── protocols/           neutral-decisions.md · agent-questions.md · context-handoff.md · multi-feature.md · …
├── roles/               repository-analyst · spec-writer · planner · test-designer · implementer · tester · reviewer (critic) · verifier
├── specialists/         security · ux-ui · database · network · performance · observability (extensible)
├── knowledge/           specification-guide · testing-techniques · code-quality · design-patterns · e2e-testing · anti-patterns/
├── scripts/             quality_gate.py
└── templates/           specification · implementation-plan · testing-plan · decision-record · handoff · final-report · feature-card
```

Artifacts created per feature in your project (default `docs/features/<slug>/`, or your project's own convention):

```
intent.md  specification.md  implementation-plan.md  testing-plan.md
decisions/D-NNN-*.md  reports/*.md  delegations.md  handoff.md
```

And once per project, after your approval: the anti-pattern registry (`config.json` with limits and checks, `anti-patterns.md`, `rules/`), either versioned at `<repo>/.quality/` or local to your clone at `<git-common-dir>/quality/`, as you choose.

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

Part of the code quality standard and of the review checklist adapts [Ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert (MIT): the smallest-complete-change ladder, `shortcut:` markers, splitting by responsibility rather than line count, and findings that require a concrete case. This workflow is stricter on comments and does not install Ponytail's hooks. The surgical-change rules (every changed line traces to the request, match the existing style, mention pre-existing dead code instead of deleting it) and test-first defect fixes adapt the [Karpathy-inspired guidelines](https://github.com/forrestchang/andrej-karpathy-skills) by Forrest Chang (MIT).

The review cycle (clean critics, a refuting verifier, a limit of three rounds) draws on research on self-attribution and self-preference bias in LLM evaluators, adversarial multi-agent review and iterative repair loops. The papers, and which piece each one justifies, are in [`docs/references.md`](docs/references.md), outside the skills, so no citation is loaded into an agent's context. Most are recent arXiv preprints.

## Requirements and status

- Claude Code with skills and subagents. Built against Claude Code 2.1.319; `claude plugin validate` passes.
- A git repository (or `WorktreeCreate`/`WorktreeRemove` hooks), because every feature runs in its own worktree.
  - The orchestrator creates each worktree with `EnterWorktree` and leaves it immediately with `ExitWorktree` (keep).
  - Subagents run without isolation and work through absolute paths into their feature's worktree.
  - New worktrees branch from `origin/<default-branch>` by default. To branch from your local HEAD instead, set `"worktree": { "baseRef": "head" }` in your Claude Code settings.
- Uses the built-in subagent types `Explore`, `Plan` and `general-purpose`, and the model aliases `haiku`, `sonnet` and `opus`.
- Early version. Measured only in controlled experiments with a simulated programmer (see *Evidence so far*), not in real day-to-day use. Phased mode and the orchestrator hierarchy have never been run. Issues and pull requests are welcome.

## License

[MIT](LICENSE)
