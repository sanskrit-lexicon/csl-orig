# MW (Monier-Williams) derivation extractor

[`analyze_mw_etymology.py`](analyze_mw_etymology.py) mines Monier-Williams'
etymology, which uses neither WIL's `<ab>E.</ab>` nor SKD/VCP's `kāraka+pratyaya`.
MW marks derivation two ways, both extracted:

| signal | count | example |
|---|--:|---|
| `parse="X+Y"` (in `<info>`) | ~7,000 | `parse="aMSI+kf"` → aṃśī + √kṛ |
| `fr. √ <s>root</s>` (prose) | ~2,300 | "(probably fr. √ aś …)" → √aś |

```sh
python analyze_mw_etymology.py mw.txt      # -> mw_etymology.{tsv,jsonl}
```

## Each parse member is classified against existing tables

No new lexica — every `parse=` member is typed by reusing the project's own data:

* **root** — member is in the canonical dhātu list
  ([`../etymology_stats/dhatu_roots.txt`](../etymology_stats/dhatu_roots.txt))
* **affix** — member is a known pratyaya (the `../wil` affix table)
* **prefix** — member is an upasarga (checked first; many prefixes share a root's
  surface form, but in `abhi+kf` the abhi is the prefix)
* **stem** — anything else (a compound member)

From these, `deriv_type` is assigned: `prefix+root`, `root+affix`,
`stem+root (denominal/cmpd)`, `compound`, `root-attribution`.

## Coverage (current run)

9,377 derivations · **90% with an identified root** · top roots `kṛ` (845),
`bhū`, `i`, `gam`, `dhā` — genuine dhātus, cross-validating the dhātu list.

MW's etymology is **root-attribution**, so it feeds the cross-dictionary **root**
agreement and **root productivity** analyses in
[`../etymology_stats/`](../etymology_stats/README.md), not the affix/kāraka ones
(MW rarely names a pratyaya).

## Columns

`L_id` · `headword` · `headword_slp1` · `root` · `root_slp1` · `root_via`
(`parse` | `fr-root`) · `prefixes` · `affix` · `affix_slp1` · `group` ·
`anubandha` · `anubandha_steps` · `affix_source` · `deriv_type` · `parse` ·
`context`. TSV committed; jsonl git-ignored.
