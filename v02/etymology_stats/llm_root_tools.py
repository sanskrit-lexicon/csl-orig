#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_root_tools.py  --  DeepSeek-assisted root tooling for the etymology pipeline.

Two modes, both validating every LLM-proposed root against the canonical dhātu
list (dhatu_roots.txt) so hallucinations are rejected, not written:

  audit    — sample the inferred root tiers (nearest-root, oracle-join) and have
             DeepSeek judge whether the assigned root is correct for the derived
             head-word. Reports precision per tier. (Closes the A35 "% has *a*
             root, not the *correct* root" gap.)
  resolve  — for a dictionary's still-empty rows, ask DeepSeek for the root,
             validate, and write <dict>_llm_roots.tsv (head-word -> root).

Reuses the DeepSeek client pattern from
SanskritLexicography/RussianTranslation/src/build_corpus_lexicon.py.

  python llm_root_tools.py audit   [--n 40]
  python llm_root_tools.py resolve --dict vcp [--limit 0]
"""
import os, sys, re, csv, json, time, random, argparse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..'))
GH = os.path.normpath(os.path.join(V02, '..', '..'))
ENV = os.path.join(GH, 'SanskritLexicography', 'RussianTranslation', 'src', '.env')
API = 'https://api.deepseek.com/chat/completions'

from indic_transliteration import sanscript
to_iast = lambda s: sanscript.transliterate(s, sanscript.SLP1, sanscript.IAST)
to_slp1 = lambda s: sanscript.transliterate(s, sanscript.IAST, sanscript.SLP1)

ROOT_SET = set(l.strip() for l in open(os.path.join(HERE, 'dhatu_roots.txt'), encoding='utf-8')
               if l.strip() and not l.startswith('#'))


def _key():
    for line in open(ENV, encoding='utf-8'):
        if line.strip().startswith('DEEPSEEK_API_KEY='):
            return line.split('=', 1)[1].strip()
    sys.exit('no DEEPSEEK_API_KEY in ' + ENV)


KEY = _key()


def deepseek(system, user, retries=3):
    body = json.dumps({'model': 'deepseek-chat', 'temperature': 0,
                       'response_format': {'type': 'json_object'},
                       'messages': [{'role': 'system', 'content': system},
                                    {'role': 'user', 'content': user}]}).encode('utf-8')
    for a in range(retries):
        try:
            req = urllib.request.Request(API, data=body, headers={
                'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=70) as r:
                return json.loads(json.load(r)['choices'][0]['message']['content'])
        except Exception as ex:
            if a == retries - 1:
                sys.stderr.write('deepseek fail: %s\n' % ex)
                return None
            time.sleep(2 * (a + 1))


def rows(dictcode):
    p = os.path.join(V02, dictcode, dictcode + '_etymology.tsv')
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))


SANSKRIT = ['skd', 'vcp', 'ap90', 'ap', 'shs', 'krm']

JUDGE_SYS = (
    'You are a Pāṇinian Sanskrit grammarian. Given a DERIVED Sanskrit word (IAST) '
    'and a CANDIDATE verbal root (dhātu, IAST), decide whether the candidate is the '
    'word\'s actual root. IGNORE surface/citation-form differences: a stem or '
    'thematic form such as "sada" for "sad", "śvasa" for "śvas", or "kṝ" for "kṛ" '
    'counts as the SAME root (correct=true). Mark correct=false ONLY if it is a '
    'genuinely DIFFERENT root. Output ONLY JSON: {"correct": true|false, '
    '"canonical_root_iast": "<the dhātupāṭha citation form of the correct root>"}.')


def cmd_audit(args):
    pool = []
    for d in SANSKRIT:
        for r in rows(d):
            if r.get('root_source') in ('nearest-root', 'oracle-join') and r.get('root'):
                pool.append((d, r['root_source'], r['headword'], r['root']))
    random.seed(11)
    random.shuffle(pool)
    by = {'nearest-root': [], 'oracle-join': []}
    for rec in pool:
        if len(by[rec[1]]) < args.n:
            by[rec[1]].append(rec)
    results = {}
    for tier, sample in by.items():
        ok = bad = 0
        details = []
        for d, src, hw, root in sample:
            v = deepseek(JUDGE_SYS, 'word: %s\ncandidate root: %s' % (hw, root))
            if v is None:
                continue
            if v.get('correct'):
                ok += 1
            else:
                bad += 1
                details.append('%s <- %s  (canonical: %s)' % (hw, root, v.get('canonical_root_iast', '?')))
            time.sleep(0.2)
        n = ok + bad
        results[tier] = (ok, n)
        print('\n[%s] precision %d/%d = %.0f%%' % (tier, ok, n, 100 * ok / max(1, n)))
        for x in details[:8]:
            print('   ✗ ' + x)
    with open(os.path.join(HERE, 'nearest_root_audit.json'), 'w', encoding='utf-8') as f:
        json.dump({k: {'correct': v[0], 'n': v[1]} for k, v in results.items()}, f,
                  ensure_ascii=False, indent=1)
    print('\nWrote nearest_root_audit.json')


RESOLVE_SYS = (
    'You are a Pāṇinian Sanskrit grammarian. Given a DERIVED Sanskrit word (IAST) '
    'and a short context, identify its underlying verbal root (dhātu) in IAST, '
    'citation form (e.g. kṛ, bhū, gam, sthā). Output ONLY JSON: '
    '{"root_iast": "<dhātu, or empty if not a primary derivative>", '
    '"confidence": "high"|"low"}. Prefer empty over a guess.')


def cmd_resolve(args):
    d = args.dict
    src = rows(d)
    empty = [r for r in src if not r.get('root_slp1')]
    if args.limit:
        empty = empty[:args.limit]
    out = os.path.join(HERE, d + '_llm_roots.tsv')
    kept = seen = 0
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['headword_slp1', 'headword_iast', 'root_slp1', 'root_iast', 'confidence'])
        for r in empty:
            seen += 1
            ctx = re.sub(r'<[^>]+>', '', r.get('context', ''))[:200]
            v = deepseek(RESOLVE_SYS, 'word: %s\ncontext: %s' % (r['headword'], ctx))
            if not v or not v.get('root_iast'):
                continue
            rt_iast = v['root_iast'].strip()
            rt_slp1 = to_slp1(rt_iast)
            if rt_slp1 in ROOT_SET:        # validate against canonical dhātu list
                w.writerow([r['headword_slp1'], r['headword'], rt_slp1, rt_iast, v.get('confidence', '')])
                kept += 1
            if seen % 25 == 0:
                f.flush()
                print('  %d/%d processed, %d validated roots' % (seen, len(empty), kept))
            time.sleep(0.15)
    print('Resolved %d/%d empty %s rows to a validated root -> %s' % (kept, seen, d.upper(), out))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('audit'); a.add_argument('--n', type=int, default=40)
    rr = sub.add_parser('resolve'); rr.add_argument('--dict', required=True); rr.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    {'audit': cmd_audit, 'resolve': cmd_resolve}[args.cmd](args)
