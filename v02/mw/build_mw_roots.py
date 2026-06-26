#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_mw_roots.py — the CANONICAL Monier-Williams verbal-root inventory.

Emits one row per MW verbal-root record: every <L>...<LEND> record in mw.txt
whose <info> carries verb in {"genuineroot", "root"}. This is the single source
of truth for "MW's verbal roots" — consumers must read this TSV rather than
re-scanning mw.txt (which is what produced three divergent, differently-defined
counts across WhitneyRoots / MWS / SanskritLexicography).

Two facets are published explicitly so a consumer picks its population on purpose
instead of silently filtering:
  - verb_type == "genuineroot"  -> MW's strict root tag (the historical "750")
  - verb_type in {genuineroot, root} -> all verbal-root records (2113)

This is the ROOT INVENTORY. It is distinct from the sibling mw_etymology.tsv,
which is the headword -> root DERIVATION table (which root a word descends from),
a different artifact.

Parser lifted from MWS/root_crosswalk/root_crosswalk.py (the de-facto canonical
MW-root reader) so no fourth parser is introduced.

Output (this dir):
  mw_roots.tsv   mw_L, e, k1_slp1, root_iast, verb_type, classes, whitney_anchor, westergaard

Run: python build_mw_roots.py   (from csl-orig/v02/mw/)
"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
MW   = os.path.join(HERE, 'mw.txt')
OUT  = os.path.join(HERE, 'mw_roots.tsv')

# SLP1 -> IAST (single-char map; lifted from root_crosswalk.py). Build artifact,
# so kept dependency-free to regenerate server-side with the dict.
_S2I = {'A':'ā','I':'ī','U':'ū','f':'ṛ','F':'ṝ','x':'ḷ','X':'ḹ','E':'ai','O':'au',
        'M':'ṃ','H':'ḥ','K':'kh','G':'gh','N':'ṅ','C':'ch','J':'jh','Y':'ñ',
        'w':'ṭ','W':'ṭh','q':'ḍ','Q':'ḍh','R':'ṇ','T':'th','D':'dh','P':'ph',
        'B':'bh','S':'ś','z':'ṣ','L':'ḻ'}
def s2i(s): return ''.join(_S2I.get(c, c) for c in s)

L_RE  = re.compile(r'^<L>([^<]*)')
K1_RE = re.compile(r'<k1>([^<]*)')
E_RE  = re.compile(r'<e>([^<]*)')
VB_RE = re.compile(r'<info verb="([^"]*)"(?:\s+cp="([^"]*)")?')
WR_RE = re.compile(r'whitneyroots="([^"]*)"')
WG_RE = re.compile(r'westergaard="([^"]*)"')

rows = []
cur_L = cur_k1 = cur_e = None
rec = []

def flush():
    if cur_L is None:
        return
    t = ''.join(rec)
    vb = VB_RE.search(t)
    if not (vb and vb.group(1) in ('genuineroot', 'root')):
        return
    verb_type = vb.group(1)
    classes   = vb.group(2) or ''
    wr = WR_RE.search(t)
    whitney = wr.group(1) if wr else ''
    westergaard = '1' if WG_RE.search(t) else ''
    root_iast = s2i(cur_k1) if cur_k1 else ''
    rows.append((cur_L, cur_e or '', cur_k1 or '', root_iast, verb_type,
                 classes, whitney, westergaard))

with open(MW, encoding='utf-8') as f:
    for line in f:
        if line.startswith('<L>'):
            flush()
            cur_L = L_RE.match(line).group(1).strip()
            k1 = K1_RE.search(line); cur_k1 = (k1.group(1).strip() if k1 else '')
            e  = E_RE.search(line);  cur_e  = (e.group(1).strip() if e else '')
            rec = []
        elif line.startswith('<LEND>'):
            flush(); cur_L = cur_k1 = cur_e = None; rec = []
        elif cur_L is not None:
            rec.append(line)
flush()

# stable order by numeric L
def lkey(r):
    try: return (0, float(r[0]))
    except ValueError: return (1, 0.0)
rows.sort(key=lkey)

with open(OUT, 'w', encoding='utf-8', newline='') as f:
    f.write('mw_L\te\tk1_slp1\troot_iast\tverb_type\tclasses\twhitney_anchor\twestergaard\n')
    for r in rows:
        f.write('\t'.join(r) + '\n')

n_total = len(rows)
n_genuine = sum(1 for r in rows if r[4] == 'genuineroot')
n_root = sum(1 for r in rows if r[4] == 'root')
n_anchor = sum(1 for r in rows if r[6])
print(f'mw_roots.tsv written: {n_total} records')
print(f'  genuineroot = {n_genuine}   root = {n_root}   whitney_anchor = {n_anchor}')
assert n_genuine == 750, f'expected 750 genuineroot, got {n_genuine}'
assert n_total == 2113, f'expected 2113 verbal-root records, got {n_total}'
print('  counts OK (750 / 2113)')
