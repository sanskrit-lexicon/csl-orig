#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_mw_etymology.py  --  etymology / derivation extractor for Monier-Williams.

MW does not use WIL's `<ab>E.</ab>` or SKD/VCP's `kāraka+pratyaya`. It marks
derivation two ways, both mined here:

  1. `parse="X+Y"`  (in <info> tags, ~7000×) — MW's own morpheme analysis,
     e.g.  parse="aMSI+kf"  (aṃśī + √kṛ),  parse="aGa+Svas".
  2. `fr. √ <s>ROOT</s>`  (prose, ~500×) — explicit root attribution.

Each parse member is CLASSIFIED by reusing the project's existing tables:
  * root   — member is in the canonical dhātu list (../etymology_stats/dhatu_roots.txt)
  * affix  — member is a known pratyaya (../wil affix table)
  * prefix — member is an upasarga
  * stem   — anything else (compound member)

    python analyze_mw_etymology.py [path/to/mw.txt]     # default ./mw.txt

Outputs next to the input:  mw_etymology.tsv  +  mw_etymology.jsonl
"""
import os, sys, re, json

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# reuse affix machinery (WIL) and the vendored dhātu list -----------------------
_WILDIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wil'))
sys.path.insert(0, _WILDIR)
import analyze_wil_etymology as wil          # noqa: E402
to_iast = wil.to_iast

UPASARGA = {'pra', 'parA', 'apa', 'sam', 'anu', 'ava', 'nis', 'nir', 'dus', 'dur',
            'vi', 'A', 'AN', 'ni', 'aDi', 'api', 'ati', 'su', 'ud', 'ut', 'aBi',
            'prati', 'pari', 'upa', 'a', 'an'}

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


# Canonical MW root register (mw_roots.tsv): SLP1 root -> verb classes. Used to
# tag each extracted MW root with its conjugation class and flag whether it is a
# canonical genuine root (vs a surface variant / parse artefact).
MW_ROOTS = {}


def load_mw_roots():
    import csv as _csv
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mw_roots.tsv')
    if os.path.exists(p):
        for r in _csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            k = r.get('k1_slp1')
            if k and k not in MW_ROOTS:
                MW_ROOTS[k] = (r.get('classes', ''), r.get('verb_type', ''))
    return len(MW_ROOTS)


PARSE_RE = re.compile(r'parse="([^"]+)"')
FRROOT_RE = re.compile(r'<ab>fr\.</ab>\s*√\s*(?:<hom>[^<]*</hom>\s*)?<s>([^<]+)</s>')
SVERB_RE = re.compile(r'<s>[^<]*√\s*([A-Za-z][A-Za-z\']*)</s>')   # <s>aMSI-√ kf</s>


def classify(member):
    """root | affix | prefix | stem for one SLP1 parse member."""
    m = member.strip()
    if not m:
        return None
    # upasarga first: many prefixes coincide with a root surface form, but in an
    # MW parse "abhi+kf" the abhi is the prefix and kf the root.
    if m in UPASARGA:
        return 'prefix'
    if m in ROOT_SET:
        return 'root'
    if to_iast(m) in wil.AFFIXES:
        return 'affix'
    return 'stem'


def parse_entry(L_id, headword, body):
    text = ' '.join(body)
    fr = FRROOT_RE.search(text) or SVERB_RE.search(text)
    fr_root = fr.group(1).strip() if fr else None

    pm = PARSE_RE.search(text)
    members, classes, root, affix, prefixes = [], [], None, None, []
    if pm:
        raw = pm.group(1).replace('√', '').strip()
        members = [x.strip() for x in re.split(r'[+]', raw) if x.strip()]
        for mem in members:
            cls = classify(mem)
            classes.append(cls)
            if cls == 'root' and root is None:
                root = mem
            elif cls == 'affix' and affix is None:
                affix = mem
            elif cls == 'prefix':
                prefixes.append(mem)
    if root is None and fr_root and (not ROOT_SET or fr_root in ROOT_SET or not members):
        root = fr_root

    if not members and not fr_root:
        return None
    # derivation type
    cset = set(classes)
    if 'root' in cset and 'affix' in cset:
        dtype = 'root+affix'
    elif 'prefix' in cset and 'root' in cset:
        dtype = 'prefix+root'
    elif 'root' in cset and 'stem' in cset:
        dtype = 'stem+root (denominal/cmpd)'
    elif len(members) >= 2 and 'root' not in cset:
        dtype = 'compound'
    elif fr_root and not members:
        dtype = 'root-attribution'
    else:
        dtype = 'other'

    note = source = group = steps = None
    if affix:
        note, source, group, steps = wil.decode_affix(affix)

    # cross-link the root to the canonical MW root register (mw_roots.tsv)
    mw_r = MW_ROOTS.get(root) if root else None
    root_class = mw_r[0] if mw_r else None
    root_canonical = 'Y' if mw_r else ('?' if root else None)

    return {
        'L_id': L_id,
        'headword': to_iast(headword) if headword else None,
        'headword_slp1': headword,
        'root': to_iast(root) if root else None,
        'root_slp1': root,
        'root_via': ('parse' if (root and root in members) else ('fr-root' if root else None)),
        'root_class': root_class,
        'root_canonical': root_canonical,
        'prefixes': ' '.join(to_iast(p) for p in prefixes) or None,
        'affix': to_iast(affix) if affix else None,
        'affix_slp1': affix,
        'group': group,
        'anubandha': note,
        'anubandha_steps': steps or None,
        'affix_source': source,
        'deriv_type': dtype,
        'parse': '+'.join(members) or None,
        'members': [{'slp1': m, 'iast': to_iast(m), 'class': c}
                    for m, c in zip(members, classes)],
        'context': re.sub(r'<[^>]+>', '', text)[:120].strip(),
    }


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'mw.txt')
    wil.load_affix_base()
    nr = load_root_set()
    nmw = load_mw_roots()
    print("Affix table + {} dhātu roots + {} canonical MW roots loaded".format(nr, nmw))

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
                rec = parse_entry(L_id, headword, buf)
                if rec:
                    records.append(rec)
                collecting = False
            else:
                buf.append(ln)

    base = os.path.dirname(os.path.abspath(path))
    cols = ['L_id', 'headword', 'headword_slp1', 'root', 'root_slp1', 'root_via',
            'root_class', 'root_canonical', 'prefixes', 'affix', 'affix_slp1',
            'group', 'anubandha', 'anubandha_steps', 'affix_source', 'deriv_type',
            'parse', 'context']
    with open(os.path.join(base, 'mw_etymology.tsv'), 'w', encoding='utf-8', newline='') as f:
        f.write('\t'.join(cols) + '\n')
        for r in records:
            f.write('\t'.join('' if r.get(c) is None else str(r[c]).replace('\t', ' ')
                              for c in cols) + '\n')
    with open(os.path.join(base, 'mw_etymology.jsonl'), 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    from collections import Counter
    print("Mined {} derivations from MW".format(len(records)))
    print("\nDerivation type:")
    for t, n in Counter(r['deriv_type'] for r in records).most_common():
        print("  {:18s} {}".format(t, n))
    rooted = sum(1 for r in records if r['root'])
    print("\nRoot identified: {}/{} ({:.0f}%)".format(rooted, len(records), 100 * rooted / max(1, len(records))))
    canon = sum(1 for r in records if r.get('root_canonical') == 'Y')
    print("Root in canonical mw_roots.tsv: {}/{} ({:.0f}% of rooted) -- rest are surface "
          "variants / parse artefacts".format(canon, rooted, 100 * canon / max(1, rooted)))
    affixed = sum(1 for r in records if r['affix'])
    print("Affix identified: {}".format(affixed))
    print("\nTop roots:")
    for a, n in Counter(r['root'] for r in records if r['root']).most_common(10):
        print("  {:10s} {}".format(a, n))


if __name__ == '__main__':
    main()
