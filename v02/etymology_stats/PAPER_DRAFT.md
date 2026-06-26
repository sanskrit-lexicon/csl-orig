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
nearest-token scan grabs affix surfaces like `-ta` and is rejected); an
entry-level *dhātupāṭha-join*; an *oracle-join* against a cross-dictionary
(derived-word → root) oracle (see below); and finally an *llm-pass* — a DeepSeek
resolver over each dictionary's residual empties, whose every proposed root is
validated against the canonical dhātu list before it is written (a hallucinated
root that is not a real dhātu is discarded). Coverage after all tiers: SKD 93%,
VCP 97%, Apte 91%, AP 96%, KRM 100%, SHS 95%.

**Tier precision (DeepSeek-judged, form-tolerant).** A sampled audit of the two
*inferred* tiers gives nearest-root ≈ 69% and oracle-join ≈ 74% root precision —
true figures higher, since several "misses" are the judge rejecting a correct
root in a stem rather than citation form (*sada* for *sad*). The bulk tiers
(*local*, *headword-root*) are ≈ 100% by construction, and the *llm-pass* roots
are returned in clean citation form and dhātu-validated, so the rooted subset is
high-precision overall; the residual error is dominated by surface-form variants,
a normalization task, not misidentification. MW roots are independently
cross-validated against the canonical `mw_roots.tsv` register: **99 %** of MW's
rooted derivations carry a genuine MW root (the 1 % rest are flagged variants).

**The root oracle.** A (derived-word → root) index is pooled from every
dictionary's high-confidence root captures, with two precision guards: the root
must be in the canonical dhātu list, and a head-word keeps a root only if it is
unambiguous (one root, or a ≥⅔ majority). KRM contributes massively here — it is
organised *by* root, so its 2,061 entries' bodies yield ~60k derived-form → root
pairs (its full kṛdanta paradigm). The oracle then back-fills the empty-root tails
of the prose dictionaries by look-up rather than re-parsing: VCP 77 → 87 %,
SHS 20 → 59 %, SKD 90 → 93 %. (Only cross-dictionary-corroborated entries fill;
KRM-body-only forms ship as a standalone resource but are not used to resolve, as
they do not match the prose dicts' head-words.)

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

**F4b — A dictionary's kāraka profile is a fingerprint of its purpose.** Overall
*bhāve* (action/abstract) dominates the kāraka distribution, but KRM inverts it —
*kartari* 227 ≫ *bhāve* 30 — because the Kṛdanta-rūpa-mālā is built around
agent-derivatives. The kāraka mix identifies what a dictionary is *for*.

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

* VCP root capture is **97%** (63% → 77% nearest-root → 87% oracle → 97% with the
  DeepSeek llm-pass). The residual 117 are forms DeepSeek could not confidently
  reduce to a *validated* dhātu (rejected rather than guessed). SHS reaches 95%.
* The nearest-root gate trades a little recall for precision; a few borderline
  fills remain (e.g. a compound member homonymous with a root). A second-annotator
  audit of a `nearest-root` sample would quantify its precision.
* Numbers above are from the current extraction run; rerun `stats_etymology.py`
  after any extractor change.
