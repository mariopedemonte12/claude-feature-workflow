# Orchestrator Hierarchy Protocol

Features can be orchestrated in three **modes**. None is mandatory; the programmer chooses, and may change mode between sessions.

| Mode | Shape | Who the programmer talks to |
| --- | --- | --- |
| **Single** | One orchestrator runs every feature (`protocols/multi-feature.md`). | That orchestrator |
| **Independent** | Several orchestrator sessions, each with its own features, unaware of a leader. | Each session directly |
| **Hierarchical** | A **principal** orchestrator coordinates **sub-orchestrators**; each sub-orchestrator runs one **group** of features with its own local context and reports to the principal. | The principal |

A **group** is a named set of features (kebab-case, e.g. `billing`, `onboarding`) that one sub-orchestrator runs. Which features form a group, and how many groups exist, is the programmer's decision. The principal may report facts that bear on it (features that touch the same files belong in one group more cheaply than in two).

Every mode keeps the rules of `SKILL.md`: one worktree per feature, gates per feature, artifacts as the source of truth, neutrality, and **one orchestrator per feature**.

## Claims: who orchestrates what

Every orchestrator, in every mode, records which features it runs in a claim file shared by all worktrees of the repository and never committed:

```
$(git rev-parse --git-common-dir)/feature-workflow/claims/<slug>.json
{ "slug": "csv-export", "group": "billing", "orchestrator": "<session or agent name>",
  "mode": "hierarchical", "principal": "<principal name or null>",
  "worktree": "<absolute path>", "featureFolder": "<absolute path>",
  "status": "Active", "updated": "2026-11-20T18:04:00Z" }
```

- Write the claim when a feature is created or resumed; update `status` and `updated` at every transition; set `status` to `Done` or `Paused` when the feature ends or pauses.
- Before creating or resuming a feature, read its claim. If another orchestrator holds it as Active, do not touch the feature. If that orchestrator no longer appears in `ListAgents` and the claim has not been updated recently, the claim may be stale: tell the programmer and take it over only with their confirmation.
- `/feature status` in any session lists every claim of the repository, so independent sessions see each other's features.

## Independent mode

