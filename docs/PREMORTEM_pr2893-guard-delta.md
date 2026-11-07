_Created: 07-11-2026 · Last updated: 07-11-2026_

# Premortem — PR #2893 (guard delta: G1 diagnostics + non-dict-dir skip)

Premortem for landing PR #2893 (`h3631-g1-fail-closed`) onto `main`: the
PR-merge commit adopts main's H4227 canonical guard and adds (1) failure-path
diagnostics in `scripts/check_generate_dict.sh` (last 40 ANSI-stripped
pipeline-output lines before the red-line summary) and (2) a skip-with-note
for `v02/` dirs that carry no canonical `<dict>.txt` in the index (e.g.
`v02/etymology_stats/`), in both `scripts/check_encoding.py` and
`scripts/check_generate_dict.sh`, pinned by suite scenario S8.

## Failure modes / chain

- **Skip-with-note masks a genuinely misnamed canonical**: a NEW dict dir
  whose canonical is named wrong (e.g. `v02/newd/newdict.txt`) would be
  skipped instead of checked. Mitigation: the dir's own staged files still
  drive the derivation, and any commit that ADDS a correctly-named canonical
  gets it validated at add time; the deletion guard still covers existing
  canonicals. Residual risk: a dict dir that never gains a canonical file
  silently has no encoding coverage — same coverage as pre-H3632.
- **Exit-status gate fails a spuriously-nonzero pipeline**: the pywork side
  (PRs #84/#88, merged) prints a red STOP and exits nonzero on every failure
  channel, so status and red output agree by construction; a pipeline that
  exits nonzero with valid output would be a pywork bug this hook is
  designed to surface, not mask.
- **Output flooding on failure**: diagnostics are bounded (last 40 lines,
  ANSI-stripped), so pre-commit output stays readable.

## Points of no return

- Merge puts the guards on `main`; any later local commit staging
  `v02/` content in a worktree (no sibling outdir layout) must use the
  disclosed `--no-verify` pattern. Reversible by a plain revert of the merge
  commit; no dictionary data files are touched (scripts + docs + CHANGELOG
  only).

## Early signals

- Already green before this doc: guard suite S1–S8 10/10 (red leg proven
  against main's old guard), live `check_encoding.py --staged` probe on the
  real merge staging set (12 dicts OK, etymology_stats noted, exit 0), CI
  `backstop` ×2 + `encoding` pass on the PR head.
- Post-merge red flag to watch: a Cologne dict CI turning red with a
  generate-dict FAIL — read the printed pipeline tail first (that is the new
  diagnostics working), then the pywork pipeline, before suspecting this
  hook.

_Dr. Mārcis Gasūns_
