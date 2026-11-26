# Multi-Feature Orchestration Protocol

One orchestrator (the main thread) can run a single feature flow or several at once. Each feature is independent: its own workflow (DIRECT, SDD, EVO or Hybrid, selected per feature), artifacts, gates, decision numbering, agents and model choices. The orchestrator is the **only** channel between the programmer and the agents of every feature.

## Portfolio

Every feature in progress has:
- a **slug** (short, unique in the session);
- a **feature folder**;
- a **worktree** (`.claude/worktrees/<slug>`) and its branch;
- a **workflow**;
- a **status**: Active · Paused · Done (pausing or stopping a feature with running agents: `SKILL.md` §7, *Pause and stop everything*);
- a current phase/step, running agents and pending decisions.

Each feature's `state.md` (§Workflow state; when it is written: `protocols/context-handoff.md` §Resume state) is its persistent source of truth. The portfolio board is **derived** from those files plus the agents currently running, so there is no separate registry file to keep in sync.

On `/feature status`, when the programmer asks, or when the state of several features changed in one turn, show the board:

| Feature | Workflow | Gates | Phase / step | Running agents | Waiting on the programmer |
| --- | --- | --- | --- | --- | --- |

Rows are alphabetical by slug. Above the board, the catch-up of `SKILL.md` §5 *How a gate message reads*: one sentence on what waits on the programmer, then what changed since their last message; below it, every pending item in full.

**One orchestrator per feature.** Never resume a feature that another live orchestrator claims (`protocols/hierarchy.md` §Claims). If the programmer asks for that, point out the risk of conflicting edits and let them decide.

**Several orchestrators.** When the portfolio is split across sessions, either independently or under a principal orchestrator, follow `protocols/hierarchy.md`.

## Communication

- Tag every message, report and decision with its feature: `[slug]`. Reference decisions as `slug/D-NNN`.
- When several features have news in the same turn, group them by feature, alphabetical by slug.
- Map each programmer message to a feature by explicit tag or unambiguous content. If a message could apply to more than one feature, ask which one before acting. Never apply a decision to a feature it was not given for.
- **Pending decisions across features:** list them in the order they arose, and say so. Make each one self-contained, so it can be decided without scrolling back. The programmer may answer them in any order.

## Independence and scheduling

- **A gate blocks only its own feature.** While a feature waits for the programmer, keep the others moving.
- Parallel launches: `SKILL.md` §4, *Delegation practice* (Grouping). Name each with its Agent `description`: `[slug] <Role>: <task>`.
- **When an agent finishes:**
  1. identify its feature;
  2. verify the output;
  3. update that feature's artifacts and `delegations.md`, and, at a stop, its `state.md`;
  4. report to the programmer, tagged.
- **You do not prioritize features.** When features compete (same files, a shared test environment, your own context capacity), the order, serialization or pausing is the programmer's decision. Present it with the decision protocol, with your recommendation.

## Interactions between features

- **Detect overlap:**
  - compare the "Components and files" of approved or proposed plans across features in progress;
  - compare specs for conflicting requirements, constraints or invariants;
  - look for shared resources (database schemas, public APIs, configuration, test infrastructure).
- **Report overlaps and conflicts as facts,** e.g. `[a] and [b] both modify src/billing/invoice.ts`, or `[a] FR-2 contradicts [b] INV-1`. Resolving them is the programmer's decision.
- **Record the relation** in both features' `state.md` (§Workflow state, *Related features*).
- **Never carry a decision** from one feature into another unless the programmer says so.

## Worktrees: what stays shared

Every feature already lives in its own built-in worktree (`SKILL.md` §2.3), so features never share a working tree, and isolation is not a decision to ask about. Three things remain shared:

- **Integration.** Branches that change the same files will conflict when integrated. Report the overlap as a fact (files, branches) as soon as plans show it, not only at the end. The integration order and method across features are the programmer's decisions, presented as `protocols/decisions.md` describes; integration is a hard stop (`protocols/gates.md` §Hard stops).
- **Runtime resources.** Test runs in different worktrees can still collide on ports, databases, caches or external services. If two features would use the same resource at the same time, report it; serializing or isolating those runs is the programmer's decision.
- **Base drift.** Each worktree branches from its base at creation. Once another feature is integrated, the remaining branches may need updating (merge or rebase of the new base). Whether and how to do that is the programmer's decision.

## Efficiency

- Launch every agent of a phase in one message, across features.
- Write the artifacts of several features in one command when their content is ready.
- Never wait with `sleep`: background agents notify when they finish.
- Verify an agent's claims with one batched check (for example, one command that runs every feature's tests), not one call per claim.
- Keep subagent returns within their word limits; do not re-read what a report already states unless you are verifying it.

## Executor sessions beside the orchestrator

A feature run by an executor session (`protocols/executor.md`) is not in this orchestrator's portfolio, but its claim is visible (`protocols/hierarchy.md` §Claims). Show it on the board as `executor: <session>` with the phase from its claim, compare its files for overlap like any other feature, and never act on it. To bring it under this orchestrator, the programmer stops the executor session and runs `/feature resume <slug>` here.

## Context economy

Many features in one session consume your context.
- Keep detail in artifacts, not in the conversation.
- When switching to a feature, re-read its `state.md` instead of relying on memory.
- Keep subagent returns short.

If context pressure starts to threaten correctness, tell the programmer and present the options (`protocols/decisions.md`), for example: pause some features, continue some in another session with `/feature resume <slug>` (DIRECT without a card is not resumable: offer a card), or move to the hierarchical mode, where each group of features keeps its own context (`protocols/hierarchy.md`).
