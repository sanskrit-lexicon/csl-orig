_Created: 30-06-2026 · Last updated: 10-11-2026_

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Audited (nightly bug hunt)
- **Bug hunt 06-11-2026** ([`BUGHUNT-FINDINGS-csl-orig-06.11.2026.md`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/BUGHUNT-FINDINGS-csl-orig-06.11.2026.md)): 0 HIGH · 1 MEDIUM · 3 LOW over the code surface (`scripts/`, `.githooks/`, `.github/workflows/`). MEDIUM: shell-injection shape (unenv-routed `${{ }}` interpolation) + unpinned floating-tag `tj-actions/changed-files@v47` in the StarDict sync workflow. LOW: malformed bot commit email (`drdhaval2785gmail.com`, missing `@`), `git diff --quiet` gates blind to untracked files in the weekly hwnorm1 pipeline, and CI `ack-deletion:` lines truncating multi-path acks to the first path. Secret sweep clean; guard suite 10/10 green; no auto-fix (nothing HIGH), no GTD row.

### Fixed
- **updateByLine.py defects cleaned with byte-identical outputs** (H7961): the `v02/gra/greek` + `v02/stc/abbrev` twins (kept byte-identical to each other) now use `except IndexError` carrying the lnum context, `sys.exit(1)`, and plain `print(out)` (py3 printed `b'...'` reprs on error paths); the dead duplicate old-line `re.search`, the unreachable second `(not m)/(not m1)` guard and the unused `sep` local are gone. The `transcoder.py` twins lose only their dead `if (False):` debug-writer block (FSM matching, the slp1_deva look-ahead and the deva_slp1 vowel-sign hack untouched), and `v02/pwkvn/update/final.py` the unreachable tail of `unused_transcode_as_misc`. Correction-queue tool outputs are byte-identical (proved by the parity harness).
- **Generate-dict guard now fails on a nonzero pipeline exit** (H4227, H3487
  audit O1 residual): `scripts/check_generate_dict.sh` discarded the
  pipeline's exit status (`|| true`) and keyed only on ANSI-red output, so a
  pipeline that died without emitting its red marker passed as "OK: no red
  lines". The status is now captured and the hook fails on nonzero exit OR
  red lines, printing which of the two fired.
- **Generate-dict guard failure path now shows the pipeline's own output**
  (H3631 audit G1, on top of H4227): on a nonzero exit or red-line hit,
  [`scripts/check_generate_dict.sh`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_generate_dict.sh) now prints the last 40 lines of its ANSI-stripped output
  before the red-line summary — a crash that died without emitting its error
  marker still shows why it died.
- **Encoding guard no longer false-fails on non-dictionary dirs under v02/**
  (H3631 fix pass 07-11): `scripts/check_encoding.py` required a canonical
  `<dict>.txt` in the index for every `v02/<dir>/` carrying staged files, but
  `v02/etymology_stats/` is analysis tooling with no dict source — every
  commit staging its files (e.g. any merge bringing them in) failed
  spuriously. A dir with no canonical source in the index is now skipped with
  a note; unacked deletions/renames of real canonical sources remain covered
  by the stage-0 deletion guard, and suite scenario S8 pins the regression.

### Added
- **Offline parity harness for the update tooling** ([`scripts/update_tooling_parity.py`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/update_tooling_parity.py)) (H7961): runs the `origin/main` copies (via `git show`) and the working-tree copies on committed fixtures — new/ins/del + old-text-mismatch + lnum-overflow for `updateByLine.py`, slp1_deva look-ahead and deva_slp1 vowel-sign strings for `transcoder_processString` — and diffs outputs byte-for-byte against committed old-code goldens; 72 checks green at landing.
- Canonical deletion/rename guard ([`scripts/check_deletions.sh`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_deletions.sh)): deleting or renaming a `v02/<dict>/<dict>.txt` source now fails the commit unless explicitly acknowledged (`CSL_ORIG_ACK_DELETION`, or `ack-deletion:` lines in CI) — H3632 finding O3/O4
- CI backstop ([`.github/workflows/guard-backstop.yml`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/guard-backstop.yml)): replicates both hook stages (encoding guard + per-dict generate pipeline, plus the deletion guard against the diff base) so hook-less clones are still gated on every `v02/`-touching push/PR — H3632 finding O10 gap
- Guard scenario test suite ([`scripts/test_pre_commit_guard.sh`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/test_pre_commit_guard.sh)): partial staging, deletion, rename, zero-`<LEND>`, and clone-move scenarios in a throwaway mini-clone

### Changed
- Pre-commit encoding guard validates **staged blobs** (`git show :v02/...`) instead of worktree bytes, so partial `git add -p` staging cannot commit unchecked content — H3632 finding O6
- `generate_dict.sh` smoke-test refuses to run when staged bytes differ from the worktree (the pipeline reads worktree bytes and would bless uncommitted content) — H3632 finding O6
- A canonical source with **zero `<LEND>` lines is now a failure** instead of a vacuous pass — H3632 finding O5
- Hook install switched to `git config core.hooksPath .githooks` (relative path survives clone moves; the old absolute symlink went stale silently); hook moved `hooks/` → `.githooks/` — H3632 finding O10

## [0.1.0] - 2026-06-30

### Added
- Initial release of csl-orig Cologne Digital Sanskrit Dictionaries source repository
- Comprehensive dictionary collections (AP90, BOR, GRA, INM, MW, PWG, PW, PWK, SCH, SHS, SKD, WIL)
- UTF-8 encoded source files with standardized markup

### Changed
- Branch reference updates: master → main for default-branch rename preparation

### Fixed
- SKD Sāyaṇa commentator attribution corrections (sAyanaH → sAyaNaH)
- INM Cologne #179 corrections
- SCH double-space normalization (DEV27)
- SKD local-dev fixes (csl-ldev#12)
- MWS issue #1060 fixes
- SHS bracket-infix k1/k2 metaline patterns (COLOGNE#430, COLOGNE#181)

### Deprecated

### Removed

### Security

_Dr. Mārcis Gasūns_
