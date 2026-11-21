#!/usr/bin/env bash
# Installs the /feature and /feature-kit skills as standalone Claude Code skills.
#   ./install.sh            -> ~/.claude/skills/{feature,feature-kit,feature-lean}   (all your projects)
#   ./install.sh --project  -> ./.claude/skills/{feature,feature-kit,feature-lean}   (current project only)
#   add --force to replace an existing installation
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="$HOME/.claude/skills"
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --project) DEST="$PWD/.claude/skills" ;;
    --force)   FORCE=1 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

for skill in feature feature-kit feature-lean; do
  if [[ -e "$DEST/$skill" && $FORCE -ne 1 ]]; then
    echo "Already exists: $DEST/$skill (re-run with --force to replace it)" >&2
    exit 1
  fi
done

mkdir -p "$DEST"
for skill in feature feature-kit feature-lean; do
  rm -rf "${DEST:?}/$skill"
  cp -R "$SRC/$skill" "$DEST/$skill"
  echo "Installed to $DEST/$skill"
done
echo "Start a new Claude Code session and type: /feature <what you want to build>"
echo "or, to work by hand with the workflow's skills on demand: /feature-kit"
echo "or, for the lean pipeline (spec + edge cases, your answers, code and tests, one clean critic): /feature-lean <feature>"
