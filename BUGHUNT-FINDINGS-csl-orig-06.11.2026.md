# BUGHUNT-FINDINGS — csl-orig — 06-11-2026

_Created: 06-11-2026 · Last updated: 06-11-2026_

**Nightly bug hunt (MG ruling 26-09-2026: nightly, one repo, auto-fix HIGH).**
Repo: [sanskrit-lexicon/csl-orig](https://github.com/sanskrit-lexicon/csl-orig) (data store; code surface = `scripts/`, `.githooks/`, `.github/workflows/`).
Scope: static hunt over CODE only — vendored copies, lockfiles, node_modules, and the `v02/` data giants skipped. Read-only hunt; report landed via PR off `origin/main` (base `fc1f5da`).

**Elapsed: ~18 min wall (hunt + live verification + report landing).**
**Verdict: 0 HIGH · 1 MEDIUM · 3 LOW. No auto-fix this run (fix lane is HIGH-code-only); no GTD row (no HIGH credential/infra finding — the secret sweep came back clean).**

## Ranked findings

### 🟠 MEDIUM-1 — Shell-injection shape + unpinned third-party action in the StarDict sync workflow

**File:** [`update-stardict.yml:87`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/update-stardict.yml#L87) (injection point) · [`update-stardict.yml:28`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/update-stardict.yml#L28) (supply chain)

Two compounding issues in one workflow that later runs steps holding `secrets.PAT_TOKEN` with `contents: write` on two external repos:

1. **CWE-78 in Actions** — a GitHub expression is interpolated *directly into the shell command* instead of an env var:
   ```yaml
   CHANGED_DICTS=$(echo "${{ steps.changed-files.outputs.all_changed_files }}" | tr ' ' '\n' | grep '^v02/' | awk -F'/' '{print $2}' | sort -u)
   ```
   `all_changed_files` derives from diff **file paths**; a path containing shell metacharacters executes in the runner. This is the exact hardening-guide violation class GitHub calls out for `run:` blocks.
2. **Unpinned floating-tag third-party action** — `tj-actions/changed-files@v47` is not commit-SHA-pinned. The same action family was compromised in March 2025 (CVE-2025-30066 — tag retargeted to dump runner secrets); a retargeted `@v47` tag is the same blast radius, here with a PAT in scope downstream.

**Live evidence (run this session):** the line at `L87` read from a fresh `origin/main` checkout. Exploitability is bounded: the workflow fires on `push` to `main` only, so a hostile *filename* requires a maintainer-merged commit — hence MEDIUM, not HIGH. Minimal repro of the interpolation shape (local, harmless):

```bash
touch 'x$(touch /tmp/pwn-marker).txt'; echo "$(ls x*.txt)" | sh -c 'cat >/dev/null; ls /tmp/pwn-marker' # marker exists → interpolation reached sh
```

**Recommended fix (not auto-applied — MEDIUM):** route the output through `env:` (`env: ALL_CHANGED: ${{ steps.changed-files.outputs.all_changed_files }}`, then `echo "$ALL_CHANGED" | …`) and SHA-pin `tj-actions/changed-files` (or replace with `git diff --name-only ${{ github.event.before }} ${{ github.sha }}`, which needs no third-party action at all — `fetch-depth: 2` is already set).

### 🟡 LOW-1 — Bot commit email is malformed (missing `@`) in the StarDict sync workflow

**File:** [`update-stardict.yml:68`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/update-stardict.yml#L68)

```yaml
git config --global user.email "drdhaval2785gmail.com"
```

Every bot commit in [cologne-stardict](https://github.com/sanskrit-lexicon/cologne-stardict) and [stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit) carries an invalid author email — attribution never links to any account and downstream mail/tooling heuristics treat the address as broken. The sibling hwnorm1 workflow gets this right (`actions@github.com`). One-character fix, report-only per the MEDIUM/LOW fence.

### 🟡 LOW-2 — `git diff --quiet` commit gates ignore untracked files in the weekly hwnorm1 pipeline

**Files:** [`regenerate-hwnorm1-sqlite.yml:113`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/regenerate-hwnorm1-sqlite.yml#L113) · [`regenerate-hwnorm1-sqlite.yml:148`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/regenerate-hwnorm1-sqlite.yml#L148) · [`regenerate-hwnorm1-sqlite.yml:181`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/regenerate-hwnorm1-sqlite.yml#L181)

All three "Commit and push" steps gate on `git diff --quiet`, which sees **tracked modifications only**. A week where the redo scripts produce *only new untracked (non-ignored) files* reports "No changes" and silently skips the whole publish chain (hwnorm2 → csl-apidev → release → gh-pages). Severity held at LOW because the primary artifacts are deliberately gitignored and published via release/gh-pages instead — verified live: [hwnorm1 `.gitignore:13`](https://github.com/sanskrit-lexicon/hwnorm1/blob/main/.gitignore#L13) ignores `*.sqlite`, while `sanhw1/hwnorm1c.txt` is tracked (`git ls-files`), so the usual regeneration path does flip the gate. The untracked-only window is a fragility, not an active hole.

### 🟡 LOW-3 — CI `ack-deletion:` lines silently truncate multi-path acknowledgments

**File:** [`guard-backstop.yml:111`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/guard-backstop.yml#L111) (and the PR-body twin at [`:113`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/guard-backstop.yml#L113))

`grep -ioE 'ack-deletion[ :=]+[^ ]+'` captures only the **first** non-space token per line. A human acking two deletions on one line (`ack-deletion: v02/aaa/aaa.txt v02/bbb/bbb.txt`) silently acks only the first; the second deletion still fails CI. Direction is fail-closed (a blocked CI, never a bypassed guard), and the local `CSL_ORIG_ACK_DELETION` path does honor space/comma lists — hence LOW. Live repro, run this session:

```bash
printf 'ack-deletion: v02/aaa/aaa.txt v02/bbb/bbb.txt\n' \
  | grep -ioE 'ack-deletion[ :=]+[^ ]+' | sed -E 's/^[^ :=]+[ :=]+//'
# → v02/aaa/aaa.txt        (v02/bbb/bbb.txt dropped)
```

## What verified green (live, this session)

| Check | Command | Result |
| --- | --- | --- |
| Guard scenario suite | `bash scripts/test_pre_commit_guard.sh` | **10/10 PASS**, 9.1 s (S1 control, S2/S3 partial-staging, S4 zero-LEND, S5/S5b/S5c deletion+ack, S6 rename, S7 clone-move) |
| Encoding guard, scan-all | `python3 scripts/check_encoding.py` | **OK** — 45 canonical sources, no BOM, valid UTF-8, balanced `<L>/<LEND>`, 9.7 s |
| Python syntax | `python3 -m py_compile scripts/check_encoding.py` | OK |
| Shell syntax | `bash -n` over all five `scripts/*.sh` + `.githooks/pre-commit` | OK |
| Committed-secrets sweep | `rg` over `scripts/ .github .githooks .agents docs reorg v00` for AWS/GitHub/Slack token shapes and private-key blocks | **clean — no matches** (all tokens correctly referenced via `secrets.*`) |
| Hook state | `git config core.hooksPath` | `.githooks` installed and firing |

## Negatives checked and cleared

- No committed secrets anywhere in the code surface (sweep above).
- No `${{ github.event.* }}`-into-`run:` injection besides MEDIUM-1 (dependabot/auto-merge routes `PR_URL` through `env:` — correct).
- [`.githooks/pre-commit`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.githooks/pre-commit) fails closed on every path probed: missing interpreter (127 → `if !`), missing guard scripts, and the suite's partial-staging scenarios all reject.
- [`check_encoding.py`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_encoding.py): `<LEND>`-before-`<L>` ordering is correct (`startswith` prefix trap avoided); staged-blob mode validates index bytes, not worktree bytes.
- [`check_deletions.sh`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_deletions.sh): rename-source/deletion path extraction (`dir`/`tail` derivation) verified against canonical and non-canonical shapes; rename-*into*-canonical correctly allowed.
- [`install-hooks.sh`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/install-hooks.sh): legacy-symlink cleanup backs up foreign hooks, never deletes unknown content.

## Fence compliance

Nothing under any `stenogrammy/` path read, exported, or served. No force-push, no history rewrite, no data deletion, no credential rotation, no votes. All edits (this report + CHANGELOG bullet) landed via a claimed worktree off `origin/main` → PR. No dictionary source under `v02/` touched.

_Dr. Mārcis Gasūns_
