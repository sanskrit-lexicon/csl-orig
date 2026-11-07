#!/usr/bin/env bash
# scripts/install-hooks.sh
# One-time setup: point git at the tracked .githooks/ directory.
#
#   git config core.hooksPath .githooks
#
# A RELATIVE hooks path is resolved against the repository each time, so the
# guard survives clone moves (the old absolute symlink went stale the moment
# a clone was relocated, and git silently skips a hook whose target is
# missing) and works in linked worktrees.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
HOOK_SRC="$REPO_ROOT/.githooks/pre-commit"

if [ ! -f "$HOOK_SRC" ]; then
    echo "ERROR: $HOOK_SRC not found. Are you in the right repo?"
    exit 1
fi

chmod +x "$HOOK_SRC"

# Clean up the legacy install (absolute symlink in .git/hooks) so the guard
# can never be silently skipped by a dangling link.
legacy="$REPO_ROOT/.git/hooks/pre-commit"
if [ -L "$legacy" ]; then
    if [ -e "$legacy" ] && [ "$(readlink "$legacy")" != "$HOOK_SRC" ]; then
        backup="${legacy}.bak.$(date +%Y%m%d%H%M%S)"
        echo "Backing up unexpected symlink $legacy -> $(readlink "$legacy") to $backup"
        mv "$legacy" "$backup"
    else
        rm -f "$legacy"
        echo "Removed legacy hook symlink: $legacy"
    fi
elif [ -e "$legacy" ]; then
    backup="${legacy}.bak.$(date +%Y%m%d%H%M%S)"
    echo "Backing up existing hook $legacy to $backup (pre-commit framework shim?)"
    mv "$legacy" "$backup"
fi

git config core.hooksPath .githooks
echo "Installed: core.hooksPath = .githooks (relative; survives clone moves)."
echo "Note: if you also use the 'pre-commit' framework, re-run 'pre-commit install'"
echo "after this — recent versions install into core.hooksPath as well."
echo "Uninstall: git config --unset core.hooksPath"
