# Agent Questions Protocol

Subagents cannot talk to the programmer. When one needs an answer only the programmer can give, it stops and returns its questions to the orchestrator, which relays them, records the answers and resumes **the same agent** with its context intact. This matters most in specification and planning, where a guessed answer becomes a requirement or an architecture.

It applies at every intensity, to the Repository Analyst, Specification Writer, Planner, Implementer and Tester. Critics and verifiers never ask: ambiguity is a finding (`roles/verifier.md`, verdict AMBIGUOUS).

## For the agent

**Check before asking.** Search the repository, the handoff and the artifacts it references first. A question that evidence answers is not asked; cite the evidence instead.

**Blocking or not.**
- **Blocking:** the answer changes what you are about to produce (a requirement, scope, observable behavior, a constraint, the set of viable approaches, the expected result of a test) and no confirmed source settles it. A question whose answer changes the output for a valid input is blocking, even if an acceptance criterion could be written around it: never weaken a criterion to avoid asking. Stop at the first safe point: finish nothing that depends on the answer. Work independent of it may continue first.
- **Non-blocking:** you can continue under an explicit assumption without producing work that would have to be thrown away. Continue, label the assumption **Hypothesis** where it is used, and list it.

Never fill a gap by inventing a requirement, a business rule, an expected result or a preference of the programmer.

**Return format.** Your return starts with the status line, then the usual summary.

```
STATUS: QUESTIONS            (or DONE)
Work so far: <what is finished and where it is saved; what is not started>

Q-<n> [blocking | non-blocking] <the question, answerable without reading anything else>
  Why it matters: <what changes in your output depending on the answer>
  Evidence: <request quote · spec ID · path:line>
  Options: <closed question: alternatives in the neutral format, alphabetical> | open
  Assumption used: <non-blocking only: what you assumed and where>
```

- At most 7 questions per return. Blocking first, then the rest; within each group, in the order the work depends on them. No preference among options (`protocols/neutral-decisions.md`).
- If you hit more than 7, return the 7 that unblock the most and say how many remain.

**When resumed with answers.** Continue from where you stopped. Do not redo finished work. Replace every assumption the answers contradict, and say which ones in your next return. New questions follow the same format, numbered on from the last.

## For the orchestrator

1. **Filter.** Answer from evidence yourself any question the repository or the artifacts settle, and send the evidence back with the other answers. Remove any recommendation or ordering by preference the agent slipped into the options.
2. **Record before presenting.** Spec questions go to `specification.md` §Open questions, with their ID, who asked, and *Pending*. Choices between options go to `decisions/D-NNN-<topic>.md` with status **Pending** and the full option block. Note in `handoff.md` the agent's ID, so that it can be resumed. An answer such as "B" must be resolvable from disk in any later session (`protocols/orchestrator-memory.md`).
3. **Present.** Blocking questions are a ⛔ gate for **that feature only**; non-blocking ones go to the feature's next gate, unless the programmer asked to see them immediately. Batch the questions of one feature in one message, tagged `[slug] Q-n (Planner)`. Keep their meaning; rewrite only to make them self-contained, never to steer.
4. **Record the answer** in the same place: the programmer's words, the date, and *Answered*. A *don't know* or *later* is recorded as *Deferred*; then ask how the agent proceeds: with the item out of scope, or under the stated assumption as a Hypothesis.
5. **Resume the same agent** with `SendMessage` to its ID: only the answers, by Q-ID, plus evidence for the questions you answered yourself, and "Continue from where you stopped." Do not repeat the brief.
   - If it cannot be resumed (a new session, the agent no longer exists, an error), launch a new agent with the same brief plus `Previous attempt: <its Work so far>` and the answers. Log it in `delegations.md` with outcome *resumed in a new agent*.
6. **Answers that change approved work.** An answer that changes an approved requirement is a spec change: bump the version and add a change-log row citing the Q-ID. An answer that changes an approved plan is a decision record. Approved work is never changed silently.

In a hierarchy (`protocols/hierarchy.md`), a sub-orchestrator relays a question with options as `DECISION-REQUEST` and an open one as `QUESTION`, keeping the feature tag and Q-ID.
