# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

**CSL-Orig** is the authoritative source data repository for the [Cologne Sanskrit Lexicon](https://www.sanskrit-lexicon.uni-koeln.de/) project. It contains digitized entries for 40+ Sanskrit dictionaries (MW, AP, BEN, GRA, etc.). Downstream repositories (csl-pywork, csl-websanlexicon, hwnorm1, stardict-sanskrit) consume this data to generate SQLite databases, web interfaces, and StarDict/Babylon files.

There are no local build commands — this is a data repository. All build and publishing is handled by GitHub Actions workflows.

## Dictionary Data Format

Each dictionary lives in `v02/<dict>/` (lowercase abbreviation), e.g., `v02/mw/`. The core files per dictionary:

| File | Purpose |
|------|---------|
| `XXX.txt` | Main entry data |
| `XXX_hwextra.txt` | Alternate/extra headwords |
| `XXXheader.xml` | TEI XML metadata (title, author, license) |
| `XXX-meta2.txt` | Format documentation for that dictionary |

### Entry format in `XXX.txt`

```
<L>1<pc>1-001,1<k1>aMSadaSA<k2>aMSadaSA
{#aMSadaSA#}¦ jy. Rice 28.
<LEND>
```

- `<L>` / `<LEND>` — entry boundary tags
- `<pc>` — page/column reference from the printed source
- `<k1>` — primary key (headword in SLP1 transliteration)
- `<k2>` — alternate key form
- `{#...#}` — Sanskrit text in SLP1 transliteration
- `{%...%}` — italic text
- `<HI>` — inline headword marker

Sanskrit is encoded in **SLP1** transliteration throughout (not IAST or Devanagari directly).

## CI/CD Workflows

All automation is in `.github/workflows/`:

- **`update-stardict.yml`** — triggers automatically on any push to `v02/**`. Detects which dictionaries changed, regenerates Babylon format, and pushes to `indic-dict/stardict-sanskrit`.
- **`generate-dict.yml`** — manual trigger; generates the full output for a chosen dictionary (SQLite, web format) by orchestrating csl-pywork and csl-websanlexicon.
- **`regenerate-hwnorm1-sqlite.yml`** — weekly cron (Sunday 5am UTC) + manual; full pipeline rebuild producing `hwnorm1c.sqlite` and per-dictionary SQLite files, published to `gh-pages`.

## Making Corrections

Corrections are tracked via issues in linked repositories:
- https://github.com/sanskrit-lexicon/csl-corrections/issues
- https://github.com/sanskrit-lexicon/AP/issues

Commit messages reference the specific issue comment URL (see git log for examples). Once a correction is pushed to `master`, the stardict workflow fires automatically; other outputs require manual workflow runs.

## Key Conventions

- All text files use **LF line endings** (enforced by `.gitattributes`).
- Files are **UTF-8** encoded.
- The `v02/` layout is the canonical structure (replaced legacy `v00/` layout; see `reorg/README.txt` for history).
- Some dictionaries have a `prep/` subdirectory with Python utilities used during data preparation — these are auxiliary scripts, not part of the main data.
