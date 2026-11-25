# Feature Workflow for Claude Code

Claude Code skills for building features with the programmer in control of every consequential decision. Two entry points, both **manual-only**: each loads only when you type its command.

| Command | What it is |
| --- | --- |
| **`/feature`** | You describe what you want built. The session recommends a **workflow** (DIRECT, SDD or EVO) with its evidence, asks whether it should be the **orchestrator** or the **executor**, and runs it. |
| `/feature-kit` | No pipeline: the workflow's skills (planning, quality, testing, review…) and your own, loaded on demand while you work by hand. |

In every other session each skill costs, at most, a one-line description (~70 tokens).

## Two axes per feature

**Workflow: how the work is done.**

| Workflow | What it does | Gates (profile `full`) | Use it when |
| --- | --- | --- | --- |
| **DIRECT** | One pass with the edge-case checklist: reach of every broad statement, the nearest existing analog, cases per input, tests for each, a self-review. Blocking questions only | Integration only | The request is clear and its risk and reach are small; the cheapest run |
| **SDD** | Specification of your intent, a plan you approve, test cases designed from the spec without seeing the plan, then build, test and review | Spec · plan · defects · acceptance | Clear intent, with enough risk or reach to want everything settled before code |
| **EVO** | No specification: your intent record, your decisions and the cases carry what the feature must do, delivered in one increment or several, as you choose | Intent and approach · one per increment · acceptance | Open requirements, technical unknowns, expected discoveries |

Hybrid is SDD with an EVO loop for one uncertain area. Which gates stop depends on the feature's gate profile (*Gate profiles*, below).

**Role of the session: who does the work.**
- **Orchestrator:** delegates every role (analyst, spec writer, planner, test designer, implementer, tester, critic) to subagents, and can run several features at once, each in its own git worktree, each with its own workflow.
- **Executor:** does one feature's work itself. The clean critic (with its verifier at R2) and specialist audits are still separate subagents. In SDD, the Test Designer must not see the plan, so it runs in a session you open with `/feature role test-designer <slug>`; the executor writes its brief and tells you when.

**Grouping is yours too:** several features under one orchestrator, independent sessions (each orchestrating or executing), or a hierarchy of orchestrators under a hub.

Every decision is yours. The agent shows the viable options with their facts, what it left out, and its labeled recommendation with what would change it.

## Skills, classified by where they apply

Every piece of knowledge the workflow uses is a **skill** with a classification in its frontmatter: its kind (`guide`, read by whoever does the phase, or `specialist`, which runs as its own agent), the phases it is used in (`intent`, `spec`, `plan`, `test-design`, `implement`, `test`, `review`, `audit`, or `general`), the workflows it applies to, and the signals that make it relevant.

| Location | Scope |
| --- | --- |
| `skills/feature/knowledge/`, `skills/feature/specialists/` | The library: code quality (with root causes and design principles), testing techniques, E2E, design patterns, specification guide, edge-case checklist, measurement, writing (messages, docs, PRs and commits); security, UI/UX, database, network, performance and observability specialists |
| `~/.claude/feature-skills/` | Yours, for every project |
| `<git-common-dir>/feature-skills/` | The repository's, local to your clone and never committed |
| `<repo>/.claude/feature-skills/` | The repository's, versioned with it |
| `<module>/.claude/feature-skills/` | One module's: active only when the feature touches files under that module |

Two commands generate repository skills from the code itself: `/feature verify-skill app` writes `verify-<app>`, a scripted way to launch, drive and capture evidence from the real app; `/feature verify-skill formal` writes `formal-<area>`, a formal check (TLA+ or a verifier) of one property, with a statechart when the model is a state machine. `/feature correct` sweeps the repository for mistakes agents repeat and enforces each at the strongest level you choose: architecture, types, a check, a test, or review.

