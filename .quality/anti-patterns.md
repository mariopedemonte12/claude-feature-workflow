# Anti-pattern registry

Format and process: `skills/feature/protocols/anti-pattern-registry.md`.

### AP-001 · Restated copy of a workflow rule
- **Status:** Active · since 2026-11-25 (workflow-learnings, workflow-learnings/D-003)
- **Scope:** skills/**, README.md, docs/** (except docs/features/** and docs/master-prompt.md)
- **Smell:** a file outside a rule's single source restates the rule's conditions, values or consequences (verbatim or paraphrased) instead of pointing to the source (`<file>` §Section).
- **Why it hurts here:** a fix made in one copy leaves the others disagreeing; in the last run, fix rounds introduced Majors in copies they did not touch.
- **Instead:** point to the source: `protocols/review-cycle.md` §R2 · The cycle. A mention may name the rule or an event it covers (for hard stops: only next to a pointer to `protocols/gates.md` §Hard stops), never its conditions or values. A nuance the source lacks is merged into the source.
- **Example:** ✗ `a new critic, within the feature's cap of 3 critic rounds` · ✓ `a new critic, within the round cap (protocols/review-cycle.md §R2 · The cycle, Stop when)`
- **Detection:** automated · `scripts/rule_copies.py` with the rules, sources and fingerprints of `scripts/rule_copies.json` (checks "rule copies (skills)" and "rule copies tests")
- **Enforced by:** check on skills/** · proven on 206cadc (the copies of the review-cap, review-level and hard-stop rules at that commit fail the check; the consolidated tree passes). README.md and docs/** are enforced by review only until they are consolidated (the default scan of the script still reports their copies). Review also covers paraphrased copies the fingerprints miss: for each rule a diff touches, the critic runs the concept searches recorded in that rule's `searches` and reads each hit; a hit that restates the rule is a finding, and a missing fingerprint for it is a candidate to extend `rule_copies.json`.
- **Seen:** earlier runs of the feature workflow on this repository (fix rounds introduced Majors in desynchronized copies) · workflow-learnings 2026-11-25 (duplication map of the repository analyst)
