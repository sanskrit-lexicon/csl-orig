#!/usr/bin/env bash
# scripts/install-hooks.sh
# One-time setup: symlinks the tracked hook into .git/hooks/.
#
# Run from anywhere inside the repo:
#   sh scripts/install-hooks.sh

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
HOOK_SRC="$REPO_ROOT/hooks/pre-commit"
HOOK_DST="$REPO_ROOT/.git/hooks/pre-commit"

if [ ! -f "$HOOK_SRC" ]; then
    echo "ERROR: $HOOK_SRC not found. Are you in the right repo?"
    exit 1
fi

chmod +x "$HOOK_SRC"

if [ -e "$HOOK_DST" ] && [ ! -L "$HOOK_DST" ]; then
    # A non-symlink hook already exists (e.g. installed by pre-commit library).
    # Back it up rather than silently overwriting.
    backup="${HOOK_DST}.bak.$(date +%Y%m%d%H%M%S)"
    echo "Backing up existing hook to: $backup"
    mv "$HOOK_DST" "$backup"
fi

ln -sf "$HOOK_SRC" "$HOOK_DST"
echo "Installed: $HOOK_DST -> $HOOK_SRC"
