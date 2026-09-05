_Created: 30-06-2026 · Last updated: 05-09-2026_

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
