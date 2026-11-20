#!/usr/bin/env bash
# Installs the /feature skill as a standalone Claude Code skill.
#   ./install.sh            -> ~/.claude/skills/feature   (all your projects)
#   ./install.sh --project  -> ./.claude/skills/feature   (current project only)
#   add --force to replace an existing installation
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/feature"
DEST="$HOME/.claude/skills/feature"
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --project) DEST="$PWD/.claude/skills/feature" ;;
    --force)   FORCE=1 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [[ -e "$DEST" && $FORCE -ne 1 ]]; then
  echo "Already exists: $DEST (re-run with --force to replace it)" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
echo "Installed to $DEST"
echo "Start a new Claude Code session and type: /feature <what you want to build>"