A more specific skill replaces a more general one with the same name. Only the frontmatter is indexed until a phase needs a skill, and each agent is briefed with the paths of the skills for its phase. In DIRECT, skills load on demand; `--no-skills` turns them all off except the edge-case checklist. Full format: [`skills/feature/protocols/skills.md`](skills/feature/protocols/skills.md).

## Evidence so far

Measured before this version, under the earlier names: `/feature-lean` is today's EVO as executor, `/feature` High was SDD as orchestrator, and the checklist prompt is close to DIRECT.

| | Plain session | `/feature-lean` | `/feature` High |
| --- | --- | --- | --- |
| Hidden tests (Django, 3 large features) | 41/43 | 42/43 | 42/43 |
| Cost | USD 1.1 | USD 5.6 | USD 15.2 |
| Input-equivalent tokens | 0.6M | 2.7M | 8.2M |

- **Real feature, maintainers' tests** (Django HTTP QUERY, #37232): plain 47/48 for USD 0.52, a checklist prompt 48/48 for USD 1.06, `/feature-lean` 47/48 for USD 2.61, `/feature` High 47/48 for USD 8.28; no regressions in any arm. The miss was the same everywhere (`RedirectView`). `/feature`'s critic found it, but the gate framed the fix as beyond the spec and the simulated programmer declined it. That led to treating the spec as the current reading of the intent (below).
- **Smaller cases:** across four experiments (a toy project, Python-Markdown, two Django runs), the full workflow passed 120/121 hidden tests against the plain session's 114/121, at about 12× the cost.
- **What helped quality was cheap:** enumerating edge cases before coding, one clean critic, and comparing with the nearest analog. DIRECT keeps the first and the third; EVO as executor keeps all three.
- **Limits of this evidence.** Each configuration ran once (n=1). The hidden tests were written by the same people who designed the workflow, the programmer was simulated, and none of this is real day-to-day use. Treat it as a direction, not a result. Details: [`docs/cost-estimates.md`](docs/cost-estimates.md).
- **Usage budgets.** An orchestrated SDD run spends millions of tokens per feature group. On plans with a usage limit, such as Pro, it can exhaust the limit within one run; DIRECT and executor sessions fit far better.

## What every workflow shares

- **The spec is a reading of your intent, not a closed contract.** Your request evolves as you talk: every statement of yours that changes the intent goes, verbatim, to an intent record that is consolidated with your confirmation at each gate. The spec (SDD) or the cases (EVO) cite it as their source and map where the broad statements in your words reach. Anything a later step finds that it did not foresee comes back to you as a discovery, framed against your own words, never dismissed as "not in the spec".
- **Decision gates with an open recommendation.** No presentation of options is neutral, since the agent picks the options and the words. So each decision shows every viable option with verifiable facts instead of adjectives, the options it left out and those excluded by a constraint, and a labeled recommendation with its reasons and the fact that would change it. You decide; nothing proceeds by silence.
- **Refinement before the workflow.** When your request names a solution without the problem, has no observable outcome, admits several readings or needs context only you hold, the agent first works out with you what you need: the problem, the context it lacks (looking up what the repository answers, asking only the rest), and two or three readings plus the smallest version that would already solve it. The workflow is recommended from that, not from the first wording. `/feature refine` does it without starting anything.
- **Gate profiles.** How often the workflow stops for you is chosen per feature: `full` stops at every gate, `key` (the default) only at the intent, the registry bootstrap, approaches that differ in what they change, discoveries outside your words and acceptance, and `auto` only at acceptance, at what is hard to undo and at a choice between two rules you wrote (§When a gate is off in [`protocols/gates.md`](skills/feature/protocols/gates.md)), which it never settles itself; in `auto` you still get a catch-up at each phase or increment ([`SKILL.md`](skills/feature/SKILL.md) §5). A gate that is off is decided by the agent with its recommendation, recorded, and listed in the final report: with `defects` off, the critic's and the Tester's Blocker and Major findings your words cover are fixed (test first when the fix changes behavior), and audit findings (except a security Blocker, which always stops) and the rest wait for acceptance; with `discoveries` off in `auto`, what lies outside your words is only recorded; with `depth` off, a higher review level by size and risk applies and is reported, a lower one is asked. Integration, cleanup, new dependencies, data migrations, breaking public interfaces, a discovery that contradicts your words, a Blocker from a security audit, a review whose rounds run out with a Blocker or Major still open ([`protocols/review-cycle.md`](skills/feature/protocols/review-cycle.md)) and a feature that turns out Critical always stop. Set it with `--gates full|key|auto`, plus `+gate` or `-gate` for single gates.
- **A clean critic.** Review is done by a new agent that never saw the code being written, with your own words as its only statement of intent. Its findings come to you; nothing is fixed silently. Review levels: R0 gate only · R1 one critic · R2 critic, verifier and fix cycle (at most 3 rounds). Commits made after the last round reach you marked as unreviewed ([`protocols/review-cycle.md`](skills/feature/protocols/review-cycle.md) §R2 · The cycle).
- **Code quality standard.** The smallest complete change, no comments except `shortcut:` markers, short functions and files as signals of mixed responsibilities, design patterns only for problems present now. A dependency-free quality gate (`scripts/quality_gate.py`) checks the change.
- **A per-project anti-pattern registry that learns.** Seeded from catalogs matching the project's architecture; agents record new anti-patterns as candidates; you approve what enters it, and what can be detected mechanically becomes a lint rule.
- **Testing discipline.** Boundary values, fuzz/property-based, symbolic/concolic, decision tables and state machines, each reported as *Applied*, *Not applicable* or *Blocked*; end-to-end tests through the real entry point; mutation testing mandatory for Critical features.

