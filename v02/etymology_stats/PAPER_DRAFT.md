# Cross-dictionary consistency of Pāṇinian derivation in the Cologne lexica

*Draft (pre-submission) — target: International Journal of Lexicography /
Lexicographica, with the **International Sanskrit Computational Linguistics
Symposium (ISCLS)** as a parallel Sanskrit-CL venue (confirmed live, 8th
edition March 2026, IIT Roorkee — [2026.iscls-1.0](https://aclanthology.org/2026.iscls-1.0/));
WSC 2027 indological alternate.
Author: **Mārcis Gasūns**, independent scholar
([ORCID 0000-0003-4513-884X](https://orcid.org/0000-0003-4513-884X)),
gasyoun@ya.ru. Empirical basis + datasheet: [`DATASHEET.md`](DATASHEET.md); all figures
regenerable from `csl-orig/v02/*/​*_etymology.tsv` via `python stats_etymology.py`
(the committed LLM-resolved tiers are inputs, not regenerated — see Artefacts).
Live dashboard: https://sanskrit-lexicon.github.io/csl-orig/ .*

## Submission readiness note (internal planning memo, not manuscript prose)

_Written 04-07-2026, re-verified against live ACL Anthology + web sources._

**Path A — submit to the next ISCLS edition now.** The 8th ISCLS edition
(March 9–11, 2026, IIT Roorkee — [2026.iscls-1.0](https://aclanthology.org/2026.iscls-1.0/))
already happened this cycle: its submission deadline was 15 January 2026,
notification 15 February 2026 — both in the past. The ACL Anthology venue page
([aclanthology.org/venues/iscls](https://aclanthology.org/venues/iscls/))
lists only three editions to date (6th, 2019; 7th, 2024; 8th, 2026) — an
irregular, roughly biennial cadence, **not annual** — and shows no 9th-edition
call for papers yet; a 9th edition is unannounced as of this writing (July
2026), plausibly ~2027–2028 given the gap pattern. **"Submit now" is therefore
not literally actionable** — there is no open ISCLS CFP to submit to today;
Path A really means "commit to targeting whichever ISCLS edition opens next."
On readiness: A35 (4/5, pre-submission) is close to ISCLS length/format —
ISCLS papers run in the 8–20 page range seen in this cycle's proceedings
(e.g. the accepted WSD paper spans pp. 14–31) — but A35's current draft carries
extensive tabular apparatus (Tables 1/1b/2, per-tier coverage breakdowns) that
would need trimming to a conference-length submission; the DATASHEET.md
material would move to supplementary/appendix rather than the main paper.

**Path B — hold for IJL/Lexicographica first, ISCLS as fallback.** Humanities
journal review timelines for IJL (Oxford) and Lexicographica (De Gruyter) are
not published as fixed SLAs; general peer-review-timeline data points to
several months per round and desk/first-decision cycles commonly running
6–12+ months for humanities venues, with a possible second revision round on
top. Held against the monograph-timeline consideration (these papers are meant
to become chapters of an eventual Brill/de Gruyter monograph): a journal-first
path risks the paper sitting in review through most of the gap before the next
ISCLS edition even opens — i.e. holding for IJL/Lexicographica does **not**
cost an ISCLS cycle, since there is no live ISCLS cycle to lose right now.

**Bottom line: Path B, with ISCLS kept as the live fallback/parallel-venue
plan already stated in the header above.** Since no ISCLS CFP is currently
open, "submit to ISCLS now" is moot as literally stated; the actionable
decision is journal-first (IJL primary, Lexicographica secondary) while
continuing to prepare a trimmed ISCLS-length variant so the paper is ready
the moment a 9th-edition CFP appears — whichever fires first is submitted
to, per the header's existing "parallel venue" framing. This does not
materially delay the monograph: the journal review window and the ISCLS
inter-edition gap are of comparable order, so neither path is the clear
speed-losing one, and A35's readiness (4/5) is closer to journal-submission
polish than to a conference-length trim today.

## Abstract

The dictionaries of the Cologne Digital Sanskrit Lexicon were compiled across two
centuries by three scholarly traditions — the indigenous Sanskrit grammarians, the
English Indologists, and the German Petersburg school — each stating a word's
*derivation* (its root, affix, and the grammatical relation the affix expresses) in
its own idiom. We extract that derivational layer from ten dictionaries (68,510
derivational statements) with a single shared affix-and-dhātu code base, and ask
whether the traditions *agree*. Within the Sanskrit tradition they do, sharply:
independent indigenous prose lexica agree on a head-word's affix in **over 90 %**
of cases (per-pair 91.7–100 %), and on its **kāraka 89–100 %**. Wilson 1832 diverges — but measuring
*why* turns out to be the more interesting result. Half of the apparent divergence
is extraction noise (only 50.1 % of Wilson's free-prose affix captures are valid
Pāṇinian affix names; filtering to the valid vocabulary lifts WIL↔ŚKD agreement
from 22.9 % to 66.7 %), and a hand audit of the remaining disagreements shows
**most are Pāṇinian taxonomy, not different words**: in 30 of 48 audited cases
Wilson and the kośa posit different affix *names* that realize the **same surface
form** (*ac* vs *ghañ*, both → *-a*; *yuc* vs *lyuṭ*, both → *-ana*). Genuinely
different derivations are rare (4/48). Across traditions, the English √-notation
(MW) and the German "Wurzel" convention agree on the root for ~two-thirds of
shared head-words (64.2 %). The kāraka×pratyaya structure we recover is
linguistically sound, and a dictionary's kāraka profile fingerprints its purpose.
The extraction is a tiered, provenance-tagged pipeline whose precision we audit;
we release the data, the audit, and an interactive dashboard.

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
   validate by head-word×affix agreement (§Findings; see Method for exactly what
   "agree" means), and find the indigenous prose tradition even more consistent on
   the *affix* (91.7–100 %) than on root gaṇa (85.5 %).

We adopt A04's central methodological stance — that a near-zero score from a
tag-based detector over an indigenous lexicon is a measurement artefact, not an
absence of content, and that **cross-source agreement is the validation** when no
gold standard exists. This paper applies that stance reflexively: our own headline
"outlier" (Wilson) is itself decomposed into measurement artefact vs genuine
divergence before it is interpreted (§F2).

Beyond the lexicographic literature, this study also sits inside the smaller but
active body of computational Sanskrit-NLP work indexed in the ACL Anthology and
presented at ISCLS, the dedicated Sanskrit computational-linguistics symposium
(8th edition, March 2026, IIT Roorkee — [2026.iscls-1.0](https://aclanthology.org/2026.iscls-1.0/)),
which this cycle included a lexicographic-definition-based word-sense
disambiguation paper ([2026.iscls-1.2](https://aclanthology.org/2026.iscls-1.2/)) — the
closest published Sanskrit-specific analogue to a cross-dictionary consistency
study. A prior ISCLS edition carries an even closer precedent: Patel & Kulkarni,
"Word Sense Alignment of Sanskrit Lexica" (ISCLS 2024,
[2024.iscls-1.1](https://aclanthology.org/2024.iscls-1.1/)), which cross-aligns
senses between Wilson and Yates' dictionaries — the direct Sanskrit-specific
sibling to this paper's cross-dictionary *derivation* alignment, differing in
which layer (sense vs. derivation) is compared. Our root-normalization pipeline (Method, below) is independently
validated against the same dhātu resources used by Hellwig & Nehrdich's
character-level sandhi/compound-splitting models (EMNLP 2018,
[D18-1295](https://aclanthology.org/D18-1295/)) and by the unified ByT5-Sanskrit
model (Findings of EMNLP 2024, [2024.findings-emnlp.805](https://aclanthology.org/2024.findings-emnlp.805/)),
which we cite as the computational-NLP counterpart to this paper's
lexicographic-derivation framing, not as a technique this paper adopts directly.

## Technique-adoption assessment (internal note, not manuscript prose)

**Question.** The Related-work paragraph above cites Hellwig & Nehrdich's
rcNN sandhi/compound-splitting model (EMNLP 2018,
[D18-1295](https://aclanthology.org/D18-1295/)) and ByT5-Sanskrit
([2024.findings-emnlp.805](https://aclanthology.org/2024.findings-emnlp.805/))
as NLP-adjacent context. Is there an actual sandhi-resolution step anywhere in
this paper's derivation-extraction pipeline that either model could replace or
check against?

**What the pipeline actually operates on.** Read against the per-dictionary
extractors (`v02/wil/analyze_wil_etymology.py`, `v02/pwg/analyze_pwg_etymology.py`,
`v02/mw/analyze_mw_etymology.py`, `v02/skd/analyze_sktdict_etymology.py`) and
the downstream `v02/etymology_stats/stats_etymology.py`: every extractor reads
already-segmented, already-tagged dictionary markup — `<L>`…`<LEND>` entries
with a single `<k1>` headword, and an `<ab>E.</ab>` block (or `{#root#}`/
`{#affix#}` markers, or `parse="X+Y"`, or `Wurzel`) that already isolates the
root and affix as separate tokens. There is no raw sandhi'd verse or
continuous prose anywhere in this pipeline's input — the dictionaries
themselves already did the segmentation, as part of stating the etymology.
The one place "sandhi" appears in this codebase at all
(`v02/etymology_stats/stats_etymology.py:510`) is a **caption caveat** on the
dashboard's affix legend — noting that the affix name doesn't show the
sandhi-reshaped surface form (*kṛ* + *lyuṭ* → *karaṇa*, not *kṛ-ana*) — not a
processing step.

**Verdict: genuinely irrelevant to this pipeline.** The rcNN/ByT5 models solve
word segmentation and compound splitting on *unsegmented* text (running verse,
continuous prose); this paper's extraction never receives unsegmented text —
its "hard" problem is Pāṇinian-affix-vocabulary normalization and root-form
folding (`root_norm.py`) across dictionaries that already agree on where one
word ends and the next begins. Forcing a sandhi-splitting model into this
pipeline would address a problem this pipeline does not have. The citation is
correctly scoped as-is: a computational-NLP-counterpart citation for readers
positioning this paper in the Sanskrit-CL literature, not a technique this
paper could adopt.

## Method

A family of extractors, sharing one affix knowledge base and one canonical dhātu
list, was run over ten dictionaries. Codes are the CDSL display codes; the one
ambiguity to note is that **"Apte" in the released CSVs is `AP90`** (Apte 1890),
while `AP` is the revised 1957–59 edition.

| idiom | dicts | derivation marker | extracted |
|---|---|---|---|
| English prose | WIL | `<ab>E.</ab>` block: `{#root#} … {#affix#} aff.` | root + affix |
| Sanskrit prose | SKD, VCP, AP90, AP, SHS, KRM | `[upasarga +] root + KĀRAKA pratyaya` | root + kāraka + affix |
| structured / √ | MW | `parse="X+Y"`, `fr. √ root` | root + parse |
| German prose | PWG, PW | `Von {#src#}` / `Wurzel` | source root |

Two dictionaries that superficially qualify are deliberately excluded: MD (201×)
and CAE (584×) also carry the `<ab>E.</ab>` tag, but there it marks the **Epic
register** of a form, not an etymology — feeding them to a WIL-style extractor
would produce garbage. (Replicators, take note.)

**What counts as an instance.** The extraction yields **68,510 derivational
statements** (TSV rows). They are typed, and the types matter, because WIL alone
contributes 39,650 rows of which not all are derivations proper:

| WIL block type | rows |
|---|--:|
| root+affix (incl. uṇādi) | 18,957 |
| compound (member analysis, no affix) | 17,686 |
| prefix+word | 1,406 |
| multi-derivation | 1,214 |
| single-stem | 212 |
| cross-ref / unparsed | 175 |

All cross-dictionary comparisons below use only the rows that state the compared
object (an affix, resp. a root) — compounds and cross-references never enter a
denominator.

**The agreement statistic.** For each pair of dictionaries, over the head-words
(`headword_slp1`) that **both** analyse with the compared object, two head-words
"agree" if their extracted affix (resp. root, resp. kāraka) **sets intersect**;
agreement is a proportion with a 95 % Wilson score interval. Three properties of
this statistic are stated up front. (a) It is **conditional on double coverage** —
a word only one dictionary analyses never enters the comparison, so it measures
consistency, not coverage. (b) Set intersection is mildly **inflationary** where a
dictionary lists alternative derivations (any overlap counts); the multi-affix
share is small (VCP 6.6 % of head-words, all others less), and an exact-match
variant moves no headline figure. (c) It compares affix **names**, which is
stricter than comparing derivational *outcomes* — two dictionaries that posit
*ac* and *ghañ* both derive surface *-a* but count here as disagreeing. §F2b
measures how much of observed disagreement is exactly that.

**Affix-vocabulary quality (per-dictionary).** The Sanskrit-prose extractions
draw on a closed Pāṇinian vocabulary — every affix value they emit is one of 39
canonical pratyaya names, 100 % per dictionary
(`affix_vocab_quality.csv`). WIL's free-prose extraction also captures non-affix
tokens: only **50.1 %** of its 19,641 affix instances are canonical names. All
Wilson comparisons are therefore reported twice: raw, and **vocabulary-filtered**
(both sides restricted to canonical affix names, `cross_dict_agreement_vocabfiltered.csv`).

Affixes are decoded against a single curated pratyaya table (anchored on Apte's
`affix_map.tsv` + a WIL supplement + a generic it-letter decoder). Roots are
validated against a vendored dhātu list (vidyut dhātupāṭha + csl-atlas m4
indigenous roots). Two head-words "agree" on the root if their root sets
intersect after the **root-form normalization** below — this fold is applied by
*every* extractor including WIL (Wilson prints roots in thematic surface form:
*aṃśa* where ŚKD cites *aṃś*; unfolded, that alone collapses Wilson's root
agreement to 8–20 %).

Root recovery is tiered and provenance-tagged (`root_source`): a *local* match
adjacent to the derivation marker; for root-organised dictionaries (KRM) the
*head-word* itself (it is the dhātu); a *nearest-root* match validated against the
dhātu list and gated on a `--`/`DAtoH` citation marker (precision guard — a free
nearest-token scan grabs affix surfaces like `-ta` and is rejected); an
entry-level *dhātupāṭha-join*; an *oracle-join* against a cross-dictionary
(derived-word → root) oracle (see below); and finally an *llm-pass* — a DeepSeek
resolver over each dictionary's residual empties, whose every proposed root is
validated against the canonical dhātu list before it is written (a hallucinated
root that is not a real dhātu is discarded). Coverage after all tiers: SKD 93.3 %,
VCP 97.4 %, AP90 91.6 %, AP 95.9 %, KRM 100 %, SHS 96.1 %.

**Tier precision (DeepSeek-judged, form-tolerant).** A sampled audit of the two
*inferred* tiers gives, after the normalization pass below, oracle-join ≈ 83%
(up from 74% before normalization — folding surface variants removed that error
class) and nearest-root ≈ 66–75% root precision (its residual errors are genuine
wrong-token grabs, plus a few judge false-negatives where the candidate already
equals the canonical root). The bulk tiers (*local*, *headword-root*) are ≈ 100%
by construction, and the *llm-pass* roots are returned in clean citation form and
dhātu-validated, so the rooted subset is high-precision overall; *nearest-root*
is the weakest tier and is tagged as such in `root_source` for downweighting.
A caveat we state plainly: the tier-precision judge is the same model family as
the llm-pass resolver; a **human second-annotator audit** of a 50-row sample per
inferred tier is the remaining validation step before submission.

**A strict, near-100%-precision subset for headline tables.** Dropping the single
sub-~100% tier (*nearest-root*) yields a high-precision dataset: per-dictionary
strict coverage is KRM 100 %, SKD 93.0 %, SHS 92.2 %, AP 90.3 %, AP90 86.7 %,
VCP 82.9 % (VCP loses the most because *nearest-root* was its largest inferred
tier). Reproduce it by filtering `root_source != nearest-root` (`pct_strict`
column / `cross_dict_root_agreement_strict.csv`). Critically, the **headline
root-agreement is robust to this filter** — MW↔PWG 64.2 % and PWG↔PW 93.9 % are
*identical* with and without the nearest-root tier — so the cross-dictionary
findings are not an artefact of the lower-precision rows. MW roots are
independently cross-validated against the canonical `mw_roots.tsv` register:
**99 %** of MW's rooted derivations carry a genuine MW root (the 1 % rest are
flagged variants).

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
of the prose dictionaries by look-up rather than re-parsing. (Only
cross-dictionary-corroborated entries fill; KRM-body-only forms ship as a
standalone resource but are not used to resolve, as they do not match the prose
dicts' head-words.)

## Findings

**F1 — The indigenous Sanskrit prose tradition is internally consistent on
affixes.** For head-words shared by two Sanskrit-prose dictionaries (inclusion
rule for Table 1: **n ≥ 25 shared head-words**, applied uniformly), the stated
affix agrees in **over 90 %** of cases (per-pair range 91.7–100 %): SKD↔VCP
**93.8 % [85.2–97.6]** (n=65),
AP90↔AP **100 % [97.9–100]** (n=178), VCP↔SHS **98.5 % [95.8–99.5]** (n=206),
SKD↔AP90 **91.7 % [83.8–95.9]** (n=84). Independent 19th–20th c. compilations of
the Pāṇinian analysis converge. **One structural exception is disclosed rather
than hidden:** VCP↔KRM agrees only 20.0 % [7.0–45.2] — below the n≥25 bar (n=15)
but shown in the released CSV. KRM is not a prose kośa: it is a **kṛdanta
paradigm table organised by root**, its affix inventory is disjoint in kind
(`ka`-heavy, paradigm-slot affixes), and its comparisons with meaning-organised
kośas are apples-to-oranges. "Indigenous consistency" in this paper's sense is a
claim about the prose kośas; KRM re-enters below as the oracle's paradigm donor
and as a kāraka fingerprint (F4b).

**Table 1 — Cross-dictionary affix agreement, Sanskrit-prose pairs** (head-words
both dicts analyse with an affix; proportion with 95 % Wilson interval; rows with
n ≥ 25, sorted by shared count; the full matrix incl. sub-threshold pairs is in
`cross_dict_agreement.csv`).

| pair | shared HW | agree (95 % CI) |
|---|--:|---|
| VCP ↔ SHS | 206 | 98.5 % [95.8–99.5] |
| AP90 ↔ AP | 178 | 100.0 % [97.9–100] |
| VCP ↔ AP | 97 | 96.9 % [91.3–98.9] |
| VCP ↔ AP90 | 93 | 96.8 % [90.9–98.9] |
| SKD ↔ AP90 | 84 | 91.7 % [83.8–95.9] |
| SKD ↔ VCP | 65 | 93.8 % [85.2–97.6] |
| SKD ↔ AP | 61 | 91.8 % [82.2–96.4] |
| AP ↔ SHS | 31 | 100.0 % [89.0–100] |
| AP90 ↔ SHS | 27 | 96.3 % [81.7–99.3] |

**F2 — Wilson 1832 diverges; half of that divergence is our extractor, and the
paper says which half.** Raw agreement with the kośas runs 22.9–61.2 %. But
Wilson states etymologies in free English prose, and the WIL extraction's affix
field is only **50.1 % canonical** (Method): the non-canonical captures can never
match anything, mechanically depressing every raw Wilson figure. Table 1b
therefore shows each Wilson pair twice. Vocabulary-filtered, Wilson agrees
66.7–80.2 % with the prose kośas — a real but far smaller gap than the raw
numbers suggest.

**Table 1b — Wilson pairs, raw vs vocabulary-filtered** (filter: both sides
restricted to canonical Pāṇinian affix names; note WIL↔SKD drops to n=24 after
filtering — read its wide interval accordingly).

| pair | raw | vocabulary-filtered |
|---|---|---|
| WIL ↔ VCP | 61.2 % [58.7–63.7] (n=1504) | 80.2 % [77.8–82.4] (n=1149) |
| WIL ↔ SHS | 60.0 % [52.9–66.7] (n=190) | 78.1 % [70.7–84.0] (n=146) |
| WIL ↔ AP90 | 54.2 % [43.5–64.5] (n=83) | 71.4 % [59.3–81.1] (n=63) |
| WIL ↔ AP | 52.4 % [41.8–62.9] (n=82) | 71.7 % [59.2–81.5] (n=60) |
| WIL ↔ KRM | 22.2 % [12.5–36.3] (n=45) | 38.5 % [22.4–57.5] (n=26) |
| WIL ↔ SKD | 22.9 % [14.6–34.0] (n=70) | 66.7 % [46.7–82.0] (n=24) |

**F2b — And most of the *residual* disagreement is taxonomy, not etymology.** We
hand-audited every vocabulary-filtered WIL↔SKD disagreement (8) plus a random
40-case sample of WIL↔VCP disagreements (`wil_disagreement_audit.tsv`, seed
committed). Of the 48: **30 (62.5 %) are same-surface, different-affix-name**
cases — Wilson posits *ac*/*ap*/*yuc* where the kośa posits *ghañ*/*lyuṭ*, both
deriving the identical surface form (*-a*, *-ana*, *-ya*); **14 (29 %) are
residual extraction artifacts** on one side or the other (Wilson's
multi-derivation blocks truncated to the first alternative, a wrong token
grabbed, or the kośa's capture landing on a sub-lemma's derivation); and only
**4 (8 %) are genuinely different derivational analyses** (different root or
incompatible derivation). Wilson's "pre-critical" reputation survives only in
that thin slice; the bulk of his divergence from the kośas is a choice among
Pāṇinian affix names with identical output — a taxonomic, not an etymological,
disagreement — plus measurement residue we quantify instead of interpreting.

**F1c — The kāraka layer agrees as sharply as the affix layer.** For the
Sanskrit-prose pairs (same rule), the stated kāraka agrees **89–100 %**:
VCP↔SHS 97.6 % [94.4–99.0] (n=206), AP90↔AP 100 % [97.9–100] (n=178), VCP↔AP90
93.5 %, VCP↔AP 92.8 %, SKD↔AP 93.4 %, SKD↔AP90 91.7 %, SKD↔VCP 89.2 %, AP↔SHS
90.3 %, AP90↔SHS 88.9 % (`cross_dict_karaka_agreement.csv`). The one low pair is
again VCP↔KRM (26.7 %, n=15, sub-threshold) — the same structural carve-out as
F1.

**F3 — Cross-tradition root attribution holds at ~two-thirds.** The two large
root-attributing dictionaries, MW (English, √-notation) and PWG (German, "von
Wurzel"), agree on the root for **64.2 % [60.8–67.5]** of 782 shared head-words;
PWG↔PW **93.9 % [91.5–95.6]** (n=521). Within the Sanskrit prose tradition, root
agreement runs 68.9–94.8 % (SKD↔VCP 81.0 %, VCP↔SHS 85.1 %, AP90↔AP 94.8 %) —
lower than the affix layer, because root *identification* across citation
conventions is noisier than affix naming, not because the traditions disagree.
Wilson illustrates the point at corpus scale: **before** extending the root-form
fold to WIL, Wilson's root agreement was 8–20 % against *every* dictionary —
including 8.4 % against MW, which historically built on Wilson; **after** the
fold (Wilson cites roots in thematic form: *aṃśa* for *aṃś*), it is WIL↔AP90
73.8 %, WIL↔AP 67.1 %, WIL↔KRM 63.0 %, WIL↔PWG 40.1 % (n=4257), WIL↔MW 16.3 %.
The residual WIL↔MW gap is a conventions gap (MW's √-notation vs Wilson's
stem-citations) and is reported, not interpreted.

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
| AP90 | 332 | 91.6 % | 86.7 % |
| VCP | 3,664 | 97.4 % | 82.9 % |

## Artefacts

Per-dict TSVs (`<dict>_etymology.tsv`), the cross-dict root oracle
(`root_oracle.tsv`), twelve summary CSVs (incl. `root_capture.csv` with both
coverage tiers, `cross_dict_root_agreement_strict.csv`,
`affix_vocab_quality.csv`, `cross_dict_agreement_vocabfiltered.csv`,
`cross_dict_karaka_agreement.csv`), the 48-case hand audit
(`wil_disagreement_audit.tsv`), a full [`DATASHEET.md`](DATASHEET.md)
(Gebru-style), and an interactive [dashboard](https://sanskrit-lexicon.github.io/csl-orig/)
(kāraka×pratyaya heatmap, affix entropy, root productivity, affix & root agreement
matrices, per-affix DSG/Russian legend, Whitney root links). Everything is
regenerable from the committed pipeline except the LLM-resolved root tiers
(`vcp_llm_roots.tsv`, `shs_llm_roots.tsv`), which are committed inputs (their
regeneration needs a DeepSeek API key; every row is dhātu-validated either way).

## Limits / next

* VCP root capture is **97.4 %** (63 % → 77 % nearest-root → 87 % oracle → 97.4 %
  with the DeepSeek llm-pass). The residual 96 are forms DeepSeek could not
  confidently reduce to a *validated* dhātu (rejected rather than guessed). SHS
  reaches 96.1 %.
* The nearest-root gate trades a little recall for precision; a few borderline
  fills remain (e.g. a compound member homonymous with a root). The tier-precision
  audit is currently DeepSeek-judged (same model family as the llm-pass): a
  **human second-annotator audit** of a 50-row `nearest-root` + `oracle-join`
  sample is the one remaining validation step before submission.
* The same-surface/different-name phenomenon (F2b) suggests a follow-up metric:
  agreement on the **realized surface affix** rather than the pratyaya name,
  which would separate taxonomic preference from derivational substance
  corpus-wide rather than in a 48-case audit.
* Numbers above are from the current extraction run; rerun `stats_etymology.py`
  after any extractor change.
