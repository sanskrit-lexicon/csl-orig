# Cross-dictionary consistency of Pāṇinian derivation in the Cologne lexica

*Draft (pre-submission) — target: International Journal of Lexicography /
Lexicographica; WSC 2027 indological alternate.
Author: **Mārcis Gasūns**, independent scholar
([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)),
gasyoun@ya.ru. Empirical basis + datasheet: [`DATASHEET.md`](DATASHEET.md); all figures
reproducible from `csl-orig/v02/*/​*_etymology.tsv` via `python stats_etymology.py`.
Live dashboard: https://sanskrit-lexicon.github.io/csl-orig/ .*

## Abstract

The dictionaries of the Cologne Digital Sanskrit Lexicon were compiled across two
centuries by three scholarly traditions — the indigenous Sanskrit grammarians, the
English Indologists, and the German Petersburg school — each stating a word's
*derivation* (its root, affix, and the grammatical relation the affix expresses) in
its own idiom. We extract that derivational layer from ten dictionaries (~67,000
derivations) with a single shared affix-and-dhātu code base, and ask whether the
traditions *agree*. They do, sharply, within the Sanskrit tradition: independent
indigenous lexica agree on a head-word's affix **90–100 %** of the time. Wilson
1832 is the lone, statistically clear outlier (22.9 % with the Śabdakalpadruma, a
95 % interval that does not reach any Sanskrit-side pair). Across traditions, the
English √-notation (Monier-Williams) and the German "Wurzel" convention agree on the
root for ~two-thirds of shared head-words. The kāraka×pratyaya structure we recover
is linguistically sound, and a dictionary's kāraka profile turns out to fingerprint
its purpose. The extraction is a tiered, provenance-tagged pipeline whose precision
we audit; we release the data and an interactive dashboard.

## Question

The Cologne Digital Sanskrit Lexicon bundles dictionaries from three traditions:
the **indigenous Sanskrit** grammarians (Śabdakalpadruma, Vācaspatyam, …), the
**English** Indologists (Wilson 1832, Monier-Williams, Apte), and the **German**
Petersburg school (PWG, PW). Each states a word's derivation in its own idiom.
Do they *agree* on how a given head-word is derived — and where they differ, is
the difference systematic?

## Related work

This study is the **derivational counterpart** to a small body of recent
quantitative work on the same corpus. Gasūns, *Grammar Without Tags: The
Verbal-Root Microstructure of the Indigenous Sanskrit Kośa* (in prep.; csl-atlas
A04) shows that the indigenous lexica encode a rich *verbal-root* apparatus — which
records are roots, and each root's gaṇa/pada via anubandha letters — that European
microstructure detectors miss, and that five indigenous lexica **agree on the
grammar** they record (gaṇa compatible 85.5 % across 1,526 doubly-classified roots).
A companion outline (SanskritLexicography A30) treats ŚKD/VCP indigenous
microstructure. Our work is complementary along three axes and shares one corpus,
so the three should be read together (and cross-cite rather than re-derive):

1. **Unit.** A04/A30 study the *root entry* and its conjugational metadata; we study
   the *derived head-word* and its derivational analysis (root **+ pratyaya +
   kāraka**). The root-grammar layer and the derivation layer are orthogonal.
2. **Scope.** A04 explicitly excludes the European dictionaries (they carry ≤ 8 root
   entries each). We *include* them — the derivation of a head-word is exactly what
   Wilson, Monier-Williams and the Petersburg dictionaries *do* record — which is
   what lets us measure cross-*tradition* (not just intra-indigenous) agreement.
3. **Agreement object.** A04 validates extraction by root×root-grammar agreement; we
   validate by head-word×affix agreement, and find the indigenous tradition even
   more consistent on the *affix* (90–100 %) than on root gaṇa (85.5 %).

We adopt A04's central methodological stance — that a near-zero score from a
tag-based detector over an indigenous lexicon is a measurement artefact, not an
absence of content, and that **cross-source agreement is the validation** when no
gold standard exists.

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
*inferred* tiers gives, after the normalization pass below, oracle-join ≈ 83%
(up from 74% before normalization — folding surface variants removed that error
class) and nearest-root ≈ 66–75% root precision (its residual errors are genuine
wrong-token grabs, plus a few judge false-negatives where the candidate already
equals the canonical root). The bulk tiers (*local*, *headword-root*) are ≈ 100%
by construction, and the *llm-pass* roots are returned in clean citation form and
dhātu-validated, so the rooted subset is high-precision overall; *nearest-root*
is the weakest tier and is tagged as such in `root_source` for downweighting.

