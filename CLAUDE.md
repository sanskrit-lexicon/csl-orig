# CLAUDE.md

_Created: 14-06-2026 · Last updated: 16-08-2026_

**csl-orig** is the Cologne Digital Sanskrit Dictionaries **data store**.
Canonical digitised text lives at [`v02/<dict>/<dict>.txt`](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
(SLP1, one record per `<L>`…`<LEND>`). It is not a generator and not a web
frontend.

## What to run

Agents **never commit** and **never push** this repository — not even a
one-line dictionary fix. Prepare the change locally, XML-validate, then
queue. Delivery is one consolidated PR at most ~monthly.

1. Express the edit as an `updateByLine.py` change file (UTF-8, **no BOM**):
   ```
   1234 old exact original line text here
   1234 new exact replacement line text here
   ```
   `ins` inserts after; `del` deletes. `;` starts a comment.
2. Validate XML **before** queueing (from sibling
   [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) `v02/`):
   `sh generate_dict.sh <dict> tempparent/<dict>` then
   `sh xmlchk_xampp.sh <dict>`. On Windows without XAMPP / `xmllint`,
   [`make_xml.py`](https://github.com/sanskrit-lexicon/csl-pywork/blob/main/v02/makotemplates/pywork/make_xml.py)
   printing `All records parsed by ET` is the validate signal.
3. Park the validated change with
   [`/cologne-correction-queue`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-correction-queue.md).
   Ship the monthly bundle with
   [`/cologne-batch-pr`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md).

The eight-stage snapshot → apply → regenerate → validate → audit sequence is
documented once:
[csl-corrections/docs/correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md).
Do not invent a second workflow.

## Do not

- Commit or push dictionary source under `v02/`.
- Write files with `utf-8-sig` (a UTF-8 BOM). After a write:
  `python -c "with open(f,'rb') as x: print(x.read(3).hex())"` must not start
  `efbbbf`.
- Comment on Cologne issues unless a human asked (maintainer-noise rule).
- Treat `printchange.txt` as a digital/markup fix log — it records
  deviations from the scanned print.

## Primer

Encodings, `key1`/`key2`, SLP1/IAST/Devanāgarī, and the broken
`iast_to_devanagari` trap:
[SANSKRIT_CONTEXT_PRIMER.md](https://github.com/gasyoun/github-spine/blob/main/SANSKRIT_CONTEXT_PRIMER.md).

Issues use the Cologne taxonomy — see
[`/cologne-issue-runbook`](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-issue-runbook.md).

_Dr. Mārcis Gasūns_
