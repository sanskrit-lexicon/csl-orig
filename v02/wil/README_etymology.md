# WIL etymology (`E.`) analyser

[`analyze_wil_etymology.py`](analyze_wil_etymology.py) parses every `<ab>E.</ab>`
etymology block in [`wil.txt`](wil.txt) (Wilson, *A Dictionary, Sanscrit and
English*, Calcutta 1832) and decomposes each into **root/stem + meaning +
affix + the affix's anubandha (it-marker) meaning**.

```sh
python analyze_wil_etymology.py            # reads ./wil.txt
python analyze_wil_etymology.py path/to/wil.txt
```

Outputs (regenerated each run, **git-ignored** — not committed):

| file | shape |
|---|---|
| `wil_etymology.tsv` | flat, one row per entry |
| `wil_etymology.jsonl` | full nested record (member list + every alternative derivation) |

## The four fields (Wilson's `anya` example)

```
{#ana#} to live, and {#yak#} <ab>aff.</ab>
```

| field | value |
|---|---|
| root / stem | `ana` |
| meaning | `to live` |
| affix | `yak` |
| **anubandha** | kṛt affix 'yak' → -ya; derivative noun/adjective \| **k = kit → blocks guṇa/vṛddhi of the root vowel (1.1.5)** |

## Entry types (nothing is dropped — every block is classified)

`root+affix` · `compound` (two words, no affix) · `prefix+word` (privative) ·
`multi-derivation` (alternatives, each parsed) · `single-stem` · `cross-ref`
("See the last.") · `unparsed`.

## Affix knowledge base & provenance

The anubandha decoding is **reused, not reinvented**. Two layers, kept
provenance-tagged so they never silently merge (`affix_source` column):

1. **`Apte-SH(affix_map.tsv)`** — the project's single canonical affix table,
   [`SanskritLexicography/RussianTranslation/research/affix_map.tsv`](../../../SanskritLexicography/RussianTranslation/research/affix_map.tsv),
   mined from the **Apte Sanskrit–Hindi** `.babylon` dictionary by `apte_parse.py`
   (~27 productive kṛt/taddhita/strī pratyayas). Loaded at runtime, re-keyed
   IAST→SLP1. Override the path with `AFFIX_MAP=/path/to/affix_map.tsv`.
2. **`WIL`** — the `SUPPLEMENT` table inside this script: ~59 affixes Wilson
   uses that `affix_map` does not carry (the long Uṇādi / rare-pratyaya tail,
   `śatṛ`, `śānac`, `kvip`, `ṇyat`, `iṭ`-augment, single-vowel Uṇādis …).
3. **`generic-decoder`** — fallback for uncurated affixes: strips and decodes the
   indicatory it-letters per Pāṇini 1.3.x (k=kit, ṇ=ṇit→vṛddhi, ś=śit, c=cit …).

**Apte-SH vs WIL in one line:** both name affixes by their Pāṇinian
(anubandha-bearing) name, so the same decoding applies — but Apte gives a
*structured* prefix-root parse over a small productive set, whereas WIL gives
*free-prose English* etymology over a far larger inventory (~70+), heavy on
Uṇādi affixes and on non-affix compounds/privatives.

Sanskrit is transcoded SLP1→IAST via `indic_transliteration`.
