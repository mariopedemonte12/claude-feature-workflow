# Specialists Protocol

A **specialist** is an extra agent with expertise in one domain (security, UI/UX, databases, networks, performance, observability…). It joins specific phases of a feature, in `/feature` and in `/feature-lean`. Specialists are defined in files, so a project or a programmer can add their own without changing the skill.

## Where specialists come from

Three locations, read in this order. A later location **replaces** an earlier specialist with the same `name`:

| Order | Location | Scope |
| --- | --- | --- |
| 1 | `<skill dir>/specialists/*.md` | Built in: `security`, `ux-ui`, `database`, `network`, `performance`, `observability` |
| 2 | `~/.claude/feature-specialists/*.md` | The programmer's own, for every project |
| 3 | `<repository>/.claude/feature-specialists/*.md` | The project's own, versioned with the repository |

So for the same name, **the project wins over the programmer's, which wins over the built-in one**. Say which file you used whenever two exist.

## The file format

```markdown
---
name: database                     # kebab-case, unique
summary: Schemas, migrations, queries, indexes, transactions, data volume
signals:                           # facts that make the specialist relevant
  - paths: ["**/migrations/**", "**/models.py", "**/*.sql"]
  - spec: ["schema", "migration", "index", "transaction", "query"]
slots: [spec, plan, test-design, audit]
model: sonnet                      # default for advisory slots; the audit slot uses opus
mandatory-when: never              # or: critical (runs whenever the feature is Critical and a signal matches)
---
# Specialist: Database
## Slot: spec
## Slot: plan
## Slot: test-design
## Slot: audit
```

The body has one section per declared slot. Each section says what the specialist examines and what it returns, within that slot's contract below.

## Loading: index first, file on activation

At the start of a feature, read **only the frontmatter** of every specialist file in the three locations: name, summary, signals, slots, `mandatory-when`. For example, `sed -n '1,/^---$/p'` after the first line. Keep that as a one-line-per-specialist index. Read a specialist's full file only when it is activated, and only the sections of its active slots. Available specialists cost almost nothing until they run.

## Activation: signals, then the programmer confirms

1. **Detect signals.** Check each specialist's signals against the request, the spec draft and the analyst's evidence, or, at the audit slot, the real diff.
2. **Present them as facts** at the feature's first gate (the spec gate in `/feature`, gate 1 in `/feature-lean`). One line per matching specialist: which signals matched (paths, terms), the slots it offers, and the estimated cost (about USD 0.15–0.30 per slot). Specialists without a match are not listed, unless the programmer asks for the full list.
3. **The programmer chooses** which specialists run and in which slots. Ask neutrally: matching specialists are facts, not recommendations.
4. **Flag:** `--with <name>[,<name>…]` in the request activates those specialists in all their slots. The programmer may restrict them at the gate.
5. **Mandatory:** a specialist with `mandatory-when: critical` runs on a Critical feature whenever one of its signals matches. State it; do not ask. The built-in `security` specialist is mandatory this way.
6. **Re-check signals** against the real diff before the verification phase, and, in ESDD, at each increment. A specialist whose signals now match but was not chosen is asked about again.

Record the choices in the feature's `decisions/` (`/feature`) or the card's *Decisions* (`/feature-lean`).

## Slots

| Slot | When | Context | Returns | Rules |
| --- | --- | --- | --- | --- |
| `spec` | After the spec draft, before its approval | Informed: the request, the spec draft and the analyst's evidence | Questions in its domain, in the format of `protocols/agent-questions.md` | It never adds requirements: gaps are questions. Its questions join the spec gate. |
| `plan` | After the Planner's options, before the plan gate | Informed: the spec and the options | Per option: facts, risks and costs in its domain (lock times, query plans, timeouts, accessibility impact…) | It never recommends or ranks. Its facts are added to each option's fields under the neutral protocol. |
| `test-design` | Alongside the Test Designer (in Lean, alongside the specification pass) | The spec only | Test cases in its domain, in the testing plan's format | Cases come from the spec. Where the spec does not settle an expected result, that is a question. |
| `audit` | After the code, in parallel with the critic | **Clean:** only the diff, the code it reaches and the project's conventions, as the critic (`roles/reviewer.md` §Clean context) | Findings with **executed evidence**: a reproduction, a measurement, a screenshot, a query plan | No evidence, no confirmed finding: it is a *Possible risk*. The model is `opus`, never `haiku`. Never resumed. Never fixed automatically. |

**Inherited rules, every slot:**
- **Agent behavior:** headless (background) launches; no delegation; the project's installed tools only, never installing one without the programmer's approval; questions through `protocols/agent-questions.md`.
- **Resuming:** advisory slots (`spec`, `plan`, `test-design`) may be resumed when work returns to them (`SKILL.md` §4, *Reusing agents*). The `audit` slot is always a new agent, and after a finding in its domain is fixed, a **new** one reviews only the fix diff.
- **Logging:** each specialist run appears in `delegations.md` (`/feature`) or the card (`/feature-lean`), as role `Specialist: <name> (<slot>)`.

## Before a gate: merge and deduplicate

When several agents report on the same location (the critic, the Tester, and one or more specialists):
- merge findings that describe the same problem into one, listing every source;
- keep the highest severity and every piece of evidence;
- never drop a finding because another agent did not report it.

Group findings by domain at the gate, so the programmer can decide a domain at once.

## Writing a new specialist

- **Copy a template:** start from a built-in file.
- **Choose signals from facts:** paths, file types, imported libraries, spec terms. Avoid signals that match almost every feature: they turn every gate into a list of specialists.
- **Audit sections need evidence:** each one states what counts as executed evidence in its domain, such as a test, a query plan, a screenshot or a timing.
- **Scope:** keep the specialist about its domain. Clean-code findings belong to the critic, and acceptance criteria to the Tester.
