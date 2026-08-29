#!/usr/bin/env bash
# scripts/test_pre_commit_guard.sh
# Scenario suite for the csl-orig commit guard (.githooks/pre-commit + scripts).
#
# Builds a throwaway mini-clone (fixture) with a stub csl-pywork sibling, then
# drives `git commit` through the real hook for each guard scenario:
#   S1 control            — fully staged valid change passes
#   S2 O6 partial-staging — broken STAGED blob fails even when worktree looks fine
#   S3 O6 partial-staging — staged/worktree drift fails stage 2 (pipeline reads worktree)
#   S4 O5 zero-LEND       — canonical file with zero <LEND> lines fails
#   S6 O3 rename          — renaming a canonical source away fails unacked
#   S5 O3/O4 deletion     — deleting a canonical source fails unacked, passes acked
#   S7 O10 clone move     — relative core.hooksPath still fires after the clone moves
#
# Usage: bash scripts/test_pre_commit_guard.sh   (from the repo, any cwd)

set -uo pipefail

SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/csl-orig-hook-test.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
FAILED=0

note() { printf '\n=== %s ===\n' "$*"; }
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; FAILED=1; }

# A commit that must FAIL, with marker text expected in its output.
expect_fail() { # name marker cmd...
    local name="$1" marker="$2"; shift 2
    local out rc
    out="$(git -C "$FIX" commit -q -m "$name" 2>&1)"
    rc=$?
    if [ "$rc" -ne 0 ] && printf '%s\n' "$out" | grep -q "$marker"; then
        pass "$name (rejected, marker matched)"
    else
        fail "$name (rc=$rc, expected rejection containing '$marker')"
        printf '%s\n' "$out" | sed 's/^/    | /'
    fi
    git -C "$FIX" reset -q --hard HEAD
}

# A commit that must SUCCEED.
expect_pass() { # name cmd...
    local name="$1"; shift
    local out rc
    out="$(git -C "$FIX" commit -q -m "$name" 2>&1)"
    rc=$?
    if [ "$rc" -eq 0 ]; then
        pass "$name"
    else
        fail "$name (rc=$rc, expected clean commit)"
        printf '%s\n' "$out" | sed 's/^/    | /'
    fi
}

# ── Build the fixture ────────────────────────────────────────────────────────
note "building fixture in $TMP"
FIX="$TMP/fixture"
mkdir -p "$FIX"
if ! git -C "$FIX" init -q -b main 2>/dev/null; then
    git -C "$FIX" init -q
    git -C "$FIX" symbolic-ref HEAD refs/heads/main
fi
git -C "$FIX" config user.email hook-test@example.com
git -C "$FIX" config user.name hook-test

cp -R "$SRC_ROOT/.githooks" "$FIX/.githooks"
chmod +x "$FIX/.githooks/pre-commit"
mkdir -p "$FIX/scripts"
cp "$SRC_ROOT/scripts/check_encoding.py" \
   "$SRC_ROOT/scripts/check_generate_dict.sh" \
   "$SRC_ROOT/scripts/check_deletions.sh" "$FIX/scripts/"

# Stub csl-pywork sibling: stage-2 prerequisite exists, pipeline is a no-op.
mkdir -p "$TMP/csl-pywork/v02" "$TMP/td1" "$TMP/td2"
printf '#!/bin/sh\nexit 0\n' > "$TMP/csl-pywork/v02/generate_dict.sh"
chmod +x "$TMP/csl-pywork/v02/generate_dict.sh"

# Seed two canonical sources (valid <L>/<LEND> format).
for d in td1 td2; do
    mkdir -p "$FIX/v02/$d"
    printf '<L>1<k1>a\nbody one\n<LEND>\n<L>2<k1>b\nbody two\n<LEND>\n' > "$FIX/v02/$d/$d.txt"
done
git -C "$FIX" add v02 scripts .githooks
git -C "$FIX" config core.hooksPath .githooks
out="$(git -C "$FIX" commit -q -m seed 2>&1)"
if [ $? -ne 0 ]; then
    fail "fixture seed commit (hook rejected the valid seed)"
    printf '%s\n' "$out" | sed 's/^/    | /'
    exit 1
fi
pass "fixture seed commit (hook accepted valid seed)"

