# csl-orig

_Created: 14-06-2026 · Last updated: 05-07-2026_

**csl-orig is the canonical source-text store for the Cologne Digital Sanskrit
Dictionaries (CDSL)** — the single git-tracked home for the plain-text bodies of
every dictionary the project publishes: [PWG](https://github.com/sanskrit-lexicon/PWG)
(Petersburger Wörterbuch, large), PW (small), [MWS](https://github.com/sanskrit-lexicon/MWS)
(Monier-Williams), PWK (Böhtlingk's shorter edition), GRA (Grassmann's
Rig-Veda dictionary), AP90 (Apte 1890), FRI (Frisch's reader), and dozens more
— currently **45 dictionary subfolders** under [v02/](v02/), from `abch` to `snp`
and beyond.

Every downstream artifact — the generated XML, the web front-ends
([csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon)),
the API layer ([csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev)),
the dashboards — traces back to a `v02/<dict>/<dict>.txt` file in this repo.
Get a correction wrong here and it propagates to every reader-facing surface
in the project; that is why this repo runs a stricter write discipline than
almost any other in the org.

---

## Why this repo is read-only for direct pushes

Upstream maintainers Jim Funderburk and Dhaval Patel commit corrections
directly to `csl-orig` — that is the canonical maintainer pattern. Agents and
downstream contributors do **not** push directly. Instead, corrections are:

1. prepared and XML-validated locally against a snapshot of the target
   dictionary file,
2. queued together with an audit-trail change file in the sibling
   [csl-corrections](https://github.com/sanskrit-lexicon/csl-corrections)
   repo,
3. delivered as **one consolidated pull request to csl-orig roughly once a
   month** — never as a stream of small PRs or bot comments.

This exists because csl-orig sits at the root of the CDSL dependency graph:
noisy, frequent, or unvalidated writes here would ripple into every
dictionary's generated XML and every reader-facing site at once. The batching
discipline is the load-bearing safety mechanism, not a formality — see the
full workflow in the root [CLAUDE.md](../CLAUDE.md#csl-orig-correction-workflow-jim-funderburk--dhaval-patel-pattern).

---

## Correction workflow (summary)

The full sequence — snapshot, apply via `updateByLine.py` or an equivalent
controlled edit, regenerate + XML-validate, write the `csl-corrections` audit
trail, then commit both repos — lives in the org
[CLAUDE.md](../CLAUDE.md#csl-orig-correction-workflow-jim-funderburk--dhaval-patel-pattern)
and this repo's own [CLAUDE.md](CLAUDE.md#dictionary-correction-safety). In short:

- `v02/<dict>/<dict>.txt` files are canonical and may only change through the
  documented workflow (snapshot → change file → validate → audit trail →
  batched PR).
- Before applying any correction issue, check sibling `csl-corrections` CFR
  and batch history for the same dictionary/L-number/headword — if it was
  already rejected or deferred, don't re-patch without a maintainer reopening
  the decision.
- Accepted corrections choose between a plain replacement or an inline
  correction layer (`{{old->new||YYYYMMDD|author|issue|}}`) that preserves the
  original reading.
- XML validation (`csl-pywork/v02/generate_dict.sh` + `xmlchk_xampp.sh`, or
  `make_xml.py`'s "All records parsed by ET" on Windows without XAMPP) is
  required before any commit.

---

## Repository layout

```
v02/
  <dict>/
    <dict>.txt      canonical source text (the file every correction targets)
    ...             per-dictionary auxiliary files (varies by dict)
```

45 dictionary directories currently exist under [v02/](v02/), including
[abch](v02/abch/), [ap90](v02/ap90/), [ben](v02/ben/), [fri](v02/fri/),
[gra](v02/gra/), [ieg](v02/ieg/), [mw](v02/mw/), [pw](v02/pw/),
[pwg](v02/pwg/), [pwkvn](v02/pwkvn/), [shs](v02/shs/), [skd](v02/skd/), and
more — this repo carries the full CDSL corpus, not only the handful of
dictionaries the parent org actively maintains tooling for.

---

## Status

Recent activity (per `git log`) is dominated by per-dictionary correction
commits (e.g. BEN `<ls>` adjustments) flowing through the documented workflow,
plus front-matter/paper-related work on specific dictionaries. As of the last
issue snapshot (2026-05-29): 68 open, 2733 closed, tracked against the
[Cologne tooling-repo taxonomy](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md)
(9 type labels, 4 severity levels, 5 milestones — API Stability, User
Experience, Data Quality, Developer Experience, Community). Org project:
[Tooling Roadmap](https://github.com/orgs/sanskrit-lexicon/projects/9).

---

## Tech stack

- **Runtime**: Python (correction tooling, `updateByLine.py`, diff generators)
- **Validation**: `csl-pywork` (`generate_dict.sh`, `xmlchk_xampp.sh`,
  `make_xml.py` for Windows-without-XAMPP fallback)
- **Pipeline docs**: [csl-observatory tooling runbook](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/runbook/cologne-tooling-runbook.md)

---

_Dr. Mārcis Gasūns_
