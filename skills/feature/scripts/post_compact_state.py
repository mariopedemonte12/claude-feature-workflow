#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from pathlib import Path

MAX_CHARS = 6000
STATE_HEADING = re.compile(r"^## State\s*$", re.MULTILINE)
PORTFOLIO_HEADING = re.compile(r"^## Portfolio\s*$", re.MULTILINE)
NEXT_HEADING = re.compile(r"^## ", re.MULTILINE)


def read_event():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return {}
    return event if isinstance(event, dict) else {}


def workflow_directory(working_directory):
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=working_directory, capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return (Path(working_directory) / result.stdout.strip() / "feature-workflow").resolve()


def section(text, heading):
    start = heading.search(text)
    if not start:
        return None
    following = NEXT_HEADING.search(text, start.end())
    return text[start.start():following.start() if following else len(text)].strip()


def truncated(text, path):
    if len(text) <= MAX_CHARS:
        return text
    return f"{text[:MAX_CHARS]}\n[cut at {MAX_CHARS} characters: read {path} in full]"


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def feature_state(claim):
    folder = Path(claim["featureFolder"])
    state = read_text(folder / "state.md")
    if state is not None:
        return folder / "state.md", state
    card = read_text(folder / "feature.md")
    card_state = section(card, STATE_HEADING) if card else None
    return (folder / "feature.md", card_state) if card_state else (None, None)


def active_claims(directory):
    for path in sorted((directory / "claims").glob("*.json")):
        try:
            claim = json.loads(read_text(path) or "")
        except ValueError:
            continue
        if isinstance(claim, dict) and claim.get("status") == "Active" and isinstance(claim.get("featureFolder"), str):
            yield claim


def blocks(directory):
    memory = read_text(directory / "memory.md")
    portfolio = section(memory, PORTFOLIO_HEADING) if memory else None
    if portfolio:
        yield truncated(portfolio, directory / "memory.md")
    for claim in active_claims(directory):
        path, state = feature_state(claim)
        if state:
            yield f"### Feature {claim.get('slug', '?')} ({path})\n{truncated(state.strip(), path)}"


def main():
    event = read_event()
    if event.get("source", "compact") != "compact":
        return
    directory = workflow_directory(event.get("cwd") or ".")
    if directory is None:
        return
    parts = list(blocks(directory))
    if not parts:
        return
    context = "State recovered after the compaction, read from the files (not from the summary):\n\n" + "\n\n".join(parts)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))


if __name__ == "__main__":
    main()