## Orchestrator mode

- **Specialized subagents,** each driven by its own role file, with a standard model per role and a per-delegation choice of the cheapest sufficient model, with floors so architecture and review are never downgraded. Every delegation is logged.
- **Agents ask you, through the orchestrator.** An agent that needs an answer only you can give stops instead of guessing; the orchestrator puts the question to you and resumes the same agent with your answer.
- **Cost limits.** An agent is resumed for short follow-ups while its context stays small; otherwise a new agent of the same role takes over through a relay, starting from notes its predecessor wrote and the work on the branch. The thresholds and the relay are in [`SKILL.md`](skills/feature/SKILL.md) §4 *Reusing agents* and [`protocols/context-handoff.md`](skills/feature/protocols/context-handoff.md) §Relay. The orchestrator session compacts at a threshold you set and is best run on sonnet (see Cost settings).
- **One git worktree per feature,** created with Claude Code's built-in worktree support. How it is integrated and whether the worktree is removed are your decisions.
- **Several features in parallel,** each with its own workflow, gates, artifacts and agents. A gate in one feature does not block the others. Overlaps between features are reported early, including those with features other sessions execute.
- **Several orchestrators, if you want them:** independent sessions that see each other's features through shared claims, or a hierarchy (`/feature hub`) whose principal is your only channel and queues every decision request by how much work it blocks.
- **Optional phased mode (experimental, never run):** with `--phased`, the orchestrator hands each phase to a short-lived runner and keeps only what needs you.
- **Pause or stop.** You can pause a feature or stop all its work at once ([`SKILL.md`](skills/feature/SKILL.md) §7); the resume state then says what must be relaunched.
- **Artifacts as source of truth:** intent record, specification, plan, testing plan, decision records, reports and a `state.md` per feature, from which any feature can be resumed in a new session (DIRECT only with a card). A handoff is written only when a new agent takes over a phase; a new agent of a role that already ran gets relay notes instead ([`protocols/context-handoff.md`](skills/feature/protocols/context-handoff.md) §Relay).

## Executor mode

