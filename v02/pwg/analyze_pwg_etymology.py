#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_pwg_etymology.py  --  derivation extractor for the German Petersburg
dictionaries PWG (großes PW) and PW (kürzere Fassung).

These mark derivation in German prose, not WIL's `<ab>E.</ab>` nor SKD/VCP's
kāraka+pratyaya. The recurring shape is a source word in SLP1 introduced by a
German derivation cue:

    — Von {#aMSa#} {%Theil%}              (from aṃśa "part")
    Wurzel {#pA#}                         (root pā)
    von <hom>1.</hom> {#aS#}              (from root aś)

Only sources in `{#..#}` (SLP1) are taken — proper-name "von <is>Viṣṇu</is>"
(= epithet "of", not "from") is in <is>..</is> and is excluded.

    python analyze_pwg_etymology.py [path/to/pwg.txt]    # default ./pwg.txt
    python analyze_pwg_etymology.py ../pw/pw.txt          # PW too

Outputs next to the input:  <dict>_etymology.tsv  +  <dict>_etymology.jsonl
"""
import os, sys, re, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

_WILDIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wil'))
sys.path.insert(0, _WILDIR)
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                 '..', 'etymology_stats')))
import analyze_wil_etymology as wil          # noqa: E402
import root_norm                             # noqa: E402
to_iast = wil.to_iast

ROOT_SET = set()


def load_root_set():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                     'etymology_stats', 'dhatu_roots.txt')
    p = os.environ.get('DHATU_ROOTS', os.path.normpath(p))
    if os.path.exists(p):
        for ln in open(p, encoding='utf-8'):
            ln = ln.strip()
            if ln and not ln.startswith('#'):
                ROOT_SET.add(ln)
    return len(ROOT_SET)


# derivation cue + source word in {#..#}, with optional <hom> and German gloss.
DERIV_RE = re.compile(
    r"(?P<cue>Von|von|Wurzel|Stamm)\s+(?:<hom>[^<]*</hom>\s*)?"
    r"\{#(?P<src>[^#]+)#\}\s*(?:\{%(?P<gloss>[^%]+)%\})?")
UPASARGA = {'pra', 'parA', 'apa', 'sam', 'anu', 'ava', 'nis', 'nir', 'dus', 'dur',
            'vi', 'A', 'AN', 'ni', 'aDi', 'api', 'ati', 'su', 'ud', 'ut', 'aBi',
            'prati', 'pari', 'upa', 'a', 'an'}


def classify(src):
    if src in ROOT_SET:
        return 'root'
    if to_iast(src) in wil.AFFIXES:
        return 'affix'
    if src in UPASARGA:
        return 'prefix'
    return 'stem/word'


def parse_entry(L_id, headword, body):
    text = ' '.join(body)
    out = []
    seen = set()
    for m in DERIV_RE.finditer(text):
        src = m.group('src').strip()
        # source words are single morphemes; skip obvious compounds / spaces
        if ' ' in src or len(src) > 18:
            continue
        cue = m.group('cue')
        marker = 'Wurzel/Stamm' if cue in ('Wurzel', 'Stamm') else ('Von' if cue == 'Von' else 'von')
        cls = classify(src)
        # "von" lowercase mid-sentence is weak unless the source is a known root
        if marker == 'von' and cls != 'root':
            continue
        if cls == 'root':
            src = root_norm.canon(src)      # fold surface variant -> citation form
        key = (src, marker)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            'L_id': L_id,
            'headword': to_iast(headword) if headword else None,
            'headword_slp1': headword,
            'source': to_iast(src),
            'source_slp1': src,
            'source_class': cls,
            'is_root': cls == 'root',
            'source_gloss_de': (m.group('gloss') or '').strip() or None,
            'deriv_marker': marker,
            'context': re.sub(r'<[^>]+>|\{[#%][^#%]*[#%]\}', lambda x: x.group(0)
                              if x.group(0).startswith('{#') else '', text)[max(0, m.start() - 30):m.start() + 60].strip()[:120],
        })
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'pwg.txt')
    dictcode = os.path.splitext(os.path.basename(path))[0]
    wil.load_affix_base()
    nr = load_root_set()
    print("Affix table + {} dhātu roots loaded".format(nr))

    records = []
    L_id = headword = None
    buf, collecting = [], False
    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        h = re.match(r'<L>(\d+).*?<k1>([^<]*)', ln)
        if h:
            L_id, headword = h.group(1), h.group(2)
            buf, collecting = [], True
            continue
        if collecting:
            if ln.startswith('<LEND>'):
                records.extend(parse_entry(L_id, headword, buf))
                collecting = False
            else:
                buf.append(ln)

    base = os.path.dirname(os.path.abspath(path))
    cols = ['L_id', 'headword', 'headword_slp1', 'source', 'source_slp1',
            'source_class', 'is_root', 'source_gloss_de', 'deriv_marker', 'context']
    with open(os.path.join(base, dictcode + '_etymology.tsv'), 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in records:
            f.write('\t'.join('' if r.get(c) is None else str(r[c]).replace('\t', ' ')
                              for c in cols) + '\n')
    with open(os.path.join(base, dictcode + '_etymology.jsonl'), 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    from collections import Counter
    print("Mined {} derivations from {}".format(len(records), os.path.basename(path)))
    print("\nDerivation marker:")
    for k, n in Counter(r['deriv_marker'] for r in records).most_common():
        print("  {:14s} {}".format(k, n))
    print("\nSource class:")
    for k, n in Counter(r['source_class'] for r in records).most_common():
        print("  {:12s} {}".format(k, n))
    print("\nTop source roots:")
    for a, n in Counter(r['source'] for r in records if r['is_root']).most_common(10):
        print("  {:10s} {}".format(a, n))


if __name__ == '__main__':
    main()
