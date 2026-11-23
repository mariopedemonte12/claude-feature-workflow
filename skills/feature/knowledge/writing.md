---
name: writing
kind: guide
summary: How the agent writes to the programmer and writes documentation, PR descriptions, commit messages and reports
use-in: [general]
---
# Writing

Write so a tired engineer understands on the first read. This guide covers every message to the programmer (gates, reports, status, questions) and every document the work produces: documentation, READMEs, PR descriptions, commit messages, the feature's reports. Adapted from the `unslop` and `technical-writing` skills of pstack (github.com/cursor/plugins, MIT). Messages to the programmer are in the programmer's language; documents follow the project's language.

## Every text

- **Cut every word that does no work.** "In order to" becomes "to"; delete "it is important to note that", "cabe destacar que", "es importante mencionar".
- **The plain, everyday word:** "use", not "utilize" or "leverage"; "usar", no "utilizar" ni "apalancar".
- **The real name:** the actual symbol, file, flag or command, not a synonym or a description of it. One name per thing, repeated; never a second name for variety.
- **One idea per sentence.** Split a sentence the reader has to reread. Mix lengths: keep a long sentence that carries one thought.
- **Say who does what,** in the active voice, unless the actor is unknown or beside the point.
- **Say what it does, not how it feels:** the mechanism, the number, the file. "A column rename fails the build", not "schema changes can cause issues". Cut a sentence that could appear unchanged in another project.
- **At most one hedge** per claim ("may", "puede"). Uncertainty goes in the evidence status (Confirmed, Hypothesis, Unknown), not in adverbs.
- **Every "it", "this", "esto", "lo cual"** points at one obvious thing, never at a whole clause.
- **No AI tells:**
  - vocabulary such as additionally, crucial, delve, enhance, foster, pivotal, robust, seamless, showcase, testament, underscore, vibrant; in Spanish, "crucial", "fundamental", "robusto", "potenciar", "sin fisuras", "en el panorama de";
  - "serves as", "stands as", "boasts": say "is" or "has" ("es", "tiene");
  - "not just X, but Y" ("no solo X, sino también Y"): state the point;
  - ideas forced into threes; "from X to Y" when X and Y are not on a real scale;
  - trailing "-ing" phrases that add no fact ("…, ensuring quality"), and their Spanish twin, the gerund of consequence ("…, garantizando la calidad");
  - vague attributions ("experts believe"): name the source or delete;
  - metaphors, aphorisms and personified code where a literal phrase exists. Established technical terms (harness, surface, scaffolding) are literal and stay;
  - praise or agreement openers ("Great question", "¡Excelente!"), chatbot closers ("I hope this helps", "Avísame si…"), generic conclusions;
  - decorative emojis; bold on every noun; a bold label that restates its line.
- **Punctuation:** em dashes are not connectors; use a period or a comma. A colon goes before a list or an example. Parentheses hold a complete unit. Sentence-case headings. Straight quotes in code and paths.
- **Lists:** numbered for sequences, bullets for the rest, introduced by a complete sentence, items parallel.

## Documents: one mode each

Pick the mode before writing; one document, one mode. Split and link instead of mixing (Diátaxis):

| Mode | For | How |
| --- | --- | --- |
| Tutorial | Learning by doing | Say what the learner will build; every step produces a visible result and you say what they should see |
| How-to | Steps to a goal | Assume competence; action only; name the guide by the task; conditions before the step they guard |
| Reference | Facts for lookup | Describe only; dry, complete and exact; mirror the structure of the thing described |
| Explanation | Understanding and why | One bounded topic; design decisions, history, constraints, alternatives. Opinion belongs here |

**Instructions** are commands, one per sentence, the condition or warning before the step, the common case first. Never "simply", "easy" or "quickly" in a procedure. Code in code font; UI elements in bold. Every count, path or tree in a document is true at the commit that lands it, with the command that regenerates it when there is one.

## PR descriptions and commit messages

- **A PR body is a briefing a reviewer reads in under a minute:** what changes for the user, why, how it was verified (the commands and their real results), what is left out or risky. One primary number when there is one (`knowledge/measurement.md`). Link logs, run lists and tables; do not paste them.
- **A commit message:** a subject that says what changes, in the project's convention; a body only for why and what is not obvious from the diff.
- Strip anything private before text goes anywhere public.

## Messages to the programmer

The rules above, plus `SKILL.md` §5 *How a gate message reads* for gates, status and catch-ups. Write what changed **for the programmer**, not how you did it: "the tests pass", not "CI is green after rebasing onto a1b2c3d". Leave out hashes, paths, commands and counts unless the programmer needs one to act.
