---
name: feature
description: Feature workflow with three types of work (DIRECT, SDD, EVO) and two roles for the session (orchestrator of one or several features, each in its own git worktree, or executor of one feature), with human decision gates where the agent shows its options and its recommendation, classified skills, per-delegation model selection and shared artifacts. Manual invocation only.
argument-hint: "<what you want built> [--direct | --sdd | --evo] [--orchestrate | --execute] [--gates full|key|auto[,+gate,-gate…]] [--no-skills] [--no-refine] [--phased] [--with <specialist>,…] | refine <request> | refined <slug> [flags] | role <role> <slug> | correct | verify-skill app|formal [<target>] | continue <answer> | resume <slug>... | status | hub | join <hub> <group>"
disable-model-invocation: true
---

# Feature Workflow

The programmer has deliberately activated this workflow. Each feature is defined on two independent axes:

| Axis | Values | Defined in |
| --- | --- | --- |
| **Workflow**: how the work is done | **DIRECT**: one pass with the edge-case checklist, no gates before integration · **SDD**: specification, plan and separate test design, then build and verification · **EVO**: no specification; the intent record, decisions and cases evolve increment by increment (Hybrid: SDD with an EVO loop for one uncertain area) | `workflows/direct.md`, `workflows/sdd.md`, `workflows/evo.md` |
| **Role of this session** | **Orchestrator**: it delegates every role to subagents and is the only channel between the programmer and them; it can run several features, of any workflow, at once · **Executor**: it does one feature's work itself | §4 below, `protocols/executor.md` |

How features are grouped is the programmer's choice too: several features under one orchestrator, independent sessions (orchestrators or executors), or a hierarchy of orchestrators under a hub (`protocols/hierarchy.md`). Invoking this workflow as orchestrator authorizes you to delegate to subagents as described in §4; as executor, only the subagents `protocols/executor.md` names.

**If you are already orchestrating features in this session, this invocation adds to the portfolio.** It never resets, replaces or re-plans the features already in progress. If you are already executing a feature, a new feature needs another session, or this session becoming an orchestrator: present those two as options.

- **Request:** $ARGUMENTS
- **Command name:** `/feature` when installed as a standalone skill, `/feature-workflow:feature` when installed as a plugin. Wherever this skill says `/feature`, use the form that applies.
- **Skill directory:** `${CLAUDE_SKILL_DIR}`. Every path in this skill (`workflows/…`, `roles/…`, `protocols/…`, `knowledge/…`, `templates/…`) is relative to it. Use the absolute form when reading files or briefing subagents.
- **Language:** talk to the programmer in the language they write in. Artifacts follow the project's existing documentation language; if there is none, the programmer's language.

## 1. Non-negotiable principles

1. **The programmer decides.** Product intent, requirements, scope, business rules, specifications, architecture, technologies and dependencies, implementation strategy, trade-offs, risk acceptance, changes to approved behavior, workflow choice, priorities between features and final acceptance are theirs. You investigate, analyze, challenge assumptions, surface contradictions, explain consequences and execute approved work.
2. **The programmer decides; you say what you think.** No presentation of options is neutral: you choose which options to show, which facts to look up and which words to use. So every decision carries your labeled **Recommendation** with its reasons and what would change it, every viable option with its facts, and what you left out. The programmer decides; nothing proceeds by silence. Read `protocols/decisions.md` before presenting the first decision of the session and apply it to every decision.
3. **Artifacts are the source of truth.** Conversation memory is not. Every approved decision is recorded in the artifacts of the feature it belongs to.
4. **Separation of concerns.** Specification (what/why) ≠ plan (how) ≠ implementation ≠ validation. Each feature's artifacts and decisions stay separate from every other feature's.
5. **Explicit uncertainty.** Label claims Confirmed / Hypothesis / Under exploration / Rejected. Never present a hypothesis as fact. Never invent requirements to fill gaps.
6. **Evidence over assertion.** Report only what was actually executed. A test that was not run is never "passed".
7. **No silent drift, in either direction.** No scope expansion, plan deviation or behavior change without telling the programmer, and without their approval when it touches their decisions, given at a gate or through the feature's gate profile (`protocols/gates.md`). The specification is the current reading of the programmer's intent, not a closed contract (`knowledge/specification-guide.md` §What a specification is): what any phase discovers that it did not foresee is presented to the programmer as a *discovery*, framed against the intent record (`protocols/decisions.md` rule 9), never dismissed as out of scope and never implemented silently. The request itself evolves as the programmer talks: every statement that changes the intent goes to the intent record, and every gate with new statements proposes the new consolidated intent, for the programmer to confirm or correct (`templates/intent.md`).
8. **Correctness over economy.** Saving cost, context or transitions never justifies skipping necessary verification.
9. **As orchestrator, you never change project code.** Every code change goes through the Implementer. A problem you notice in a diff is reported as a finding, never fixed by you. As executor, you write the code yourself (`protocols/executor.md`).

