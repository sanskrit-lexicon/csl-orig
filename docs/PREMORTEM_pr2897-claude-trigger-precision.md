_Created: 07-11-2026 · Last updated: 07-11-2026_

# Premortem — PR#2897 (H4575): CLAUDE.md trigger precision

## Failure modes / chain

- **Resolution drops main's H7474 guard-backstop wording.** Chain: conflict
  resolved in favor of the stale branch → main's CI inventory regresses.
  Mitigation: resolution = main's file verbatim + only the verified delta
  (checked with `git diff origin/main -- CLAUDE.md` before commit — the delta
  is the two intended hunks, nothing else).
- **Trigger-precision claim is wrong.** Chain: docs assert encoding-guard
  fires on `scripts/check_encoding.py` while the workflow does not → false
  doc. Mitigation: verified live against
  [`.github/workflows/encoding-guard.yml`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/.github/workflows/encoding-guard.yml)
  push paths before writing the doc line.
- **`--no-verify` skips the local guard.** Chain: broken bytes or a bad
  deletion land on `main`. Mitigation: guard-backstop CI re-runs the same
  gates on the PR head (full-tree encoding scan + per-dict generate_dict);
  all three workflows SUCCESS on this head.

## Points of no return

- Merge to `main` rewrites the canonical agent doc. But the diff is
  docs-only (CLAUDE.md + this premortem doc), no `v02/**` data touched — a
  single `git revert` restores state at any time. No downstream artifact
  (stardict/hwnorm1/pywork) reads CLAUDE.md.

## Early signal

- The three PR-head CI workflows (`encoding`, `backstop`,
  `Changelog — no duplicated entries`) — any FAIL blocks the landing before
  it reaches `main`; on this head all three already returned SUCCESS.

_Dr. Mārcis Gasūns_
