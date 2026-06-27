# SKD / VCP Pāṇinian derivation extractor

[`analyze_sktdict_etymology.py`](analyze_sktdict_etymology.py) mines the
Pāṇinian **derivation** (vyutpatti) stated inside the entry bodies of the two
Sanskrit→Sanskrit dictionaries:

* **SKD** — Śabdakalpadruma ([`skd.txt`](skd.txt))
* **VCP** — Vācaspatyam ([`../vcp/vcp.txt`](../vcp/vcp.txt))

```sh
python analyze_sktdict_etymology.py skd.txt          # -> skd_etymology.{tsv,jsonl}
python analyze_sktdict_etymology.py ../vcp/vcp.txt   # -> ../vcp/vcp_etymology.{tsv,jsonl}
```

## Also runs on other Cologne Sanskrit-prose dictionaries

The same kāraka + pratyaya pattern appears in several more dicts — the extractor
takes any of them as its argument:

| dict | derivations | root captured | note |
|---|--:|--:|---|
| SKD | 2,214 | 90% | Śabdakalpadruma |
| VCP | 3,664 | 77% | Vācaspatyam |
| **Apte (AP90)** | 332 | 89% | Apte 1890 — the Apte representative |
| AP | 339 | 91% | Apte (practical) |
| SHS | 258 | 20% | Śabda-sāgara (Wilson tradition; rarely links root to kāraka) |
| KRM | 305 | 100% | Kṛdanta-rūpa-mālā — organised by root, so head-word = dhātu |

Cross-dictionary statistics over all of these (plus WIL) live in
[`../etymology_stats/`](../etymology_stats/README.md).

## Why a different parser from WIL / Apte

WIL and Apte mark etymology in a dedicated field (WIL's `<ab>E.</ab>`, Apte's
structured parse). **SKD and VCP have no such field** — they carry **zero
`<ab>E.</ab>` blocks**. Their derivations are written *in Sanskrit* inside the
prose, in the classical shape:

| dict | separator | example | reads as |
|---|---|---|---|
| SKD | `+` chain | `vi + kzip + BAve GaY` | vi-√kṣip, **bhāve**, ghañ → *vikṣepa* |
| VCP | `--` / `-` | `kf--BAve lyuw` | √kṛ, **bhāve**, lyuṭ → *karaṇa* |
| both | `<root>DAtoH …` | `jiDAtoH karmmaRi yat` | √ji, **karmaṇi**, yat |

So this tool keys off the **kāraka + pratyaya** adjacency, recovering the root
from the `+`-chain (SKD), the `--`/`-` separator (VCP), or a `…DAtoH` genitive.

## What it adds over WIL: the kāraka

SKD/VCP state the **kāraka** — the *sense* in which the affix derives the word —
which WIL leaves implicit. It is captured in `karaka` / `karaka_sense`:

`BAve` action/abstract · `karaRe` instrument · `karmaRi` object ·
`kartari` agent · `aDikaraRe` location · `apAdAne` source · `sampradAne` recipient.

## Shared affix decoding (reused, not reinvented)

The `affix`, `group`, `anubandha`, `anubandha_steps`, `affix_source` columns come
straight from the WIL analyser's machinery, imported from
[`../wil/analyze_wil_etymology.py`](../wil/analyze_wil_etymology.py) (which itself
reuses the canonical `affix_map.tsv` mined from Apte Sanskrit–Hindi, plus the WIL
supplement and a generic it-letter decoder). One owner for the affix data across
WIL, SKD and VCP.

## Columns

`L_id` · `headword` · `headword_slp1` · `root` · `root_slp1` · `root_source` ·
`prefixes` · `karaka` · `karaka_sense` · `affix` · `affix_slp1` · `group` ·
`anubandha` · `anubandha_steps` · `affix_source` · `context`

`root_source` records how the root was recovered, tiered most-to-least direct:
* `local` — a `+`/`--`/`DAtoH` pattern next to the kāraka.
* `headword-root` — for root-organised dictionaries (KRM = Kṛdanta-rūpa-mālā) the
  head-word *is* the dhātu, so it fills every derivation in the entry (KRM → 100%).
* `nearest-root` — the nearest known dhātu (validated against the dhātu list) that
  sits in a `--`/`DAtoH`/`Ric` citation context within the preceding window. The
  citation gate is the precision guard: a free nearest-token scan grabbed affix
  surfaces (`-ta`) and inflected non-roots; gating on the marker keeps it clean
  (e.g. `kzuBa--Ric karmmaRi` → kṣubh). This recovers most of VCP's tail (63→77%).
* `dhatupatha-join` — entry-level fallback: an entry citing exactly one root that
  is in the canonical list.
* empty — no root recoverable; kept honest rather than mis-filled.

Coverage: SKD 90% · VCP 77% · Apte 89% · AP 91% · KRM 100% · SHS 20%.

`*_etymology.tsv` is committed; the larger `*_etymology.jsonl` is git-ignored
(regenerate from the script).

## Coverage (current run)

| dict | derivations | distinct entries | root recovered |
|---|--:|--:|--:|
| SKD | 2,214 | 2,038 | 89% |
| VCP | 3,660 | 2,967 | 62% |

Empty-root rows are honest gaps: the root sits in a far-away gaṇa gloss
(`aMSa viBAjane …`) with no `+`/`--`/`DAtoH` link to the kāraka — the kāraka,
affix and anubandha are still extracted.

## Use cases

* **Cross-dictionary derivation comparison** — join WIL `root`+`affix` against
  SKD/VCP `root`+`affix`+**`karaka`** to see where the dictionaries agree on a
  word's formation and where the Sanskrit tradition adds the kāraka WIL omits.
* **Kāraka-conditioned affix study** — which pratyaya forms which kāraka sense
  (e.g. `lyuṭ` overwhelmingly `bhāve`/`karaṇe`); the kāraka × affix matrix.
* **Teaching** — "√root + kāraka → affix → word" cards with `anubandha_steps`.
* **Root-frequency / productivity** across the Sanskrit lexicographic tradition.
* **Seeding a derivation layer** for SKD/VCP that they never had as markup.
