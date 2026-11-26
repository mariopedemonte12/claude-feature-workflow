# Context Handoff Protocol

**Purpose:** let the next agent continue correctly without reconstructing the previous phase. Transfer knowledge, not conversation.

## Who writes it

`handoff.md` is a message between agents of different phases, in orchestrator mode only. It is written at a phase transition only when the incoming agent is new (a same-role replacement is a relay instead: §Relay), in every workflow; a resumed agent gets a brief with the new task and the artifact sections it needs instead. Executor mode never writes one.

The outgoing agent writes it, when its brief's Task line says the incoming agent is new (`SKILL.md` §4 *Briefing a subagent*). The Repository Analyst and the Planner are read-only, so they return their content and the orchestrator writes the handoff. The orchestrator also writes the handoffs whose outgoing role writes none: Request → Specification, Specification → Planning and Specification → Test design (in EVO, Intent → Planning and Intent → Test design). The orchestrator checks every handoff before the next delegation.

`handoff.md` lives in the feature folder and is overwritten each time it is written. When two new agents start in parallel (SDD step 5, EVO step 4: Test Designer and Planner), each gets its own `handoff-<role>.md`. It holds no resume state: that is `state.md` (§Resume state). History lives in the artifacts (specification change log, decisions, reports), not in old handoffs.

## Rules

- Reference canonical artifacts (path + section, or file:line) instead of copying them.
- Cite approved decisions by ID (D-NNN). Never present a pending option as decided, or a superseded decision as current.
- Mark findings Confirmed or Hypothesis explicitly.
- Write for the receiver: include what its responsibility needs (checklists below) and omit sections that would be empty.
- Keep it concise, normally one page. Correctness beats brevity: include anything whose absence could produce a wrong result.
- Never include full conversation histories, repeated explanations, irrelevant code details, superseded decisions shown as current, or speculation shown as fact.

Structure: `templates/handoff.md`.

## What each transition must carry

In every workflow, these checklists define what a new agent's handoff carries, and what a resumed agent's brief points to.

**Request → Specification**
`intent.md` path, its consolidated intent version and last S-ID · repository references (analyst report): existing behavior in the area, constraints it imposes · workflow · criticality if already known.

**Intent → Planning** (EVO)
`intent.md` (consolidated intent version, statements since) · decisions that settle behavior (D refs) · completion criteria · main flows · open questions (blocking ones flagged) · repository references (analyst report, including the nearest analog) · areas of technical uncertainty.

**Intent → Test design** (EVO; the Test Designer never reads the plan beyond the increment entry)
`intent.md` version and last S-ID · behavior-settling decisions (D refs) · the increment: the flow it delivers and its planned edge cases · reach of the intent found so far · existing test framework, location, style and commands · E2E tooling · existing behavior of the area and the nearest analog (analyst report).

**Specification → Planning**
Intent · confirmed FR/AC IDs · constraints · invariants · open questions (blocking ones flagged) · repository references (analyst report) · areas of technical uncertainty.

**Specification → Test design** (the Test Designer never reads the plan)
Approved spec version · confirmed FR/AC/INV IDs · reach of the intent and outside the intent (with who drew each boundary) · existing test framework, location, style and commands · E2E tooling · existing behavior of the area (analyst report).

**Planning → Implementation**
Approved approach (D ref) · alternatives not chosen, with the reason only when that prevents re-litigating · technical decisions · affected files and components · dependencies · implementation sequence · risks · `testing-plan.md` (the behaviors the code must handle; the Implementer writes no tests, except `SKILL.md` §4) · decisions still pending and what must not be touched until they are made · verification depth (mutation testing yes or no · review level R0 / R1 / R2) · end-to-end harness · registry entries (AP IDs) relevant to the change.

**Implementation → Testing** (critics and verifiers never read handoffs: `protocols/review-cycle.md` §Clean context)
Implemented functionality by FR/AC · verification run after committing on a clean tree (`roles/implementer.md` §Rules touched and verification) · files modified · actual behavior implemented · deviations from the plan, with D refs · assumptions · known limitations · test commands · test data and setup · higher-risk areas · base commit for the diff · how to start the system for end-to-end tests · quality gate result · suggested testing focus.

**Testing → Evolution** (EVO)
Tests executed, with results and evidence · failures · uncovered scenarios · discrepancies between the intent or cases and the implementation · newly discovered behavior (as hypotheses or discoveries) · deferred edge cases still open · invalidated assumptions · risks · possible intent, case or plan changes, phrased as options with your recommendation, labeled (`protocols/decisions.md`).