Each session runs `/feature` as usual. In addition:
- **Claims** prevent two sessions from orchestrating the same feature.
- **Overlap across sessions:** when a plan is approved, compare its "Components and files" with the plans of the features other sessions claim (their `implementation-plan.md` is readable through the claim's `featureFolder`). Report overlaps to the programmer as facts, as in `protocols/multi-feature.md` §Interactions.
- Sessions do not message each other unless the programmer asks for it.

## Hierarchical mode

### Principal orchestrator

Started with `/feature hub`. It:
- is the programmer's channel: receives every request from the sub-orchestrators and routes every answer back;
- keeps **no feature detail** in its context. It knows groups, features, statuses, pending requests and overlaps, and reads a feature's artifacts only to answer a specific question;
- never delegates feature roles (analyst, planner, implementer, tester, critic, verifier) itself: that is the sub-orchestrator's job;
- detects overlaps **between groups** (plans, specs, shared resources) and reports them as facts;
- does not prioritize features or groups. Ordering, serializing or pausing them is the programmer's decision.

**Board** (`/feature status`), derived from claims and the latest reports, rows alphabetical by group, then by slug:

| Group | Feature | Sub-orchestrator | Phase / step | Waiting on the programmer |
| --- | --- | --- | --- | --- |

### Sub-orchestrator

Runs `SKILL.md` for its group, exactly as a single orchestrator does, with these differences:
- Its programmer channel is the principal. Every gate becomes a **decision request** sent up; it never presents a gate to the programmer directly unless the programmer writes to it directly (then it answers, and informs the principal with a status report).
- While a request is pending, it keeps working on everything that does not depend on it.
- It records every answer in the feature's `decisions/`, as today. The feature's artifacts stay the source of truth.
- It sends a **status report** at every phase transition and whenever the principal asks.

### Messages

Every message starts with a header line, then the body:

```
[hub:<hub>] [group:<group>] [<slug>] <TYPE> <id>
```

| Type | From → to | Body |
| --- | --- | --- |
| `STATUS` | sub → principal | phase / step, running agents, pending decisions, overlaps noticed; at most 120 words |
| `DECISION-REQUEST` | sub → principal | id `slug/D-NNN`; what it blocks (the whole feature · part of it · nothing yet); the decision in the neutral format of `protocols/neutral-decisions.md`, self-contained |
| `DECISION` | principal → sub | id; the programmer's answer, verbatim where it matters |
| `QUESTION` / `ANSWER` | either way | a clarification that is not a decision |
| `OVERLAP` | principal → subs | the facts of a cross-group overlap and the decision id if the programmer must resolve it |
| `DONE` | sub → principal | the feature reached final acceptance, integration and cleanup gates; links to the final report |

A message is self-contained: the receiver acts on it without the sender's conversation.

### Ordering the programmer's queue

The principal presents pending requests as **one queue**, with the ordering criterion stated each time:

1. requests that block a whole feature, then those that block part of it, then those that block nothing yet;
2. within each level, in the order they arrived.

This orders by consequence of waiting, as severity orderings do (`protocols/neutral-decisions.md` rule 11). It never ranks the options inside a request. The programmer may answer in any order, defer any request, or set their own priority for a group; the principal follows it until told otherwise.

Every request keeps its own neutral presentation, untouched by the principal except to remove preference language, as rule 14 of that protocol requires.

## Transports for the hierarchical mode

How sub-orchestrators run and exchange messages is chosen by the programmer when the hub starts, presented with the neutral protocol (alphabetical):

| Transport | How it works | Facts |
| --- | --- | --- |
| **Agent team** | The principal is the team lead; each sub-orchestrator is a teammate, told to read this `SKILL.md` and this protocol for its group. Messages go through `SendMessage` and the team mailbox. | Experimental: requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, which the programmer sets. Teammates are full sessions with their own context, can launch subagents (in the foreground only), and the programmer can talk to them directly. In-process teammates are not restored by `/resume`; one team per session; teams do not nest. |
| **Separate sessions** | The programmer opens one Claude Code session per group and runs `/feature join <hub-name> <group>` in it; the principal is another session, named with `/rename`. Messages go through cross-session messaging (`ListAgents`, `SendMessage`). | Requires Claude Code 2.1.224+ (2.1.234+ on native Windows). Each session is independent and resumable. Messages travel over a local socket; the `crossSessionInbound` setting can hold or refuse them, which may show approval dialogs. The programmer starts and names each session. |
| **Subagents** | The principal launches each sub-orchestrator as a `general-purpose` subagent with the brief below. At a gate it ends its turn with its decision requests; the principal continues it with `SendMessage` carrying the answers. | No setting needed. Depth: principal → sub-orchestrator → feature role is 2 of the default 3 levels (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). The programmer cannot talk to a sub-orchestrator directly. Its context lives only as long as the principal's session; afterwards, the group resumes from handoffs. The principal creates the feature worktrees itself (`SKILL.md` §2.3) and passes their paths, so the sub-orchestrator never calls `EnterWorktree`. |

**Brief for a subagent sub-orchestrator:**

```
You are the sub-orchestrator of group "<group>" in hub "<hub>" of a multi-agent feature workflow.
Read and follow <absolute path to SKILL.md>, and <absolute path to protocols/hierarchy.md> §Sub-orchestrator.
Your programmer channel is the principal: you cannot talk to the programmer. At every gate, end your turn
with DECISION-REQUEST messages; you will be continued with DECISION messages. Never call EnterWorktree.
Features: <slug> — <worktree path> — <feature folder> — <one-line intent> (one line each)
Task: <start or resume each feature at its current step>
```

## Leaving the hierarchy

The programmer may end the hierarchy at any time. Each sub-orchestrator updates its features' `handoff.md` and claims, sends a final `STATUS`, and stops. Any feature can then be resumed in any mode with `/feature resume <slug>`.
