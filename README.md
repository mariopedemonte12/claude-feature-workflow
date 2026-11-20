# Feature Workflow for Claude Code

A Claude Code skill that turns a session into an orchestrated, multi-agent software engineering process (specification → planning → implementation → testing → validation) in which **the programmer makes every consequential decision**.

It loads **only when you call it** (`/feature`). In every other session it costs, at most, a one-line description (~70 tokens). The workflow itself (~3.3k tokens for the entry point) loads only on invocation.

## What you get

- **Two workflows, chosen per feature by uncertainty, not size.**
  - **SDD Direct:** for well-understood features.
  - **Evolutionary Spec-Driven Development (ESDD):** for features with open requirements or technical unknowns.
  - **Hybrid:** ESDD only for the uncertain part.
- **Specialized subagents.** Repository Analyst, Planner, Implementer, Tester and Independent Reviewer, each driven by its own role file.
- **Per-task model selection.** Every role has a standard model, and the orchestrator picks the cheapest sufficient model for *each* delegation. That can be higher or lower than the standard, with floors so architecture and review are never downgraded. Every non-standard choice is announced, and every delegation is logged.
- **Neutral decision gates.** Options are never recommended or ranked: they are sorted alphabetically, given symmetric pros and cons, described with verifiable facts instead of adjectives, and excluded options are listed with the constraint they violate. The agent gives an opinion only if you explicitly insist on one.
- **Several features in parallel.** One orchestrator acts as the single intermediary between you and the agents of every feature. Each feature has its own workflow, gates, artifacts and agents. A gate in one feature does not block the others. Overlaps between features are reported, and the isolation strategy (git worktree per feature, serialized implementation, or shared tree) is your decision.
- **Artifacts as source of truth.** Specification, plan, testing plan, decision records, reports and a handoff file per feature. Any feature can be resumed in a new session.
- **Testing discipline.** Boundary value analysis, fuzz/property-based, symbolic/concolic, decision tables and state machines, each reported as *Applied*, *Not applicable* (with a reason) or *Blocked* (with an explanation). Mutation testing is mandatory for features you mark as critical.

## Install

**Option A: plugin** (inside Claude Code)

```
/plugin marketplace add mariopedemonte12/claude-feature-workflow
/plugin install feature-workflow@feature-workflow
```

When installed as a plugin, the command is namespaced: `/feature-workflow:feature`.

**Option B: script** (standalone skill, invoked as `/feature`)

```bash
git clone https://github.com/mariopedemonte12/claude-feature-workflow.git
cd claude-feature-workflow
./install.sh              # all your projects   -> ~/.claude/skills/feature
./install.sh --project    # current project only -> ./.claude/skills/feature
```

**Option C: manual.** Copy `skills/feature/` to `~/.claude/skills/feature/` (or to `<project>/.claude/skills/feature/`).

Then start a new Claude Code session.

## Usage

```
/feature add CSV export to the reports page       # new feature; you choose the workflow after an uncertainty assessment
/feature migrate auth to OAuth --esdd             # choose the workflow up front (--sdd | --esdd)
/feature status                                   # board of every feature in progress
/feature resume csv-export                        # continue a feature (or several) from its handoff
```

A typical SDD Direct run:

1. **Workflow selection.** The orchestrator assesses uncertainty per dimension, with evidence, and you choose the workflow.
2. **Specification.** Intent, requirements, constraints, invariants and acceptance criteria. You approve it and set the criticality.
3. **Planning.** The Planner subagent maps the viable approaches, which are presented neutrally. You choose, and you decide verification depth (mutation testing, independent review).
4. **Implementation.** The Implementer follows the approved plan. Any deviation comes back to you as a decision.
5. **Testing and review.** The Tester and Reviewer run in parallel. Defects come back to you as decisions.
6. **Final report.** Built only from evidence. You decide acceptance.

ESDD adds exploration, disposable prototypes, increments, discovery classification (Confirmed / Hypothesis / Under exploration / Rejected) and a traceable spec change log.

## How it stays out of your context

- `disable-model-invocation: true` in the skill frontmatter: Claude never loads the skill on its own; only you can, by typing the command. Per Claude Code's documentation, such a skill's description is not offered to the model. `claude plugin details` estimates ~70 always-on tokens as an upper bound; its estimate is the same with or without the flag.
- **Progressive disclosure.** On invocation, only `SKILL.md` (the orchestrator) loads. Workflows, protocols, guides and templates are read when a phase needs them.
- **Roles are files, not global agents.** Agents defined in `~/.claude/agents/` have their descriptions injected into every session. Here, the orchestrator spawns Claude Code's built-in subagents (`Explore`, `Plan`, `general-purpose`) with a model override and points each one at its role file.

## Repository layout

```
.claude-plugin/          plugin + marketplace manifests
install.sh               standalone installer
skills/feature/
├── SKILL.md             orchestrator: principles, startup, roles & model selection, gates
├── workflows/           sdd-direct.md · esdd.md (incl. hybrid)
├── protocols/           neutral-decisions.md · context-handoff.md · multi-feature.md
├── roles/               repository-analyst · planner · implementer · tester · reviewer
├── knowledge/           specification-guide.md · testing-techniques.md
└── templates/           specification · implementation-plan · testing-plan · decision-record · handoff · final-report
```

Artifacts created per feature in your project (default `docs/features/<slug>/`, or your project's own convention):

```
specification.md  implementation-plan.md  testing-plan.md
decisions/D-NNN-*.md  reports/*.md  delegations.md  handoff.md
```

## Customizing

| What | Where |
| --- | --- |
| Standard model per role, deviations and floors | `skills/feature/SKILL.md` §4 |
| Default feature folder | `SKILL.md` §2.3 |
| Neutrality rules, e.g. never giving an opinion even when asked | `protocols/neutral-decisions.md` rule 12 |
| Add engineering knowledge (security review, refactoring…) | new `knowledge/<topic>.md`, plus a row in `SKILL.md` §3 or a reference in the role that uses it |
| Rename the command | rename the `skills/feature` folder and the `name:` field |

## Design background

The workflow was derived from a longer design document, included as [`docs/master-prompt.md`](docs/master-prompt.md). Its header lists where the skill deliberately departs from it: neutrality instead of recommendations, per-delegation model selection, multi-feature orchestration and a consolidated skills library.

## Requirements and status

- Claude Code with skills and subagents. Built against Claude Code 2.1.319; `claude plugin validate` passes.
- Uses the built-in subagent types `Explore`, `Plan` and `general-purpose`, and the model aliases `haiku`, `sonnet` and `opus`.
- Early version: the structure is validated, but the workflow has not yet been exercised across many real projects. Issues and pull requests are welcome.

## License

[MIT](LICENSE)
