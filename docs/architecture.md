# Architecture of the Feature Workflow

There are two entry points: `/feature` and `/feature-kit`. Each feature in `/feature` has a **workflow** (DIRECT, SDD or EVO) and the session has a **role** (orchestrator or executor). Most of this document describes how the orchestrated workflows are built: who takes part, how a feature moves from request to integration, which files hold the state, and what each agent is responsible for. The behavior itself is defined by the files under `skills/feature/`. When this document and those files disagree, the files win, and each section names the file it summarizes.

Diagrams use Mermaid and render on GitHub.

## Contents

1. [Building blocks](#1-building-blocks)
2. [Entry points and modes](#2-entry-points-and-modes)
3. [Startup of a feature](#3-startup-of-a-feature)
4. [SDD](#4-sdd)
5. [EVO and Hybrid](#5-evo-and-hybrid)
6. [Skills and their classification](#6-skills-and-their-classification)
7. [Agent questions](#7-agent-questions)
8. [Review cycle](#8-review-cycle)
9. [Anti-pattern registry and quality gate](#9-anti-pattern-registry-and-quality-gate)
10. [Several features and several orchestrators](#10-several-features-and-several-orchestrators), including phased mode
11. [Responsibilities per agent](#11-responsibilities-per-agent)
12. [Artifacts and state](#12-artifacts-and-state)
13. [Design principles](#13-design-principles)

## 1. Building blocks

```mermaid
flowchart TB
    P(["Programmer"])

    subgraph Session["Claude Code session, the main conversation"]
        O["Orchestrator<br/>SKILL.md"]
    end

    subgraph Skill["Skill library: skills/feature/, read on demand"]
        W["workflows/<br/>direct · sdd · evo"]
        PR["protocols/<br/>decisions · agent-questions · context-handoff<br/>executor · skills · review-cycle · anti-pattern-registry<br/>multi-feature · hierarchy · orchestrator-memory"]
        R["roles/<br/>repository-analyst · spec-writer · planner<br/>implementer · tester · reviewer · verifier"]
        K["knowledge/ (guides)<br/>edge-cases · specification-guide · code-quality · design-patterns<br/>testing-techniques · e2e-testing · anti-patterns/*"]
        T["templates/<br/>specification · implementation-plan · testing-plan<br/>intent · decision-record · handoff · state · final-report · feature-card"]
        S["scripts/quality_gate.py"]
    end

    subgraph Agents["Subagents, one per task, launched by the orchestrator"]
        A1["Repository Analyst"]
        A2["Specification Writer"]
        A3["Planner"]
        A8["Test Designer"]
        A4["Implementer"]
        A5["Tester"]
        A6["Clean Code Critic"]
        A7["Finding Verifier"]
        A9["Specialists<br/>security · ux-ui · database · network ·<br/>performance · observability · your own"]
    end

    subgraph Repo["Project repository"]
        WT["Feature worktree<br/>.claude/worktrees/&lt,slug&gt, on its own branch<br/>code + feature folder with artifacts"]
        Q[".quality/<br/>config.json · anti-patterns.md · rules/"]
        G["git common dir: feature-workflow/<br/>memory.md · claims/"]
    end

    P <-->|"requests, answers, decisions"| O
    O -->|"reads the step it needs"| W & PR & T
    O -->|"brief: role file + handoff (new agent) + task"| Agents
    Agents -->|"read their role file and knowledge"| R & K
    Agents -->|"summary, STATUS, questions"| O
    O -.->|"resumes with answers via SendMessage"| Agents
    A4 & A6 -->|"run"| S
    Agents -->|"absolute paths, no isolation"| WT
    Agents -->|"read"| Q
    O -->|"memory, claims"| G
```

| Block | What it is | Source |
| --- | --- | --- |
| **Programmer** | Makes every consequential decision: requirements, scope, architecture, dependencies, trade-offs, acceptance, integration. | `SKILL.md` §1 |
| **Orchestrator** | The main session after `/feature`, in orchestrator role. The only party that talks to the programmer. It parses requests, creates worktrees, briefs subagents, verifies what they return, relays their questions, presents gates and records decisions. It writes no production code. | `SKILL.md` |
| **Executor** | The main session after `/feature`, in executor role: it does one feature's work itself; only the critic (with its verifier at R2) and audits are subagents, and in SDD the Test Designer is a session the programmer opens. | `protocols/executor.md` |
| **Subagents** | Claude Code built-in subagents (`Explore`, `Plan`, `general-purpose`) with a model chosen per task. Each one is pointed at its role file and never delegates further. | `SKILL.md` §4 |
| **Skill library** | Markdown files read only when a step needs them (progressive loading), plus one script. Knowledge and specialists are classified skills, extensible per user, repository and module (§6). | `SKILL.md` §3, `protocols/skills.md` |
| **Feature worktree** | One git worktree and branch per feature. Code and artifacts travel together on that branch. | `SKILL.md` §2.3 |
| **`.quality/`** | The project's quality configuration and anti-pattern registry. It outlives features. The programmer chooses at bootstrap whether it is versioned (`<repo>/.quality/`) or local to the clone (`<git-common-dir>/quality/`). | `protocols/anti-pattern-registry.md` |
| **Git common dir** | Shared by every worktree and never committed: the orchestrator's project memory and the feature claims. | `protocols/orchestrator-memory.md`, `protocols/hierarchy.md` |

## 2. Entry points and modes

```mermaid
flowchart LR
    C1["/feature &lt;request&gt; [--direct|--sdd|--evo] [--orchestrate|--execute]"] --> REC["Recommend a workflow,<br/>ask the role"]
    REC --> M1["Orchestrator<br/>one or several features, any workflow each"]
    REC --> M7["Executor<br/>one feature, this session works"]
    M7 -.->|"SDD: Test Designer"| C8["/feature role test-designer &lt;slug&gt;<br/>a session the programmer opens"]
    C2["/feature resume &lt;slug&gt;… · status · continue &lt;answer&gt;"] --> M1
    C3["/feature in several sessions"] --> M2["Independent sessions<br/>orchestrators or executors, coordinated through claims"]
    C4["/feature hub"] --> M3["Principal orchestrator"]
    C5["/feature join &lt;hub&gt; &lt;group&gt;"] --> M4["Sub-orchestrator of one group"]
    M3 <-->|"STATUS · DECISION-REQUEST · DECISION<br/>QUESTION · ANSWER · OVERLAP · DONE"| M4
    C6["/feature-kit [module…] | list | off"] --> M5["No workflow: skills loaded on demand<br/>for hand-driven work"]
```

| Workflow | Orchestrator | Executor |
| --- | --- | --- |
| **DIRECT** | One Implementer subagent runs the edge-case checklist, writes code and tests, and reports; the orchestrator relays blocking questions and runs integration | The session does it in the current checkout (or a worktree if asked). No gates before integration; a critic only if asked |
| **SDD** | Every role is a subagent (§4) | The session specifies, plans, implements and tests. The Test Designer runs in a session the programmer opens, so it never sees the plan. Critic and audits are subagents |
| **EVO** | Every role is a subagent (§5) | The session runs the increments with one card; gates 3 and 5 are merged. The review at the validated level and the audits are subagents, per increment ([`executor.md`](executor.md)) |

| Command | Effect |
| --- | --- |
| `/feature refine <request>` | Refines a request with the programmer without starting a feature; saves the record locally for `/feature refined <slug>`. |
| `/feature <request>` | Checks whether the request is ready and refines it if not, recommends a workflow with its evidence, asks the role, and starts. In an orchestrating session, adds to the portfolio; features in progress are never reset. |
| `/feature role <role> <slug>` | A session that runs one role of an executor's feature, from the brief the executor wrote. |
| `/feature resume <slug>…` | Continues features from their `state.md` or card, after a freshness check. |
| `/feature status` | Board of every feature in progress, plus the ones other sessions claim. |
| `/feature continue <answer>` | A fresh session answers a pending gate, using `memory.md` and `decisions/` on disk. |
| `/feature hub`, `/feature join <hub> <group>` | Hierarchical mode (§10). |
| `/feature correct` | Correction sweep: classes of repeated mistakes, enforced at the level the programmer chooses (§9). |
| `/feature verify-skill app\|formal [<target>]` | Generates a repository verification skill (§6). |
| `/feature-kit` | Separate skill. It exposes the roles and skills as modules (edge-cases, explore, spec, plan, decide, quality/ponytail, patterns, antipatterns, test, e2e, gate, review, writing, measure, correct, verify-skill, formal-skill, card, specialists) plus the programmer's, repository's and modules' own skills, without phases, gates, artifacts or worktrees. Only `review` launches subagents. |

`feature-kit` has `disable-model-invocation: true`: it loads only when the programmer types the command. `feature` does not, so Claude can launch it when the programmer explicitly asks for a feature; its description says never on its own initiative.

## 3. Startup of a feature

Source: `SKILL.md` §2.

```mermaid
flowchart TB
    S0["0 · Read project memory<br/>git-common-dir/feature-workflow/memory.md"] --> S1["1 · Parse the request<br/>new · role · resume · status · continue · hub · join"]
    S1 --> CL{"Claim held by another<br/>live session?"}
    CL -->|"yes"| STOP["Do not touch the feature,<br/>report to the programmer"]
    CL -->|"no"| S2["2 · Project context<br/>from memory, or CLAUDE.md / README / commands,<br/>Repository Analyst if many files"]
    S2 --> S4["4 · Skill index<br/>frontmatter of library, user, repo and module skills"]
    S4 --> R5{"5 · Request ready?<br/>problem, observable outcome,<br/>one reading, context at hand"}
    R5 -->|"no"| RF["Refine with the programmer<br/>problem · context gaps · readings<br/>→ consolidated intent v1 + verdict"]
    R5 -->|"yes, or --no-refine"| S5
    RF --> S5{"Workflow chosen<br/>by a flag?"}
    S5 -->|"no"| S5b["Assess each dimension with evidence,<br/>RECOMMEND a workflow and a gate profile,<br/>the programmer validates"]
    S5 -->|"yes"| S6
    S5b --> S6{"6 · Role chosen<br/>by a flag?"}
    S6 -->|"no"| S6b["Question: orchestrator or executor"]
    S6 -->|"yes"| S3
    S6b --> S3["3 · Worktree<br/>orchestrator: create, record, leave it<br/>executor: create and stay (DIRECT: checkout unless asked)"]
    S3 --> S7["7 · Load the workflow file<br/>direct.md · sdd.md · evo.md"]
```

- **Refinement** (`protocols/refinement.md`) runs before the recommendation when the request is not ready: it names a solution without its problem, its outcome is not observable, several readings survive, or it needs context only someone else has. The session restates the request as a problem, finds what the repository can answer, asks the rest from fixed dimensions, offers two or three readings plus the smallest version, and stops when the programmer confirms version 1 of the intent. It runs in every gate profile (one round in `auto`). `/feature refine` runs it alone, without starting a feature.
- **Dimensions** for the workflow recommendation, assessed on the refined intent when refinement ran: requirement clarity, functional uncertainty, technical feasibility, architectural uncertainty, expected discoveries, need for prototypes, risk and reach. The role is a question; as with every decision, the agent may recommend one, labeled.
- **Gate profile** (`protocols/gates.md`), recommended with the workflow: `full` (every gate) for likely Critical features, `key` (the default) for SDD and EVO, `auto` for DIRECT. Per-gate changes with `--gates key,+increment,-intent`.

| Gate | `full` | `key` | `auto` |
| --- | --- | --- | --- |
| `intent` (spec approval, intent gate) | stops | stops | agent |
| `specialists` | stops | agent: mandatory and `--with` run | agent |
| `bootstrap` (registry) | stops | stops | agent: local registry only |
| `approach` | stops | stops when options differ in API, data, dependencies or shared structure | agent |
| `depth` (testing plan, mutation, review level, E2E harness) | stops | agent: defaults; review level per `protocols/gates.md` §When a gate is off | same |
| `increment` (EVO) | stops | report and continue, unless a gate still on or a stop in `protocols/gates.md` applies | same, as a catch-up (`SKILL.md` §5) |
| `defects` | stops | Implementer fixes the critic's and the Tester's Blocker and Major the programmer's words cover (test first when the fix changes behavior); audit findings (a security Blocker always stops) and the rest to acceptance (cap with one open: stop, `protocols/review-cycle.md` §Round cap) | same |
| `discoveries` | stops | stops when outside or contradicting the intent | agent: covered ones fixed, outside ones not built, listed; contradicting: stops |
| `candidates` | stops | at acceptance | listed only |
| `acceptance` | stops | stops | stops |

A gate that is off is decided by the agent with its recommendation, recorded as *Decided by agent* and listed in the final report; in `auto`, a choice between rules the author wrote goes to the programmer instead (`protocols/gates.md` §When a gate is off). What always stops, in every profile, is listed in `protocols/gates.md` §Hard stops. Questions are always allowed.

- **Worktree failures** (not a git repository, a git error, already inside a worktree session) stop the feature and are presented to the programmer. The orchestrator never falls back to the shared checkout.

## 4. SDD

For well-understood features. Source: `workflows/sdd.md`. ⛔ is a human gate: it stops this feature only, and other features keep moving.

```mermaid
flowchart TB
    subgraph F1["Phase 1 · Specification"]
        U["1 · Understand<br/>orchestrator starts intent.md (request verbatim),<br/>Repository Analyst inspects the area"] --> SP["2 · Specify<br/>Specification Writer drafts specification.md,<br/>its questions are relayed until STATUS: DONE,<br/>orchestrator checks the draft, asks criticality"]
        SP --> G1{"⛔ 3 · Spec gate<br/>programmer approves"}
    end
    subgraph F2["Phase 2 · Implementation"]
        AN["4 · Analyze<br/>architecture, folders, tests, E2E and quality tooling,<br/>registry bootstrap if no .quality/"] --> PL["5 · Plan + design tests, in parallel<br/>Planner: options and outlines<br/>Test Designer: testing-plan.md from the spec only"]
        PL --> G2{"⛔ 6 · Plan gate<br/>approach · testing plan · mutation testing ·<br/>review level recommended and validated · E2E harness"}
        G2 --> IM["7 · Implement<br/>Implementer: production code only, self-review,<br/>quality gate, report, handoff if the Tester is new"]
        IM -->|"plan invalid or deviation"| G2b{"⛔ Deviation gate"}
        G2b --> IM
    end
    subgraph F3["Phase 3 · Testing and validation"]
        TE["8–11 · Test<br/>Tester: implements the designed cases, functional, E2E,<br/>exploration, mutation if decided, validation report"]
        RV["Review at the validated level<br/>what each level runs, the round limit and the stop rule:<br/>protocols/review-cycle.md<br/>+ specialist audits chosen"]
        TE & RV --> G3{"⛔ Defects and anti-pattern candidates gate<br/>fix now · accept as limitation · change spec"}
        G3 -->|"fix"| FX["Implementer (resumed or relayed, SKILL.md §4): makes the Tester's failing test pass<br/>→ Tester re-runs (resumed or relayed, SKILL.md §4) → new clean critic per the review level"]
        FX --> G3
    end
    subgraph F4["Phase 4 · Finalization"]
        FR["12 · Final report, from evidence only"] --> G4{"⛔ 13 · Acceptance"} --> G5{"⛔ 14 · Integration<br/>merge · rebase · PR · leave unmerged"} --> G6{"⛔ 15 · Cleanup<br/>remove worktree and branch?"}
    end
    G1 --> AN
    IM --> TE & RV
    G3 -->|"no open defects"| FR
```

**Definition of done** (checked before acceptance):
- Spec and plan are approved.
- The scope matches, and any deviation is approved.
- Every acceptance criterion has evidence.
- E2E and every black-box technique have a status.
- The quality gate passes, or each remaining violation has a decision.
- Anti-pattern candidates were presented.
- Mutation testing and review ran as decided.
- Regressions were evaluated, and no blocking issue is hidden.

## 5. EVO and Hybrid

For features with open requirements or technical unknowns. Source: `workflows/evo.md`. **There is no specification:** the intent record (`intent.md`), the programmer's decisions (`decisions/`) and the designed cases (`testing-plan.md`, the executable criteria) carry what the feature must do, increment by increment, main flows first.

```mermaid
flowchart TB
    P1["Phase 1 · Intent<br/>intent.md, analyst and nearest analog,<br/>reach of broad statements, main flows"] --> G1{"⛔ Intent gate<br/>consolidated intent v1, blocking questions only,<br/>criticality, completion criteria"}
    G1 --> P2["Phase 2 · Approach<br/>Planner: approaches, prototypes as options<br/>Test Designer: cases of the first flow, from the intent"]
    P2 --> G2{"⛔ Approach gate<br/>approach · first increment · verification depth<br/>(again only when the approach is in question)"}
    G2 --> INC["Increment: entry written by the orchestrator<br/>flow · hypotheses · edge cases covered or deferred (D-ID)"]
    INC --> P3["Implement the increment<br/>a blocking discovery stops it (⛔), the rest wait"]
    P3 --> P4["Test and review the increment<br/>Tester, E2E, black-box statuses, critic on its diff"]
    P4 --> G4{"⛔ Increment gate, the only one<br/>results, findings, discoveries, hypotheses,<br/>deferred edge cases, new consolidated intent, next increment"}
    G4 -->|"next increment"| EV["Evolve<br/>consolidate the intent, update the plan,<br/>Test Designer designs cases; see roles/test-designer.md for cases that depend on a change"]
    EV --> INC
    G4 -->|"approach in question"| G2
    G4 -->|"completion criteria met"| P6["Finalization<br/>mutation testing once · short final report<br/>⛔ acceptance · ⛔ integration · ⛔ cleanup"]
```

- **Leaner by design:** one gate per increment, the Planner only at the start and when the approach is in question, mutation testing once at the end, `handoff.md` only when a new agent takes over a phase (relay notes instead for a new agent of a role that already ran: `protocols/context-handoff.md` §Relay; resume state in `state.md`), and a short final report that links the intent, the cases and the decisions.
- **Hypotheses** are the team's, kept in the plan's *Increments* with their status (Hypothesis, Under exploration, Confirmed, Rejected) and evidence. The programmer's words stay in the intent record.
- **Deferred edge cases** need a programmer decision naming the increment that will cover them; they never accumulate silently.
- **Prototypes** live outside production paths. They are discarded unless the programmer promotes them.
- **Hybrid:** SDD for the feature as a whole, with a specification; Phases 2–4 apply only to the uncertain area, marked *Under exploration*, until it can be specified.

## 6. Skills and their classification

Source: `protocols/skills.md`. Every piece of knowledge is a skill whose frontmatter says where it can be used.

| Field | Values |
| --- | --- |
| `kind` | `guide`: read by whoever does the phase · `specialist`: runs as its own agent in its phases |
| `use-in` | `intent` · `spec` · `plan` · `test-design` · `implement` · `test` · `review` · `audit` · or `general` |
| `workflows` | `direct` · `sdd` · `evo` (all when omitted) |
| `signals` | paths, terms, trust boundaries that make it relevant |
| `mandatory-when` | `critical` for specialists that must run on Critical features |

```mermaid
flowchart LR
    L1["library<br/>skills/feature/knowledge · specialists"] --> L2["~/.claude/feature-skills/<br/>the programmer's"] --> L3["git-common-dir/feature-skills/ · repo/.claude/feature-skills/<br/>the repository's: local or versioned"] --> L4["module/.claude/feature-skills/<br/>active when the feature touches the module"]
    L4 --> IX["Index: frontmatter only<br/>same name: the more specific wins"]
    IX --> PH["Each phase: guides whose use-in covers it,<br/>listed by path in the agent's brief"]
    IX --> SP["Specialists: signals → facts at the first gate →<br/>the programmer chooses phases"]
```

- **Library classification:** `edge-cases` general; `writing` general; `specification-guide` intent, spec, test-design; `code-quality` plan, implement, test, review; `design-patterns` plan, implement; `measurement` plan, test, review, audit (by signals); `testing-techniques` test-design, test; `e2e-testing` test-design, test; the six specialists in their phases.
- **Generated skills** (`protocols/verification-skills.md`): `/feature verify-skill app` writes `verify-<app>` (launch, doctor, drive, evidence, cleanup, feature map; test-design, test, review); `/feature verify-skill formal` writes `formal-<area>` (a property checked by a model checker or verifier, with its coverage record and sync commit; plan, test, review). Each is proven once before handover, and checked for drift when a diff touches its paths.
- **DIRECT** has no phases: it loads skills on demand; `--no-skills` leaves only the edge-case checklist.
- **Why not `.claude/skills/`:** Claude Code loads those descriptions into every session; these folders load only when the workflow runs.

## 7. Agent questions

Subagents cannot talk to the programmer, so they ask through the orchestrator. Source: `protocols/agent-questions.md`.

```mermaid
sequenceDiagram
    autonumber
    actor P as Programmer
    participant O as Orchestrator
    participant A as Agent (e.g. Specification Writer)
    participant D as Disk, intent.md · spec §Open questions · decisions/ · state.md

    O->>A: Brief (role file, handoff if new, task)
    A->>A: Check repo and artifacts first
    A-->>O: STATUS: QUESTIONS + work so far + Q-1..Q-n
    O->>O: Answer from evidence what it can, strip any steering
    O->>D: Record questions as Pending, agent ID in state.md
    O->>P: ⛔ [slug] Q-n (Spec Writer), batched, with recommendations
    P->>O: Answers
    O->>D: Record answers (words, date) · Answered / Deferred
    O->>A: SendMessage: answers by Q-ID, "continue from where you stopped"
    A-->>O: STATUS: DONE (or new questions, numbered on)
```

- **Blocking** questions are the ones whose answer changes the agent's output: a requirement, scope, observable behavior, a constraint, the viable approaches, or a test's expected result. The agent stops and does not guess. A question that changes the output for a valid input is always blocking, and the agent never weakens an acceptance criterion to avoid it.
- **Non-blocking** questions: the agent continues under an assumption labeled Hypothesis and lists it. The question goes to the next gate.
- **If the agent cannot be resumed** (a new session or an error), a new agent takes over through a relay (`protocols/context-handoff.md` §Relay) with the earlier "work so far" and the answers.
- **Answers that change approved work** become a spec version bump or a decision record. Approved work never changes silently.
- **Critics and verifiers never ask:** they report ambiguity as a finding.

## 8. Review cycle

Source: `protocols/review-cycle.md`. The orchestrator **recommends** the level with evidence, and the programmer validates it. 

| Level | What runs | Typical feature |
| --- | --- | --- |
| R0 | Quality gate and project lint only | Mechanical change, about 50 changed lines, no risk areas |
| R1 | One clean critic, in parallel with the Tester | Standard feature with new logic |
| R2 | The cycle in `protocols/review-cycle.md` §R2 · The cycle | Critical, or large or complex |

```mermaid
flowchart LR
    C["Critic round n<br/>new agent, clean context:<br/>code + diff + conventions + registry only"] --> V["Verifier round n<br/>new clean agent: tries to refute<br/>VALID · INVALID · AMBIGUOUS<br/>fix class: behavior-preserving or changing"]
    V -->|"VALID + behavior-preserving<br/>Blocker/Major/Minor"| I["Implementer fixes<br/>tests + quality gate"]
    V -->|"behavior-changing · AMBIGUOUS ·<br/>correctness or security Blockers"| G{"⛔ Defects gate"}
    V -->|"Nits"| FRP["Final report"]
    I --> STOP{"Stop?<br/>stop rule in<br/>protocols/review-cycle.md"}
    STOP -->|"no"| C
    STOP -->|"cap with Blocker/Major open"| H{"⛔ Programmer<br/>(§Round cap)"}
    STOP -->|"yes"| RT["Tester re-runs affected<br/>regression and E2E"]
```

- **Cap reached with a Blocker or Major open** (`protocols/review-cycle.md` §Round cap): the feature stops and asks the programmer, in every profile. Commits made after the last round reach acceptance marked unreviewed (`protocols/review-cycle.md`).

- **Review level:** the default, the recommendation and what a standing "accept your recommendation" covers are in `protocols/review-cycle.md` §Review levels; with the `depth` gate off, `protocols/gates.md` §When a gate is off decides.
- **Automatic fixes** happen only at R2, except that with the `defects` gate off the Implementer (resumed or relayed, `SKILL.md` §4, *Reusing agents*) fixes the critic's and the Tester's covered Blocker and Major at any level (`protocols/gates.md`). Each one is listed at the next gate with its hunks and a revert option. The orchestrator never changes code itself (`SKILL.md` §1, principle 9).
- **Convergence:** what each round reviews and reports is in `protocols/review-cycle.md` §R2 · The cycle.
- **Clean context:** the critic and the verifier never read the spec, plan, decisions, handoffs, implementation report or earlier rounds. Each round launches a **new** critic.
- **Round log** in `reports/review/rounds.md`. Findings that recur become anti-pattern candidates. The INVALID rate shows how noisy the critic is.
- **Why it is built this way:** self-attribution and self-preference bias in LLM evaluators, adversarial refutation, and diminishing returns after three or four repair iterations. The papers are cited in [`references.md`](references.md).

## 9. Anti-pattern registry and quality gate

Sources: `protocols/anti-pattern-registry.md`, `knowledge/code-quality.md`, `scripts/quality_gate.py`.

```mermaid
flowchart LR
    B["Bootstrap (⛔)<br/>seed catalogs matching the architecture:<br/>general · feature-folders · layered ·<br/>frontend-ui · backend-api · tests"] --> REG[".quality/anti-patterns.md<br/>+ config.json limits + rules/"]
    REG -->|"read before coding / reviewing"| IMP["Implementer · Critic · Planner"]
    IMP -->|"new occurrences"| CAND["reports/anti-pattern-candidates.md"]
    CAND --> GATE{"⛔ Candidates gate<br/>approve · reject · automate"}
    GATE -->|"approved"| REG
    GATE -->|"enforce at a level"| RULE["architecture · types · check (ast-grep, Semgrep,<br/>import rules, linter) · test · review"]
    RULE --> REG
```

**Enforcement levels** go from making the mistake impossible (architecture, types) to catching it (a check, a test) to describing it (review); the programmer chooses per entry, and each new check is proven on a real past occurrence. The programmer's own corrections become candidates. `/feature correct` sweeps commits, reverts and review comments for classes of repeated mistakes (two occurrences make a class) and enforces the chosen ones, one commit each.

The **quality standard** applies to every agent that writes code:
- **Smallest complete change:** reuse what exists, then the standard library, then an installed dependency, then the minimum new code.
- **No comments,** except `shortcut: <limit>, <when to upgrade>` markers and tool directives.
- **Limits as signals of mixed responsibilities:** file ≤ 400 lines, function ≤ 30, parameters ≤ 4, cyclomatic complexity ≤ 10, nesting ≤ 3.
- **Structure:** declarative names, single responsibility, feature folders when the project already uses them (the existing structure wins), and patterns only for problems present now.
- **Root causes:** reproduce, ask whether the triggering state is legitimate (if not, a guard hides the bug), fix the pattern; after two failed fixes with one premise, write the premise down and test it before a third.
- **Design principles:** model the domain in data structures, data shape before logic, validation only at boundaries, subtract before adding.

The **quality gate** checks only the feature's changes against its base:
- file length, flagged only for files that are new or grew;
- full-line comments;
- function size and complexity with `lizard` if it is installed;
- the project's checks from `config.json`.

## 10. Several features and several orchestrators

Sources: `protocols/multi-feature.md`, `protocols/hierarchy.md`, `protocols/orchestrator-memory.md`.

```mermaid
flowchart TB
    P(["Programmer"]) <--> H["Principal orchestrator<br/>/feature hub<br/>groups, statuses, request queue, overlaps,<br/>no feature detail, no feature roles"]
    H <-->|"messages: agent team · separate sessions · subagents"| SA["Sub-orchestrator: group A"]
    H <--> SB["Sub-orchestrator: group B"]
    SA --> FA1["feature a1<br/>worktree + agents"] & FA2["feature a2"]
    SB --> FB1["feature b1"]
    CL[("claims/&lt,slug&gt,.json<br/>in the git common dir")] -.- SA & SB & H
```

- **Single orchestrator, several features:**
  - Each feature has its own workflow, gates, artifacts and agents.
  - A gate in one feature never blocks another.
  - Agents of the same phase launch together across features.
  - Overlapping files between features are reported early, as facts.
- **Independent sessions** see each other only through claims. Two orchestrators never run the same feature.
- **Hierarchy:**
  - The principal is the programmer's only channel.
  - Each gate of a sub-orchestrator travels up as a `DECISION-REQUEST`.
  - The queue is ordered by how much work a request blocks, then by arrival.
  - The principal never prioritizes features: that stays the programmer's decision.
### Specialists

Source: `protocols/skills.md`.

```mermaid
flowchart LR
    IX["Specialists in the skill index<br/>library → user → repo → module<br/>(same name: the more specific wins)"] --> SG["Signals matched<br/>paths · spec terms · trust boundaries"]
    SG --> G{"⛔ First gate<br/>matching specialists as facts,<br/>you choose who runs in which phase"}
    G --> S1["spec phase<br/>questions on the draft"]
    G --> S2["plan phase<br/>facts per option; a labeled recommendation<br/>for its own domain only"]
    G --> S3["test-design phase<br/>cases in testing-plan.md"]
    G --> S4["audit phase<br/>clean, opus, executed evidence"]
    S1 & S2 --> GA{"⛔ Spec and plan gates"}
    S4 --> GD{"⛔ Defects / findings gate<br/>merged with the critic, by domain"}
```

- **Two kinds:** advisors (`spec`, `plan`, `test-design`) can be resumed; auditors are always new, never fixed automatically, and re-run on the fix diff after a fix.
- **Mandatory specialists:** a specialist declares `mandatory-when: critical` in its file to run on every Critical feature its signals match. The built-in `security` specialist does.
- **Re-check:** signals are checked again against the real diff before verification, so a specialist that now matches is offered again.

### Phased mode (optional, experimental)

Source: `protocols/phase-runners.md`. Unphased mode is the default.

```mermaid
flowchart LR
    P(["Programmer"]) <--> O["Orchestrator<br/>startup, intent.md, gates from disk,<br/>question relay, portfolio, integration"]
    O -->|"brief: phase, steps, decisions in force"| PR["Phase runner<br/>one per feature and phase,<br/>stops at the first gate that is on,<br/>or at the end of its range"]
    PR -->|"briefs, verifies, relays questions"| RO["Role agents of that phase"]
    PR -->|"Pending decisions, state.md"| DK[("feature folder")]
    PR -->|"PHASE … ended at GATE · DONE · QUESTIONS · FAILED"| O
    O -->|"reads the gate from disk + consistency check"| DK
```

- **Phases:** SDD has Specification, Planning, Build and Fixes. EVO has Intent, Approach, Increment and Evolution.
- **Experimental, never run.** By design the decisions are the same: the runner cannot reach the programmer, so it must stop at each gate that is on. That has not been tested.
- **What changes:** you see results at the gates instead of agent by agent, and you can stop a whole runner but not steer it mid-phase.

- **Project memory** (`memory.md`, ≤ 80 lines) carries the project context and the portfolio across sessions. Before every stop, pending decisions are written to `decisions/` with their option labels, so an answer like "B" still resolves in a fresh session.

## 11. Responsibilities per agent

Standard executor and model. The orchestrator picks the cheapest sufficient model for each delegation, within the floors, and logs it in `delegations.md`.

| Agent | Executor · standard model | Responsible for | Reads | Writes | Never |
| --- | --- | --- | --- | --- | --- |
| **Orchestrator** | main session | Talking to the programmer, worktrees, workflow recommendation and role, the intent record `intent.md` (original request, consolidated intent confirmed at each gate, statements since), briefs, verifying returns, relaying questions, gates, decision records, handoffs between phases, delegation log, final report, integration and cleanup on approval | Only the skill files the current step needs; artifacts; reports | `intent.md`, `decisions/`, handoffs whose outgoing role writes none (read-only roles, Request → Specification, Specification or Intent → Planning and Test design), `state.md`, `delegations.md`, `reports/review/rounds.md`, `final-report.md`, `memory.md`, claims | Hide a recommendation in the order or wording of options, write production code, approve on the programmer's behalf at a gate that is on, integrate or delete without confirmation |
| **Repository Analyst** | `Explore` · haiku (sonnet for large or unfamiliar code) | Evidence for one task: components, dependencies, conventions, existing behavior, tests and commands, architecture style, quality and E2E tooling; observed vs inferred | The feature worktree, only what the brief needs | Nothing: returns a context report of about 600 words | Recommend approaches, assume a stack without evidence, modify files |
| **Specification Writer** | `general-purpose` · opus (sonnet for short, clear requests; never haiku) | Turning the request into the current reading of its intent (not a closed contract): the source version of the intent record, the reach of its broad statements, FR/NFR, constraints, invariants, Given/When/Then criteria, what is outside the intent (and who drew each boundary) and open questions, each item traced to a source; Hybrid statuses; applying approved spec changes. Not used in EVO | `intent.md`, handoff, the specification guide and template, the repository (read-only) | `specification.md` (Draft) | Invent requirements, resolve ambiguity, include implementation details, write vague criteria to avoid a question |
| **Planner** | `Plan` · opus (sonnet for one mechanical approach; never haiku) | The solution space: viable approaches in the decision format, per-option outlines that follow the quality standard, the E2E harness, other decisions needed, excluded options with the constraint they violate | Handoff, spec sections, code, registry | Nothing: returns the decision block | Choose, rank, change requirements, add speculative abstractions |
| **Test Designer** | `general-purpose` · sonnet (opus if Critical; never haiku) | Test cases derived from the approved spec alone, in parallel with the Planner: each technique applied or justified, error, security, worst-case and E2E cases, traceability from every AC to its cases | Spec, analyst report, testing techniques, E2E guide (never the plan or code) | `testing-plan.md` | Invent expected results, design around an implementation, write test code |
| **Implementer** | `general-purpose` · sonnet (haiku if mechanical, opus if risky) | Production code for the approved plan only, to the quality standard. Self-review against the critic's checklist before the quality gate, so review finds little to rework. Runs the existing tests; **writes no tests** (exceptions: DIRECT, a fixture or helper the plan assigns, an anti-pattern entry's check or test). Makes the Tester's reproducing tests pass when resumed for fixes. Copies of the rules it touches and verification after committing: `roles/implementer.md` §Rules touched and verification. | Handoff, plan, testing plan, quality standard, design patterns, registry | Production code, `implementation-report.md`, handoff to testing (new Tester only), DIRECT report | Write tests (outside those exceptions), drift from the plan silently, add comments, leave quality violations unreported, expand scope |
| **Tester** | `general-purpose` · sonnet (haiku for re-runs, opus for hard state) | The author of the tests (except the Implementer's exceptions): implements every designed case, runs functional, regression and E2E testing, explores beyond the plan, mutation testing if decided, validation against the spec. Keeps failing tests as reproductions for fixes. Resumed to re-run after fixes. | Handoff, testing plan, spec, testing techniques, E2E guide | Tests, case statuses in `testing-plan.md`, `reports/e2e/`, `validation-report.md`, handoff (new agent only) | Change a designed expected result, decide one the spec leaves open, weaken or skip failing tests, report a test it did not run as passed |
| **Clean Code Critic** | `general-purpose` · opus (never haiku) | Maximally critical review from scratch: names, responsibilities, function design, structure, patterns misused, registry violations, places the request's words reach that the diff leaves untouched; each finding with a concrete case | The original request and the programmer's statements, verbatim; code, `git diff <base>`, project conventions, quality standard, registry | `reports/review/round-<n>-critic.md` (EVO: `inc<k>-round-<n>-critic.md`) | Read the spec, plan, handoffs or earlier rounds; be reused across rounds |
| **Phase runner** (phased mode) | `general-purpose` · sonnet (opus if Critical; never haiku) | Orchestrating one phase of one feature: delegating its steps, choosing models, verifying returns, relaying agent questions, writing the gate's Pending decisions | Its brief, `SKILL.md` §4, the workflow steps in range, skills and agent-questions protocols | `delegations.md`, `decisions/` (Pending), `state.md` | Talk to the programmer, pass a gate, run startup or integration, be reused for the next phase |
| **Finding Verifier** | `general-purpose` · sonnet (never haiku) | Trying to refute each finding against the code: VALID, INVALID or AMBIGUOUS; fix class; recurring findings marked as candidates | The critic's report, the code | `reports/review/round-<n>-verification.md` (EVO: `inc<k>-round-<n>-verification.md`) | Read the spec or plan, fix code, accept a finding without checking it |
| **Specialists** | `general-purpose` · sonnet in `spec`/`plan`/`test-design`, opus in `audit` (never haiku there) | Domain expertise in the phases you activate: questions on the spec draft, facts per plan option (a recommendation only for its own domain, labeled), test cases, and a clean audit with executed evidence (exploit, query plan, timing, screenshot) | Advisory phases: request, spec, options. Audit: the diff and the code it reaches only | Questions, facts, cases in `testing-plan.md`, `reports/review/<name>.md` | Add requirements, recommend options outside its domain, report unproven findings as confirmed, install tools, be resumed in `audit` |

**Floors:** no haiku for specification, planning, test design, the critic, the verifier, a specialist's audit or a phase runner. Critical features use opus for specification, planning, test design, the critic, specialist audits and phase runners.

**Shared rules for every subagent:**
- **Location:** run without `isolation`. Confirm the feature branch first, and work through absolute paths (`cd <worktree> && …`). Never call `EnterWorktree`.
- **No delegation:** feature roles never spawn further agents.
- **Headless:** every subagent runs in the background. The programmer sees one line when an agent starts or finishes, and the full content only at gates.
- **Reuse:** when work returns to a role that already ran for the feature, the same agent is resumed with `SendMessage`, or a new agent of the same role takes over through a relay, as `SKILL.md` §4, *Reusing agents*, decides. In a relay the outgoing agent writes notes on what it explored, and the new one reads them plus the whole diff. Each agent's ID, model and last token count are recorded in `state.md`. Critics and verifiers are never resumed. The relay is in `protocols/context-handoff.md` §Relay.
- **Pause and stop:** the programmer can pause a feature or stop all its work at once, and `state.md` records what must be relaunched (`SKILL.md` §7).
- **Catch-ups in `auto`:** the programmer gets one at each phase or increment transition without asking (`SKILL.md` §5).
- **Orchestrator cost:** the orchestrator session compacts at the threshold the programmer sets and is recommended to run on sonnet (README §Cost settings).
- **Questions:** questions only the programmer can answer follow the agent-questions protocol. A blocking one stops the agent; it never guesses.
- **Return:** a `STATUS` line, a summary within the word limit, the questions, and any decision in the decision format.

## 12. Artifacts and state

```
<repo>/.claude/worktrees/<slug>/                 feature worktree, own branch
└── docs/features/<slug>/                        or the project's own convention
    ├── intent.md                orchestrator        original request + consolidated intent + statements since
    ├── intent-history.md        orchestrator        absorbed statements, by consolidation version
    ├── specification.md         Specification Writer  versioned; change log
    ├── implementation-plan.md   orchestrator        approved approach only
    ├── testing-plan.md          Test Designer (cases) · Tester (statuses)
    ├── decisions/D-NNN-*.md     orchestrator        Pending → decided, full option block
    ├── reports/
    │   ├── implementation-report.md   Implementer
    │   ├── validation-report.md       Tester
    │   ├── anti-pattern-candidates.md orchestrator (from agents)
    │   ├── e2e/                       Tester: traces, screenshots, logs
    │   ├── review/rounds.md · round-<n>-critic.md · round-<n>-verification.md (EVO: inc<k>-round-<n>-…)
    │   └── final-report.md            orchestrator
    ├── delegations.md           orchestrator        role · model · reason · outcome
    ├── handoff.md               outgoing agent      message to a new agent at a phase transition
    └── state.md                 orchestrator        resume state, written at every stop
    (EVO as executor: feature.md card, whose State replaces state.md, + review/ + decisions/; SDD as executor: no handoff.md or delegations.md; DIRECT: none unless asked)

<repo>/.quality/ or <git-common-dir>/quality/   project-wide registry, after the programmer's approval
<git-common-dir>/feature-workflow/memory.md      project memory, ≤ 80 lines, never committed
<git-common-dir>/feature-workflow/relay/<slug>/  relay notes, one per role, never committed (protocols/context-handoff.md §Relay)
<git-common-dir>/feature-workflow/claims/        one JSON per feature: who orchestrates it
```

**Handoffs** transfer knowledge, not conversation (`protocols/context-handoff.md`):
- **When:** in orchestrator mode only, at a phase transition whose incoming agent is new; a resumed agent gets a brief instead, and a new agent of a role that already ran gets relay notes (`protocols/context-handoff.md` §Relay). Resume state lives in `state.md` (the card's *State* in EVO as executor and in DIRECT with a card).
- **Transitions:** Request → Specification, Specification → Planning, Planning → Implementation, Implementation → Testing, Intent → Planning and Intent → Test design (EVO), Testing → Evolution (EVO), and Testing → Finalization. Each one has a checklist.
- **Content:** handoffs reference artifacts by path and section instead of copying them, and record freshness (commit, branch, dirty state, artifact versions).
- **Critics and verifiers** never read handoffs.

## 13. Design principles

1. **The programmer decides, and the agent's view is in the open.** No presentation of options is neutral, since the agent picks the options and the words. So every decision shows each viable option with facts instead of adjectives, the options left out and those excluded by a constraint, and a labeled recommendation with its reasons and the fact that would change it. Nothing proceeds by silence.
2. **Artifacts are the source of truth.** Any feature can be resumed in a new session from its folder (DIRECT only with a card).
3. **Separation of concerns:** spec (what and why) ≠ plan (how) ≠ implementation ≠ validation, and each feature is separate from every other.
4. **Explicit uncertainty and evidence:** claims carry a status. A test that was not run is never "passed".
5. **No silent drift:** deviations, scope changes and behavior changes go back to the programmer, at a gate or, when its gate is off, as `protocols/gates.md` §When a gate is off describes.
9. **Supervision is chosen per feature:** the gate profile sets how often the programmer is stopped; what is hard to undo always stops.
6. **Ask, don't guess:** gaps become questions relayed by the orchestrator, never invented requirements.
7. **Clean review:** whoever reviews code never saw it being written.
8. **Pay only for what is needed:** progressive loading, skills indexed by frontmatter, three workflows from DIRECT up, a model chosen per delegation, and batched launches and verification. Correctness still beats economy.
