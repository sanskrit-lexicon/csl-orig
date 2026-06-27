#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_dhatu_roots.py  --  build the vendored SLP1 dhātu list used by the
dhātupāṭha JOIN in analyze_sktdict_etymology.py.

Sources (read at build time; the result is committed so the extractor needs no
cross-repo runtime dependency):
  1. vidyut dhātupāṭha  (WhitneyRoots/scratch/vidyut_data/.../dhatupatha.tsv) —
     ~2260 roots; anubandhas/accents stripped to a matchable surface form.
  2. csl-atlas m4 indigenous root-headwords (skd/vcp/krm/shs/yat) — already
     clean SLP1 root head-words.
  3. the extractor's OWN high-confidence local roots (root_source=local) from the
     existing *_etymology.tsv — guarantees the join set is in the same surface
     form the extractor produces (recovers e.g. 'jan', which vidyut stores 'janI').

  python build_dhatu_roots.py        # -> dhatu_roots.txt
"""
import os, re, csv, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
GH = os.path.normpath(os.path.join(HERE, '..', '..', '..'))   # GitHub/
V02 = os.path.normpath(os.path.join(HERE, '..'))
SLP1 = r"[a-zA-ZAIUEOfFxXMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh]+"


def from_vidyut(roots):
    p = os.path.join(GH, 'WhitneyRoots', 'scratch', 'vidyut_data', 'prakriya', 'dhatupatha.tsv')
    if not os.path.exists(p):
        return
    for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
        d = re.sub(r'[~\\^\d].*$', '', r['dhatu']).strip('\\^~')
        d = re.sub(r'^[wqd]u', '', d)                     # drop wu/qu/du it-prefix
        if 1 <= len(d) <= 8 and re.fullmatch(SLP1, d):
            roots.add(d)


def from_m4(roots):
    p = os.path.join(GH, 'csl-atlas', 'data', 'lexico', 'indigenous_roots.csv')
    if not os.path.exists(p):
        return
    for r in csv.DictReader(open(p, encoding='utf-8')):
        if r.get('dict') in ('skd', 'vcp', 'krm', 'shs', 'yat'):
            k = r['k1'].strip()
            if 1 <= len(k) <= 10 and re.fullmatch(r'[a-zA-Z]+', k):
                roots.add(k)


def from_mw_roots(roots):
    """Canonical MW verbal-root inventory (SHARED_CODE.md §11). Read the TSV;
    never re-scan mw.txt for roots."""
    p = os.path.join(V02, 'mw', 'mw_roots.tsv')
    if not os.path.exists(p):
        return
    for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
        k = (r.get('k1_slp1') or '').strip()
        if 1 <= len(k) <= 10 and re.fullmatch(SLP1, k):
            roots.add(k)


def from_local_tsv(roots):
    for sub in ('skd', 'vcp', 'ap90', 'ap', 'krm'):
        p = os.path.join(V02, sub, sub + '_etymology.tsv')
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            if r.get('root_source') == 'local' and r.get('root_slp1'):
                roots.add(r['root_slp1'])


def main():
    roots = set()
    from_vidyut(roots); n1 = len(roots)
    from_m4(roots);     n2 = len(roots)
    from_mw_roots(roots); n3 = len(roots)
    from_local_tsv(roots)
    roots = {r for r in roots if 1 <= len(r) <= 10}
    out = os.path.join(HERE, 'dhatu_roots.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write("# canonical SLP1 dhātu list for the dhātupāṭha join.\n")
        f.write("# sources: vidyut dhatupatha + csl-atlas m4 indigenous roots + canonical mw_roots.tsv + local extractor roots.\n")
        f.write("# regenerate: python build_dhatu_roots.py\n")
        for r in sorted(roots):
            f.write(r + '\n')
    print("vidyut={} +m4={} +mw_roots={} +local={} -> {} roots".format(
        n1, n2 - n1, n3 - n2, len(roots) - n3, len(roots)))
    print("wrote", out)


if __name__ == '__main__':
    main()
