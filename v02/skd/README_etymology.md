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

`L_id` · `headword` · `headword_slp1` · `root` · `root_slp1` · `prefixes` ·
`karaka` · `karaka_sense` · `affix` · `affix_slp1` · `group` · `anubandha` ·
`anubandha_steps` · `affix_source` · `context`

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
