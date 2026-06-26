#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_wil_etymology.py  --  Parse the etymology (E.) blocks of Wilson 1832 (WIL).

Wilson gives, for most entries, an `<ab>E.</ab>` block that decomposes the
head-word into a root/stem + an affix (pratyaya), e.g.

    <L>1878...<k1>anya...
    <ab>E.</ab>
    {#ana#} to live, and {#yak#} <ab>aff.</ab>

  -> root   = ana      (IAST)        meaning = "to live"
     affix  = yak                    anubandha = function + it-marker decoding of `yak`

The field is highly varied (compounds with no affix, privative prefixes,
Unadi affixes, cross-references, multiple alternative derivations), so every
block is CLASSIFIED with a `type` and nothing is silently dropped.

Output (next to wil.txt):
    wil_etymology.tsv     -- flat, one row per entry (multi-derivation -> first only, rest in raw)
    wil_etymology.jsonl   -- full nested record incl. every alternative derivation

Usage:
    python analyze_wil_etymology.py [path/to/wil.txt]
"""
import sys, os, re, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from indic_transliteration import sanscript
    def to_iast(s):
        return sanscript.transliterate(s, sanscript.SLP1, sanscript.IAST)
except Exception:
    def to_iast(s):
        return s  # fall back to raw SLP1 if library missing

# ---------------------------------------------------------------------------
# Anubandha (it-marker) letter decoding -- general Paninian it-samjna rules.
# Used both to build the curated table notes and as a fallback decoder for
# affixes not individually curated below.
# ---------------------------------------------------------------------------
IT_LETTERS = {
    'k': "kit: blocks guna/vrddhi of the root vowel (1.1.5 kniti ca)",
    'N': "nit: blocks guna/vrddhi of the root vowel (1.1.5 kniti ca)",
    'G': "git: treated as nit -> blocks guna/vrddhi (1.1.5)",
    'Y': "nit (n~): causes adi-vrddhi of the base (7.2.117) and svarita/ubhayapada",
    'R': "nit (.n): causes vrddhi of the base vowel (7.2.115-117)",
    'w': "tit (.t): feminine is formed with nip -i (4.1.15)",
    'q': "dit (.d): the .ti portion of the base is elided (6.4.143)",
    'z': "sit (.s): feminine is formed with nis -i (4.1.41)",
    'S': "sit (z): marks a sarvadhatuka / sit krt (3.4.113)",
    'c': "cit: final acute accent, antodatta (6.1.163)",
    'l': "lit: acute on the vowel just before the it-letter (6.1.193)",
    'm': "mit: as an augment, inserted after the last vowel of the base (1.1.47)",
    'p': "pit: the affix is anudatta / light (3.1.4)",
    't': "tit: svarita accent on the affix (6.1.185)",
    'u': "indicatory u: distinguishes the affix; conditions i.t in some forms",
    'f': "indicatory .r",
    'B': "indicatory bh",
}

# ---------------------------------------------------------------------------
# Curated affix table  (IAST head -> (realized, kind, function, anubandha, src))
#
# PROVENANCE is kept explicit so the two dictionaries never silently merge:
#   * BASE  = the project's single canonical source, reused not reinvented --
#     SanskritLexicography/RussianTranslation/research/affix_map.tsv, which is
#     mined from the Apte Sanskrit-Hindi (.babylon) dictionary by apte_parse.py.
#     These entries are tagged source = "Apte-SH(affix_map.tsv)".
#   * SUPPLEMENT = affixes Wilson 1832 uses that affix_map does NOT carry
#     (the long Unadi / rare-pratyaya tail). Tagged source = "WIL".
#
# Apte-SH vs WIL, in one line: both name the affix by its Paninian (anubandha-
# bearing) name, so the SAME decoding applies -- but Apte gives a STRUCTURED
# prefix-root parse over ~27 productive krt/taddhita pratyayas, whereas WIL gives
# FREE-PROSE English etymology over a far larger inventory (~70+), heavy on
# Unadi affixes and on non-affix compounds/privatives. That superset is exactly
# why SUPPLEMENT exists, and why its provenance is tagged.
# ---------------------------------------------------------------------------

# WIL affixes absent from affix_map.tsv (the long tail of Wilson's etymologies).
SUPPLEMENT = {
 'yak':   ("ya",   "kṛt",      "derivative noun/adjective",                       "k = kit -> blocks guṇa/vṛddhi of the root vowel (1.1.5)"),
 'śatṛ':  ("at",   "kṛt",      "present active participle (parasmaipada)",        "ś = śit -> sārvadhātuka (3.4.113); ṛ indicatory"),
 'śānac': ("āna",  "kṛt",      "present middle participle (ātmanepada)",          "ś = śit -> sārvadhātuka (3.4.113); c = cit final acute"),
 'śānan': ("āna",  "kṛt",      "present middle participle (reduplicated/liṭ)",    "ś = śit -> sārvadhātuka; n = nit"),
 'tṛn':   ("tṛ",   "kṛt",      "agent noun ('-er, doer')",                        "n = nit; udātta on first syllable"),
 'ktavatu':("tavat","kṛt",     "past active participle ('having done')",          "k = kit -> no guṇa; u indicatory"),
 'ktvā':  ("tvā",  "kṛt",      "absolutive / gerund ('having done')",             "k = kit -> no guṇa/vṛddhi of the root (1.1.5)"),
 'lyap':  ("ya",   "kṛt",      "absolutive of prefixed roots ('having done')",    "l = lit; p = pit; replaces ktvā after a prefix (7.1.37)"),
 'tavya': ("tavya","kṛt",      "future passive participle ('ought to be done')",  "gerundive; t = tit svarita accent"),
 'anīyar':("anīya","kṛt",      "future passive participle ('fit to be done')",    "r indicatory -> accent; gerundive"),
 'kvip':  ("",     "kṛt",      "zero affix -> root used directly as a noun",       "k,v,i,p all it -> the whole affix elides (6.1.67)"),
 'kvin':  ("",     "kṛt",      "zero affix forming agent / root-nouns",           "k,v,i,n it -> affix elides; root-final retained"),
 'ghinuṇ':("in",   "kṛt",      "agent / habitual-doer adjective ('-in')",         "ṇ = ṇit -> vṛddhi; gh = git -> no guṇa"),
 'ṇini':  ("in",   "kṛt",      "agent '-in' ('one who does')",                    "ṇ = ṇit -> vṛddhi of the base (7.2.115)"),
 'in':    ("in",   "taddhita", "possessive '-in' ('having')",                     "matvartha (possessive) affix"),
 'mayaṭ': ("maya", "taddhita", "'made of, consisting of, full of'",               "ṭ = ṭit -> feminine with ṅīp; material/abundance"),
 'itac':  ("ita",  "taddhita", "'furnished with, having' (denominal)",            "c = cit -> final acute (6.1.163)"),
 'ilac':  ("ila",  "taddhita", "'having, abounding in'",                          "c = cit -> final acute (6.1.163)"),
 'ila':   ("ila",  "taddhita", "'having, abounding in'",                          "matvartha (possessive) affix"),
 'ap':    ("a",    "kṛt",      "action / agent noun",                             "p = pit -> anudātta affix (3.1.4)"),
 'kyap':  ("ya",   "kṛt",      "future passive participle / gerundive",           "k = kit -> no guṇa; p = pit -> anudātta"),
 'ṛyat':  ("ya",   "kṛt",      "future passive participle (gerundive)",           "ṇ = ṇit -> vṛddhi (7.2.115); t = tit svarita"),
 'ki':    ("i",    "kṛt",      "noun of agency / instrument ('-i')",              "k = kit -> no guṇa/vṛddhi (1.1.5)"),
 'iñ':    ("i",    "kṛt",      "agent / action noun ('-i')",                      "ñ = ñit -> ādi-vṛddhi (7.2.117)"),
 'u':     ("u",    "uṇādi",    "Uṇādi agent/instrument noun ('-u')",              "indicatory u; Uṇādi affix"),
 'ku':    ("u",    "uṇādi",    "Uṇādi noun ('-u')",                               "k = kit -> no guṇa/vṛddhi (1.1.5)"),
 'asun':  ("as",   "uṇādi",    "Uṇādi neuter noun ('-as')",                       "u,n indicatory; Uṇādi affix"),
 'lā':    ("la",   "taddhita", "possessive '-la' ('having')",                     "matvartha (possessive) affix"),
 'ṇīn':   ("ī",    "strī",     "feminine in long -ī (ṅīn)",                       "ṇ = ṇit; feminine '-ī'"),
 'ṛī':    ("ī",    "strī",     "feminine in long -ī",                             "ṅī feminine; vṛddhi conditions"),
 'dhā':   ("dhā",  "taddhita", "adverb of manner ('in ... -fold / ways')",        "distributive / manner affix"),
 'ṭhañ':  ("ika",  "taddhita", "relational '-ika' adjective ('connected with')",  "ṭha -> ika (7.3.50); ñ = ñit -> ādi-vṛddhi"),
 'ḍhak':  ("eya",  "taddhita", "patronymic / relational adjective",               "ḍha -> eya; k = kit"),
 'yañ':   ("ya",   "taddhita", "patronymic (gotra) adjective",                    "ñ = ñit -> ādi-vṛddhi of the base (7.2.117)"),
 'vuñ':   ("aka",  "taddhita", "relational noun; vu -> aka",                      "ñ = ñit -> ādi-vṛddhi (7.2.117); vu -> aka (7.1.1)"),
 'vun':   ("aka",  "kṛt",      "agent / diminutive; vu -> aka",                   "vu -> aka (7.1.1); n = nit conditions"),
 'ḍa':    ("a",    "kṛt",      "agent noun (esp. after an upapada)",              "ḍ = ḍit -> the ṭi of the base is elided (6.4.143)"),
 'kha':   ("a",    "kṛt",      "agent noun in upapada compounds (mum-augment)",   "kh adds mu(ṭ) to the base (6.3.67)"),
 'cha':   ("iya",  "taddhita", "patronymic / relational adjective",               "ch -> īya substitute"),
 'ṇyat':  ("ya",   "kṛt",      "future passive participle / gerundive ('-ya')",   "ṇ = ṇit -> vṛddhi (7.2.115); t = tit svarita accent"),
 'yuc':   ("ana",  "kṛt",      "agent / action noun (yu -> ana)",                 "c = cit -> final acute accent (6.1.163)"),
 'tasi':  ("tas",  "taddhita", "ablatival adverb ('from, -wards')",               "'-tas' adverbial affix"),
 'añ':    ("a",    "taddhita", "patronymic / relational adjective (vṛddhi)",      "ñ = ñit -> ādi-vṛddhi of the base (7.2.117)"),
 'lac':   ("la",   "taddhita", "'having, abounding in' (matvartha)",              "c = cit -> final acute accent (6.1.163)"),
 'ṭac':   ("a",    "taddhita", "samāsānta '-a' (compound-final)",                 "ṭ = ṭit -> feminine with ṅīp (4.1.15)"),
 'gha':   ("iya",  "taddhita", "comparative-of-two / relational ('-īya')",        "gh -> īya in some envs; relational affix"),
 'khac':  ("a",    "kṛt",      "agent noun in upapada compounds (mum-augment)",   "kh adds mu(ṭ) (6.3.67); c = cit final acute"),
 'kvun':  ("aka",  "kṛt",      "agent noun; vu -> aka",                           "k = kit -> no guṇa; vu -> aka (7.1.1)"),
 'manin': ("man",  "uṇādi",    "Uṇādi noun ('-man')",                             "n indicatory; Uṇādi affix"),
 'rak':   ("ra",   "uṇādi",    "Uṇādi adjective/noun ('-ra')",                    "k = kit -> no guṇa/vṛddhi (1.1.5)"),
 'ra':    ("ra",   "uṇādi",    "Uṇādi adjective/noun ('-ra')",                    "Uṇādi affix"),
 'la':    ("la",   "taddhita", "possessive '-la' ('having')",                     "matvartha (possessive) affix"),
 # --- next tier: augments + single-vowel (ambiguous) Uṇādis ---
 'iṭ':    ("i",    "augment",  "iṭ-āgama: the 'i' inserted before an ārdhadhātuka affix (seṭ roots)", "augment (āgama), not a derivational affix; ṭ = ṭit -> prefixed (1.1.46)"),
 'aṭ':    ("a",    "augment",  "aṭ-āgama: the past-tense augment 'a-' (before the root)",            "augment (āgama); ṭ = ṭit -> prefixed to the root (1.1.46)"),
 'i':     ("i",    "uṇādi",    "Uṇādi noun ('-i') — AMBIGUOUS: also a bare stem-vowel in WIL",       "single-vowel Uṇādi; no it-marker to decode"),
 'ṇa':    ("a",    "kṛt",      "agent / action noun ('-a', vṛddhi)",                                "ṇ = ṇit -> vṛddhi of the base vowel (7.2.115)"),
 'ṭa':    ("a",    "kṛt",      "agent noun (samāsānta '-a')",                                       "ṭ = ṭit -> feminine with ṅīp (4.1.15)"),
 'ṅa':    ("a",    "kṛt",      "agent / action noun ('-a')",                                        "ṅ = ṅit -> no guṇa/vṛddhi of the root (1.1.5)"),
 'ṇvi':   ("",     "kṛt",      "zero-realised agent affix (vi -> ∅)",                               "ṇ = ṇit -> vṛddhi; v,i it -> affix elides"),
}

AFFIXES = {}  # populated by load_affix_base(): canonical map first, then SUPPLEMENT

# Roots / words frequently used as the *first* member that are prefixes,
# flagged by the abbreviation that follows them.
PREFIX_ABBR = {'neg.', 'priv.', 'privative', 'affir.', 'affirmative', 'possess.', 'poss.'}

TOKEN_RE = re.compile(r'\{#([^#]+)#\}')
AB_RE    = re.compile(r'<ab>([^<]*)</ab>')


# default sibling-repo location of the canonical affix table
DEFAULT_MAP = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..',
    'SanskritLexicography', 'RussianTranslation', 'research', 'affix_map.tsv'))


def load_affix_base(map_path=None):
    """Populate AFFIXES (IAST-keyed) from the canonical affix_map.tsv, then
    overlay the WIL SUPPLEMENT. Falls back to SUPPLEMENT-only if map absent."""
    AFFIXES.clear()
    path = map_path or os.environ.get('AFFIX_MAP') or DEFAULT_MAP
    loaded = 0
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.startswith('##') or not line.strip():
                    continue
                c = line.rstrip('\n').split('\t')
                if len(c) < 7:
                    continue
                surface, pratyaya_iast, kind, func = c[0], c[2], c[5], c[6]
                # map key may carry a homophone disambiguator; first pratyaya only
                key = pratyaya_iast.split('|')[0].strip()
                # (realized, kind, function, anubandha, source); anubandha filled generically
                AFFIXES[key] = (surface, kind, func, "", "Apte-SH(affix_map.tsv)")
                loaded += 1
    # WIL supplement, provenance-tagged so it never silently merges with Apte
    for k, v in SUPPLEMENT.items():
        AFFIXES[k] = v + ("WIL",)
    return loaded, path


def generic_it(slp1):
    """Decode the indicatory it-letters of an affix from its SLP1 form."""
    notes = [IT_LETTERS[ch] for ch in slp1 if ch in IT_LETTERS]
    return "; ".join(dict.fromkeys(notes))  # de-dup, keep order


# ---------------------------------------------------------------------------
# Teaching helpers MIRRORED (not re-derived) from the project's affix teaching
# tool:  SanskritLexicography/RussianTranslation/research/affix_pedagogy.py
# Kept here verbatim because that module's import chain (apte_parse ->
# sanskrit_util in WhitneyRoots) is too heavy to import into a csl-orig script.
#   * group_of(fn, kind)  -> the teaching GROUP an affix belongs to (what it MAKES)
#   * ANUBANDHA_STEPS     -> per-pratyaya it-marker stripping steps (P.1.3.2-1.3.9)
# ---------------------------------------------------------------------------
def group_of(fn, kind):
    f = (fn or '').lower()
    if 'agent' in f:            return 'Agent — the doer'
    if 'participle' in f:       return 'Participle'
    if 'gerundive' in f:        return 'Gerundive — “to-be-Xed”'
    if 'action' in f or 'result' in f: return 'Action / result noun'
    if 'abstract' in f:         return 'Abstract quality — “-ness”'
    if kind in ('strī', 'str"i', 'fem'): return 'Feminine stem'
    if 'possessive' in f or 'having' in f: return 'Possessive — “having X”'
    if 'comparative' in f or 'superlative' in f: return 'Comparison'
    if 'adverb' in f:           return 'Adverb'
    if 'temporal' in f:         return 'Temporal'
    if 'relational' in f or 'patronymic' in f: return 'Relational / patronymic'
    if 'diminutive' in f:       return 'Diminutive / self-sense'
    if 'augment' in f or kind == 'augment': return 'Augment (āgama)'
    # --- WIL-tail buckets (extension beyond affix_pedagogy.py's groups) ---
    if 'absolutive' in f or 'gerund' in f: return 'Absolutive — “having Xed”'
    if 'zero affix' in f or 'root used directly' in f or 'root-noun' in f or 'root as' in f:
        return 'Bare root / zero affix'
    if 'made of' in f or 'consisting' in f or 'full of' in f or 'material' in f:
        return 'Material / abundance'
    if 'samāsānta' in f or 'compound-final' in f: return 'Compound-final (samāsānta)'
    if kind == 'uṇādi':         return 'Uṇādi formation'
    if 'derivative' in f or 'noun' in f or 'adjective' in f:
        return 'Derivative noun / adjective'
    return 'Other'

# pratyaya_iast -> [stripping steps]  (mirrored from affix_pedagogy.py)
ANUBANDHA_STEPS = {
    'kta':   ['k = it (P.1.3.8)', '→ surface -ta'],
    'lyuṭ':  ['l = it', 'ṭ = it', 'yu → ana (P.7.1.1)', '→ -ana'],
    'ṇvul':  ['ṇ = it (→ vṛddhi)', 'l = it', 'vu → aka (P.7.1.1)', '→ -aka'],
    'tṛc':   ['c = it (P.1.3.3)', '→ -tṛ'],
    'ghañ':  ['gh = it (initial)', 'ñ = it (→ vṛddhi)', '→ -a'],
    'ac':    ['c = it', '→ -a'],
    'ktin':  ['k = it', 'n = it', '→ -ti'],
    'yat':   ['t = it', '→ -ya'],
    'aṇ':    ['ṇ = it (→ vṛddhi)', '→ -a'],
    'ṭhak':  ['ṭha → ika (P.7.3.50)', 'k = it (→ vṛddhi)', '→ -ika'],
    'ṣyañ':  ['ṣ = it (initial)', 'ñ = it (→ vṛddhi)', '→ -ya'],
    'ini':   ['final i = it', '→ -in'],
    'tva':   ['(no it-marker)', '→ -tva'],
    'tal':   ['l = it', '→ -tā (fem.)'],
    'matup': ['u, p = it', 'm → v after a/ā (P.8.2.9)', '→ -mat / -vat'],
    'tarap': ['p = it', '→ -tara'],
    'tamap': ['p = it', '→ -tama'],
    'tasil': ['l = it', '→ -tas'],
    'śas':   ['(adverbial)', '→ -śas'],
    'vini':  ['final i = it', '→ -vin'],
    'valac': ['c = it', '→ -vala'],
    'ṭyu':   ['ṭ = it', 'yu → ana → -tana', '→ -tana'],
    'kan':   ['k = it', 'n = it', '→ -ka'],
    'ka':    ['→ -ka'],
    'ṭāp':   ['ṭ = it', 'p = it', '→ -ā (fem.)'],
    'ṅīp':   ['ṅ = it', 'p = it', '→ -ī (fem.)'],
    'ṅīṣ':   ['ṅ = it', 'ṣ = it (→ vṛddhi)', '→ -ī (fem.)'],
}


def decode_affix(slp1):
    """Compose the explanation for one SLP1 affix token. Returns
    (note, source, group, steps) where:
      source = WHICH dictionary's affix data explained it (Apte-SH / WIL / generic)
      group  = teaching group (group_of) — what the affix MAKES
      steps  = ' ; '-joined anubandha-stripping steps, or '' if none curated."""
    iast = to_iast(slp1)
    entry = AFFIXES.get(iast)
    steps = ' ; '.join(ANUBANDHA_STEPS.get(iast, []))
    if entry:
        realized, kind, func, anu, source = entry
        note = "{} affix '{}' -> -{}; {}".format(kind, iast, realized or '∅', func)
        anu = anu or generic_it(slp1)
        if anu:
            note += " | anubandha: " + anu
        return note, source, group_of(func, kind), steps
    gen = generic_it(slp1)
    if gen:
        return ("uncurated affix '{}' | it-letters: {}".format(iast, gen),
                "generic-decoder", 'Other', steps)
    return "uncurated affix '{}'".format(iast), "generic-decoder", 'Other', steps


def clean_gloss(s):
    s = AB_RE.sub(r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip(' ,.;:')
    # drop a trailing connector that joins to the next member ("X, and", "X with")
    s = re.sub(r'[\s,]+(and|with|or|&c\.?)\s*$', '', s, flags=re.I).strip(' ,.;:')
    return s.strip()


AFF_WORD_RE = re.compile(r'\b(aff|affs|affix|affixes|added)\b', re.I)


def parse_block(raw):
    """Classify and parse one E. block (markup form). Returns a dict."""
    rec = {'type': None, 'root': None, 'root_meaning': None,
           'affix': None, 'affix_slp1': None, 'anubandha': None,
           'affix_source': None, 'group': None, 'anubandha_steps': None,
           'members': [], 'derivations': []}
    text = raw.strip()

    # 1. cross-reference
    if re.match(r'^\s*See\b', text, re.I) or re.match(r'^\s*[Ss]ee the last', text):
        rec['type'] = 'cross-ref'
        return rec

    toks = TOKEN_RE.findall(text)
    if not toks:
        rec['type'] = 'unparsed'
        return rec

    # mark whether an affix word is present
    has_aff = bool(AFF_WORD_RE.search(AB_RE.sub(r'\1', text)))

    # multiple alternative derivations: " or " that INTRODUCES a fresh clause,
    # i.e. it is immediately followed by a new {#token#} (not "to walk or run").
    parts = re.split(r'\s+\bor\b\s+(?=(?:<ab>[^<]*</ab>\s*)?\{#)', text)
    if len(parts) > 1 and all(TOKEN_RE.search(p) for p in parts):
        rec['type'] = 'multi-derivation'
        for p in parts:
            rec['derivations'].append(_parse_simple(p))
        # surface the first as the headline columns
        first = rec['derivations'][0]
        rec.update({k: first[k] for k in ('root', 'root_meaning', 'affix',
                                          'affix_slp1', 'anubandha', 'affix_source',
                                          'group', 'anubandha_steps')})
        return rec

    simple = _parse_simple(text)
    rec.update(simple)

    # decide type
    if not has_aff and simple['affix'] is None:
        # prefix+word or compound (two members, no affix)
        ab_after_first = _abbr_after_first_token(text)
        if ab_after_first in PREFIX_ABBR:
            rec['type'] = 'prefix+word'
        elif len(toks) >= 2:
            rec['type'] = 'compound'
        else:
            rec['type'] = 'single-stem'
    else:
        # unadi flagged in text?
        if re.search(r'\bUn?ā?adi\b|\bUnadi\b', text):
            rec['type'] = 'root+affix(unadi)'
        else:
            rec['type'] = 'root+affix'
    return rec


def _abbr_after_first_token(text):
    m = TOKEN_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    am = AB_RE.search(rest[:30])
    if am:
        return am.group(1).strip()
    return None


# bare abbreviation / connector that is NOT a real gloss
_NOT_A_GLOSS = re.compile(
    r'^(neg|priv|privative|affir|affirmative|poss|possess|and|with|or|for|added|'
    r'aff|affs|affix|affixes|&c|do|the root|repeated)\.?$', re.I)


def _members(text):
    """Return [(slp1, iast, gloss), ...] -- each {#token#} with the prose that
    follows it up to the next token, abbreviations expanded, connectors dropped."""
    out = []
    toks = list(TOKEN_RE.finditer(text))
    for i, m in enumerate(toks):
        end = toks[i + 1].start() if i + 1 < len(toks) else len(text)
        gloss = clean_gloss(text[m.end():end])
        gloss = re.sub(r'^(neg\.|priv\.|privative|affir\.|poss\.)\s*', '', gloss, flags=re.I).strip()
        if gloss and _NOT_A_GLOSS.match(gloss):
            gloss = ''
        out.append((m.group(1), to_iast(m.group(1)), gloss or None))
    return out


def _parse_simple(text):
    """Best-effort root + meaning + affix from a single derivation clause."""
    out = {'root': None, 'root_meaning': None, 'affix': None,
           'affix_slp1': None, 'anubandha': None, 'affix_source': None,
           'group': None, 'anubandha_steps': None, 'members': []}
    mem = _members(text)
    if not mem:
        return out
    out['members'] = [{'slp1': s, 'iast': i, 'gloss': g} for s, i, g in mem]

    # root / stem = first member
    out['root'], out['root_meaning'] = mem[0][1], mem[0][2]

    # affix present? -> it is the token immediately before the affix word.
    if AFF_WORD_RE.search(AB_RE.sub(r'\1', text)):
        # the affix is the last token that is NOT followed by its own real gloss
        # (Wilson puts the affix last: "{#root#} <gloss>, {#affix#} aff.")
        s, i, _g = mem[-1]
        out['affix_slp1'], out['affix'] = s, i
        (out['anubandha'], out['affix_source'],
         out['group'], out['anubandha_steps']) = decode_affix(s)
        # if the affix coincides with the only member, there is no separate root
        if len(mem) == 1:
            out['root'] = out['root_meaning'] = None
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'wil.txt')
    n_base, map_path = load_affix_base()
    if n_base:
        print("Loaded {} canonical affixes from {}".format(n_base, map_path))
    else:
        print("Canonical affix_map.tsv not found ({}); using SUPPLEMENT only".format(map_path))
    print("Affix table size: {} (incl. {} WIL supplement)".format(len(AFFIXES), len(SUPPLEMENT)))
    lines = open(path, encoding='utf-8').read().split('\n')

    records = []
    L_id = headword = None
    collecting = False
    buf = []
    for ln in lines:
        m = re.match(r'<L>(\d+).*?<k1>([^<]*)', ln)
        if m:
            L_id, headword = m.group(1), m.group(2)
        if '<ab>E.</ab>' in ln:
            collecting = True
            buf = []
            continue
        if collecting:
            if ln.startswith('<LEND>') or ln.startswith('<L>'):
                raw = ' '.join(s.strip() for s in buf).strip()
                rec = parse_block(raw)
                rec['L_id'] = L_id
                rec['headword_slp1'] = headword
                rec['headword'] = to_iast(headword) if headword else None
                rec['raw'] = raw
                records.append(rec)
                collecting = False
                buf = []
                if ln.startswith('<L>'):
                    m2 = re.match(r'<L>(\d+).*?<k1>([^<]*)', ln)
                    if m2:
                        L_id, headword = m2.group(1), m2.group(2)
            else:
                buf.append(ln)

    # ---- write TSV ----
    base = os.path.dirname(path)
    tsv = os.path.join(base, 'wil_etymology.tsv')
    cols = ['L_id', 'headword', 'headword_slp1', 'type', 'root', 'root_meaning',
            'affix', 'affix_slp1', 'group', 'anubandha', 'anubandha_steps',
            'affix_source', 'raw']
    with open(tsv, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in records:
            row = []
            for c in cols:
                v = r.get(c)
                v = '' if v is None else str(v).replace('\t', ' ').replace('\n', ' ')
                row.append(v)
            f.write('\t'.join(row) + '\n')

    # ---- write JSONL ----
    jl = os.path.join(base, 'wil_etymology.jsonl')
    with open(jl, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # ---- summary ----
    from collections import Counter
    types = Counter(r['type'] for r in records)
    print("Parsed {} E. blocks".format(len(records)))
    print("Wrote {}".format(tsv))
    print("Wrote {}".format(jl))
    print("\nType breakdown:")
    for t, n in types.most_common():
        print("  {:24s} {}".format(t, n))
    withaff = sum(1 for r in records if r['affix_slp1'])
    srcs = Counter(r['affix_source'] for r in records if r['affix_source'])
    print("\nAffix provenance (of {} entries with an affix):".format(withaff))
    for s, n in srcs.most_common():
        print("  {:26s} {}".format(s, n))


if __name__ == '__main__':
    main()
