#!/usr/bin/env bash
# scripts/check_deletions.sh
# Deletion guard: fails when a canonical v02/<dict>/<dict>.txt source is
# deleted or renamed away (diff statuses D / R). These files are the input to
# the whole generation pipeline; losing one silently disables every downstream
# gate for that dictionary, so the loss must be explicit.
#
# Acknowledge an intentional deletion by exporting
#   CSL_ORIG_ACK_DELETION="v02/<dict>/<dict>.txt ..."   (space/comma separated)
# or CSL_ORIG_ACK_DELETION=all. In CI, acks are read from PR body / commit
# message lines of the form:  ack-deletion: v02/<dict>/<dict>.txt
#
# Usage:
#   scripts/check_deletions.sh --cached          # pre-commit: index vs HEAD
#   scripts/check_deletions.sh <base> [<head>]   # CI: endpoint diff (default head=HEAD)

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [ "${1:-}" = "--cached" ]; then
    range_args=(--cached)
else
    base="${1:?usage: check_deletions.sh --cached | <base> [<head>]}"
    head_rev="${2:-HEAD}"
    range_args=("$base" "$head_rev")
fi

deleted=()
while IFS=$'\t' read -r st p1 p2; do
    [ -n "$p1" ] || continue
    case "$st" in
        D*) candidate="$p1" ;;           # deletion
        R*) candidate="$p1" ;;           # rename source = old path going away
        *)  continue ;;
    esac
    rest="${candidate#v02/}"
    dir="${rest%%/*}"
    tail="${rest#*/}"
    if [ "$rest" != "$candidate" ] && [ -n "$dir" ] && [ "$tail" = "$dir.txt" ]; then
        deleted+=("$candidate")
    fi
done < <(git diff --name-status --diff-filter=DR "${range_args[@]}" -- 'v02/')

if [ "${#deleted[@]}" -eq 0 ]; then
    exit 0
fi

ack="${CSL_ORIG_ACK_DELETION:-}"
ack_all=0
case "$ack" in
    1|all|ALL|yes|YES) ack_all=1 ;;
esac

remaining=()
for p in "${deleted[@]:-}"; do
    [ -n "$p" ] || continue
    ok=0
    if [ "$ack_all" -eq 1 ]; then
        ok=1
    else
        for a in ${ack//,/ }; do
            if [ "$a" = "$p" ]; then ok=1; fi
        done
    fi
    if [ "$ok" -ne 1 ]; then
        remaining+=("$p")
    fi
done

if [ "${#remaining[@]}" -gt 0 ]; then
    echo "ERROR [deletion-guard]: canonical source(s) deleted/renamed away:"
    for p in "${remaining[@]}"; do
        echo "  D/R $p"
    done
    echo "  v02/<dict>/<dict>.txt is the canonical source consumed by the generation pipeline;"
    echo "  deleting it silently disables every gate for that dictionary."
    echo "  To acknowledge intentionally, rerun with:"
    echo "    CSL_ORIG_ACK_DELETION=\"${remaining[*]}\" git commit ..."
    echo "  (or CSL_ORIG_ACK_DELETION=all; in CI put 'ack-deletion: <path>' in the PR body or a commit message)."
    exit 1
fi

echo "deletion-guard: acknowledged canonical deletion/renaming: ${deleted[*]}"
exit 0