One feature per session, in its own worktree (DIRECT works in the current checkout unless you ask for one). EVO as executor keeps everything in one card (target 500 lines; overflow goes to linked files, never cut): your intent, the reach of your words, the nearest analog, the cases of every main flow, the increments and the result. Its first gate settles your intent, the approach, the cases and how many increments; each increment then has one gate with its results, the findings of the review at the level you validated, and the next increment. How it works, step by step: [`docs/executor.md`](docs/executor.md).

## `/feature-kit`

When you work by hand, `/feature-kit` makes the skills available as a catalog of modules (edge-cases, explore, refine, spec, plan, decide, quality/ponytail, patterns, anti-patterns, test, e2e, gate, review, writing, measure, correct, verify-skill, formal-skill, card, specialists) plus your own skills from the same folders, loaded only when the task needs one or you name it. No phases, gates, artifacts, worktrees or subagents, except a clean critic when you ask for a review.

## Install

**Option A: plugin** (inside Claude Code)

```
/plugin marketplace add mariopedemonte12/claude-feature-workflow
/plugin install feature-workflow@feature-workflow
```

When installed as a plugin, the commands are namespaced: `/feature-workflow:feature` and `/feature-workflow:feature-kit`.

**Option B: script** (standalone skill, invoked as `/feature`)

```bash
git clone https://github.com/mariopedemonte12/claude-feature-workflow.git
cd claude-feature-workflow
./install.sh              # all your projects   -> ~/.claude/skills/{feature,feature-kit}
./install.sh --project    # current project only -> ./.claude/skills/{feature,feature-kit}
```

**Option C: manual.** Copy `skills/feature/` and `skills/feature-kit/` side by side into `~/.claude/skills/` (or `<project>/.claude/skills/`). The kit reads from `../feature`.

Then start a new Claude Code session.

### Cost settings

These are your settings; the workflow never edits them.

- **Orchestrator compaction.** In `settings.json`:

  ```json
  { "autoCompactWindow": 150000 }
  ```

  or `CLAUDE_CODE_AUTO_COMPACT_WINDOW=150000` in the environment. It applies to the whole session. 150k is recommended and 100k is possible at a risk; the reasons are in `skills/feature/SKILL.md` §3, which is their one source. Compacting is safe because each feature's `state.md` holds what is needed to resume.
- **Compact Instructions.** Paste the block of `skills/feature/protocols/compaction.md` §Compact Instructions into your `CLAUDE.md`. Claude Code gives it to the summary, so a compaction keeps each feature's state, decisions, agent IDs and pending stops, and drops tool outputs and reports already saved. The skill cannot edit your `CLAUDE.md`.
- **State after a compaction.** A hook re-reads the project memory's portfolio and the `state.md` of each active feature right after a compaction (`skills/feature/protocols/compaction.md` §State after a compaction). With the plugin it is already on (`hooks/hooks.json`). With `install.sh` or a manual copy, add this to `settings.json` (use the path of your install, here the user-level one):

  ```json
  {
    "hooks": {
      "SessionStart": [
        { "matcher": "compact",
          "hooks": [{ "type": "command",
                      "command": "python3 \"$HOME/.claude/skills/feature/scripts/post_compact_state.py\"" }] }
      ]
    }
  }
  ```
- **Orchestrator model.** Run the orchestrator session on sonnet: `/model sonnet`, or `--model sonnet` at launch. The skill says so at startup if it is not, and cannot switch it. Roles that need opus keep it (`skills/feature/SKILL.md` §4).
- **Subagent caps.** The setting above is per session, not per model, so the workflow enforces the caps itself: `SKILL.md` §4, *Reusing agents*.

## Usage

