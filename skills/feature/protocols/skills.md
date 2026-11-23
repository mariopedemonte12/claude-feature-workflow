# Skills Protocol

A **skill** is a file of engineering knowledge that the workflow uses in some phases and not others. The library brings its own; the programmer, the repository and each module of the repository can add more, or replace a library skill, without changing the workflow. Every skill declares **where it can be used**, so each phase reads only what applies to it.

## Two kinds

| Kind | What it is | Who uses it |
| --- | --- | --- |
| `guide` | Knowledge: rules, checklists, techniques, conventions | Whoever does the phase reads it: the agent briefed for it, or the session itself when it executes the phase |
| `specialist` | An expert in one domain (security, UI/UX, databases…) that runs as **its own agent** in its phases | A separate agent per phase, as §Specialists describes |

## The classification

Every skill starts with this frontmatter:

```markdown
---
name: payments-rules                 # kebab-case, unique within its location
kind: guide                          # guide · specialist
summary: Rounding, currencies and idempotency rules of the billing module
use-in: [spec, plan, implement, review]   # phases, or [general]
workflows: [direct, sdd, evo]        # optional; all three when omitted
signals:                             # optional for a guide; facts that make it relevant
  - paths: ["billing/**"]
  - terms: ["invoice", "currency", "refund"]
model: sonnet                        # specialists only: default for advisory phases; audit uses opus
mandatory-when: never                # or: critical (runs on every Critical feature whose signals match)
---
```

**Phases** (`use-in`):

| Phase | DIRECT | SDD | EVO |
| --- | --- | --- | --- |
| `intent` | — | Intent and request understanding (step 1) | Intent pass (steps 1–2) |
| `spec` | — | Specification (step 2) | — |
| `plan` | — | Planning (steps 4–5) | Approach (step 4) and each increment's entry |
| `test-design` | — | Test design (step 5) | Cases of each increment |
| `implement` | the session's work | Implementation (step 7) | Implementation of each increment |
| `test` | the session's work | Testing (steps 8–11) | Testing of each increment |
| `review` | the self-check, and a critic if one runs | Critic and verifier | Critic and verifier |
| `audit` | — | Specialist audits | Specialist audits |
| `general` | every step | every phase | every phase |

A `guide` may declare any phase. A `specialist` declares only `spec`, `plan`, `test-design` and `audit`: the phases where it runs as its own agent. `slots:` in an older file means `use-in:`, and `spec:` under signals means `terms:`.

**DIRECT has no phases.** It reads the skills that declare `implement`, `test`, `review` or `general`, and those whose `workflows` include `direct`, lazily: when the task reaches them or their signals match. A specialist in DIRECT is a checklist: the session applies the sections of its phases to its own work, and its `audit` runs as a clean agent only if the programmer asks. `--no-skills` turns every skill off for that feature, the library's included; only the edge-case checklist (`knowledge/edge-cases.md`) stays.

## Where skills come from

Five locations, from the most general to the most specific. **A more specific skill replaces a more general one with the same `name`.** Say which file you used whenever two exist.

| Order | Location | Scope |
| --- | --- | --- |
| 1 | `<skill dir>/knowledge/*.md`, `<skill dir>/specialists/*.md` | The library |
| 2 | `~/.claude/feature-skills/*.md` | The programmer's own, for every project |
| 3 | `$(git rev-parse --git-common-dir)/feature-skills/*.md` | The repository's own, local to this clone: never committed, shared by its worktrees (used by generated skills when the programmer keeps them out of the repository, `protocols/verification-skills.md`) |
| 3 | `<repository>/.claude/feature-skills/*.md` | The repository's own, versioned with it. With a local skill of the same name, the versioned one wins |
| 4 | `<module>/.claude/feature-skills/*.md`, for any directory `<module>` inside the repository | One module's own. Active only for a feature that reads or changes files under `<module>` |

`~/.claude/feature-specialists/` and `<repository>/.claude/feature-specialists/`, the earlier names, are still read, at the same level as `feature-skills/` next to them.

These folders are not Claude Code's own `.claude/skills/`: that folder's descriptions load into every session, and these load only when the workflow runs.

**Finding module skills**, once per feature: `find <repo> -path '*/.claude/feature-skills/*.md' -not -path '<repo>/.claude/*' -not -path '*/node_modules/*'`, run in the feature's worktree, or the checkout when there is none. A module skill becomes active when the feature's planned files, or its diff, include a path under its `<module>`; check again whenever the diff grows.

## Loading: index first, file on use

