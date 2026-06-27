#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_root_normalization.py  --  build root_norm.tsv, a (variant -> canonical)
SLP1 map that folds surface-form root variants onto their dhātupāṭha citation
form (the error class the DeepSeek audit found: `sada`->`sad`, `gama`->`gam`,
`SvasA`->`Svas`, `kF`->`kf`).

CANON = authoritative citation-form roots only (mw_roots.tsv k1_slp1 + the cleaned
vidyut dhātupāṭha). The *local-bootstrap* variants are deliberately NOT in CANON,
so they reduce onto it. A variant maps ONLY when it is not itself canonical and
exactly one deterministic reduction lands in CANON — so a real -a root that the
registries already know (it is in CANON) is never touched, and ambiguous cases
are left alone. Conservative by construction; the map is auditable + reversible.

  python build_root_normalization.py        # -> root_norm.tsv
"""
import os, sys, re, csv

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..'))
GH = os.path.normpath(os.path.join(V02, '..', '..'))
from indic_transliteration import sanscript
to_iast = lambda s: sanscript.transliterate(s, sanscript.SLP1, sanscript.IAST)
SLP1 = r"[a-zA-ZAIUEOfFxXMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh]+"


def canon_set():
    # CANON must be CITATION-form roots only. mw_roots.tsv k1_slp1 is MW's curated
    # root head-word (gam, sad, bhuj — no thematic -a). The vidyut dhātupāṭha is
    # deliberately NOT used here: its surface forms keep the thematic vowel
    # (dyuta~\ -> dyuta), i.e. the very stem variant we are folding away.
    canon = set()
    p = os.path.join(V02, 'mw', 'mw_roots.tsv')
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            k = (r.get('k1_slp1') or '').strip()
            if k:
                canon.add(k)
    return canon


def reductions(v):
    """deterministic surface-form reductions of a variant."""
    out = set()
    if v.endswith('a'):
        out.add(v[:-1])                       # sada->sad, gama->gam
    out.add(v.replace('F', 'f').replace('X', 'x'))   # ṝ->ṛ, ḹ->ḷ
    if v.endswith('a'):
        out.add(v[:-1].replace('F', 'f').replace('X', 'x'))
    out.discard(v)
    return out


def extracted_roots():
    roots = set()
    for d in ('skd', 'vcp', 'ap90', 'ap', 'shs', 'krm', 'mw'):
        p = os.path.join(V02, d, d + '_etymology.tsv')
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            if r.get('root_slp1'):
                roots.add(r['root_slp1'])
    for d in ('pwg', 'pw'):
        p = os.path.join(V02, d, d + '_etymology.tsv')
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            if r.get('is_root') == 'True' and r.get('source_slp1'):
                roots.add(r['source_slp1'])
    return roots


def main():
    CANON = canon_set()
    rows = []
    for v in sorted(extracted_roots()):
        if v in CANON:
            continue
        hits = [c for c in reductions(v) if c in CANON]
        if len(hits) == 1 and hits[0] != v:
            rows.append((v, to_iast(v), hits[0], to_iast(hits[0])))
    out = os.path.join(HERE, 'root_norm.tsv')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['variant_slp1', 'variant_iast', 'canonical_slp1', 'canonical_iast'])
        w.writerows(rows)
    print("CANON {} roots; wrote {} (variant -> canonical) mappings -> {}".format(
        len(CANON), len(rows), out))


if __name__ == '__main__':
    main()
