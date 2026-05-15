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

---

## GitHub Issue Conventions

All issues follow the Sanskrit Lexicon taxonomy shared across the org.

### Milestones

| # | Title | Types |
|---|---|---|
| 4 | Dictionary to Book | `link-target`, `link-splitting` |
| 5 | Digitization Quality | `text-correction`, `encoding`, `bug`, `scan-quality` |
| 6 | Structured Data | `markup`, `question` |
| 7 | Major Enhancements | `content-enhancement` |

### Type labels — color `#0075ca`

| Label | When to use |
|---|---|
| `link-target` | Building click-throughs from `<ls>` abbreviations to scanned PDF pages |
| `link-splitting` | Splitting combined `SOURCE N,N` refs into individual per-page links |
| `markup` | Normalising XML tag content (`<ls>`, `<lex>`, `<ab>`, etc.) |
| `text-correction` | Corrections to dictionary text (definitions, headwords) |
| `content-enhancement` | New material, display upgrades, structural additions beyond correction |
| `encoding` | SLP1/IAST transcoding, character rendering, hyphen/dash normalisation |
| `scan-quality` | Replacing blurry, skewed, or missing scan pages |
| `bug` | Broken links, XML structure errors, broken download files |
| `question` | Scholarly or editorial questions requiring research before any code change |

### Severity labels

| Label | Color | When to use |
|---|---|---|
| `minor` | `#e4e669` | Targeted, self-contained fix |
| `medium` | `#fbca04` | Standard unit of work — one index, a batch of corrections |
| `hard` | `#d93f0b` | Large effort spanning many sources, files, or dictionaries |

---

## Data format

### Markup tags in `v02/<dict>/<dict>.txt`

| Tag | Role | Example |
|---|---|---|
| `<L>NNNN` | Entry begin, with line number | `<L>12345` |
| `<LEND>` | Entry end | |
| `<pc>page` | Page/column reference in the print source | `<pc>1-001,1` |
| `<k1>headword` | Primary headword in SLP1 | `<k1>rAma` |
| `<k2>variant` | Secondary spelling or transliteration | `<k2>rAma` |
| `<e>N` | Homonym number | `<e>1` |
| `<lex>code` | Lexical category (gender, part of speech) | `<lex>m.` |
| `<ls>source` | Literary source citation | `<ls>Rv. 1.22.16` |
| `<ab>tag` | Italicised abbreviation | `<ab>m.</ab>` |
| `<HI>text` | Inline headword marker | `<HI>rAma` |
| `{#text#}` | Sanskrit text in SLP1 | `{#rAmaH#}` |
| `{%text%}` | Italicised display text | `{%abc%}` |

### Annotated example (AP90, abridged)

```
<L>8687<pc>2-302,2<k1>uttaraNga<k2>uttaraNga<e>1
{#uttaraNga#}¦ <lex>a.</lex> Having a high or projecting roof;
{%uttaraNgaH -raH%} <ab>m.</ab> A kind of pavilion or summer-house.
<LEND>
```

- `<L>8687` — line number used for `updateByLine.py` change files
- `<pc>2-302,2` — page 302, column 2 of the print source
- `<k1>uttaraNga` — headword in SLP1 (maps to IAST *uttaraṅga*)
- `<e>1` — homonym index
- `{#uttaraNga#}` — Sanskrit text in SLP1 for display
- `<lex>a.</lex>` — adjective marker
- `<ab>m.</ab>` — gender abbreviation (masculine)
- `<LEND>` — entry close
