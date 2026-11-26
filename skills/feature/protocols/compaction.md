# Compaction of the Orchestrator Session

Claude Code summarizes the orchestrator session when it compacts. Two things decide what survives: the instructions the summary receives, and what is put back into the context afterwards. This file is the one source of both. The threshold and the proactive suggestion are in `SKILL.md` §3.

## Compact Instructions

Claude Code reads a section named `Compact Instructions` in the programmer's `CLAUDE.md` and passes it to the summary. The skill never edits `CLAUDE.md`: the programmer pastes the text below (the README shows where). The text is the block under this line, verbatim.

```markdown
## Compact Instructions

When this session is compacted, keep, for every active feature: its slug, workflow, role of the session, phase or step, and the gate or decision it is waiting on; the decision IDs (D-NNN) and the programmer's statement IDs (S-NNN) with one line each; every agent ID with its last reported token count; every pending confirmation of the programmer (integration, cleanup) and every pending question to the programmer; and the paths of the feature folders and worktrees.

Drop: tool outputs, agent reports that are already saved in the feature folder (keep only the path and the verdict), diffs, file contents and test logs. They can be read again from the artifacts.
```

The summary is lossy by nature. What it keeps is a convenience; the source of truth stays `state.md`, the project memory and the claims (`protocols/orchestrator-memory.md`, `protocols/hierarchy.md` §Claims).

## State after a compaction

The script `scripts/post_compact_state.py` runs as a `SessionStart` hook with the matcher `compact`, so it runs after every compaction, manual or automatic. It prints, as additional context for the model:

- the Portfolio section of the project memory (`$(git rev-parse --git-common-dir)/feature-workflow/memory.md`);
- for each claim with status `Active` (`$(git rev-parse --git-common-dir)/feature-workflow/claims/*.json`), the claim's `state.md` in its `featureFolder`, or, when the folder has no `state.md`, the *State* section of its `feature.md` card (EVO as executor, DIRECT with a card).

It acts only for a session that used the feature skill. When the event carries `transcript_path`, it scans that transcript line by line and acts only if it finds an invocation of the skill (`/feature` command, the skill's "Base directory" line, or a `Skill` call with `feature`; `feature-lean` does not count). When the event has no readable `transcript_path`, it falls back to the claims: it acts only if at least one claim is `Active`. In every other case it prints nothing.

It reads files only, never writes, and prints nothing when there is nothing to report, when the directory is not a git repository, or when the input is not what it expects. Each file is cut to a fixed size; a cut is marked and names the file to read in full. The hook is optional: without it, the orchestrator recovers by re-reading `state.md` and the memory (`SKILL.md` §3).

The programmer enables it: with the plugin, `hooks/hooks.json` does it; with a standalone install, they add the `SessionStart` entry shown in the README to their `settings.json`.
