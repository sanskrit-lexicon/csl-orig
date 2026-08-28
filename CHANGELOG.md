# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Fixed
- **G1 hook gate (H3631):** `scripts/check_generate_dict.sh` now gates on the
  `generate_dict.sh` pipeline EXIT STATUS as the primary verdict, and the
  `|| true` that discarded the pipeline status is gone — a pipeline dying with
  no red output can no longer pass as "OK: no red lines" (O1). Red lines
  remain as a secondary diagnostic channel (failures are printed, stripped of
  ANSI codes, together with the failing status).

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