```
/feature add CSV export to the reports page       # recommends a workflow, asks orchestrator or executor
/feature refine we need reports to be faster      # work out what is needed first; starts nothing
/feature refined faster-reports --evo             # start the feature from that refined request
/feature fix the date parser for ISO weeks --direct --execute    # both chosen up front
/feature migrate auth to OAuth --evo --execute    # EVO in this session, one card
/feature add audit log --sdd --orchestrate --with security,database
/feature add bulk import --direct --no-skills     # the bare baseline: checklist only
/feature role test-designer audit-log             # in a new session: the Test Designer of an SDD executor
/feature status                                   # every feature in progress, including other sessions'
/feature resume csv-export                        # continue a feature from its state.md or card
/feature hub                                      # principal orchestrator of several groups
/feature join main-hub billing                    # in another session: run the "billing" group
/feature-kit                                      # work by hand; skills load on demand
/feature-kit plan quality                         # same, loading the plan and quality modules now
```

A typical SDD run as orchestrator:

1. **Refinement, when the request is not ready.** If it names a solution without its problem, has no observable outcome, admits several readings or needs context only you have, the session restates it as a problem, looks up what the repository answers, asks you the rest, and offers two or three readings plus the smallest version. You confirm what you need.
2. **Recommendation.** The session assesses clarity, uncertainty, risk and reach with evidence, recommends a workflow, and asks the role. You validate.
3. **Specification.** The Specification Writer turns your request (kept in `intent.md`: your original request, a consolidated intent you confirm at each gate, and your statements since) into requirements, constraints, invariants and acceptance criteria, each traced to its source. You approve it and set the criticality.
4. **Planning and test design.** In parallel, the Planner maps the viable approaches and the Test Designer derives the cases from the spec. You choose an approach, approve the testing plan, decide mutation testing, and validate the recommended review level.
5. **Implementation.** The Implementer writes production code for the approved plan, without tests (except the fixtures, helpers and anti-pattern checks of `SKILL.md` §4). Any deviation comes back to you.
6. **Testing and review.** The Tester implements and runs the designed cases while a clean critic reviews. Defects come back to you as decisions.
7. **Final report, acceptance, integration and cleanup,** each decided by you.

## How it stays out of your context

- `disable-model-invocation: true` in the `feature-kit` frontmatter: Claude never loads that skill on its own; only you can, by typing the command. The `feature` skill does not have it: Claude can launch it when you explicitly ask for a feature (its description says never on its own initiative), at the cost of its description being always in context (~70 tokens as an upper bound per `claude plugin details`).
- **Progressive disclosure.** On invocation, only `SKILL.md` loads. Workflows, protocols, skills and templates are read when a phase needs them; skills are indexed by their frontmatter alone.
- **Roles are files, not global agents.** Agents defined in `~/.claude/agents/` have their descriptions injected into every session. Here, the orchestrator spawns Claude Code's built-in subagents (`Explore`, `Plan`, `general-purpose`) with a model override and points each one at its role file.

## Repository layout

```
.claude-plugin/          plugin + marketplace manifests
install.sh               standalone installer
skills/feature-kit/
└── SKILL.md             module catalog for hand-driven work (reads from skills/feature)
skills/feature/
├── SKILL.md             principles, startup (recommendation, role), roles & model selection, gates
├── workflows/           direct.md · sdd.md · evo.md (incl. hybrid)
├── protocols/           executor.md · skills.md · decisions.md · agent-questions.md · multi-feature.md · …
├── roles/               repository-analyst · spec-writer · planner · test-designer · implementer · tester · reviewer (critic) · verifier
├── specialists/         security · ux-ui · database · network · performance · observability (extensible)
├── knowledge/           edge-cases · specification-guide · testing-techniques · code-quality · design-patterns · e2e-testing · anti-patterns/
├── scripts/             quality_gate.py
└── templates/           specification · implementation-plan · testing-plan · decision-record · handoff · state · final-report · feature-card
```

