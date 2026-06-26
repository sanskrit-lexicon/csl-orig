# Cross-dictionary etymology statistics

[`stats_etymology.py`](stats_etymology.py) aggregates the per-dictionary
`*_etymology.tsv` extractions (produced by
[`../wil/analyze_wil_etymology.py`](../wil/analyze_wil_etymology.py) and
[`../skd/analyze_sktdict_etymology.py`](../skd/analyze_sktdict_etymology.py))
into cross-dictionary statistics and one self-contained HTML dashboard.

```sh
python stats_etymology.py        # auto-detects sibling <dict>/<dict>_etymology.tsv
```

## Dictionaries covered

| dict(s) | style | gives |
|---|---|---|
| WIL | English-prose `<ab>E.</ab>` | root + affix |
| SKD, VCP, **Apte (AP90)**, AP, SHS, KRM | Sanskrit-prose `kāraka + pratyaya` | root + kāraka + affix |
| MW | `parse="X+Y"` + `fr. √ root` | root + parse |
| PWG, PW | German `Von {#src#}` / `Wurzel` | source root |

Affix & kāraka analyses use the affix-tagging dicts (WIL + Sanskrit-side); the
**root** analyses (productivity, cross-dict root agreement) span every dict that
yields a verbal root (Sanskrit-side + MW + PWG/PW). **CAE and MD are excluded on
purpose**: their `<ab>E.</ab>` means "Epithet of" / "Epic", not Etymology.

## Outputs

`affix_frequency.csv` · `karaka_distribution.csv` · `karaka_x_affix_matrix.csv` ·
`group_distribution.csv` · `affix_entropy.csv` · `cross_dict_agreement.csv` ·
`root_productivity.csv` · `root_capture.csv` · **`dashboard_etymology.html`**
(open in a browser — Chart.js loaded from CDN; the heatmap is inline).

## Headline findings (current run)

* **The Sanskrit grammatical tradition is internally consistent.** Sanskrit-side
  dicts agree on a head-word's affix **90–100%** of the time (SKD↔VCP 94%,
  Apte↔AP 100%, VCP↔SHS 98%) — strong cross-validation of the extraction.
* **Wilson diverges.** WIL agrees with SKD only 23% and VCP 61% — confirming
  Wilson's idiosyncratic 1832 etymologies vs the indigenous tradition.
* **kāraka × pratyaya structure** is linguistically sound: `lyuṭ` → bhāve/karaṇe,
  `kta` spreads bhāve/karmaṇi/kartari, `lyu` is monosemous (kartari, entropy 0.33).
* **Affix generality** (kāraka-spread entropy): `ḍa`, `anīyar`, `yat`, `ac` are
  generalists; `lyu`, `ṣṭran`, `aṅ` are specialised.

Regenerate after re-running any analyser; CSVs + dashboard are committed.
