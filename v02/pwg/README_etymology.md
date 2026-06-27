# PWG / PW (German Petersburg) derivation extractor

[`analyze_pwg_etymology.py`](analyze_pwg_etymology.py) mines the derivation notes
of the German Petersburg dictionaries PWG (großes PW) and PW (kürzere Fassung).
They mark derivation in German prose with the source word in SLP1:

| cue | example | reads as |
|---|---|---|
| `Von {#src#} {%gloss%}` | `Von {#aMSa#} {%Theil%}` | from aṃśa "part" |
| `(von {#src#})` | `aMSaka (von {#aMSa#})` | aṃśaka ← aṃśa |
| `Wurzel {#src#}` | `Wurzel {#pA#}` | root pā |

```sh
python analyze_pwg_etymology.py pwg.txt        # -> pwg_etymology.{tsv,jsonl}
python analyze_pwg_etymology.py ../pw/pw.txt   # PW too
```

## Precision guard

`von` is ordinary German "of/from", so two filters keep precision high:
* the source must be in `{#..#}` (SLP1) — proper-name epithets ("von
  <is>Viṣṇu</is>") are in `<is>..</is>` and excluded;
* a lowercase `von` is only kept when its source is a **known dhātu** (validated
  against [`../etymology_stats/dhatu_roots.txt`](../etymology_stats/dhatu_roots.txt));
  capitalised `Von` and `Wurzel/Stamm` are kept regardless.

Each source is classified `root | affix | prefix | stem/word` via the same dhātu
list + affix table the other extractors use.

## Coverage

PWG 10,266 derivations · PW 767. Top source roots `kṛ`, `i`, `dhā`, `bhū`, `han`,
`sthā` — genuine dhātus. PWG feeds the cross-dictionary **root** productivity and
agreement in [`../etymology_stats/`](../etymology_stats/README.md); PWG↔PW agree
93% on roots, MW↔PWG 65% (a cross-tradition English/German check).

## Columns

`L_id` · `headword` · `headword_slp1` · `source` · `source_slp1` ·
`source_class` · `is_root` · `source_gloss_de` · `deriv_marker` · `context`.
TSV committed; jsonl git-ignored.
