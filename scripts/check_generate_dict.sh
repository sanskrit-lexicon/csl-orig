#!/usr/bin/env bash
# scripts/check_generate_dict.sh
# Pre-commit hook: for each dict with staged changes under v02/<dict>/,
# runs the full generate_dict.sh pipeline from ../csl-pywork/v02 and
# fails if any red-line (ANSI \033[31m) output is produced.
#
# Called by pre-commit with the list of staged file paths as arguments
# (pass_filenames: true).  The outdir convention matches the project:
#   cd ../csl-pywork/v02 && sh generate_dict.sh <dict> ../../<dict>
# which targets the sibling directory /path/to/sanskrit-lexicon/<dict>.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYWORK_V02="$REPO_ROOT/../csl-pywork/v02"

# ---------------------------------------------------------------------------
# Prerequisite check — hard block if csl-pywork is absent
# ---------------------------------------------------------------------------
if [ ! -d "$PYWORK_V02" ]; then
    echo "ERROR [generate-dict-check]: ../csl-pywork/v02 not found."
    echo "  Expected at: $PYWORK_V02"
    echo "  csl-pywork must be a sibling of csl-orig."
    exit 1
fi

# ---------------------------------------------------------------------------
# Collect the unique dict names from staged v02/<dict>/... paths
# (bash 3.2-compatible — no associative arrays)
# ---------------------------------------------------------------------------
dicts=()
while IFS= read -r dict; do
    dicts+=("$dict")
done < <(
    for f in "$@"; do
        if [[ "$f" =~ ^v02/([^/]+)/ ]]; then
            echo "${BASH_REMATCH[1]}"
        fi
    done | sort -u
)

if [ "${#dicts[@]}" -eq 0 ]; then
    # Nothing under v02/<dict>/ was staged — nothing to do.
    exit 0
fi

# ---------------------------------------------------------------------------
# Run the pipeline for each affected dict
# ---------------------------------------------------------------------------
overall_exit=0

for dict in "${dicts[@]}"; do
    outdir_abs="$REPO_ROOT/../$dict"   # absolute path to target dir
    outdir_rel="../../$dict"           # relative path as seen from csl-pywork/v02

    echo ""
    echo "=== [generate-dict-check] dict='$dict' ==="

    if [ ! -d "$outdir_abs" ]; then
        echo "ERROR: output directory does not exist: $outdir_abs"
        echo "  Cannot run generate_dict.sh for '$dict' — pre-build the target first."
        overall_exit=1
        continue
    fi

    # Run the full pipeline; capture stdout+stderr (ANSI codes are always
    # emitted by generate_dict.sh regardless of tty status).
    pipeline_output=$(cd "$PYWORK_V02" && sh generate_dict.sh "$dict" "$outdir_rel" 2>&1) || true

    # Detect red lines: generate_dict.sh marks errors with \033[31m ... \033[0m
    red_lines=$(printf '%s\n' "$pipeline_output" | grep -F $'\033[31m' || true)

    if [ -n "$red_lines" ]; then
        echo "FAIL: generate_dict.sh produced error (red) output for '$dict':"
        echo "------"
        # Strip ANSI codes for cleaner display in pre-commit's output
        printf '%s\n' "$red_lines" | sed $'s/\033\\[[0-9;]*m//g'
        echo "------"
        overall_exit=1
    else
        echo "OK: no red lines for '$dict'."
    fi
done

echo ""
exit $overall_exit
