# Refinement Protocol

Find out what the programmer needs before choosing how to build it. The intent phase of each workflow finds gaps in what the request **says**: the reach of its broad statements, the ambiguity checklist, *Deepen the request*. Refinement starts from the **problem** the request serves, finds the context the agent lacks, and offers readings the programmer can recognize instead of having to spell out. It runs before the workflow is recommended, so the recommendation rests on the refined intent, not on the first wording.

## When it runs

At startup (`SKILL.md` §2 step 5), check whether the request is **ready**, from the request and the project context. It is not ready when any of these holds:
- it names a solution without the problem it solves ("add a cache", "use Redis"), and the repository does not make the problem evident;
- the outcome is not observable: you cannot say how the programmer would tell that it works;
- several readings with different results are plausible, and the repository evidence does not pick one;
- it depends on context only the programmer or a third party holds: users, volumes, deadlines, an external system's behavior, a decision taken elsewhere;
- the programmer asks for it (`/feature refine <request>`) or says they are not sure what they need.

Ready: say so in one line, with the evidence ("ready: the request names the problem, the outcome and the place"), and continue. `--no-refine` skips the check; record that it was skipped.

**Gate profiles.** Refinement is a conversation, not a gate, so it runs in every profile when the request is not ready: a wrong reading here costs the whole feature. In `auto`, one round at most; what stays open is decided with the reading the evidence supports best and recorded as *Decided by agent* (`protocols/gates.md` §When a gate is off).

**Who.** The session that talks to the programmer, orchestrator or executor; refinement is that conversation, so no subagent runs it. Context the repository can answer: look it up yourself when it takes a few files; otherwise brief the Repository Analyst with the exact questions.

## Steps

1. **Restate the request as a problem:** who has it, what happens today (the current behavior with evidence, the workaround they use), what changes for them when it is done (a signal they can observe), and why now. Mark the source of each part: the request (quoted), the repository (evidence), or your reading (to confirm). When the request names a solution, the problem it serves is the first question; the named solution stays as the programmer's preferred option, never dropped silently.
2. **List the context gaps:** what you would need to know to build the right thing. Each gap goes to one of three places:
   - the repository, the docs or a run can answer it: find the answer now and report it as a fact;
   - only the programmer knows: a question;
   - a third party knows (a user, another team, an external system's owner): name who, and what to ask them.
3. **Ask from the dimensions, not only from the words.** Go through: users and actors; trigger and frequency; volume and size; the cost of a wrong result; what exists already and earlier attempts; deadline or order with other work; what stays out; how the programmer will check the result. Keep a dimension only when its answer changes what gets built. Add question 1 of `knowledge/specification-guide.md` §Deepen the request (what a top professional would do that the request does not ask for).
4. **Offer readings.** When more than one reading survives, present two or three distinct ones, each with what would be built, what it leaves out and its relative cost, plus the **smallest version** that would already solve the problem. Use the decision format (`protocols/decisions.md`), with your recommendation labeled. The programmer may pick one, combine them or reject them all.
5. **Rounds.** At most five questions per round, ordered by how much the answer changes what gets built, each with your proposed answer and its evidence, so a plain "yes" is a valid reply. Record every answer that changes the intent as a statement (`templates/intent.md`). Stop when you can state the intent in a few sentences in the programmer's terms, every blocking gap is answered or assigned to someone, and the programmer confirms your restatement. Stop too when the programmer says so: what is open stays as questions. After three rounds without converging, say so and propose either the smallest version as a first increment (EVO) or a pause to gather the missing context.
6. **Output:**
   - the **consolidated intent, version 1**, confirmed by the programmer, with the *Refinement* section of `templates/intent.md`;
   - the **readiness verdict**: ready, with the evidence that feeds the workflow recommendation (for example, readings still open point to EVO; a fixed outcome with a wide reach points to SDD), and the criticality evidence that feeds the gate profile; or **blocked**, on whom, with what to ask them.

## Standalone: `/feature refine <request>`

Runs steps 1–6 without starting a feature: no worktree, no feature folder. The record (`templates/intent.md`, with the verdict) is saved at `$(git rev-parse --git-common-dir)/feature-workflow/refined/<slug>.md`: local to the clone, never committed. It ends with a question:
- **start now:** continue at `SKILL.md` §2 step 5, with the refined intent;
- **later:** `/feature refined <slug> [flags]` starts the feature from the record;
- **hand it to someone:** the record as a brief for another person, written as `knowledge/writing.md` describes.

When the feature starts, the record is copied into `intent.md` (or the card's *Intent*) and the local file is removed. DIRECT keeps no intent record: the confirmed intent goes in its report (`workflows/direct.md` step 6), or in its card when the programmer asked for one.

## Afterwards

- The intent gate (SDD 3, EVO 3) does not ask again what refinement settled: it shows version 1 and only what changed since (new statements, the analyst's findings).
- The Specification Writer, the Test Designer and the critic receive the refined intent as they receive any intent record.
- Refinement does not choose the approach. An implementation choice that came up goes to the approach gate as an option.

## Do not

- Ask what the repository can answer, or a question whose answer would not change what gets built.
- Widen the scope: readings and professional practice are proposals; nothing enters without the programmer's word (`protocols/decisions.md` rule 9).
- Replace the programmer's named solution with yours without saying so.
- Build during refinement: only read-only probes.
