# CORRECTION_MANUAL.md — metadoc

_Created: 11-07-2026 · Last updated: 11-07-2026_

Companion record for
[docs/CORRECTION_MANUAL.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/docs/CORRECTION_MANUAL.md).

## Purpose

The csl-orig-resident operator manual for the correction discipline: the
8-stage workflow distilled self-contained, the CFR preflight and
plain-vs-correction-layer decision, the local safety hooks, and — the reason
it exists — the delivery split (maintainer direct commits vs the agent
queue-then-ONE-batched-PR lane). The deep reference stays
[csl-corrections/docs/correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md);
this manual makes csl-orig safe to operate without leaving the repo.

## Audience

- An agent or downstream contributor preparing a correction (the queue lane).
- A new maintainer learning the direct-commit + paired-audit pattern.
- Anyone about to touch `v02/` who needs the gotcha catalogue and the hooks.

## Provenance

Authored 11-07-2026 by Fable 5 (`claude-fable-5`) under handoff
[H515-Fable_csl-orig_batched_pr_correction_manual_10.07.26](https://github.com/gasyoun/Uprava/blob/main/handoffs/H515-Fable_csl-orig_batched_pr_correction_manual_10.07.26.md)
(the H501–H531 per-repo manuals programme, Litpam-Indexator MANUAL.md gold
standard). Distilled from the canonical correction-workflow doc, this repo's
README/CLAUDE.md, the hooks/scripts sources, and the org-root delivery rules
— none invented. Shipped as a doc-only PR per the handoff's explicit csl-orig
discipline note (no `v02/` contact).

## Ranked improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | Make the safety hooks non-opt-in (CI mirror of `check_encoding.py` + the generate smoke-test on PRs) — today a fresh clone has no net until `install-hooks.sh` runs | open |
| 2 | Label `v00/` and `reorg/` as historical in-tree (a one-line README each) | open |
| 3 | A queue-lane pointer file in this repo (the `/cologne-correction-queue` + `/cologne-batch-pr` skills live in claude-config; a non-agent contributor has no discoverable path to them from here) | open |
| 4 | Cross-link this manual from CONTRIBUTING.md | open |

## Known limitations

- The generation pipeline internals (`generate_dict.sh` sub-stages, Mako
  templates, dictparms) are summarized at interface level — csl-pywork's
  docs govern.
- The scholarly batch workflows (Scott/Andhrabharati-style correction forms)
  are routed to the canonical doc §7, not re-taught here.
- The correction queue mechanics are described by contract; the queue itself
  lives in csl-corrections + the org skills.

## Related documents

- [csl-corrections/docs/correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md) — the authoritative deep reference (tutorial, tooling table, evidence)
- [README.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/README.md) — repo overview + the no-direct-push rationale
- [CLAUDE.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/CLAUDE.md) — correction safety + CFR preflight rules
- [scripts/](https://github.com/sanskrit-lexicon/csl-orig/tree/main/scripts) + [hooks/](https://github.com/sanskrit-lexicon/csl-orig/tree/main/hooks) — the local safety layer
- [Cologne tooling runbook](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md) — issue-class ownership

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Initial version (H515) | Fable 5 (`claude-fable-5`) |

---

_Dr. Mārcis Gasūns_
