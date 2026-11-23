# Verification Skills Protocol

Two generators of **project skills** that let any later feature verify its work against the real thing, plus how to keep them true to the code. Each one writes a skill in the format of `protocols/skills.md`, so the skill index finds it and the phases that declare it read it. Adapted from the `create-verification-skill`, `create-formal-verification-skill`, `maintain-*` and `statechart` skills of pstack (github.com/cursor/plugins, MIT).

| Generator | Command | Writes | Proves |
| --- | --- | --- | --- |
| App verification | `/feature verify-skill app [<surface>]` | `verify-<app>.md` and its feature map | Behavior, by driving the real app the way a user does |
| Formal verification | `/feature verify-skill formal [<area or bug>]` | `formal-<area>.md` and its model or harness | One property for every case in a stated scope: every order of steps in a model, every input up to a bound, or every input |

**When they run:** only when the programmer asks, from `/feature`, `/feature-kit` (modules `verify-skill` and `formal-skill`), or at a gate where an end-to-end status was **Blocked** for lack of a way to drive the app, or a Critical feature touches concurrency, retries, a state machine, a parser or unsafe code. At a gate it is offered as an option among others (`protocols/neutral-decisions.md`), with its cost.

**Cost.** Each run is one session's work plus the runs of the app or the tool. A tool or runtime not installed (a browser for Playwright, Java and TLC for TLA+, a verifier) is a dependency: installing it is the programmer's decision, asked before.

## Where the skill lives

Asked once per repository, neutrally, with the facts of the repository (its own project or a contribution; what its `.gitignore` and contributing guide say about tool files):

| Location | Path | What follows |
| --- | --- | --- |
| Local to this clone | `$(git rev-parse --git-common-dir)/feature-skills/` | Never committed; shared by every worktree of the clone; lost with the clone; other developers do not see it |
| Versioned with the project | `<repo>/.claude/feature-skills/` | Committed on its own branch, reviewed like code |
| A module of the project | `<module>/.claude/feature-skills/` | Versioned; active only for features that touch `<module>` |

Supporting files (the feature map, a model, a harness, helper scripts) go in a folder with the skill's name next to it: `verify-<app>/`, `formal-<area>/`.

## Writing for the next agent

Both generated skills are read cold, mid-task, by an agent that has never seen the app or the model. So: the repository's real commands, paths, selectors and nouns; no placeholders; every helper script executable, with its invocation shown in the skill body; frontmatter complete, or the index never finds it.

## App verification (`verify-<app>`)

### 1. Interview the repository, not the programmer

Answer from the code; ask the programmer only what cannot be observed:
- **Surface:** what a user touches (web UI, CLI or TUI, desktop, API, mobile, library). Pick the primary one and note the others.
- **Run:** how the app starts locally, from the repository's own documented commands. Ports, environment variables, seed data, authentication.
- **Drive:** existing harnesses first (Playwright or Cypress specs, PTY helpers, HTTP endpoints, a debug port), then a generic recipe from `knowledge/e2e-testing.md` §1.
- **Observe:** what evidence can be captured: screenshots, terminal transcripts, response bodies, logs, exit codes, database state.
- **Isolate:** whether two instances can run side by side (ports, data directories, profiles). If not, the skill says so and refuses to drive a shared instance.

If the checkout does not build or start, report it precisely and stop: a skill written against a broken base teaches wrong steps. An irrelevant missing asset that blocks startup may be created by the skill, marked as verification scaffolding and removed in cleanup.

### 2. Generate the skill

```markdown
---
name: verify-<app>
kind: guide
summary: Launch, drive and capture evidence from <app> through its <surface>
use-in: [test-design, test, review]
signals:
  - paths: ["<the app's source globs>"]
---
```

