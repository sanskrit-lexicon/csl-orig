#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_root_oracle.py  --  build a (derived-word -> root) oracle for resolving
empty-root entries across the Cologne dictionaries.

Two clean sources, every root validated against the canonical dhātu list
(dhatu_roots.txt) so only real roots enter the oracle:

  1. CROSS-DICT captured roots — every (head-word -> root) already extracted with
     high confidence across SKD/VCP/Apte/AP/KRM/MW/PWG/PW.
  2. KRM PARADIGM — KRM (Kṛdanta-rūpa-mālā) is organised by root: each entry's
     head-word IS the dhātu and its body lists that root's derivatives. We mine
     the <div n="NI">/<div n="P"> derivative sections and map each derived form
     to the entry's root (k1), which is always a real dhātu.

A head-word keeps a root only if it is UNAMBIGUOUS (one root, or a ≥2/3 majority).

    python build_root_oracle.py        # -> root_oracle.tsv

Consumed by analyze_sktdict_etymology.py (the `oracle-join` root tier).
"""
import os, sys, re, csv, collections

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..'))

try:
    from indic_transliteration import sanscript
    to_iast = lambda s: sanscript.transliterate(s, sanscript.SLP1, sanscript.IAST)
except Exception:
    to_iast = lambda s: s

ROOTS = set()
for ln in open(os.path.join(HERE, 'dhatu_roots.txt'), encoding='utf-8'):
    ln = ln.strip()
    if ln and not ln.startswith('#'):
        ROOTS.add(ln)

# KRM body tokens that are grammatical prose / sūtra refs, never a derivative
KRM_STOP = {
    'iti', 'DAtu', 'DAto', 'DAtoH', 'rUpa', 'rUpam', 'rUpARi', 'rUpe', 'pAWe',
    'ekam', 'ekameva', 'ityAdi', 'ityAdirUpARi', 'nizWAyAM', 'vacanAt', 'tu',
    'ca', 'vA', 'eva', 'devaH', 'Slo', 'iti', 'aDikAni', 'avaSizwAni', 'jYeyAni',
    'Bavati', 'na', 'viByAzA', 'viSezaRe', 'pUjana', 'gati', 'gatyarTaka',
}


def add_crossdict(oracle):
    specs = [('skd', 'root_slp1'), ('vcp', 'root_slp1'), ('ap90', 'root_slp1'),
             ('ap', 'root_slp1'), ('krm', 'root_slp1'), ('mw', 'root_slp1'),
             ('pwg', 'source_slp1'), ('pw', 'source_slp1')]
    for sub, col in specs:
        p = os.path.join(V02, sub, sub + '_etymology.tsv')
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            hw, rt = r.get('headword_slp1'), r.get(col)
            if hw and rt in ROOTS:
                oracle[hw][rt] += 1
            src.setdefault(hw, set()).add(sub if sub != 'ap90' else 'apte')


def add_krm_body(oracle):
    p = os.path.join(V02, 'krm', 'krm.txt')
    if not os.path.exists(p):
        return
    k1 = None
    buf, coll = [], False
    div_re = re.compile(r'<div n="(?:NI|P)">')
    for ln in open(p, encoding='utf-8'):
        h = re.match(r'<L>\d+.*?<k1>([^<]*)', ln)
        if h:
            k1, buf, coll = h.group(1), [], True
            continue
        if coll and ln.startswith('<LEND>'):
            body = ' '.join(buf)
            if k1 in ROOTS and div_re.search(body):
                # only the derivative <div> sections
                for sec in re.split(r'<div n="[^"]*">', body)[1:]:
                    for m in re.finditer(r'<s>([^<]+)</s>', sec):
                        for tok in re.split(r'[\s,;]+', m.group(1)):
                            tok = tok.strip("‘’\"().-—:0123456789")
                            if re.fullmatch(r"[a-zA-Z]{4,}", tok) and tok not in KRM_STOP:
                                oracle[tok][k1] += 1
                                src.setdefault(tok, set()).add('krm-body')
            coll = False
        elif coll:
            buf.append(ln.strip())


def main():
    oracle = collections.defaultdict(collections.Counter)
    global src
    src = {}
    add_crossdict(oracle)
    n_cross = len(oracle)
    add_krm_body(oracle)
    print("cross-dict headwords {} ; +KRM body -> {}".format(n_cross, len(oracle)))

    rows = []
    for hw, c in oracle.items():
        top, n = c.most_common(1)[0]
        if len(c) == 1 or n / sum(c.values()) >= 0.66:
            rows.append((hw, to_iast(hw), top, to_iast(top), n,
                         ','.join(sorted(src.get(hw, [])))))
    rows.sort()
    out = os.path.join(HERE, 'root_oracle.tsv')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['form_slp1', 'form_iast', 'root_slp1', 'root_iast', 'support', 'sources'])
        w.writerows(rows)
    print("Wrote {} unambiguous (form -> root) entries -> {}".format(len(rows), out))
    krm_only = sum(1 for r in rows if r[5] == 'krm-body')
    print("  KRM-body-only: {} ; multi-source: {}".format(
        krm_only, sum(1 for r in rows if ',' in r[5])))


if __name__ == '__main__':
    main()