Artifacts created per feature in your project (default `docs/features/<slug>/`, or your project's own convention):

```
intent.md  specification.md  implementation-plan.md  testing-plan.md     (SDD)
feature.md (the card)  decisions/  review/                               (EVO as executor)
decisions/D-NNN-*.md  reports/*.md  delegations.md  handoff.md     (orchestrator)
state.md                                                          (orchestrator, SDD as executor; not DIRECT)
```

And once per project, after your approval: the anti-pattern registry (`config.json` with limits and checks, `anti-patterns.md`, `rules/`), either versioned at `<repo>/.quality/` or local to your clone at `<git-common-dir>/quality/`, as you choose.

## Customizing

| What | Where |
| --- | --- |
| Standard model per role, deviations and floors | `skills/feature/SKILL.md` §4 |
| Default feature folder | `SKILL.md` §2.3 |
| How decisions and recommendations are presented | `protocols/decisions.md` |
| Add engineering knowledge or a specialist | a skill file in `~/.claude/feature-skills/`, `<repo>/.claude/feature-skills/` or `<module>/.claude/feature-skills/`, with its classification (`protocols/skills.md`) |
| Workflow recommendation criteria | `SKILL.md` §2.5 |
| Code quality rules and default limits | `knowledge/code-quality.md`; per project in `.quality/config.json` |
| Anti-pattern seed catalogs | `knowledge/anti-patterns/*.md` |
| Rename the command | rename the `skills/feature` folder and the `name:` field |

## Design background

A detailed description of the current architecture, with diagrams of every flow and the responsibilities of each agent, is in [`docs/architecture.md`](docs/architecture.md).

The workflow was derived from a longer design document, included as [`docs/master-prompt.md`](docs/master-prompt.md). Its header lists where the skill deliberately departs from it: recommendations that must show what they left out, per-delegation model selection, multi-feature orchestration and a consolidated skills library.

Part of the code quality standard and of the review checklist adapts [Ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert (MIT): the smallest-complete-change ladder, `shortcut:` markers, splitting by responsibility rather than line count, and findings that require a concrete case. This workflow is stricter on comments and does not install Ponytail's hooks. The surgical-change rules (every changed line traces to the request, match the existing style, mention pre-existing dead code instead of deleting it) and test-first defect fixes adapt the [Karpathy-inspired guidelines](https://github.com/forrestchang/andrej-karpathy-skills) by Forrest Chang (MIT). Several pieces adapt skills of [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT): root causes and attacking the premise, the design principles (model the domain, data shape first, boundary discipline, subtract before you add), the measurement checklist, deepening the request, enforcement levels and the correction sweep, the app and formal verification generators, and the statechart rules. They are rewritten to fit this workflow's decisions and gates; none of pstack's scripts are included.

The review cycle (clean critics, a refuting verifier, a limit of three rounds) draws on research on self-attribution and self-preference bias in LLM evaluators, adversarial multi-agent review and iterative repair loops. The papers, and which piece each one justifies, are in [`docs/references.md`](docs/references.md), outside the skills, so no citation is loaded into an agent's context. Most are recent arXiv preprints.

## Requirements and status

- Claude Code with skills and subagents. Built against Claude Code 2.1.319; `claude plugin validate` passes.
- A git repository (or `WorktreeCreate`/`WorktreeRemove` hooks), because every orchestrated or SDD/EVO feature runs in its own worktree.
  - The orchestrator creates each worktree with `EnterWorktree` and leaves it immediately with `ExitWorktree` (keep).
  - Subagents run without isolation and work through absolute paths into their feature's worktree.
  - New worktrees branch from `origin/<default-branch>` by default. To branch from your local HEAD instead, set `"worktree": { "baseRef": "head" }` in your Claude Code settings.
- Uses the built-in subagent types `Explore`, `Plan` and `general-purpose`, and the model aliases `haiku`, `sonnet` and `opus`.
- Early version. Measured only in controlled experiments with a simulated programmer (see *Evidence so far*), not in real day-to-day use. Phased mode, the orchestrator hierarchy, DIRECT as a named workflow, SDD as executor and module skills have never been run. Issues and pull requests are welcome.

## License

[MIT](LICENSE)
