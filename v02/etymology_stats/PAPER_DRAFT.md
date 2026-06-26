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
sets intersect.

## Findings

**F1 — The indigenous Sanskrit tradition is internally consistent on affixes.**
For head-words shared by two Sanskrit-side dictionaries, the stated affix agrees
**90–100%** of the time: SKD↔VCP 94%, Apte↔AP 100%, VCP↔SHS 98%, SKD↔Apte 92%.
This is strong cross-validation: independent 19th–20th c. compilations of the
Pāṇinian analysis converge.

**F2 — Wilson 1832 is the outlier.** WIL agrees with SKD only **23%** and VCP
**61%** on affixes — far below the Sanskrit-side block — confirming Wilson's
idiosyncratic, pre-critical etymologies.

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

* VCP root capture is 63% — the gaṇa-gloss tail resists a *safe* join (the dhātu
  is far from the kāraka); a per-derivation dhātupāṭha resolver or an LLM pass
  would lift it.
* KRM (a dedicated kṛdanta dictionary) needs a per-derivation local pass.
* Numbers above are from the current extraction run; rerun `stats_etymology.py`
  after any extractor change.
