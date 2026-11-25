# Workflow: DIRECT

One session does the whole feature with the edge-case checklist: no specification, no plan document, no separate test design, no gates before integration. It is the baseline the other workflows are measured against. Use it when the request is clear and its risk is low, or when the programmer wants the cheapest run.

**Skills.** The session may use every skill that applies to DIRECT (`protocols/skills.md` §The classification): the library's, the programmer's, the repository's and the modules'. `--no-skills` turns them all off except `knowledge/edge-cases.md`.

**Artifacts.** None by default: the result is reported in the conversation. If the programmer asks for a record, write `feature.md` from `templates/feature-card.md`, filling only Intent, Scope, Cases, Result and State (at every stop).

## Steps

**1. Read.** CLAUDE.md, the code of the affected area, its tests, and the build, test and lint commands; the anti-pattern registry if it exists (`<repo>/.quality/` or `$(git rev-parse --git-common-dir)/quality/`); `knowledge/edge-cases.md`; and the skill index (frontmatter only), unless `--no-skills`.

**2. Checklist before code** (`knowledge/edge-cases.md` §Before code): reach of every broad statement, nearest analog, cases per input, probes when they apply.

**3. Questions.** Ask only the blocking ones that refinement (if it ran at startup) left open, in one message, each with what the analog does as a fact, under `protocols/decisions.md`. If there are none, do not stop: say in one line that there were none and continue.

**4. Implement and test.** Code that follows the active guides, a test for every case, the project's tests, lint and type checks, and, if the library guides are active, `python3 <skill dir>/scripts/quality_gate.py --repo <repo> --base <base>`.

**5. Self-review** (`knowledge/edge-cases.md` §After code), and fix what it finds. A clean critic (`roles/reviewer.md`, a new `opus` subagent, as in `protocols/executor.md` §The critic) runs only if the programmer asks for one.

**6. Report.** Files changed; test commands and their real results; the reach found and the cases covered; questions asked and answers; anything you saw that the request seems to reach and you did not do, as a discovery (`protocols/decisions.md` rule 9), never dropped silently; self-review findings and their fixes.

**7. ⛔ Integration** (hard stop: `protocols/gates.md` §Hard stops). DIRECT has no other gate in any profile (`protocols/gates.md`); its blocking questions (step 3) are asked in every profile. Present it (merge, pull request, leave the branch or changes as they are), with the facts: uncommitted changes, commits ahead and behind. Execute only what is chosen.

## Where the work happens

- **Executor:** in the current checkout, unless the programmer asks for a worktree; then create it with `EnterWorktree` and stay in it. If the checkout has unrelated uncommitted changes, say so before writing.
- **Orchestrated:** the feature has its worktree like any other (`SKILL.md` §2.3), and the orchestrator briefs **one** Implementer (`roles/implementer.md`) with: `Workflow: DIRECT. Follow <skill dir>/workflows/direct.md steps 1–6 yourself, writing code and tests; return blocking questions per protocols/agent-questions.md.` The orchestrator relays the questions, verifies the report and runs step 7.
