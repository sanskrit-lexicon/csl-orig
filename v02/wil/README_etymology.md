# WIL etymology (`E.`) analyser

[`analyze_wil_etymology.py`](analyze_wil_etymology.py) parses every `<ab>E.</ab>`
etymology block in [`wil.txt`](wil.txt) (Wilson, *A Dictionary, Sanscrit and
English*, Calcutta 1832) and decomposes each into **root/stem + meaning +
affix + the affix's anubandha (it-marker) meaning**.

```sh
python analyze_wil_etymology.py            # reads ./wil.txt
python analyze_wil_etymology.py path/to/wil.txt
```

Outputs (regenerated each run):

| file | shape | tracked? |
|---|---|---|
| `wil_etymology.tsv` | flat, one row per entry | **yes** — committed |
| `wil_etymology.jsonl` | full nested record (member list + every alternative derivation) | no (21 MB, git-ignored; regenerate from the script) |

### TSV columns

`L_id` · `headword` · `headword_slp1` · `type` · `root` · `root_meaning` ·
`affix` · `affix_slp1` · `group` · `anubandha` · `anubandha_steps` ·
`affix_source` · `raw`

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

## Teaching layer (`group` + `anubandha_steps`)

Two helpers are **mirrored from** the project's affix teaching tool
[`affix_pedagogy.py`](../../../SanskritLexicography/RussianTranslation/research/affix_pedagogy.py)
(copied, not imported, because its `apte_parse → sanskrit_util` chain is too
heavy for a csl-orig script):

* **`group`** — `group_of(function, kind)` buckets each affix by *what it makes*.
  The base buckets are mirrored from `affix_pedagogy.py`; this script extends
  them for Wilson's tail: Agent · Participle · Gerundive · Action/result noun ·
  Abstract quality · Feminine stem · Possessive · Comparison · Adverb · Temporal ·
  Relational/patronymic · Diminutive · Augment (āgama) · **Absolutive** ·
  **Bare root / zero affix** · **Material / abundance** ·
  **Compound-final (samāsānta)** · Uṇādi formation ·
  **Derivative noun / adjective** · Other.
* **`anubandha_steps`** — the per-pratyaya it-marker **stripping steps** (P.1.3.2–
  1.3.9 + substitutions), e.g. `kta` → `k = it (P.1.3.8) ; → surface -ta`;
  `ghañ` → `gh = it (initial) ; ñ = it (→ vṛddhi) ; → -a`. Populated for the
  canonical pratyayas; WIL-supplement affixes fall back to the prose `anubandha`
  note and the generic it-letter decoder.

## Use cases

* **Lexicography QA** — flag entries whose stated affix is inconsistent with the
  surface ending, or where Wilson's derivation differs from MW/Apte (join on
  `affix` + `affix_source`).
* **Teaching / grammar drills** — generate "root + meaning → affix → form" cards;
  `group` gives the pedagogical bucket, `anubandha_steps` the Pāṇinian derivation.
* **Affix productivity stats** — count distinct roots per `affix`/`group` across
  WIL and compare with the Apte-SH base (`affix_map.tsv`) to measure each
  dictionary's formation-affix coverage.
* **Uṇādi / rare-affix study** — filter `affix_source = WIL` to isolate the long
  Uṇādi tail Wilson records that the productive Apte set omits.
* **Compound & privative mining** — `type = compound` / `prefix+word` rows give a
  ready word-formation dataset (members in the JSONL) with no affix noise.
* **Cross-dictionary linking** — `root` + `root_meaning` keyed in SLP1/IAST for
  joins to MW, Apte, PWG, etc.

## Not applicable to SKD / VCP (and other Sanskrit→Sanskrit dictionaries)

This parser targets Wilson's `<ab>E.</ab>` English-prose etymology. The
Sanskrit→Sanskrit dictionaries **Śabdakalpadruma (SKD)** and **Vācaspatyam
(VCP)** carry **zero `<ab>E.</ab>` blocks** — their derivations are stated *in
Sanskrit* (`vyākaraṇam`, `dhātuḥ`, pratyaya names in Devanāgarī, citations via
`iti`), so this tool does not apply to them. A separate Sanskrit-side derivation
extractor would be needed for SKD/VCP.

Sanskrit is transcoded SLP1→IAST via `indic_transliteration`.
