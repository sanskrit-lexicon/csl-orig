# Datasheet — Cologne Cross-Dictionary Derivation Dataset

A datasheet (after Gebru et al., *Datasheets for Datasets*, 2021) for the
Pāṇinian-derivation extraction underlying paper A35. All figures are the current
extraction snapshot and are reproducible from the committed code + dictionary
sources (`python build_dhatu_roots.py && build_root_oracle.py && stats_etymology.py`,
plus the per-dict `analyze_*` extractors).

## Motivation

- **Why was it created?** To test whether the dictionaries of the Cologne Digital
  Sanskrit Lexicon (CDSL) — drawn from the indigenous Sanskrit, English-Indological
  and German-Petersburg traditions — *agree* on how a given head-word is derived
  (root + affix + kāraka), and to expose that derivational layer as structured data.
- **Who created it?** M. Gasūns, within the CDSL ecosystem (sanskrit-lexicon org).
- **Funding / support.** Part of the CDSL maintenance + research effort.

## Composition

- **What do instances represent?** One *derivation*: a dictionary head-word, its
  root (dhātu), affix (pratyaya) and — for the Sanskrit-prose dicts — the kāraka
  sense in which the affix derives it, plus provenance tags.
- **How many instances?** **68,510 derivational statements** across **10
  dictionaries**: WIL 39,650 · MW 9,377 · PWG 11,526 · PW 846 · VCP 3,664 · SKD
  2,213 · AP 339 · Apte (AP90) 332 · SHS 258 · KRM 305. Rows are **typed** and not
  all are root+affix derivations proper — WIL's 39,650 split into root+affix
  18,957 / compound 17,686 / prefix+word 1,406 / multi-derivation 1,214 /
  single-stem 212 / cross-ref+unparsed 175; comparisons use only rows stating the
  compared object. Plus a derived **root oracle** of ~60,000
  (derived-word → root) pairs (incl. KRM's full kṛdanta paradigm).
- **What does each instance consist of?** Per-dict TSV columns vary by idiom but
  share: `headword(_slp1)`, `root(_slp1)`, `affix(_slp1)`, `root_source`
  (provenance tier), `context`. Sanskrit-prose dicts add `karaka(_sense)`; MW adds
  `parse`, `root_class`, `root_canonical`; German dicts add `source_gloss_de`.
- **Is anything missing?** Roots are recovered for 83–100 % of derivations per dict
  (see Tiers); the rest are left `empty` rather than guessed. Affix is present only
  where the source states a pratyaya (MW/PWG rarely do — they attribute a root).
- **Labels / ground truth?** No human gold standard yet; correctness is established
  by (a) cross-dictionary agreement and (b) a DeepSeek-judged precision audit (see
  Collection). This is a silver-standard resource.
- **Sampling.** Not a sample — every `<ab>E.</ab>` / kāraka+pratyaya / `parse=` /
  `Von {#…#}` derivation in each source is extracted.

## Collection & processing

- **Sources.** The CDSL digitisations (`csl-orig/v02/<dict>/<dict>.txt`), each a
  faithful digitisation of a printed dictionary (Wilson 1832; Monier-Williams;
  Apte; Petersburg Wörterbuch gross/klein; Śabdakalpadruma; Vācaspatyam;
  Kṛdantarūpamālā; Śabda-Sāgara). Affix decoding reuses the project's `affix_map.tsv`
  (mined from Apte Sanskrit-Hindi) + the Dictionary of Sanskrit Grammar (`dsg.json`).
  The canonical dhātu list combines the vidyut dhātupāṭha, csl-atlas m4 indigenous
  roots, and `mw_roots.tsv`.
- **Extraction.** Per-idiom regex/markup extractors (one shared affix + dhātu code
  base). No model is in the extraction loop except the final root tier.
- **Root-recovery tiers** (`root_source`, most-to-least direct): `local` ·
  `headword-root` (KRM) · `nearest-root` (citation-gated) · `dhatupatha-join` ·
  `oracle-join` (cross-dict) · `llm-pass` (DeepSeek, **every proposed root validated
  against the canonical dhātu list** — hallucinated non-dhātu roots are discarded).
- **Normalization.** Roots are folded to dhātupāṭha citation form by a deterministic
  `mw_roots.tsv`-anchored map, guarded so a genuinely distinct root (`kṝ` ≠ `kṛ`) is
  never collapsed (622 variants folded; distinct roots 2,493 → 2,090).
- **Quality / precision.** DeepSeek-judged, form-tolerant audit of the inferred
  tiers: `oracle-join` ≈ 83 %, `nearest-root` ≈ 66–75 % root precision; `local`,
  `headword-root`, `llm-pass` ≈ 100 %. MW roots are 99 % canonical vs `mw_roots.tsv`.
  A **strict** subset (drop `nearest-root`) is ≈ 100 % precise; the headline
  cross-dict findings are identical strict vs inclusive (see paper).

## Recommended uses

- Cross-dictionary metalexicography (agreement / tradition comparison).
- A derived-word → root oracle and a (root × affix × kāraka) frequency resource.
- Teaching: affix → IAST surface + function + Russian (DSG) legend; Whitney links.
- **Not** for: a human-validated gold benchmark (no gold yet); per-instance claims
  on `nearest-root`-sourced rows without checking `root_source`.

## Distribution & maintenance

- **Where.** `csl-orig/v02/*/​*_etymology.tsv` + `v02/etymology_stats/` (oracle,
  CSV summaries, dashboard). Live dashboard: https://sanskrit-lexicon.github.io/csl-orig/ .
- **License.** Follows the CDSL source dictionaries' terms (per-dict).
- **Maintenance.** Regenerated from source by the committed pipeline; re-run after
  any extractor change. Versioned in git (csl-orig master).
- **Citation.** Cite paper A35 + this datasheet; the dataset is the empirical basis.