# ── S1 control: fully staged valid change passes ─────────────────────────────
note "S1 control — fully staged valid change passes"
printf '<L>3<k1>c\nbody three\n<LEND>\n' >> "$FIX/v02/td1/td1.txt"
git -C "$FIX" add v02/td1/td1.txt
expect_pass "S1 control"

# ── S2 (O6): broken STAGED blob must fail even though the worktree is fine ──
note "S2 O6 partial-staging — broken staged blob, clean worktree"
printf '<L>4<k1>d\n\377\376 broken utf8 bytes\n<LEND>\n' > "$FIX/v02/td1/td1.txt"
git -C "$FIX" add v02/td1/td1.txt
printf '<L>4<k1>d\nvalid worktree bytes\n<LEND>\n' > "$FIX/v02/td1/td1.txt"
expect_fail "S2 O6 staged-blob check" "invalid UTF-8"

# ── S3 (O6): staged/worktree drift must fail stage 2 ─────────────────────────
note "S3 O6 partial-staging — drift between staged blob and worktree"
printf '<L>5<k1>e\nstaged version\n<LEND>\n' > "$FIX/v02/td1/td1.txt"
git -C "$FIX" add v02/td1/td1.txt
printf '<L>5<k1>e\nUNSTAGED worktree edit\n<LEND>\n' > "$FIX/v02/td1/td1.txt"
expect_fail "S3 O6 stage-2 drift guard" "differs from worktree"

# ── S4 (O5): zero <LEND> lines must fail ─────────────────────────────────────
note "S4 O5 zero-LEND — vacuous pass is gone"
printf '<L>6<k1>f\nno end tag anywhere\n' > "$FIX/v02/td1/td1.txt"
git -C "$FIX" add v02/td1/td1.txt
expect_fail "S4 O5 zero-LEND" "zero <LEND>"

# ── S6 (O3): renaming a canonical source away must fail unacked ─────────────
note "S6 O3 rename — canonical source renamed away, unacked"
git -C "$FIX" mv v02/td1/td1.txt v02/td1/td1renamed.txt
expect_fail "S6 O3 canonical rename" "deleted/renamed away"

# ── S5 (O3/O4): deleting a canonical source fails unacked, passes acked ─────
note "S5 O3/O4 deletion — canonical source deleted, unacked"
git -C "$FIX" rm -q v02/td1/td1.txt
expect_fail "S5 O3 canonical deletion" "deleted/renamed away"

note "S5b deletion acknowledged via CSL_ORIG_ACK_DELETION"
git -C "$FIX" rm -q v02/td1/td1.txt
out="$(CSL_ORIG_ACK_DELETION="v02/td1/td1.txt" git -C "$FIX" commit -q -m "S5b acked deletion" 2>&1)"
if [ $? -eq 0 ]; then
    pass "S5b acked deletion"
else
    fail "S5b acked deletion (expected commit to succeed)"
    printf '%s\n' "$out" | sed 's/^/    | /'
fi
# Restore td1 for later scenarios from the pre-deletion commit.
mkdir -p "$FIX/v02/td1"
git -C "$FIX" show 'HEAD^:v02/td1/td1.txt' > "$FIX/v02/td1/td1.txt"
git -C "$FIX" add v02/td1/td1.txt
expect_pass "S5c td1 restored"

# ── S7 (O10): relative core.hooksPath survives a clone move ─────────────────
note "S7 O10 clone move — guard still fires after the fixture directory moves"
if [ "$(git -C "$FIX" config core.hooksPath)" != ".githooks" ]; then
    fail "S7 setup (core.hooksPath is not the relative '.githooks')"
fi
mv "$FIX" "$FIX-moved"
FIX="$FIX-moved"
printf '<L>7<k1>g\n\377\376 broken after move\n<LEND>\n' > "$FIX/v02/td2/td2.txt"
git -C "$FIX" add v02/td2/td2.txt
printf '<L>7<k1>g\nvalid worktree bytes\n<LEND>\n' > "$FIX/v02/td2/td2.txt"
expect_fail "S7 O10 hook fires after move" "invalid UTF-8"

# ── Verdict ──────────────────────────────────────────────────────────────────
printf '\n'
if [ "$FAILED" -eq 0 ]; then
    echo "ALL SCENARIOS PASSED"
else
    echo "SCENARIO FAILURES PRESENT"
fi
exit "$FAILED"