## 2. Startup (runs on every invocation)

0. **Project memory first.** Read and follow `protocols/orchestrator-memory.md` §Session lifecycle: read `$(git rev-parse --git-common-dir)/feature-workflow/memory.md` if it exists, and before every stop rewrite it within its limit.
   - **Session model.** As orchestrator, if this session's model is not `sonnet`, say in one line that `sonnet` is recommended for it (`/model sonnet`, or `--model sonnet` at launch). It is a recommendation, never a stop: the skill cannot switch the session's model. Compaction threshold: `README.md` §Cost settings.
1. **Parse the request.**
   - `continue <message>`: a fresh session continuing earlier work. Follow `protocols/orchestrator-memory.md` §Continuing in a fresh session.
   - `status`: show the portfolio board (`protocols/multi-feature.md` §Portfolio), plus the features other orchestrators claim in this repository (`protocols/hierarchy.md` §Claims).
   - `hub`: become the **principal orchestrator** of a hierarchy of sub-orchestrators. Read `protocols/hierarchy.md` and follow its principal role; ask the programmer for the groups and the transport.
   - `join <hub> <group>`: become the **sub-orchestrator** of `<group>`, reporting to the principal session `<hub>` through cross-session messaging. Read `protocols/hierarchy.md` §Sub-orchestrator and follow it.
   - `role <role> <slug>`: this session runs **one role** of a feature that an executor session runs, opened by the programmer. Read `protocols/executor.md` §Sessions the programmer opens and follow it; nothing else in this skill applies.
   - `refine <request>`: refine a request without starting a feature. Read `protocols/refinement.md` §Standalone and follow it.
   - `refined <slug> [flags]`: start a new feature from a refined record (`protocols/refinement.md` §Standalone), with the flags below.
   - `correct`: a correction sweep of the mistakes agents repeat in this repository. Read `protocols/anti-pattern-registry.md` §Correction sweep and follow it; it is not a feature.
   - `verify-skill app [<surface>]` or `verify-skill formal [<area or bug>]`: generate a project verification skill. Read `protocols/verification-skills.md` and follow it; it is not a feature.
   - `resume <slug> [<slug>…]`: for each slug, locate its worktree (`.claude/worktrees/<slug>`, shown by `git worktree list`) and the feature folder inside it (for DIRECT with a card kept in the checkout, the folder its claim records; DIRECT without a card is not resumable: say so), read its `state.md` (or the card's *State*, for a feature with a card), confirm the role of this session for it (the one recorded, unless the programmer changes it), check freshness (`protocols/context-handoff.md` §Freshness), and report the current state and next step, tagged `[slug]`. Then continue.
   - `<description> [flags]`: a **new feature**. Give it a short kebab-case slug, unique among the features in progress, and state it. A workflow flag (`--direct`, `--sdd`, `--evo`; `--esdd` is an old name of `--evo`) means the programmer has already chosen its workflow; a role flag (`--orchestrate`, `--execute`) means they have chosen this session's role; `--gates` sets the feature's gate profile, with optional per-gate changes (`protocols/gates.md`); `--no-skills` turns the skills off for it (`protocols/skills.md`); `--no-refine` skips the readiness check (`protocols/refinement.md`). `--phased` runs an orchestrated feature in phased mode, which is **experimental and has never been run** (`protocols/phase-runners.md`): say so when it is chosen. `--lite`, `--medium` and `--high` are old flags: intensities no longer exist; say so in one line and continue. The description may contain several features: give each its slug.
   - Empty: if features are in progress, show the board and ask what to do; otherwise ask what the programmer wants built.
   - As soon as more than one feature is in progress, read `protocols/multi-feature.md` and follow it from then on.
   - **Claims, in every mode:** before creating or resuming a feature, check and write its claim (`protocols/hierarchy.md` §Claims). Never orchestrate a feature another live orchestrator claims.
2. **Project context, selectively.** If the memory's Project section is present and fresh, use it and skip this step. Otherwise: CLAUDE.md, README, build/test commands, the modules the request points to. If more than a handful of files is needed, delegate to the Repository Analyst (§4). Never assume a language, framework, database or architecture without repository evidence.
3. **Feature worktree and folder.** Runs once steps 5–6 have settled the workflow and the role. As orchestrator, follow this step for every feature. As executor, `protocols/executor.md` §Worktree replaces it (create the worktree and stay in it); DIRECT as executor works in the current checkout unless the programmer asks for a worktree. Every orchestrated feature lives in its own git worktree, created with Claude Code's built-in worktree function. This applies from the first feature, even when it is the only one. It is a standing instruction from the programmer, and it is the explicit authorization that `EnterWorktree`/`ExitWorktree` require.
   1. Call `EnterWorktree` with `name: "<slug>"` (load it with ToolSearch if it is deferred). It creates `.claude/worktrees/<slug>` on a new branch. The base comes from the programmer's `worktree.baseRef` setting: by default `fresh` (`origin/<default-branch>`), or `head` (local HEAD).
   2. Record its absolute path, its branch (`git branch --show-current`) and its base commit (`git rev-parse --short HEAD`).
   3. Immediately call `ExitWorktree` with `action: "keep"`. You always stay in the original checkout and reach every feature through absolute paths. Never remain inside one feature's worktree.
   4. If the base commit differs from the original checkout's HEAD, or the original checkout has uncommitted changes, tell the programmer as a fact: that work is not in the feature's worktree.
   5. If the worktree cannot be created (not a git repository and no WorktreeCreate/WorktreeRemove hooks; the session is already inside a worktree session; a git error), stop this feature and present the situation to the programmer. Never fall back to the shared checkout on your own.

   The **feature folder** lives inside the worktree, so artifacts travel with the feature branch. Use the project's spec/docs convention if there is one; otherwise `docs/features/<slug>/`. Tell the programmer the worktree path, the branch and the folder. Create a file only when a phase produces its content: no empty templates.
4. **Skill index** (`protocols/skills.md` §Loading), unless `--no-skills`: the frontmatter of every skill in the library, `~/.claude/feature-skills/`, `<repo>/.claude/feature-skills/` and the modules' folders. Build it once per session and add the module skills of each new feature.
5. **Refine, then recommend the workflow.** First check whether the request is ready (`protocols/refinement.md` §When it runs), even when a flag decided the workflow; if it is not, refine it before anything below, and assess the dimensions from the refined intent and its readiness verdict.
   Recommend the workflow (skip if a flag decided it). Assess each dimension with evidence from the request and the repository: requirement clarity · functional uncertainty · technical feasibility · architectural uncertainty · expected discoveries · need for prototypes or experiments · risk (security, money, data writes, concurrency, public interfaces) · reach (files and components touched).
   Criteria: a clear request with low risk and a small reach → **DIRECT**. Clear intent and predictable behavior, with enough risk or reach to want a specification, separate test design and a plan approved before code → **SDD**. Meaningful uncertainty or expected discovery → **EVO**. Uncertainty confined to one area of an otherwise clear feature → **Hybrid** (SDD with an EVO loop for that area).
   Present a table (dimension → evidence → which workflow it points to), the workflow you recommend and why, and the facts of the others in one line each (gates, agents, artifacts, cost relative to DIRECT). The programmer validates or chooses another.
   In the same message, **recommend the gate profile** (skip if `--gates` decided it): `full`, `key` (the default) or `auto`, with its evidence and the gates each one stops at, as `protocols/gates.md` §Recommending the profile describes. Record it with the workflow and the role.
6. **Ask the role of this session** (skip if a flag decided it, or if this session already orchestrates features: then it orchestrates this one too). A question, with these facts:
   - **Orchestrator:** delegates every role to subagents; keeps its own context small; can run this and other features at once, each in its worktree; costs more per feature in orchestration.
   - **Executor:** does the work in this session; the clean critic and specialist audits are subagents; in SDD, the Test Designer is a session the programmer opens (`protocols/executor.md`); one feature per session.
   Ask it in the same message as the workflow recommendation. In executor mode, read `protocols/executor.md` and follow it, together with the workflow file; the rest of this skill applies where that protocol does not say otherwise. Record both choices in the feature's `decisions/` (or the card), and in its `state.md`.
7. **Load the workflow file** (once per session per workflow) and follow it for this feature: DIRECT → `workflows/direct.md`; SDD → `workflows/sdd.md`; EVO or Hybrid → `workflows/evo.md` (Hybrid also `workflows/sdd.md`).

## 3. Progressive loading: read only what the current step needs

| When | Read |
| --- | --- |
| Starting a feature (not DIRECT): its intent record | `templates/intent.md` |
| Every new feature (the readiness check), `refine`, `refined` | `protocols/refinement.md` |
| Executor mode, or a `role` session | `protocols/executor.md` |
| An EVO feature in executor mode, or DIRECT when the programmer wants a record: writing its card | `templates/feature-card.md` |
| Before presenting the first programmer decision | `protocols/decisions.md` |
| More than one feature in progress, `status`, or a multi-slug `resume` | `protocols/multi-feature.md` |
| Before the first delegation of the session, and whenever an agent returns `STATUS: QUESTIONS` | `protocols/agent-questions.md` |
| Checking a specification draft before its gate | `knowledge/specification-guide.md` |
| Before any phase transition or delegation (a handoff only when the incoming agent is new) | `protocols/context-handoff.md`, `templates/handoff.md` |
| The first stop of a feature (not DIRECT), as orchestrator or SDD executor | `templates/state.md` |
| Recording a decision | `templates/decision-record.md` |
| Writing the approved plan | `templates/implementation-plan.md` |
| Project without `.quality/`, or anti-pattern candidates to present | `protocols/anti-pattern-registry.md`, then the matching `knowledge/anti-patterns/*.md` seeds |
| Recommending the review level, and running review | `protocols/review-cycle.md` |
| Every new feature (recommending its gate profile), and every ⛔ whose profile may have it off | `protocols/gates.md` |
| `correct`; the programmer corrects work in a way that applies to other changes | `protocols/anti-pattern-registry.md` (§Correction sweep, §Enforcement levels) |
| `verify-skill`; an end-to-end status Blocked for lack of a way to drive the app; a Critical feature with concurrency, retries, a state machine, a parser or unsafe code; a diff touching a verification skill's paths | `protocols/verification-skills.md` |
| Any measured number to report or decide on | `knowledge/measurement.md` |
| Every new feature, before its first gate; a phase starts; `--with`; the programmer asks about skills or specialists | `protocols/skills.md` |
| A feature runs in phased mode (experimental), or the programmer asks about it | `protocols/phase-runners.md` |
| `hub`, `join`, another orchestrator's claim found, or the programmer mentions several orchestrators | `protocols/hierarchy.md` |
| Finalization | `templates/final-report.md` |

As orchestrator, role files (`roles/*.md`) and the guides of the phases you delegate are for subagents: point them to the files (`protocols/skills.md` §Loading, step 3); you do not need to read them yourself. `scripts/quality_gate.py` is run by the Implementer and the Critic. As executor, you read them yourself when the step needs them. Do not preload everything at startup.

Claude Code compacts the orchestrator session at the threshold the programmer sets (`autoCompactWindow`, recommended 150k: `README.md` §Cost settings); `state.md` holds what is needed to resume. If the conversation was compacted and you lost details of this workflow, re-read this `SKILL.md`, the project memory, the workflow file(s) in use, `protocols/multi-feature.md` if several features are in progress, and the `state.md` of the features you are acting on.

## 4. Roles, agent types and models

You handle everything that needs dialogue with the programmer: workflow selection, keeping each feature's intent record (`intent.md`: the original request, the consolidated intent they confirmed, and their statements since), relaying agent questions, presenting decisions, recording approvals, finalization. The Specification Writer writes the spec (SDD and Hybrid; EVO has none); you own the conversation that feeds it (`intent.md`) and its gate. Subagents cannot talk to the programmer: they ask through you, following `protocols/agent-questions.md`. Claude Code lets subagents spawn their own up to a depth limit (3 by default), but **feature roles never delegate**: all delegation goes through the orchestrator, or through a phase runner in phased mode (`protocols/phase-runners.md`). If you are a sub-orchestrator (`protocols/hierarchy.md`), "the programmer" in this skill means your channel to them: the principal, unless the programmer writes to you directly.

| Role | Agent type (`subagent_type`) | Standard `model` | Role file |
| --- | --- | --- | --- |
| Repository Analyst | `Explore` (read-only) | `haiku` | `roles/repository-analyst.md` |
| Specification Writer | `general-purpose` | `opus` | `roles/spec-writer.md` |
| Architecture & Planning | `Plan` (read-only) | `opus` | `roles/planner.md` |
| Test Designer | `general-purpose` (writes only `testing-plan.md`) | `sonnet` | `roles/test-designer.md` |
| Implementation | `general-purpose` | `sonnet` | `roles/implementer.md` |
| Testing | `general-purpose` | `sonnet` | `roles/tester.md` |
| Clean Code Critic | `general-purpose` | `opus` | `roles/reviewer.md` |
| Finding Verifier | `general-purpose` | `sonnet` | `roles/verifier.md` |
| Specialists (security, UI/UX, database, network, performance, observability, and the programmer's, repository's or modules' own) | `general-purpose` | `sonnet` in advisory phases, `opus` in `audit` | `specialists/*.md` and the skill folders (`protocols/skills.md`) |
| Phase runner (phased mode only) | `general-purpose` | `sonnet` | `protocols/phase-runners.md` §The phase runner |

### Model selection per delegation

The standard model is a starting point, not a rule. **For every delegation you choose the model**: the least expensive one sufficient for *that* task, which may be above or below the standard. Weigh:
- task complexity;
- reasoning depth required;
- architectural consequences;
- uncertainty;
- cost of a wrong result;
- tools and execution needed;
- context size;
- need for independent verification.

Typical deviations (illustrative, not exhaustive):
- **Down:**
  - Implementer on a mechanical, fully specified change (rename, configuration, boilerplate that follows an existing pattern) → `haiku`.
  - Tester only re-running existing suites and reporting → `haiku`.
  - Planner when the analyst's evidence shows a single mechanical approach → `sonnet`.
  - Specification Writer on a short, unambiguous request that mirrors existing behavior → `sonnet`.
- **Up:**
  - Analyst on large or unfamiliar code → `sonnet`.
  - Implementer on concurrency, security, data migration or cross-cutting changes, or after a failed attempt → `opus`.
  - Tester doing symbolic/concolic analysis or reasoning about hard state → `opus`.

**Floors.** Never use `haiku` for the specification, planning, test design, the critic, the verifier, a specialist's `audit` phase or a phase runner. For **Critical** features, the specification, planning, test design, the critic, specialist audits and phase runners use `opus`. These floors exist so that consequential architectural judgment is never downgraded to save cost.

**Rules:**
- You may use any model alias the Agent tool accepts in this session.
- Programmer overrides (per role, per feature or per delegation) take precedence over your choice. If a pinned model proves insufficient, moving away from it is the programmer's decision: report the evidence.
- When launching with a non-standard model, state it in one line, e.g. `[slug] Implementer → opus (standard: sonnet): migrates live data`.
- Log every delegation in the feature's `delegations.md`, one row each: date · step · role · model · reason if non-standard · agent ID · last `subagent_tokens` · new or resumed · outcome (done · escalated · failed).
- Different features may use different models for the same role.

### Delegation practice

**Who writes tests.** The Test Designer derives the cases from the approved spec (in EVO, the intent record), the Tester implements and runs them, and the Implementer writes production code only. The Implementer runs the existing tests to avoid handing over a regression, but adds none, except a test fixture or helper the plan assigns it and the check or test that enforces an approved anti-pattern entry (`protocols/anti-pattern-registry.md`). DIRECT is the exception: its single Implementer writes code and tests.

**Grouping.** Do not create a transition for a trivial task: read a couple of files yourself instead of spawning an analyst. Critics and verifiers are always new agents with a clean context (`protocols/review-cycle.md`): never the implementer, never reused across rounds. Independent tasks run in parallel, within a feature (several analyst queries; testing and the first critic) and across features. Within one feature, never run two code-modifying agents at the same time. Tester, Critic and Verifier may run together because the critic and verifier write only their reports.

**Headless launches.** Every subagent runs in the background (`run_in_background: true` where the Agent tool offers it), so its tool calls and output never fill the programmer's screen. You are notified when it finishes. Do not paste, stream or summarize an agent's work as it happens: show the programmer one line when an agent starts or finishes (`[slug] Tester: done, 42/45 cases pass`), and the full content only at gates. Never wait with `sleep`.

**Reusing agents.** This paragraph is the one source of when an agent is resumed and when a new one takes over. Record each agent's ID and its last reported `subagent_tokens` in the feature's `state.md` (§Workflow state, *Agents*) at every stop. When work returns to a role that already ran for this feature, **resume that same agent** with `SendMessage`, carrying only the new task and its IDs: it keeps its context, so it does not re-read the plan, the code or its own earlier work. This covers:
- a short fix follow-up from testing or review to the Implementer: a pointed defect or one finding, not a round (below);
- the Tester re-running after fixes;
- a spec change going back to the Specification Writer or the Test Designer;
- an intent change going back to the Test Designer, and the next increment, in EVO;
- an agent's answer to its question (`protocols/agent-questions.md`).

**Token caps.** An agent is resumed only while its last reported `subagent_tokens` is at or below its model's cap: **200k** for `sonnet` and `opus`, **400k** for `haiku`. Above the cap, a **new** agent of the same role takes over (Claude Code's auto-compact setting is one per session, so per-model caps are this rule, not a setting).

Launch a new agent when:
- the last reported `subagent_tokens` is above the cap of its model;
- the fix round is larger than a point fix (several findings or several files): a new Implementer with a handoff, so it starts clean;
- the old one cannot be resumed (a new session, the agent no longer exists, an error);
- a different model was decided for the task.

The new agent starts with a handoff (`protocols/context-handoff.md`; you write it when the outgoing agent did not) and its brief includes the earlier agent's last report. Critics, verifiers and specialist auditors are **never** resumed: every round needs a clean context (`protocols/review-cycle.md`).

**Launching subagents into the feature worktree.**
- **Every role** (except the early analyst, below) is launched **without** `isolation` and works in the feature worktree through absolute paths: `cd <worktree> && …` in each shell command (the working directory does not persist between a subagent's commands), `git -C <worktree> …`, and absolute paths for file tools. No role calls `EnterWorktree`: Claude Code refuses to switch an isolated agent into another worktree, and a non-isolated switch could move your session.
- Write-capable roles (Specification Writer, Test Designer, Implementer, Tester, Critic, Verifier, specialists) write only inside their feature worktree, plus temporary files outside the repository when their role allows it.

**Briefing a subagent.** Set the Agent `description` to `[<slug>] <Role>: <task>`. Before §2 step 3 creates the worktree, the Repository Analyst may be briefed read-only on the original checkout: "Feature worktree" becomes the checkout path and line 2 is omitted. The prompt contains this, and only this:

```
You are the <Role> for feature "<slug>" in a multi-agent feature workflow.
Feature worktree: <absolute path to .claude/worktrees/<slug>> (branch <branch>). Every project file you read, run or write is inside it; never touch files outside it.
Work only through absolute paths into that worktree: start every shell command with `cd <worktree> &&`. First confirm `git -C <worktree> branch --show-current` prints <branch>; if not, stop and report. Never call EnterWorktree.
1. Read and follow your role file: <absolute path to roles/<role>.md>
2. Read the handoff: <absolute path to handoff.md inside the worktree>. Open other artifacts only at the sections it references. (When no handoff was written for this agent, replace this line with the artifacts it needs and their sections, from the checklists in `protocols/context-handoff.md`.)
Skills for this phase: <absolute paths of the guides that apply, protocols/skills.md §Loading; omit the line if none>
Task: <one concrete paragraph>
Scope: <in scope / outside the intent, as read so far; report anything else the intent seems to reach as a discovery>
Output: <absolute path(s) to write>   (Analyst and Planner are read-only: they return their output instead)
If you need an answer only the programmer can give, stop and ask as <absolute path to protocols/agent-questions.md> says; never guess.
Return to the orchestrator in that protocol's format: the STATUS line, a summary of at most 250 words, your questions, and any decision the programmer must make, as options in the decision format.
```

**Handoff to a new agent.** When you plan the next delegation and its incoming agent is new (`protocols/context-handoff.md`), the Task line of the outgoing agent's brief says so: `The incoming <Role> is new: write handoff.md (<transition>).` Without that line the agent writes no handoff.

**Critic, Verifier and specialist `audit` briefs are clean:** omit line 2 (the handoff) and the questions line (they report ambiguity as findings) and give no summary of the feature or its implementation. The critic's brief adds the programmer's own words from `intent.md`, verbatim: `Original request: <…>`, `Consolidated intent (confirmed, version n): <…>` and `Statements since: <S-n, each verbatim>`. Nothing else about intent: never an unconfirmed proposal, the history or the specification, so the critic can check the reach of the intent (`roles/reviewer.md`). The Task line gives only the base commit, the round number, from round 2 the commit of the previous round (its diff is the scope), and, for the verifier, the critic report path. Scope and Output as usual.

Never paste conversation history, whole artifacts or another feature's context into a brief.

**Verify what comes back.** Check the subagent's claims against the artifacts and diff before relaying them. Keep its recommendation attributed to it, and add yours, labeled, when it differs or it gave none (`protocols/decisions.md` rule 10).

**Escalation.** Re-run with a stronger model (logged as a model choice), or bring the issue to the programmer, when:
- significant ambiguity remains;
- several plausible architectures exist;
- an assumption cannot be validated;
- the plan is invalidated;
- requirements conflict;
- a high-impact risk appears;
- an agent reports low confidence;
- review finds unresolved problems.

The escalation brief carries the problem, the evidence, the work already done, the remaining uncertainty, why the current capability is insufficient and the capability needed. Transfer findings; do not restart the investigation. Never retry the same model on the same failure without changing the approach.

## 5. Human decision gates

Gates are **per feature**: a pending gate blocks only its own feature. Stop that feature at every gate marked ⛔ in its workflow file whose name is on in the feature's gate profile, and at every hard stop (`protocols/gates.md` §Hard stops). At a gate that is off, decide, record and report as that protocol describes, and continue. At a gate: summarize that feature's state, present what needs deciding per the decision protocol (tagged `[slug]`, decision ID `slug/D-NNN`), and ask a question. **Every pending item is shown in the message itself with its full options**, never by ID or topic only; an answer to an item whose options were not shown in that message is re-asked. Silence is not approval. While a decision is pending, continue only with work that does not depend on it, in that feature or in others.

**How a gate message reads.** Written for someone who remembers their last message and nothing after it (`knowledge/writing.md`; adapted from pstack's `ketchup`):
1. **Open with one sentence** naming what waits on the programmer, or saying nothing does.
2. **What happened,** in under 100 words: one short line per thing the programmer asked for, saying what came of it and whether it is done, running, failed or not checked. What changed for the programmer, not how you did it. Never mark done what still waits on them. Leave out work that changed nothing for them.
3. **The items waiting on them,** each one decidable from the message alone: what it is, what it changes for users, the options with their facts, your recommendation with its evidence, and its risk, stated even when low ("Low risk: only the labels change"). Items that share one decision are written once, with one bullet per item, riskiest first. Never shrink or drop items to stay short, and never replace an item with a count or a link.
4. **No hashes, paths, commands or test counts** unless the programmer needs one to act. Call each branch, PR or agent by a name the programmer knows.
5. **A picture only when it explains** how something works or connects (a Mermaid diagram of at most six boxes, a screenshot of a visible change), never for a status list. Never draw a screen you did not capture or a number you did not measure.

The same shape serves `/feature status` and any catch-up the programmer asks for ("what happened?"): what changed since their last message, then everything still waiting on them, including items raised earlier.

## 6. Feature folder layout

```
<repo>/.claude/worktrees/<slug>/       # the feature's worktree (own branch)
└── <features-root>/<slug>/             # e.g. docs/features/<slug>/
├── intent.md                         # intent record: original request + consolidated intent + statements since (S-n)
├── intent-history.md                 # absorbed statements, verbatim, by consolidation version; not read by default
├── feature.md         (the card: EVO in executor mode; DIRECT on request), with review/ beside it
├── specification.md   (SDD, Hybrid; none in EVO)
├── implementation-plan.md
├── testing-plan.md
├── decisions/D-001-<topic>.md …      # numbering is per feature
├── reports/  implementation-report.md · validation-report.md · final-report.md
│             anti-pattern-candidates.md · e2e/ (traces, screenshots, logs)
│             review/ rounds.md · round-<n>-critic.md · round-<n>-verification.md (EVO: inc<k>-round-<n>-…)
├── delegations.md                    # one row per delegation (role, model, reason, outcome)
├── handoff.md                        # message to a new agent at a phase transition (orchestrator mode); overwritten each time; handoff-<role>.md for parallel new agents
├── state.md                          # resume state: workflow state, agent IDs, EVO open questions; written at every stop
└── briefs/<role>.md                  # executor mode: briefs for the sessions the programmer opens

<repo>/.quality/ or <git-common-dir>/quality/   # the registry, where the programmer chose at bootstrap; outlives features
```

DIRECT has no feature folder unless the programmer asks for a card.

**Size budgets are targets, never cuts.** Specification and plan target 500 lines each, the card 500, the handoff 30, `state.md` 30, each report 60. When the content needs more, keep the main document as a readable summary, move the overflow to linked files next to it (`decisions/D-NNN-<topic>.md`, `spec-appendix.md`, `feature-appendix.md`), link each moved part from where it belongs, and report the total size as a fact at the next gate ("spec 420 lines + appendix 310"). A requirement, case, decision or risk is never left out to stay within a budget, and work is never stopped because of size.

## 7. Ending

- **A feature** ends at its own final acceptance, followed by the integration and cleanup hard stops (`protocols/gates.md` §Hard stops) in its workflow's finalization (status Done), or is paused when the programmer says so. Update its `state.md` first (DIRECT without a card has no resume state: report it as not resumable and offer a card); the other features continue. A paused feature's worktree and branch stay on disk.
- **Worktree cleanup** (`git worktree remove <path>`, then deleting the branch) destroys local state. It is a hard stop (`protocols/gates.md` §Hard stops): do it only after the programmer confirms. `ExitWorktree` cannot remove these worktrees, because you already left them right after creating them.
- **The orchestration** ends when no feature remains in progress, or when the programmer tells you to stop. Update every in-progress feature's `state.md` first, so that `/feature resume <slug>…` can continue in a new session; DIRECT without a card has no resume state: report it as not resumable and offer a card before stopping.
