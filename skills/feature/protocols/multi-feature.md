# Multi-Feature Orchestration Protocol

One orchestrator (the main thread) can run a single feature flow or several at once. Each feature is independent: its own workflow (SDD Direct, ESDD or Hybrid, selected per feature), artifacts, gates, decision numbering, agents and model choices. The orchestrator is the **only** channel between the programmer and the agents of every feature.

## Portfolio

Every feature in progress has:
- a **slug** (short, unique in the session);
- a **feature folder**;
- a **working directory** (the main tree or its own worktree);
- a **workflow**;
- a **status**: Active · Paused · Done;
- a current phase/step, running agents and pending decisions.

Each feature's `handoff.md` (§Workflow state) is its persistent source of truth. The portfolio board is **derived** from those handoffs plus the agents currently running, so there is no separate registry file to keep in sync.

On `/feature status`, when the programmer asks, or when the state of several features changed in one turn, show the board:

| Feature | Workflow | Phase / step | Running agents | Waiting on the programmer |
| --- | --- | --- | --- | --- |

Rows are alphabetical by slug.

**One orchestrator per feature.** Never resume a feature that another live session is orchestrating. If the programmer asks for that, point out the risk of conflicting edits and let them decide.

## Communication

- Tag every message, report and decision with its feature: `[slug]`. Reference decisions as `slug/D-NNN`.
- When several features have news in the same turn, group them by feature, alphabetical by slug.
- Map each programmer message to a feature by explicit tag or unambiguous content. If a message could apply to more than one feature, ask which one before acting. Never apply a decision to a feature it was not given for.
- **Pending decisions across features:** list them in the order they arose, and say so. Make each one self-contained, so it can be decided without scrolling back. The programmer may answer them in any order.

## Independence and scheduling

- **A gate blocks only its own feature.** While a feature waits for the programmer, keep the others moving.
- Launch independent agents in parallel, within and across features. Name each with its Agent `description`: `[slug] <Role>: <task>`.
- **When an agent finishes:**
  1. identify its feature;
  2. verify the output;
  3. update that feature's artifacts, `handoff.md` and `delegations.md`;
  4. report to the programmer, tagged.
- **You do not prioritize features.** When features compete (same files, a shared test environment, your own context capacity), the order, serialization or pausing is the programmer's decision. Present it with the neutral protocol: options alphabetical, by slug where they name features.

## Interactions between features

- **Detect overlap:**
  - compare the "Components and files" of approved or proposed plans across features in progress;
  - compare specs for conflicting requirements, constraints or invariants;
  - look for shared resources (database schemas, public APIs, configuration, test infrastructure).
- **Report overlaps and conflicts as facts,** e.g. `[a] and [b] both modify src/billing/invoice.ts`, or `[a] FR-2 contradicts [b] INV-1`. Resolving them is the programmer's decision.
- **Record the relation** in both features' handoffs (§Related features).
- **Never carry a decision** from one feature into another unless the programmer says so.

## Working-directory isolation

Concurrent implementation or testing in a single working tree can collide: the same files edited, diffs from several features mixed together, test runs interfering with each other.

The first time two features would be in implementation or testing at the same time, present the **isolation policy** as a decision (neutral protocol). The viable options usually include:

- **Git worktree per feature** (requires git):
  - Setup: `git worktree add <path> -b feature/<slug>`. All of that feature's agents work only in its worktree, and its artifacts live there.
  - Diffs per feature stay clean.
  - Integration (merge or rebase) becomes an explicit step at finalization, and that step is a programmer decision. Conflicts surface at integration time.
- **Serialized implementation:**
  - One feature implements and tests at a time in the shared tree; the others keep progressing through specification and planning.
  - No integration step. Features wait for each other.
- **Shared tree, concurrent:**
  - Viable only when file sets and test resources are disjoint.
  - Diffs mix in one tree, so `git diff <base>` for one feature includes the others' changes. The reviewer must then be given an explicit file list.

Record the choice in each affected feature's `decisions/`. It becomes the session's isolation policy. Re-ask only when conditions change, for example when a new overlap appears. Brief every agent with its feature's working directory.

## Context economy

Many features in one session consume your context.
- Keep detail in artifacts, not in the conversation.
- When switching to a feature, re-read its `handoff.md` instead of relying on memory.
- Keep subagent returns short.

If context pressure starts to threaten correctness, tell the programmer and present the options neutrally, for example: pause some features, or continue some in another session with `/feature resume <slug>`.