**Testing → Finalization**
Validation results · status of each acceptance criterion · end-to-end status and evidence · black-box technique statuses · mutation testing results · known defects · remaining risks · limitations.

## Incoming agent

1. Read the handoff (when there is none, the artifacts the brief names) and identify your own responsibility.
2. Open only the referenced artifacts and sections.
3. Check freshness (below).
4. Retrieve additional context only as needed.
5. Do not redo completed investigations.
6. Report inconsistencies or missing information instead of guessing. The handoff is a starting point and may be incomplete.

## Relay

A relay replaces an agent by a new agent of the **same role**, when `SKILL.md` §4, *Reusing agents*, says to replace it instead of resuming it. **Relation to the handoff:** `handoff.md` starts the first agent of a role at a phase transition; relay notes start a new agent of a role that already ran for this feature. One delegation uses one of them, never both: a role that already ran gets relay notes even at a phase transition.

**Who writes the notes.** Before the replacement, the orchestrator resumes the **outgoing** agent for one turn, whatever its usage, with only this task: `Write the relay notes to <path>, as protocols/context-handoff.md §Relay says, and stop.` A read-only role (Repository Analyst, Planner) returns the notes instead, and the orchestrator writes them. If the outgoing agent cannot be resumed (a new session, the agent no longer exists, an error), the orchestrator, or the phase runner that drives the phase, writes the notes from the agent's last reports and says so in the notes' first line.

**Where.** `$(git rev-parse --git-common-dir)/feature-workflow/relay/<slug>/<role>.md`: local, shared by the worktrees of the repository, never committed, and available in DIRECT, which has no feature folder. Each relay of that role overwrites it; two agents of one role in the same phase (specialists) use `<role>-<specialist>.md`. Worktree cleanup deletes `relay/<slug>/` (`SKILL.md` §7).

**What the notes hold:** the exploration the new agent would otherwise repeat, and nothing else. No diffs, no file contents, no logs: those are on disk.

```markdown
# Relay: <role> · <slug> · HEAD <short sha> · base <commit> · <date> · written by <the outgoing agent | the orchestrator, from the last reports>

## Map
- <rule, copy or component>: <path:line, …> · proof: `<grep or command that finds every place>`

## Verification
- `<command>`: what it checks · trap: <what makes it pass or fail for the wrong reason, e.g. a verification run on uncommitted changes (`roles/implementer.md` §Rules touched and verification)>

## Decisions in force
- D-NNN: <one line>

## Read in full
- <path>, …
```

**The incoming agent** reads the notes **and** the full diff and log of the work so far (`git -C <worktree> diff <base>..HEAD`, `git -C <worktree> log <base>..HEAD`), because the notes hold only what the outgoing agent chose to write. Its brief names both on line 2 (`SKILL.md` §4, *Briefing a subagent*), plus the earlier agent's last report. It checks freshness against the notes' HEAD (§Freshness) and treats a claim in the notes that the diff or a grep contradicts as stale.

## Freshness

**When writing** a handoff or `state.md`: run these inside the feature worktree. Record `git rev-parse --short HEAD`, the branch, whether the working tree is dirty (`git status --porcelain` is non-empty), and the artifact versions (spec vN, plan status). If the project is not a git repository, record the date and time and the list of files touched.

**When receiving or resuming:** compare against the current state (`git log --oneline <recorded>..HEAD`, `git diff --stat <recorded>`). Re-read only the changed files that matter to your task. Re-verify a decision only if the changes touch what it depends on. A change does not automatically invalidate the handoff or `state.md`.

## Resume state

`state.md` (`templates/state.md`) in the feature folder holds what a fresh session needs to resume: the workflow state, with each resumable agent's ID, model and last reported `subagent_tokens`, after a pause or a stop everything (`SKILL.md` §7, *Pause and stop everything*), the agents that finished, were interrupted or must be relaunched, and, in EVO, the open questions. Whoever drives the session writes it at every stop (a gate, a pending question, the end of the turn, a pause): the orchestrator, a phase runner (`protocols/phase-runners.md`), or the SDD executor. In EVO as executor, the card's *State* plays this role. DIRECT keeps neither, unless the programmer asks for a card: then its *State* plays this role. Resuming, building the portfolio board and recovering from a compaction read `state.md`, never the handoff.

## A transition is complete when

- the phase deliverable exists;
- important decisions are recorded;
- unresolved issues are documented;
- the handoff is written and checked by the orchestrator when §Who writes it calls for one (otherwise the brief names the artifacts);
- the next agent can start without reconstructing the previous phase.