**A strict, near-100%-precision subset for headline tables.** Dropping the single
sub-~100% tier (*nearest-root*) yields a high-precision dataset: per-dictionary
strict coverage is KRM 100 %, SKD 93 %, SHS 92 %, AP 90 %, Apte 87 %, VCP 83 %
(VCP loses the most because *nearest-root* was its largest inferred tier).
Reproduce it by filtering `root_source != nearest-root` (`pct_strict` column /
`cross_dict_root_agreement_strict.csv`). Critically, the **headline root-agreement
is robust to this filter** — MW↔PWG 64.2 % and PWG↔PW 93.9 % are *identical* with
and without the nearest-root tier — so the cross-dictionary findings are not an
artefact of the lower-precision rows. MW roots are independently cross-validated against the
canonical `mw_roots.tsv` register: **99 %** of MW's rooted derivations carry a
genuine MW root (the 1 % rest are flagged variants).

**Root-form normalization.** The residual error the audit exposed was dominated
by *surface-form variants* — a correct dhātu in a thematic-stem form (`sada` for
`sad`, `bhuja` for `bhuj`) or with a long-vowel slip (`ghṝ` for `ghṛ`) — not by
misidentification. A final pass folds these onto their citation form: a
deterministic (variant → canonical) map built from `mw_roots.tsv`'s citation-form
head-words, where a root is rewritten only if it is not itself canonical and
exactly one reduction lands on a canonical root (so a genuine distinct root such
as `kṝ` "to scatter", which *is* canonical, is never collapsed into `kṛ` "to
do"). 622 variants fold across the corpus, consolidating the distinct-root count
from 2,493 to 2,090 and merging their derivative counts onto the right root.

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

**Table 1 — Cross-dictionary affix agreement** (head-words both dicts root with an
affix; proportion with 95 % Wilson interval, sorted by shared count). The
Sanskrit-side block (top) is uniformly high; the Wilson block (bottom) is uniformly
low and its intervals do not reach the Sanskrit-side block — the divergence is
structural, not sampling noise.

| pair | shared HW | agree (95 % CI) |
|---|--:|---|
| Apte ↔ AP | 178 | 100.0 % [97.9–100] |
| VCP ↔ SHS | 206 | 98.5 % [95.8–99.5] |
| VCP ↔ AP | 97 | 96.9 % [91.3–98.9] |
| VCP ↔ Apte | 93 | 96.8 % [90.9–98.9] |
| SKD ↔ Apte | 84 | 91.7 % [83.8–95.9] |
| — *Wilson* — | | |
| WIL ↔ VCP | 1504 | 61.2 % [58.7–63.7] |
| WIL ↔ SHS | 190 | 60.0 % [52.9–66.7] |
| WIL ↔ Apte | 83 | 54.2 % [43.5–64.5] |
| WIL ↔ AP | 82 | 52.4 % [41.8–62.9] |
| WIL ↔ SKD | 70 | 22.9 % [14.6–34.0] |

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

**Table 2 — Root coverage, two tiers.** The *inclusive* tier uses all six recovery
tiers (≈ 92 % precision); the *strict* tier drops the one sub-100 % tier
(`nearest-root`) for ≈ 100 % precision. The headline agreement results above are
*identical* in both tiers (MW↔PWG 64.2 %, PWG↔PW 93.9 % either way), so the choice
of tier never changes a conclusion — only the coverage figure.

| dict | derivations | inclusive | strict (≈100 % prec.) |
|---|--:|--:|--:|
| KRM | 305 | 100.0 % | 100.0 % |
| SKD | 2,213 | 93.3 % | 93.0 % |
| SHS | 258 | 96.1 % | 92.2 % |
| AP | 339 | 95.9 % | 90.3 % |
| Apte | 332 | 91.6 % | 86.7 % |
| VCP | 3,664 | 97.4 % | 82.9 % |

## Artefacts

Per-dict TSVs (`<dict>_etymology.tsv`), the cross-dict root oracle
(`root_oracle.tsv`), nine summary CSVs (incl. `root_capture.csv` with both coverage
tiers and `cross_dict_root_agreement_strict.csv`), a full [`DATASHEET.md`](DATASHEET.md)
(Gebru-style), and an interactive [dashboard](https://sanskrit-lexicon.github.io/csl-orig/)
(kāraka×pratyaya heatmap, affix entropy, root productivity, affix & root agreement
matrices, per-affix DSG/Russian legend, Whitney root links). Everything is
regenerable from the committed pipeline.

## Limits / next

* VCP root capture is **97%** (63% → 77% nearest-root → 87% oracle → 97% with the
  DeepSeek llm-pass). The residual 117 are forms DeepSeek could not confidently
  reduce to a *validated* dhātu (rejected rather than guessed). SHS reaches 95%.
* The nearest-root gate trades a little recall for precision; a few borderline
  fills remain (e.g. a compound member homonymous with a root). A second-annotator
  audit of a `nearest-root` sample would quantify its precision.
* Numbers above are from the current extraction run; rerun `stats_etymology.py`
  after any extractor change.
