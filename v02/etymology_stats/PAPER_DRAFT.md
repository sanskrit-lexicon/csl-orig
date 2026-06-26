# Cross-dictionary consistency of Pāṇinian derivation in the Cologne lexica

*Draft — methods + findings. Generated from the etymology extractions in
`csl-orig/v02/*/​*_etymology.tsv`. Regenerate stats: `python stats_etymology.py`.*

## Question

The Cologne Digital Sanskrit Lexicon bundles dictionaries from three traditions:
the **indigenous Sanskrit** grammarians (Śabdakalpadruma, Vācaspatyam, …), the
**English** Indologists (Wilson 1832, Monier-Williams, Apte), and the **German**
Petersburg school (PWG, PW). Each states a word's derivation in its own idiom.
Do they *agree* on how a given head-word is derived — and where they differ, is
the difference systematic?

## Method

A family of extractors, sharing one affix knowledge base and one canonical dhātu
list, was run over ten dictionaries:

| idiom | dicts | derivation marker | extracted |
|---|---|---|---|
| English prose | WIL | `<ab>E.</ab> {#root#} … {#affix#} aff.` | root + affix |
| Sanskrit prose | SKD, VCP, AP90, AP, SHS, KRM | `[upasarga +] root + KĀRAKA pratyaya` | root + kāraka + affix |
| structured / √ | MW | `parse="X+Y"`, `fr. √ root` | root + parse |
| German prose | PWG, PW | `Von {#src#}` / `Wurzel` | source root |

Affixes are decoded against a single curated pratyaya table (anchored on Apte's
`affix_map.tsv` + a WIL supplement + a generic it-letter decoder). Roots are
validated against a vendored dhātu list (vidyut dhātupāṭha + csl-atlas m4
indigenous roots). Two head-words "agree" if their extracted affix (resp. root)
sets intersect; agreement is reported as a proportion with a 95% Wilson score
interval.

Root recovery is tiered and provenance-tagged (`root_source`): a *local* match
adjacent to the derivation marker; for root-organised dictionaries (KRM) the
*head-word* itself (it is the dhātu); a *nearest-root* match validated against the
dhātu list and gated on a `--`/`DAtoH` citation marker (precision guard — a free
nearest-token scan grabs affix surfaces like `-ta` and is rejected); and an
entry-level *dhātupāṭha-join*. Coverage: SKD 90%, VCP 77%, Apte/AP ~90%, KRM 100%,
SHS 20% (SHS rarely links its root to the kāraka).

## Findings

**F1 — The indigenous Sanskrit tradition is internally consistent on affixes.**
For head-words shared by two Sanskrit-side dictionaries, the stated affix agrees
**90–100%** of the time (proportion, 95% Wilson score interval): SKD↔VCP
**93.8% [85.2–97.6]** (n=65), Apte↔AP **100% [97.9–100]** (n=178), VCP↔SHS
**98.5% [95.8–99.5]** (n=206), SKD↔Apte **91.7% [83.8–95.9]** (n=84). Independent
19th–20th c. compilations of the Pāṇinian analysis converge.

**F2 — Wilson 1832 is the outlier.** WIL agrees with SKD only **22.9%
[14.6–34.0]** (n=70) and VCP **61.2% [58.7–63.7]** (n=1504) on affixes. The WIL↔SKD
interval (≤34%) does not overlap any Sanskrit-side pair's interval (≥83%), so the
divergence is statistically clear, not sampling noise — confirming Wilson's
idiosyncratic, pre-critical etymologies as a distinct stratum.

**F3 — Cross-tradition root attribution holds at ~two-thirds.** The two large
root-attributing dictionaries, MW (English, √-notation) and PWG (German, "von
Wurzel"), agree on the root **65%** of shared head-words; PWG↔PW 93%. Root
agreement is lower than affix agreement because root *identification* is noisier
across scripts/conventions, not because the traditions disagree.

**F4 — kāraka × pratyaya structure is linguistically sound.** Pooling the
Sanskrit-side dicts, `lyuṭ` concentrates in bhāve/karaṇe, `kta` spreads across
bhāve/karmaṇi/kartari (its three participial readings), `lyu` is monosemous
(kartari, entropy 0.33 bits), while `ḍa`, `anīyar`, `ac` are kāraka-generalists
(entropy ~2 bits). bhāve dominates the kāraka distribution (51%).

## Artefacts

Per-dict TSVs (`<dict>_etymology.tsv`), eight summary CSVs, and an interactive
[`dashboard_etymology.html`](dashboard_etymology.html) (kāraka×pratyaya heatmap,
affix entropy, root productivity, affix & root agreement matrices).

## Limits / next

* VCP root capture is **77%** (was 63% before the citation-gated nearest-root
  pass). The residual 841 empties cite no root in a recoverable position; an LLM
  pass over those entries is the remaining lever.
* The nearest-root gate trades a little recall for precision; a few borderline
  fills remain (e.g. a compound member homonymous with a root). A second-annotator
  audit of a `nearest-root` sample would quantify its precision.
* Numbers above are from the current extraction run; rerun `stats_etymology.py`
  after any extractor change.