1. At the start of a feature, read **only the frontmatter** of every skill in the five locations (`sed -n '1,/^---$/p'` after the first line) and keep a one-line-per-skill index: name, kind, location, `use-in`, `workflows`, signals, `mandatory-when`.
2. Read a guide's body when its phase starts and it applies: no signals, or a signal matches. Read a specialist's file only once it is activated, and only the sections of its active phases (`## Slot: <phase>`).
3. **Briefing an agent** for a phase: list in its brief the absolute paths of the guides that apply to that phase, after its role file (`Skills for this phase: <path>, <path>`). Never paste their content. Library guides a role file already names are not listed again.
4. Announce each skill outside the library in one line when it first applies, e.g. `Skill: payments-rules (repo) → implement, review`.

## Specialists

### Activation: signals, then the programmer confirms

1. **Detect signals.** Check each specialist's signals against the request, the spec draft or intent pass, and the analyst's evidence, or, at the audit phase, the real diff.
2. **Present them as facts** at the feature's first gate. One line per matching specialist: which signals matched (paths, terms), the phases it offers, and the estimated cost (about USD 0.15–0.30 per phase). Specialists without a match are not listed, unless the programmer asks for the full list.
3. **The programmer chooses** which specialists run and in which phases. Ask neutrally: matching specialists are facts, not recommendations.
4. **Flag:** `--with <name>[,<name>…]` in the request activates those specialists in all their phases. The programmer may restrict them at the gate.
5. **Mandatory:** a specialist with `mandatory-when: critical` runs on a Critical feature whenever one of its signals matches. State it; do not ask. The built-in `security` specialist is mandatory this way.
6. **Re-check signals** against the real diff before verification, and in EVO at each increment. A specialist whose signals now match but was not chosen is asked about again.

Record the choices in the feature's `decisions/`, or the card's *Decisions* when the feature uses a card.

### Phase contracts

| Phase | When | Context | Returns | Rules |
| --- | --- | --- | --- | --- |
| `spec` | After the spec draft (EVO: the intent pass), before its gate | Informed: the request, the draft and the analyst's evidence | Questions in its domain, in the format of `protocols/agent-questions.md` | It never adds requirements: gaps are questions. Its questions join the gate. |
| `plan` | After the Planner's options (or the executor's), before the plan or approach gate | Informed: the spec or intent, and the options | Per option: facts, risks and costs in its domain (lock times, query plans, timeouts, accessibility impact…) | It never recommends or ranks. Its facts are added to each option's fields under the neutral protocol. |
| `test-design` | Alongside the Test Designer, or the executor's case design | The spec, or the intent record and decisions | Test cases in its domain, in the testing plan's or card's format | Cases come from the statement of what the feature must do. Where it does not settle an expected result, that is a question. |
| `audit` | After the code, in parallel with the critic | **Clean:** only the diff, the code it reaches and the project's conventions, as the critic (`roles/reviewer.md` §Clean context) | Findings with **executed evidence**: a reproduction, a measurement, a screenshot, a query plan | No evidence, no confirmed finding: it is a *Possible risk*. The model is `opus`, never `haiku`. Never resumed. Never fixed automatically. |

**Inherited rules, every phase:**
- **Agent behavior:** headless (background) launches; no delegation; the project's installed tools only, never installing one without the programmer's approval; questions through `protocols/agent-questions.md`.
- **Resuming:** advisory phases (`spec`, `plan`, `test-design`) may be resumed when work returns to them (`SKILL.md` §4, *Reusing agents*). The `audit` phase is always a new agent, and after a finding in its domain is fixed, a **new** one reviews only the fix diff.
- **Logging:** each specialist run appears in `delegations.md`, or in the card, as role `Specialist: <name> (<phase>)`.
- **Executor sessions** (`protocols/executor.md`) launch specialists as subagents exactly like the critic.

### Before a gate: merge and deduplicate

When several agents report on the same location (the critic, the Tester, and one or more specialists):
- merge findings that describe the same problem into one, listing every source;
- keep the highest severity and every piece of evidence;
- never drop a finding because another agent did not report it.

Group findings by domain at the gate, so the programmer can decide a domain at once.

## Writing a new skill

- **Guide or specialist.** Knowledge that whoever does the phase should apply is a guide. An independent look by a separate agent, with its own evidence, is a specialist.
- **Copy a template:** start from a library file of the same kind.
- **Choose `use-in` narrowly.** A rule about how code is written is `implement, review`; a rule about what a feature must do is `intent, spec, test-design`. `general` is for knowledge every phase needs, and costs a read in every phase.
- **Choose signals from facts:** paths, file types, imported libraries, request terms. Avoid signals that match almost every feature.
- **Generated skills.** `protocols/verification-skills.md` writes two kinds from the repository itself: `verify-<app>` (drive the real app) and `formal-<area>` (a formal property of the code). They are ordinary guides once written.
- **Module skills** hold what is true of that module only: its invariants, its test fixtures, the analog to imitate. What is true of the whole repository goes in the repository's folder.
- **Specialist audit sections need evidence:** each one states what counts as executed evidence in its domain.
- **Scope:** clean-code findings belong to the critic, and acceptance criteria to the Tester.