Sections, each grounded in what the interview found:
- **Launch:** the exact command, from an empty data directory (migrations and seed data included), and how to tell it is **usable**, not only that a process answers. Teardown. For a short-lived CLI: build once, then each drive in its own isolated PTY or temporary directory.
- **Doctor:** one read-only check that this instance is worth driving: process up, right build, port owned by this run, authentication valid. Run first whenever anything looks off.
- **Drive:** the harness recipe with this repository's real selectors and commands, preferring stable handles (roles and accessible names, data attributes, prompt strings, routes).
- **Evidence:** what to capture and where (the feature's `reports/e2e/`, or a path the skill names). The proof standards: the real user path, never internal setters or test-only endpoints; the action and the resulting state, not only the final screen; side effects (files, rows, messages) next to what is visible; fakes only at an existing production boundary (`knowledge/e2e-testing.md` §2). A dry-run or test mode is verified by observing what it skips, not by its name.
- **Cleanup:** tear down what this run started, never by process name. Evidence survives cleanup.

### 3. Seed the feature map

`verify-<app>/features/README.md` plus one file per user-facing feature, starting with the top 3 to 5 (from routes, commands, menus, docs). Each file has four sections: *Sub-features*, *How to get to it (user's point of view)*, *Driving it*, *Gotchas*. A journey whose precondition the seed data lacks reports a failure and the reason goes in *Gotchas*; a journey is never weakened to pass. A proof that drives one convenient entry point is incomplete when the map lists others.

### 4. Prove it before handing it over

Follow the generated skill once, end to end: launch, doctor, drive **one** mapped feature, capture evidence, clean up, and confirm the evidence still exists. Fix what fails, running the cleanup after every failed attempt. A skill never executed is a draft. If it was proven in a stand-in (a container instead of the real target), list each setup step the stand-in did that the target will not: those stay unverified.

## Formal verification (`formal-<area>`)

### 1. Choose the target from the code

A good target is a **promise the code makes**, where a break harms users and tests rarely reach the case that breaks it. Start from the area or bug the programmer named; otherwise choose the strongest such target in the repository, not the easiest to verify. ⛔ Present the target, the property in one plain sentence and the harm in another, with the candidate tools, before building anything.

### 2. Let the question choose the tool

The tool that answers the question at the lowest cost, presented neutrally with what each needs installed:
- whether events can happen in a bad order (concurrency, retries, protocols, product flows): a model checker over a small model of the design; TLA+ with TLC fits any language;
- whether the code itself behaves for every input (memory safety, overflow, a data-structure invariant): a verifier that runs on the code (for example Kani, CBMC, Dafny, a symbolic executor), or bounded checking;
- a property that must hold at every size, where a bound is not enough: a proof assistant;
- no verifier for this language: generated inputs against the real code (property-based testing, `knowledge/testing-techniques.md`), never a hand model of the function.

### 3. What makes it good

- **True to the code.** Every part of the model points to code a reviewer can open; what the model treats as one indivisible step is one indivisible step in the code; names come from the repository.
- **Able to fail.** Show each property failing on a broken variant of the code it guards (a removed check, a reordered step). A check never seen failing proves nothing.
- **Findings stay findings.** When the current code breaks the property, report the counterexample in the code's terms. Never weaken the property or the model until it passes, and never change product code unless the programmer asks.
- **Honest about scope.** What is verified, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, not the whole system.
- **Readable without the tool.** The property and the harm in one plain sentence each; a counterexample as a short numbered sequence of steps in the code's words.
- **Cheap to rerun.** One command, a pinned tool version, a run short enough to use on every relevant change.
- **Kept in step.** A coverage record: the files and functions each property covers, and the **sync commit** at which the model was last confirmed to describe them.

### 4. Generate the skill

```markdown
---
name: formal-<area>
kind: guide
summary: <property in plain words>, checked with <tool> over <scope and bounds>
use-in: [plan, test, review]
signals:
  - paths: ["<the covered files>"]
---
```

From the skill alone, the next agent must be able to: tell whether a change touches the verified code; run the check; tell a real bug from a modeling error; update the model when a change is intended; and move the sync commit forward **only after** confirming the model describes the code at the new commit. It holds the coverage record and the sync commit.

### 5. Prove it before handing it over

Follow the generated skill once on a scratch change that breaks the property in the real code: it must catch the break. Drop the scratch change and confirm the check is back where it started (passing, or failing only on the findings reported). If it misses the break, fix the skill or the model, never the scratch change.

### 6. Hand off

What was verified, the tool and why, the bounds, what the check found in plain words, how to run it, and what it does not cover.

## Statecharts: showing a model to the programmer

When the model is a state machine (a TLA+ spec, or the states of a feature in its specification), show it as a Mermaid `stateDiagram-v2` so the programmer can judge whether the behavior is right:

- **The programmer's words.** Label each state with what the user sees or cares about ("Paying", "Lease held, write pending"), each arrow with what happens as the user would say it ("you press play", "the connection fails"), never with variable or action names. A condition goes in brackets at the end of the arrow label: `you press play [while the file loads]`.
- **Small enough to read:** about 20 arrows or fewer. Merge values that act the same and leave out details the reader does not need, but keep every state of a bug path, never merge two states that break different rules, keep every state reachable from a start state, and keep an arrow out of every state that has a step out. Say which steps the chart hides.
- **Mark the broken rules.** A state that breaks an invariant is marked, and the legend names the rule. Each bug is one line: the rule, the reader's sentence for it, and its shortest path as numbered steps.
- **End states** need an explicit "done" step in the model, or the checker reports a deadlock.
- **Replay every bug path against the real code,** as a test or a live reproduction, one step per action. If the bug does not occur, assume the model is wrong until shown otherwise.
- **Bounds.** Keep the model's constants small, or add a constraint: a checker that goes past broken states can run without end. State the bounds next to the chart.

If the programmer has pstack's `/statechart` tool installed, it runs TLC and draws the chart from a view module; otherwise draw the chart by hand from the checker's output, following the rules above.

## Keeping them true to the code

Run when a feature's diff touches the paths a verification skill covers (its signals), at the test phase, or when the programmer asks:

- **App verification:** drive the mapped features the diff touches. A journey that no longer works is either a defect of the feature or drift of the skill: decide which with evidence, fix the skill only for drift, in its own commit, with the proof run.
- **Formal verification:** list the commits since the sync commit that touched covered code (`git log <sync>..HEAD -- <covered files>`), update the model to describe the code as it is now, re-run, and classify each failure as **drift in the model** or **a bug in the code**, with the counterexample replayed against the code. Move the sync commit only after that confirmation. A bug is a finding for the programmer, never fixed silently.
