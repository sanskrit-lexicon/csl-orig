# CSL-Orig

Source data repository for the [Cologne Sanskrit Lexicon](https://www.sanskrit-lexicon.uni-koeln.de/) project. Contains digitized entries for 40+ Sanskrit dictionaries, including Monier-Williams (MW), Apte (AP), Böhtlingk (PW/PWG), Grassmann (GRA), and many others.

This repository holds the **raw source data only**. Downstream repositories use it to generate SQLite databases, web interfaces, and StarDict/Babylon files for end users.

## Repository Layout

```
v02/<dict>/          # One directory per dictionary (lowercase abbreviation)
    XXX.txt          # Main entry data
    XXX_hwextra.txt  # Alternate/extra headwords
    XXXheader.xml    # TEI XML metadata (title, author, license)
    XXX-meta2.txt    # Format documentation for that dictionary
    prep/            # Auxiliary preparation scripts (not main data)
```

The `v00/` directory is a legacy archive retained for initialization history only. All active data is in `v02/`.

## Entry Format

Each entry in `XXX.txt` looks like:

```
<L>1<pc>1-001,1<k1>aMSadaSA<k2>aMSadaSA
{#aMSadaSA#}¦ jy. Rice 28.
<LEND>
```

| Tag / marker | Meaning |
|---|---|
| `<L>` … `<LEND>` | Entry boundary |
| `<pc>` | Page/column in the printed source |
| `<k1>` | Primary headword key |
| `<k2>` | Alternate headword key |
| `{#…#}` | Sanskrit text (SLP1 transliteration) |
| `{%…%}` | Italic text |
| `<HI>` | Inline headword marker |

Sanskrit is encoded throughout in **SLP1** transliteration. See each dictionary's `XXX-meta2.txt` for format specifics.

## Automation

Pushing to `v02/**` automatically triggers a GitHub Actions workflow that regenerates StarDict/Babylon output and syncs it to [indic-dict/stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit).

Other outputs (SQLite, web formats) are rebuilt via manually triggered workflows in `.github/workflows/`.

## Making Corrections

Corrections are discussed and tracked in:
- https://github.com/sanskrit-lexicon/csl-corrections/issues
- https://github.com/sanskrit-lexicon/AP/issues

When committing a correction, include the relevant issue comment URL in the commit message (see `git log` for examples).

## Related Repositories

| Repository | Role |
|---|---|
| [csl-pywork](https://github.com/sanskrit-lexicon/csl-pywork) | Dictionary processing pipelines |
| [csl-websanlexicon](https://github.com/sanskrit-lexicon/csl-websanlexicon) | Web interface generation |
| [hwnorm1](https://github.com/sanskrit-lexicon/hwnorm1) | Normalized headword database |
| [cologne-stardict](https://github.com/sanskrit-lexicon/cologne-stardict) | Babylon format generation |
| [stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit) | End-user StarDict distribution |
| [csl-sqlite](https://github.com/sanskrit-lexicon/csl-sqlite) | SQLite release distribution |
