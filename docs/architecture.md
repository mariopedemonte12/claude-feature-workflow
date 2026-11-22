# Architecture of the Feature Workflow

There are three entry points: `/feature-lean`, the main mode (§2), the full `/feature` workflow, and `/feature-kit`. Most of this document describes how the full `/feature` workflow is built: who takes part, how a feature moves from request to integration, which files hold the state, and what each agent is responsible for. The behavior itself is defined by the files under `skills/feature/`. When this document and those files disagree, the files win, and each section names the file it summarizes.

Diagrams use Mermaid and render on GitHub.

## Contents

1. [Building blocks](#1-building-blocks)
2. [Entry points and modes](#2-entry-points-and-modes)
3. [Startup of a feature](#3-startup-of-a-feature)
4. [SDD Direct](#4-sdd-direct)
5. [ESDD and Hybrid](#5-esdd-and-hybrid)
6. [Intensity levels](#6-intensity-levels)
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
        W["workflows/<br/>sdd-direct · esdd"]
        PR["protocols/<br/>neutral-decisions · agent-questions · context-handoff<br/>intensity · review-cycle · anti-pattern-registry<br/>multi-feature · hierarchy · orchestrator-memory"]
        R["roles/<br/>repository-analyst · spec-writer · planner<br/>implementer · tester · reviewer · verifier"]
        K["knowledge/<br/>specification-guide · code-quality · design-patterns<br/>testing-techniques · e2e-testing · anti-patterns/*"]
        T["templates/<br/>specification · implementation-plan · testing-plan<br/>intent · decision-record · handoff · final-report · feature-card"]
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
    O -->|"brief: role file + handoff + task"| Agents
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
| **Orchestrator** | The main session after `/feature`. The only party that talks to the programmer. It parses requests, creates worktrees, briefs subagents, verifies what they return, relays their questions, presents gates and records decisions. It writes no production code. | `SKILL.md` |
| **Subagents** | Claude Code built-in subagents (`Explore`, `Plan`, `general-purpose`) with a model chosen per task. Each one is pointed at its role file and never delegates further. | `SKILL.md` §4 |
| **Skill library** | Markdown files read only when a step needs them (progressive loading), plus one script. | `SKILL.md` §3 |
| **Feature worktree** | One git worktree and branch per feature. Code and artifacts travel together on that branch. | `SKILL.md` §2.3 |
| **`.quality/`** | The project's quality configuration and anti-pattern registry. It outlives features. The programmer chooses at bootstrap whether it is versioned (`<repo>/.quality/`) or local to the clone (`<git-common-dir>/quality/`). | `protocols/anti-pattern-registry.md` |
| **Git common dir** | Shared by every worktree and never committed: the orchestrator's project memory and the feature claims. | `protocols/orchestrator-memory.md`, `protocols/hierarchy.md` |

## 2. Entry points and modes

```mermaid
flowchart LR
    C1["/feature &lt,description&gt, [--sdd|--esdd] [--lite|--medium|--high]"] --> M1["Single orchestrator<br/>one or several features"]
    C2["/feature resume &lt,slug&gt,… · status · continue &lt,answer&gt,"] --> M1
    C3["/feature in several sessions"] --> M2["Independent orchestrators<br/>coordinated only through claims"]
    C4["/feature hub"] --> M3["Principal orchestrator"]
    C5["/feature join &lt,hub&gt, &lt,group&gt,"] --> M4["Sub-orchestrator of one group"]
    M3 <-->|"STATUS · DECISION-REQUEST · DECISION<br/>QUESTION · ANSWER · OVERLAP · DONE"| M4
    C7["/feature-lean &lt;description&gt; | resume &lt;slug&gt;"] --> M6["Lean pipeline: this session works,<br/>one clean critic subagent"]
    C6["/feature-kit [module…] | list | off"] --> M5["No workflow: modules loaded on demand<br/>for hand-driven work"]
```

| Command | Effect |
| --- | --- |
| `/feature <description>` | A new feature is added to the portfolio. Features already in progress are never reset. |
| `/feature resume <slug>…` | Continues features from their `handoff.md`, after a freshness check. |
| `/feature status` | Board of every feature in progress, plus the ones other orchestrators claim. |
| `/feature continue <answer>` | A fresh session answers a pending gate, using `memory.md` and `decisions/` on disk. |
| `/feature hub`, `/feature join <hub> <group>` | Hierarchical mode (§10). |
| `/feature-lean <description>` | Separate skill: one session, one feature, no orchestrator relay; the only artifacts are a card and the review. Steps below. |
| `/feature-kit` | Separate skill. It exposes the roles and knowledge as modules (explore, spec, plan, decide, quality/ponytail, patterns, antipatterns, test, e2e, gate, review, card) without phases, gates, artifacts or worktrees. Only `review` launches subagents: a clean critic and, if asked, a verifier. |

**`/feature-lean` steps** (detailed in [`lean.md`](lean.md)):
1. A specification pass covers edge, error, security and worst-case behavior. Each case states what the project's nearest existing analog does with it.
2. ⛔ Gate 1: questions and approach. Options carry their security consequence and their probed worst case.
3. Code and tests: every case, a status for each testing technique, and fuzz or property tests at trust boundaries. Then the quality gate.
4. One clean critic (opus), plus the specialist audits you chose (security mandatory if Critical and matching). Each finding is checked against the code.
5. ⛔ Gate 2: every finding, each with fix · accept · change behavior.
6. ⛔ Acceptance, integration and cleanup.

All three skills have `disable-model-invocation: true`: they load only when the programmer types the command.

## 3. Startup of a feature

Source: `SKILL.md` §2.

```mermaid
flowchart TB
    S0["0 · Read project memory<br/>git-common-dir/feature-workflow/memory.md"] --> S1["1 · Parse the request<br/>new · resume · status · continue · hub · join"]
    S1 --> CL{"Claim held by another<br/>live orchestrator?"}
    CL -->|"yes"| STOP["Do not touch the feature,<br/>report to the programmer"]
    CL -->|"no"| S2["2 · Project context<br/>from memory, or CLAUDE.md / README / commands,<br/>Repository Analyst if many files"]
    S2 --> S3["3 · Create the worktree<br/>EnterWorktree name=slug, record path, branch, base,<br/>ExitWorktree keep: the orchestrator stays outside"]
    S3 --> S4["4 · Intensity<br/>Lite · Medium · High, Critical forces High"]
    S4 --> S5{"5 · Workflow chosen<br/>by a flag?"}
    S5 -->|"no"| S5b["Assess uncertainty per dimension with evidence,<br/>present the workflows neutrally, the programmer chooses"]
    S5 -->|"yes"| S6
    S5b --> S6["6 · Load the workflow file<br/>sdd-direct.md or esdd.md"]
```

- **Uncertainty dimensions** for the workflow choice: requirement clarity, functional uncertainty, technical feasibility, architectural uncertainty, expected discoveries, need for prototypes. Feature size alone never decides.
- **Worktree failures** (not a git repository, a git error, already inside a worktree session) stop the feature and are presented to the programmer. The orchestrator never falls back to the shared checkout.

## 4. SDD Direct

For well-understood features. Source: `workflows/sdd-direct.md`. ⛔ is a human gate: it stops this feature only, and other features keep moving.

```mermaid
flowchart TB
    subgraph F1["Phase 1 · Specification"]
        U["1 · Understand<br/>orchestrator starts intent.md (request verbatim),<br/>Repository Analyst inspects the area"] --> SP["2 · Specify<br/>Specification Writer drafts specification.md,<br/>its questions are relayed until STATUS: DONE,<br/>orchestrator checks the draft, asks criticality"]
        SP --> G1{"⛔ 3 · Spec gate<br/>programmer approves"}
    end
    subgraph F2["Phase 2 · Implementation"]
        AN["4 · Analyze<br/>architecture, folders, tests, E2E and quality tooling,<br/>registry bootstrap if no .quality/"] --> PL["5 · Plan + design tests, in parallel<br/>Planner: neutral options and outlines<br/>Test Designer: testing-plan.md from the spec only"]
        PL --> G2{"⛔ 6 · Plan gate<br/>approach · testing plan · mutation testing ·<br/>review level R0/R1/R2 recommended and validated · E2E harness"}
        G2 --> IM["7 · Implement<br/>Implementer: production code only, self-review,<br/>quality gate, report, handoff"]
        IM -->|"plan invalid or deviation"| G2b{"⛔ Deviation gate"}
        G2b --> IM
    end
    subgraph F3["Phase 3 · Testing and validation"]
        TE["8–11 · Test<br/>Tester: implements the designed cases, functional, E2E,<br/>exploration, mutation if decided, validation report"]
        RV["Review at the validated level<br/>R1 critic in parallel · R2 cycle<br/>max 3 critic rounds per feature<br/>+ specialist audits chosen"]
        TE & RV --> G3{"⛔ Defects and anti-pattern candidates gate<br/>fix now · accept as limitation · change spec"}
        G3 -->|"fix"| FX["same Implementer resumed: makes the Tester's failing test pass<br/>→ same Tester re-runs → new clean critic at R1/R2"]
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

## 5. ESDD and Hybrid

For features with open requirements or technical unknowns. Source: `workflows/esdd.md`.

```mermaid
flowchart TB
    P1["Phase 1 · Initial spec<br/>intent.md, known vs unknown, Specification Writer<br/>with status per item, criticality, completion criteria"] --> G1{"⛔ Collaborative review<br/>blocking questions only"}
    G1 --> P2["Phase 2 · Explore<br/>Planner: approaches, feasibility, reversibility,<br/>disposable prototypes as options"]
    P2 --> G2{"⛔ Decide<br/>explore more · validate hypothesis · prototype ·<br/>select approach · modify requirements · defer"}
    G2 --> INC["Plan the next increment only<br/>goal · hypothesis it validates · done criteria"]
    INC --> P3["Phase 3 · Implement the increment<br/>record discoveries and invalidated assumptions"]
    P3 --> RA{"Discovery touches a<br/>programmer decision?"}
    RA -->|"yes"| G3{"⛔ Reassess"}
    RA -->|"no"| P4
    G3 --> P4["Phase 4 · Test and discover<br/>functional, E2E, black-box, mutation, review"]
    P4 --> G4{"⛔ Validation<br/>facts vs interpretations, anti-pattern candidates"}
    G4 --> P5["Phase 5 · Evolve<br/>classify discoveries, Specification Writer applies<br/>approved spec changes with version + change log,<br/>impact analysis before significant changes"]
    P5 --> DONE{"Completion criteria met?"}
    DONE -->|"approach in question"| P2
    DONE -->|"next increment"| INC
    DONE -->|"yes"| P6["Phase 6 · Final report<br/>⛔ acceptance · ⛔ integration · ⛔ cleanup"]
```

- **Statuses** for spec items and discoveries: Confirmed, Hypothesis, Under exploration, Rejected.
- **Requirement changes** are typed Added, Clarified, Modified, Replaced or Retired, and every one is approved by the programmer.
- **Prototypes** live outside production paths. They are discarded unless the programmer promotes them.
- **Hybrid:** SDD Direct for the feature as a whole, with Phases 2–5 applied only to the uncertain area.

## 6. Intensity levels

Set per feature or per group. Source: `protocols/intensity.md`.

| Aspect | Lite | Medium | High |
| --- | --- | --- | --- |
| Workflow | SDD Direct | SDD Direct, ESDD, Hybrid | SDD Direct, ESDD, Hybrid |
| Repository Analyst | no | only if the memory lacks the evidence | yes |
| Specification Writer | no: the orchestrator writes the card's spec section | yes | yes |
| Planner | no: the orchestrator writes one approach | main decision only | full solution space |
| Test Designer | no | yes, from the spec, in parallel with the Planner | yes, every technique |
| Implementer | code **and** its unit and E2E tests | production code only | same as Medium |
| Tester | no | implements and runs the designed cases, with E2E | same, plus every technique and mutation testing |
| Review (default the recommendation starts from) | R0 | R1 | R2 |
| Specialists | you choose at the spec + plan gate | you choose at the spec gate | you choose at the spec gate (mandatory ones run if Critical) |
| Mutation testing | no | asked at the plan gate | yes |
| Gates | one spec+plan gate, then acceptance | spec, plan, defects, acceptance | all |
| Artifacts | one `feature.md` card (target 500 lines) + `decisions/` | full set, with size targets (overflow goes to linked files, never cut) | full set |
| Agent questions | yes | yes | yes |

Critical features always run at High.

## 7. Agent questions

Subagents cannot talk to the programmer, so they ask through the orchestrator. Source: `protocols/agent-questions.md`.

```mermaid
sequenceDiagram
    autonumber
    actor P as Programmer
    participant O as Orchestrator
    participant A as Agent (e.g. Specification Writer)
    participant D as Disk, intent.md · spec §Open questions · decisions/ · handoff.md

    O->>A: Brief (role file, handoff, task)
    A->>A: Check repo and artifacts first
    A-->>O: STATUS: QUESTIONS + work so far + Q-1..Q-n
    O->>O: Answer from evidence what it can, strip any steering
    O->>D: Record questions as Pending, agent ID in handoff
    O->>P: ⛔ [slug] Q-n (Spec Writer), batched, neutral
    P->>O: Answers
    O->>D: Record answers (words, date) · Answered / Deferred
    O->>A: SendMessage: answers by Q-ID, "continue from where you stopped"
    A-->>O: STATUS: DONE (or new questions, numbered on)
```

- **Blocking** questions are the ones whose answer changes the agent's output: a requirement, scope, observable behavior, a constraint, the viable approaches, or a test's expected result. The agent stops and does not guess. A question that changes the output for a valid input is always blocking, and the agent never weakens an acceptance criterion to avoid it.
- **Non-blocking** questions: the agent continues under an assumption labeled Hypothesis and lists it. The question goes to the next gate.
- **If the agent cannot be resumed** (a new session or an error), a new agent gets the same brief plus the earlier "work so far" and the answers.
- **Answers that change approved work** become a spec version bump or a decision record. Approved work never changes silently.
- **Critics and verifiers never ask:** they report ambiguity as a finding.

## 8. Review cycle

Source: `protocols/review-cycle.md`. The orchestrator **recommends** the level with evidence, and the programmer validates it. This is the one standing exception to neutrality.

| Level | What runs | Typical feature |
| --- | --- | --- |
| R0 | Quality gate and project lint only | Mechanical change, about 50 changed lines, no risk areas |
| R1 | One clean critic, in parallel with the Tester | Standard feature with new logic |
| R2 | Critic → verifier → automatic fixes → new critic on the fixes only, 3 critic rounds per feature at most | Critical, or large or complex |

```mermaid
flowchart LR
    C["Critic round n<br/>new agent, clean context:<br/>code + diff + conventions + registry only"] --> V["Verifier round n<br/>new clean agent: tries to refute<br/>VALID · INVALID · AMBIGUOUS<br/>fix class: behavior-preserving or changing"]
    V -->|"VALID + behavior-preserving<br/>Blocker/Major/Minor"| I["Implementer fixes<br/>tests + quality gate"]
    V -->|"behavior-changing · AMBIGUOUS ·<br/>correctness or security Blockers"| G{"⛔ Defects gate"}
    V -->|"Nits"| FRP["Final report"]
    I --> STOP{"Stop?<br/>no new Blocker or Major ·<br/>3 critic rounds · oscillation"}
    STOP -->|"no"| C
    STOP -->|"yes"| RT["Tester re-runs affected<br/>regression and E2E"]
```

- **Review level:** the recommendation starts from the intensity default (Lite R0, Medium R1, High R2, Critical R2). A standing "accept your recommendation" covers only that default; a deviation is asked every time.
- **Automatic fixes** happen only at R2. Each one is listed at the next gate with its hunks and a revert option. The orchestrator never changes code itself (`SKILL.md` §1, principle 9).
- **Convergence:** round 1 reviews the whole diff. Later rounds review only the fixes, and report only Blocker and Major findings.
- **Clean context:** the critic and the verifier never read the spec, plan, decisions, handoffs, implementation report or earlier rounds. Each round launches a **new** critic on the whole diff from the base.
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
    GATE -->|"automate"| RULE["lint rule: ast-grep · Semgrep ·<br/>import rules · project linter"]
    RULE --> REG
```

The **quality standard** applies to every agent that writes code:
- **Smallest complete change:** reuse what exists, then the standard library, then an installed dependency, then the minimum new code.
- **No comments,** except `shortcut: <limit>, <when to upgrade>` markers and tool directives.
- **Limits as signals of mixed responsibilities:** file ≤ 400 lines, function ≤ 30, parameters ≤ 4, cyclomatic complexity ≤ 10, nesting ≤ 3.
- **Structure:** declarative names, single responsibility, feature folders when the project already uses them (the existing structure wins), and patterns only for problems present now.

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
  - Each feature has its own workflow, intensity, gates, artifacts and agents.
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

Source: `protocols/specialists.md`.

```mermaid
flowchart LR
    IX["Index: one line per specialist<br/>built-in → ~/.claude/feature-specialists/ → repo/.claude/feature-specialists/<br/>(same name: project wins)"] --> SG["Signals matched<br/>paths · spec terms · trust boundaries"]
    SG --> G{"⛔ First gate<br/>matching specialists as facts,<br/>you choose who runs in which slot"}
    G --> S1["spec slot<br/>questions on the draft"]
    G --> S2["plan slot<br/>facts per option, no ranking"]
    G --> S3["test-design slot<br/>cases in testing-plan.md"]
    G --> S4["audit slot<br/>clean, opus, executed evidence"]
    S1 & S2 --> GA{"⛔ Spec and plan gates"}
    S4 --> GD{"⛔ Defects / findings gate<br/>merged with the critic, by domain"}
```

- **Two kinds:** advisors (`spec`, `plan`, `test-design`) can be resumed; auditors are always new, never fixed automatically, and re-run on the fix diff after a fix.
- **Mandatory specialists:** a specialist declares `mandatory-when: critical` in its file to run on every Critical feature its signals match. The built-in `security` specialist does.
- **Re-check:** signals are checked again against the real diff before verification, so a specialist that now matches is offered again.

### Phased mode (optional, experimental)

Source: `protocols/phase-runners.md`. Direct mode is the default.

```mermaid
flowchart LR
    P(["Programmer"]) <--> O["Orchestrator<br/>startup, intent.md, gates from disk,<br/>question relay, portfolio, integration"]
    O -->|"brief: phase, steps, decisions in force"| PR["Phase runner<br/>one per feature and phase,<br/>dies at the first gate"]
    PR -->|"briefs, verifies, relays questions"| RO["Role agents of that phase"]
    PR -->|"Pending decisions, handoff"| DK[("feature folder")]
    PR -->|"PHASE … ended at GATE · QUESTIONS · FAILED"| O
    O -->|"reads the gate from disk + consistency check"| DK
```

- **Phases:** SDD Direct has Specification, Planning, Build and Fixes. ESDD has Initial specification, Exploration, Increment and Evolution.
- **Experimental, never run.** By design the decisions are the same: the runner cannot reach the programmer, so it must stop at each gate. That has not been tested.
- **What changes:** you see results at the gates instead of agent by agent, and you can stop a whole runner but not steer it mid-phase.

- **Project memory** (`memory.md`, ≤ 80 lines) carries the project context and the portfolio across sessions. Before every stop, pending decisions are written to `decisions/` with their option labels, so an answer like "B" still resolves in a fresh session.

## 11. Responsibilities per agent

Standard executor and model. The orchestrator picks the cheapest sufficient model for each delegation, within the floors, and logs it in `delegations.md`.

| Agent | Executor · standard model | Responsible for | Reads | Writes | Never |
| --- | --- | --- | --- | --- | --- |
| **Orchestrator** | main session | Talking to the programmer, worktrees, intensity and workflow selection, the intent record `intent.md` (original request, the programmer's statements verbatim, Current intent), briefs, verifying returns, relaying questions, gates, decision records, handoffs between phases, delegation log, final report, integration and cleanup on approval | Only the skill files the current step needs; artifacts; reports | `intent.md`, `decisions/`, handoffs for read-only roles, `delegations.md`, `reports/review/rounds.md`, `final-report.md`, `memory.md`, claims | Recommend or rank options (except the review level), write production code, approve on the programmer's behalf, integrate or delete without confirmation |
| **Repository Analyst** | `Explore` · haiku (sonnet for large or unfamiliar code) | Evidence for one task: components, dependencies, conventions, existing behavior, tests and commands, architecture style, quality and E2E tooling; observed vs inferred | The feature worktree, only what the brief needs | Nothing: returns a context report of about 600 words | Recommend approaches, assume a stack without evidence, modify files |
| **Specification Writer** | `general-purpose` · opus (sonnet for short, clear requests; never haiku) | Turning the request into the current reading of its intent (not a closed contract): the source version of the intent record, the reach of its broad statements, FR/NFR, constraints, invariants, Given/When/Then criteria, what is outside the intent (and who drew each boundary) and open questions, each item traced to a source; ESDD statuses; applying approved spec changes | `intent.md`, handoff, the specification guide and template, the repository (read-only) | `specification.md` (Draft) | Invent requirements, resolve ambiguity, include implementation details, write vague criteria to avoid a question |
| **Planner** | `Plan` · opus (sonnet for one mechanical approach; never haiku) | The solution space: viable approaches in the neutral format, per-option outlines that follow the quality standard, the E2E harness, other decisions needed, excluded options with the constraint they violate | Handoff, spec sections, code, registry | Nothing: returns the decision block | Choose, rank, change requirements, add speculative abstractions |
| **Test Designer** | `general-purpose` · sonnet (opus if Critical; never haiku) | Test cases derived from the approved spec alone, in parallel with the Planner: each technique applied or justified, error, security, worst-case and E2E cases, traceability from every AC to its cases | Spec, analyst report, testing techniques, E2E guide (never the plan or code) | `testing-plan.md` | Invent expected results, design around an implementation, write test code |
| **Implementer** | `general-purpose` · sonnet (haiku if mechanical, opus if risky) | Production code for the approved plan only, to the quality standard. Self-review against the critic's checklist before the quality gate, so review finds little to rework. Runs the existing tests; **writes no tests** (Lite is the exception). Makes the Tester's reproducing tests pass when resumed for fixes. | Handoff, plan, testing plan, quality standard, design patterns, registry | Production code, `implementation-report.md`, handoff to testing, Lite card result | Write tests (outside Lite), drift from the plan silently, add comments, leave quality violations unreported, expand scope |
| **Tester** | `general-purpose` · sonnet (haiku for re-runs, opus for hard state) | The only author of tests: implements every designed case, runs functional, regression and E2E testing, explores beyond the plan, mutation testing if decided, validation against the spec. Keeps failing tests as reproductions for fixes. Resumed to re-run after fixes. | Handoff, testing plan, spec, testing techniques, E2E guide | Tests, case statuses in `testing-plan.md`, `reports/e2e/`, `validation-report.md`, handoff | Change a designed expected result, decide one the spec leaves open, weaken or skip failing tests, report a test it did not run as passed |
| **Clean Code Critic** | `general-purpose` · opus (never haiku) | Maximally critical review from scratch: names, responsibilities, function design, structure, patterns misused, registry violations, places the request's words reach that the diff leaves untouched; each finding with a concrete case | The original request and the programmer's statements, verbatim; code, `git diff <base>`, project conventions, quality standard, registry | `reports/review/round-<n>-critic.md` | Read the spec, plan, handoffs or earlier rounds; be reused across rounds |
| **Phase runner** (phased mode) | `general-purpose` · sonnet (opus if Critical; never haiku) | Orchestrating one phase of one feature: delegating its steps, choosing models, verifying returns, relaying agent questions, writing the gate's Pending decisions | Its brief, `SKILL.md` §4, the workflow steps in range, intensity and agent-questions protocols | `delegations.md`, `decisions/` (Pending), `handoff.md` | Talk to the programmer, pass a gate, run startup or integration, be reused for the next phase |
| **Finding Verifier** | `general-purpose` · sonnet (never haiku) | Trying to refute each finding against the code: VALID, INVALID or AMBIGUOUS; fix class; recurring findings marked as candidates | The critic's report, the code | `reports/review/round-<n>-verification.md` | Read the spec or plan, fix code, accept a finding without checking it |
| **Specialists** | `general-purpose` · sonnet in `spec`/`plan`/`test-design`, opus in `audit` (never haiku there) | Domain expertise in the slots you activate: questions on the spec draft, facts per plan option (never a recommendation), test cases, and a clean audit with executed evidence (exploit, query plan, timing, screenshot) | Advisory slots: request, spec, options. Audit: the diff and the code it reaches only | Questions, facts, cases in `testing-plan.md`, `reports/review/<name>.md` | Add requirements, recommend options, report unproven findings as confirmed, install tools, be resumed in `audit` |

**Floors:** no haiku for specification, planning, critic, verifier or phase runner. Critical features use opus for specification, planning, the critic and phase runners.

**Shared rules for every subagent:**
- **Location:** run without `isolation`. Confirm the feature branch first, and work through absolute paths (`cd <worktree> && …`). Never call `EnterWorktree`.
- **No delegation:** feature roles never spawn further agents.
- **Headless:** every subagent runs in the background. The programmer sees one line when an agent starts or finishes, and the full content only at gates.
- **Reuse:** when work returns to a role that already ran for the feature (fixes, re-tests, spec changes, the next increment), the same agent is resumed with `SendMessage`, and its ID is recorded in `handoff.md`. Critics and verifiers are never resumed.
- **Questions:** questions only the programmer can answer follow the agent-questions protocol. A blocking one stops the agent; it never guesses.
- **Return:** a `STATUS` line, a summary within the word limit, the questions, and any decision in the neutral format.

## 12. Artifacts and state

```
<repo>/.claude/worktrees/<slug>/                 feature worktree, own branch
└── docs/features/<slug>/                        or the project's own convention
    ├── intent.md                orchestrator        original request + statements S-n + Current intent
    ├── specification.md         Specification Writer  versioned; change log
    ├── implementation-plan.md   orchestrator        approved approach only
    ├── testing-plan.md          Test Designer (cases) · Tester (statuses)
    ├── decisions/D-NNN-*.md     orchestrator        Pending → decided, full option block
    ├── reports/
    │   ├── implementation-report.md   Implementer
    │   ├── validation-report.md       Tester
    │   ├── anti-pattern-candidates.md orchestrator (from agents)
    │   ├── e2e/                       Tester: traces, screenshots, logs
    │   ├── review/rounds.md · round-<n>-critic.md · round-<n>-verification.md
    │   └── final-report.md            orchestrator
    ├── delegations.md           orchestrator        role · model · reason · outcome
    └── handoff.md               outgoing agent      overwritten at each transition
    (Lite: feature.md card + decisions/ instead of the set above)

<repo>/.quality/ or <git-common-dir>/quality/   project-wide registry, after the programmer's approval
<git-common-dir>/feature-workflow/memory.md      project memory, ≤ 80 lines, never committed
<git-common-dir>/feature-workflow/claims/        one JSON per feature: who orchestrates it
```

**Handoffs** transfer knowledge, not conversation (`protocols/context-handoff.md`):
- **Transitions:** Request → Specification, Specification → Planning, Planning → Implementation, Implementation → Testing, Testing → Evolution (ESDD), and Testing → Finalization. Each one has a checklist.
- **Content:** handoffs reference artifacts by path and section instead of copying them, and record freshness (commit, branch, dirty state, artifact versions).
- **Critics and verifiers** never read handoffs.

## 13. Design principles

1. **The programmer decides.** Options are neutral: alphabetical, with symmetric pros and cons, facts instead of adjectives, and excluded options listed with the constraint they violate. The one exception is the review level, which is recommended and then validated.
2. **Artifacts are the source of truth.** Any feature can be resumed in a new session from its folder.
3. **Separation of concerns:** spec (what and why) ≠ plan (how) ≠ implementation ≠ validation, and each feature is separate from every other.
4. **Explicit uncertainty and evidence:** claims carry a status. A test that was not run is never "passed".
5. **No silent drift:** deviations, scope changes and behavior changes go back to the programmer.
6. **Ask, don't guess:** gaps become questions relayed by the orchestrator, never invented requirements.
7. **Clean review:** whoever reviews code never saw it being written.
8. **Pay only for what is needed:** progressive loading, intensity levels, a model chosen per delegation, and batched launches and verification. Correctness still beats economy.
