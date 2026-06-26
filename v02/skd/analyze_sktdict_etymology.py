#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_sktdict_etymology.py  --  Pāṇinian derivation extractor for the
Sanskrit->Sanskrit dictionaries SKD (Śabdakalpadruma) and VCP (Vācaspatyam).

Unlike WIL/Apte, SKD & VCP carry NO `<ab>E.</ab>` block: their derivations are
stated IN Sanskrit inside the entry body, in the classical shape

    [upasarga +] root + KĀRAKA  PRATYAYA
        e.g.  vi + kzip + BAve GaY        (vi-kṣip, bhāve, ghañ -> vikṣepa)
    <root>DAtoH  KĀRAKA  <pratyaya>pratyaya
        e.g.  jiDAtoH karmmaRi yatpratyayaH   (√ji, karmaṇi, yat)

This tool mines those, producing the SAME affix decoding as the WIL analyser
(reused by import) PLUS the kāraka (derivation sense) that SKD/VCP uniquely give.

    python analyze_sktdict_etymology.py [path/to/skd.txt]     # default ./skd.txt
    python analyze_sktdict_etymology.py ../vcp/vcp.txt         # VCP too

Outputs next to the input:  <dict>_etymology.tsv  +  <dict>_etymology.jsonl
"""
import sys, os, re, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# --- reuse the WIL affix machinery (single owner, no re-derivation) ----------
_WILDIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '..', 'wil'))
sys.path.insert(0, _WILDIR)
import analyze_wil_etymology as wil          # noqa: E402
to_iast = wil.to_iast
decode_affix = wil.decode_affix              # (note, source, group, steps)

# ---------------------------------------------------------------------------
# Kāraka (derivation sense) — the grammar layer SKD/VCP add over WIL/Apte.
# SKD orthography often doubles consonants (karmmaRi, karttari) -> normalise.
# ---------------------------------------------------------------------------
KARAKA_RE = r'(BAve|karaRe|karmma?Ri|kartt?ari|aDikaraRe|apAdAne|sampradAne)'
KARAKA_SENSE = {
    'BAve':      'action / abstract (bhāve)',
    'karaRe':    'instrument (karaṇe)',
    'karmaRi':   'object (karmaṇi)',
    'kartari':   'agent (kartari)',
    'aDikaraRe': 'location (adhikaraṇe)',
    'apAdAne':   'source (apādāne)',
    'sampradAne':'recipient (sampradāne)',
}


def norm_karaka(k):
    return k.replace('mm', 'm').replace('tt', 't')


# Recognised pratyaya surface forms (SLP1). Longest-first so 'kta' wins over 'ka'.
PRATYAYA = sorted([
    'anIyar', 'ktavatu', 'ktic', 'ktin', 'ktvA', 'SAnac', 'Satf', 'GinuR',
    'manin', 'asun', 'RamuL', 'zwran', 'zyaY', 'matup', 'tavya', 'Rvul',
    'lyuw', 'kyap', 'Ryat', 'GaYar', 'yuc', 'vun', 'tfc', 'tfn', 'Wak',
    'wak', 'kan', 'Ina', 'GaY', 'kta', 'kvip', 'kvin', 'lyu', 'yat', 'aR',
    'aN', 'ap', 'ac', 'Sa', 'qa', 'ka', 'in', 'ini', 'Ru', 'Ral', 'DA',
    'tal', 'tasi', 'u',
], key=len, reverse=True)
PRATYAYA_ALT = '|'.join(PRATYAYA)

# KĀRAKA  PRATYAYA  (pratyaya may carry case -H or be glued before 'pratyaya')
HIT_RE = re.compile(
    r"(?P<kar>" + KARAKA_RE + r")\s+(?P<aff>" + PRATYAYA_ALT + r")(?:H)?(?=pratyay|[^A-Za-zĀ-ɏ]|$)")

# SKD style: a "+ morpheme" chain before the kāraka; LAST morph may lack '+'
# ("vi + kzip + " and also "aNka + Ric " -> aṅka denominal + ṇic before kāraka)
CHAIN_RE = re.compile(r"((?:[A-Za-z']+\s*\+\s*)+(?:[A-Za-z']+\s*)?)$")
# VCP style: "<root>--" or "<root>- " (double/single hyphen) before the kāraka
HYPHEN_RE = re.compile(r"([A-Za-z']+)-{1,2}\s*$")
# "<root>DAtoH" just before the kāraka
DHATU_RE = re.compile(r"([A-Za-z']+)DAt(?:oH|u|o)\b")
TOKEN_HEAD = re.compile(r"([A-Za-z']+)\s*$")

# upasargas / common prefixes (SLP1) -> go to `prefixes`, never the root
UPASARGA = {
    'pra', 'parA', 'apa', 'sam', 'anu', 'ava', 'nis', 'nir', 'dus', 'dur',
    'vi', 'A', 'AN', 'ni', 'aDi', 'api', 'ati', 'su', 'ud', 'ut', 'aBi',
    'prati', 'pari', 'upa', 'na', 'agni', 'agra', 'agre', 'sa', 'nI', 'dur',
}
# secondary affixes that may sit between root and kāraka -> not the root
SECONDARY_AFF = {'Ric', 'Rici', 'Ri', 'san', 'sani', 'yaN', 'yaNi', 'kyac',
                 'RijantaH', 'yaNluk'}
# referential / quote words that are never a root
STOPWORD = {
    'iti', 'ityasmAt', 'ityasya', 'asmAt', 'asya', 'tasya', 'paWitvA',
    'yasya', 'saH', 'tataH', 'tena', 'anena', 'atra', 'ca', 'tu', 'vA',
    'idam', 'ayam', 'ezaH', 'sma', 'kftvA', 'BUtvA', 'iva',
}


def _is_rootlike(tok):
    return tok and tok not in UPASARGA and tok not in SECONDARY_AFF \
        and tok not in STOPWORD and tok not in PRATYAYA


# --- conservative gaṇa-gloss backreference (fills empty roots, tagged low-conf) -
# Reuses the dhātupāṭha class markers from csl-atlas m4_indigenous.py (_GANA).
GANA_RE = re.compile(r"(?:Bv|ad|juhoty|div|sv|tud|ruD|tan|kry|cur)AdiH|DAt(?:u|oH)")
# dhātu citation: a clause boundary, then ROOT, then an artha in the locative (-e)
CITE_RE = re.compile(r"[(¦.]\s*([a-zA-Z']{2,})\s+[a-zA-Z']+e\b")
_CITE_STOP = {'na', 'su', 'vi', 'sam', 'pra', 'agni', 'agra', 'iti', 'tri',
              'anu', 'ava', 'upa', 'tasya', 'yasya', 'tatra', 'atra', 'asya'}


def entry_dhatu(text):
    """Return the entry's single unambiguous dhātupāṭha root, or None.
    Conservative: requires a gaṇa/dhātu marker AND exactly one distinct cited
    root — so multi-root entries stay empty rather than get a wrong fill."""
    if not GANA_RE.search(text):
        return None
    cands = []
    for m in CITE_RE.finditer(text):
        r = m.group(1)
        if r not in _CITE_STOP and r not in cands:
            cands.append(r)
    return cands[0] if len(cands) == 1 else None


def find_root(prefix_text):
    """Given the text immediately BEFORE the kāraka, recover (root, prefixes).
    Prefers an explicit '+ chain'; filters upasargas to prefixes and skips
    secondary affixes / stopwords; returns (None, []) rather than a wrong root."""
    chain = CHAIN_RE.search(prefix_text)
    if chain:
        morphs = [m.strip() for m in re.split(r'\+', chain.group(1)) if m.strip()]
        prefixes = [m for m in morphs if m in UPASARGA]
        # root = last content morpheme that is not an upasarga/affix/stopword
        for tok in reversed(morphs):
            if _is_rootlike(tok):
                return tok, [p for p in prefixes if p != tok]
        # chain was all prefixes/affixes -> keep prefixes, no clear root
        if morphs:
            return None, prefixes
    hy = HYPHEN_RE.search(prefix_text)          # VCP "root--" / "root-"
    if hy and _is_rootlike(hy.group(1)):
        return hy.group(1), []
    dh = None
    for dh in DHATU_RE.finditer(prefix_text):
        pass                      # nearest (last) DAtoH before the kāraka
    if dh and _is_rootlike(dh.group(1)):
        return dh.group(1), []
    tok = TOKEN_HEAD.search(prefix_text)
    if tok and _is_rootlike(tok.group(1)):
        return tok.group(1), []
    return None, []


def parse_entry(L_id, headword, body):
    """Return a list of derivation records mined from one entry body."""
    out = []
    text = re.sub(r'\s+', ' ', body)
    e_dhatu = entry_dhatu(text)          # computed once per entry
    seen = set()
    for m in HIT_RE.finditer(text):
        kar = norm_karaka(m.group('kar'))
        aff_slp1 = m.group('aff')
        before = text[max(0, m.start() - 60):m.start()]
        root_slp1, pref_slp1 = find_root(before)
        root_source = 'local' if root_slp1 else None
        if not root_slp1 and e_dhatu:    # conservative gaṇa-gloss backreference
            root_slp1, root_source = e_dhatu, 'gana-backref'
        key = (root_slp1, kar, aff_slp1, root_source)
        if key in seen:
            continue
        seen.add(key)
        note, source, group, steps = decode_affix(aff_slp1)
        out.append({
            'L_id': L_id,
            'headword': to_iast(headword) if headword else None,
            'headword_slp1': headword,
            'root': to_iast(root_slp1) if root_slp1 else None,
            'root_slp1': root_slp1,
            'root_source': root_source,
            'prefixes': ' '.join(to_iast(p) for p in pref_slp1) or None,
            'karaka': norm_karaka(m.group('kar')),
            'karaka_sense': KARAKA_SENSE.get(kar, kar),
            'affix': to_iast(aff_slp1),
            'affix_slp1': aff_slp1,
            'group': group,
            'anubandha': note,
            'anubandha_steps': steps or None,
            'affix_source': source,
            'context': text[max(0, m.start() - 40):m.end() + 5].strip(),
        })
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'skd.txt')
    dictcode = os.path.splitext(os.path.basename(path))[0]
    n_base, map_path = wil.load_affix_base()
    print("Affix base: {} canonical + {} WIL supplement".format(n_base, len(wil.SUPPLEMENT)))

    records = []
    L_id = headword = None
    buf = []
    collecting = False
    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        h = re.match(r'<L>(\d+).*?<k1>([^<]*)', ln)
        if h:
            L_id, headword = h.group(1), h.group(2)
            buf = []
            collecting = True
            continue
        if collecting:
            if ln.startswith('<LEND>'):
                records.extend(parse_entry(L_id, headword, ' '.join(buf)))
                collecting = False
                buf = []
            else:
                buf.append(ln)

    base = os.path.dirname(os.path.abspath(path))
    cols = ['L_id', 'headword', 'headword_slp1', 'root', 'root_slp1', 'root_source',
            'prefixes', 'karaka', 'karaka_sense', 'affix', 'affix_slp1', 'group',
            'anubandha', 'anubandha_steps', 'affix_source', 'context']
    tsv = os.path.join(base, dictcode + '_etymology.tsv')
    with open(tsv, 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in records:
            f.write('\t'.join('' if r.get(c) is None else str(r[c]).replace('\t', ' ')
                              for c in cols) + '\n')
    jl = os.path.join(base, dictcode + '_etymology.jsonl')
    with open(jl, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    from collections import Counter
    n_entries = len(set(r['L_id'] for r in records))
    print("Mined {} derivations from {} distinct entries in {}".format(
        len(records), n_entries, os.path.basename(path)))
    print("Wrote {}".format(tsv))
    print("Wrote {}".format(jl))
    print("\nKāraka breakdown:")
    for k, n in Counter(r['karaka'] for r in records).most_common():
        print("  {:12s} {}".format(k, n))
    print("\nTop affixes:")
    for a, n in Counter(r['affix'] for r in records).most_common(12):
        print("  {:10s} {}".format(a, n))
    print("\nAffix provenance:")
    for s, n in Counter(r['affix_source'] for r in records).most_common():
        print("  {:26s} {}".format(s, n))
    rs = Counter(r['root_source'] for r in records)
    have = rs['local'] + rs['gana-backref']
    print("\nRoot capture: {}/{} ({:.0f}%) -- local {}, gaṇa-backref {}, empty {}".format(
        have, len(records), 100 * have / max(1, len(records)),
        rs['local'], rs['gana-backref'], rs[None]))


if __name__ == '__main__':
    main()
