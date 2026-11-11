#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""update_tooling_parity.py — offline behavior-preservation gate (H7961).

Compares the base-ref copies (via `git show`, default origin/main) of the
csl-orig update tooling against the working-tree copies on identical committed
fixtures, and against golden outputs captured from the old code:

  * v02/gra/greek/updateByLine.py   — behavior; its twin v02/stc/abbrev/
    updateByLine.py is covered by a byte-identity check of the pair.
  * v02/pwkvn/update/transcoder.py  — behavior via transcoder_processString;
    its twin v02/abch/prep/transcoder.py is covered by byte-identity.
  * v02/pwkvn/update/final.py       — compile-checked only: its H7961 change
    deletes unreachable code after a `return`.

Checks (all offline: `git show` of a local ref, no network):

  1. twin pairs byte-identical (md5 receipts printed).
  2. py_compile clean on every touched file.
  3. updateByLine old-vs-new: identical exit code and byte-identical fileout
     on the new/ins/del fixture; identical refusal (exit 1, no fileout) on the
     old-text-mismatch and lnum-overflow error fixtures.  stdout is compared
     only where the H7961 defect-fix leaves it unchanged: the fix replaces
     `print(out.encode('utf-8'))` (py3 b'...' reprs) with plain `print(out)`
     on the old-text-mismatch error path, so that path's stdout is expected
     to move and is deliberately not byte-compared.
  4. transcoder_processString old-vs-new byte-identical outputs on fixture
     strings covering the slp1_deva consonant look-ahead and the deva_slp1
     vowel-sign look-ahead.
  5. golden outputs (captured from the old code, committed in
     scripts/update_tooling_parity_fixtures/goldens.json) reproduced exactly
     by the working tree — the own-data canary that keeps its value after the
     PR merges and base == working tree.

Usage:
    python scripts/update_tooling_parity.py [--base REF] [--write-goldens]

Exit 0 = every check green.
"""
from __future__ import print_function
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

import py_compile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # repo root
FIXDIR = os.path.join(HERE, 'update_tooling_parity_fixtures')
GOLDENS = os.path.join(FIXDIR, 'goldens.json')

UPD = 'v02/gra/greek/updateByLine.py'
UPD_TWIN = 'v02/stc/abbrev/updateByLine.py'
TRN = 'v02/pwkvn/update/transcoder.py'
TRN_TWIN = 'v02/abch/prep/transcoder.py'
FIN = 'v02/pwkvn/update/final.py'

# The transcoder FSM xml files live beside the pwkvn copy (final.py runs the
# pipeline with transcoder_set_dir('./')); pin them explicitly so both the old
# and the new module read the same committed FSM data.
TRN_DATA_DIR = os.path.join(ROOT, 'v02', 'pwkvn', 'update')

TOUCHED = [UPD, UPD_TWIN, TRN, TRN_TWIN, FIN,
           'scripts/update_tooling_parity.py']

# updateByLine fixture cases.  'compare_stdout' False only where the mandated
# H7961 print fix changes error-path stdout (see module docstring).
UPD_CASES = [
    {'name': 'new-ins-del', 'input': 'input.txt', 'change': 'change_ok.txt',
     'out': 'out.txt', 'rc': 0, 'fileout': True, 'compare_stdout': True},
    {'name': 'old-text-mismatch', 'input': 'input.txt',
     'change': 'change_mismatch.txt', 'out': 'out.txt', 'rc': 1,
     'fileout': False, 'compare_stdout': False},
    {'name': 'lnum-overflow', 'input': 'input.txt', 'change': 'change_lnum.txt',
     'out': 'out.txt', 'rc': 1, 'fileout': False, 'compare_stdout': True},
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def git_show(ref, relpath):
    p = subprocess.run(['git', '-C', ROOT, 'show', '%s:%s' % (ref, relpath)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.write(p.stderr.decode('utf-8', 'replace'))
        raise SystemExit('FATAL: git show %s:%s failed' % (ref, relpath))
    return p.stdout


def read_file(path):
    with open(path, 'rb') as f:
        return f.read()


def run_update_by_line(script_bytes, case):
    """Run one updateByLine copy on one fixture case.  Fixtures are copied
    into a per-run temp dir and referenced by bare filename, so captured
    stdout is machine-independent (golden-stable)."""
    tmp = tempfile.mkdtemp(prefix='updparity_')
    try:
        with open(os.path.join(tmp, 'updateByLine.py'), 'wb') as f:
            f.write(script_bytes)
        for name in (case['input'], case['change']):
            shutil.copy(os.path.join(FIXDIR, name), os.path.join(tmp, name))
        p = subprocess.run(
            [sys.executable, 'updateByLine.py',
             case['input'], case['change'], case['out']],
            cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_path = os.path.join(tmp, case['out'])
        fileout = read_file(out_path) if os.path.exists(out_path) else None
        return {'rc': p.returncode, 'stdout': p.stdout, 'fileout': fileout}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def load_transcoder(script_bytes, tag):
    tmp = tempfile.mkdtemp(prefix='trnparity_%s_' % tag)
    path = os.path.join(tmp, 'transcoder.py')
    with open(path, 'wb') as f:
        f.write(script_bytes)
    spec = importlib.util.spec_from_file_location(
        'transcoder_parity_%s' % tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.transcoder_set_dir(TRN_DATA_DIR)
    return mod, tmp


def transcoder_outputs(mod, fixtures):
    out = {}
    for fx in fixtures:
        out[fx['id']] = mod.transcoder_processString(
            fx['text'], fx['from'], fx['to'])
    return out


def load_transcoder_fixtures():
    with open(os.path.join(FIXDIR, 'transcoder_strings.json'), 'rb') as f:
        return json.loads(f.read().decode('utf-8'))['fixtures']


class Checker(object):
    def __init__(self):
        self.n = 0
        self.failures = []

    def check(self, name, ok, detail=''):
        self.n += 1
        if ok:
            print('[PASS] %s' % name)
        else:
            print('[FAIL] %s %s' % (name, detail))
            self.failures.append(name)


def compute_all(base):
    """Run old (base) and new (working tree) on every fixture; return raw
    results for comparison and golden capture."""
    res = {'upd': {}, 'trn': {}}
    upd_old, upd_new = git_show(base, UPD), read_file(os.path.join(ROOT, UPD))
    for case in UPD_CASES:
        res['upd'][case['name']] = {
            'old': run_update_by_line(upd_old, case),
            'new': run_update_by_line(upd_new, case),
        }
    trn_old, trn_new = git_show(base, TRN), read_file(os.path.join(ROOT, TRN))
    fixtures = load_transcoder_fixtures()
    mod_old, tmp_old = load_transcoder(trn_old, 'old')
    mod_new, tmp_new = load_transcoder(trn_new, 'new')
    try:
        res['trn']['old'] = transcoder_outputs(mod_old, fixtures)
        res['trn']['new'] = transcoder_outputs(mod_new, fixtures)
    finally:
        shutil.rmtree(tmp_old, ignore_errors=True)
        shutil.rmtree(tmp_new, ignore_errors=True)
    res['trn_fixtures'] = fixtures
    return res


def goldens_from(res):
    g = {'update_by_line': {}, 'transcoder': {}}
    for case in UPD_CASES:
        old = res['upd'][case['name']]['old']
        g['update_by_line'][case['name']] = {
            'rc': old['rc'],
            'fileout_text': (None if old['fileout'] is None
                             else old['fileout'].decode('utf-8')),
            'stdout_sha256': (sha256(old['stdout'])
                              if case['compare_stdout'] else None),
        }
    for fx in res['trn_fixtures']:
        g['transcoder'][fx['id']] = res['trn']['old'][fx['id']]
    return g


def verify(ck, res, goldens):
    # 3. updateByLine old-vs-new and vs goldens
    for case in UPD_CASES:
        name = case['name']
        old, new = res['upd'][name]['old'], res['upd'][name]['new']
        ck.check('upd/%s old-vs-new exit code (%d)' % (name, old['rc']),
                 old['rc'] == new['rc'] == case['rc'],
                 'old=%d new=%d expected=%d' % (old['rc'], new['rc'],
                                                case['rc']))
        if case['fileout']:
            ck.check('upd/%s old-vs-new fileout bytes' % name,
                     old['fileout'] is not None and
                     old['fileout'] == new['fileout'])
        else:
            ck.check('upd/%s old-vs-new fileout absent' % name,
                     old['fileout'] is None and new['fileout'] is None)
        if case['compare_stdout']:
            ck.check('upd/%s old-vs-new stdout bytes' % name,
                     old['stdout'] == new['stdout'])
        gg = goldens['update_by_line'][name]
        for side in ('old', 'new'):
            run = res['upd'][name][side]
            ck.check('upd/%s %s-vs-golden exit code' % (name, side),
                     run['rc'] == gg['rc'],
                     'run=%d golden=%d' % (run['rc'], gg['rc']))
            if gg['fileout_text'] is None:
                ok = run['fileout'] is None
            else:
                ok = run['fileout'] == gg['fileout_text'].encode('utf-8')
            ck.check('upd/%s %s-vs-golden fileout' % (name, side), ok)
            if gg['stdout_sha256'] is not None:
                ck.check('upd/%s %s-vs-golden stdout' % (name, side),
                         sha256(run['stdout']) == gg['stdout_sha256'])

    # 4./5. transcoder old-vs-new and vs goldens
    for fx in res['trn_fixtures']:
        fid = fx['id']
        old, new = res['trn']['old'][fid], res['trn']['new'][fid]
        ck.check('trn/%s old-vs-new bytes' % fid, old == new)
        ck.check('trn/%s old-vs-golden bytes' % fid, old == goldens['transcoder'][fid])
        ck.check('trn/%s new-vs-golden bytes' % fid, new == goldens['transcoder'][fid])
        if fx.get('must_transform'):
            ck.check('trn/%s fixture not vacuous' % fid, old != fx['text'],
                     'output equals input — fixture exercises nothing')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--base', default='origin/main',
                    help='git ref holding the old tooling copies '
                         '(default: origin/main)')
    ap.add_argument('--write-goldens', action='store_true',
                    help='(re)capture goldens.json from the base copies')
    args = ap.parse_args()

    if not os.path.isdir(FIXDIR):
        raise SystemExit('FATAL: fixtures dir missing: %s' % FIXDIR)

    print('update_tooling_parity — base=%s' % args.base)
    p = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'],
                       stdout=subprocess.PIPE)
    print('working tree HEAD=%s' % p.stdout.decode().strip())

    ck = Checker()

    # 1. twin-pair identity (md5 receipts)
    for a, b, tag in ((UPD, UPD_TWIN, 'updateByLine'),
                      (TRN, TRN_TWIN, 'transcoder')):
        ma, mb = md5file(os.path.join(ROOT, a)), md5file(os.path.join(ROOT, b))
        print('md5 %s %s' % (ma, a))
        print('md5 %s %s' % (mb, b))
        ck.check('twin identity %s' % tag, ma == mb,
                 '%s != %s' % (ma, mb))

    # 2. compile clean
    for rel in TOUCHED:
        try:
            py_compile.compile(os.path.join(ROOT, rel), doraise=True)
            ck.check('py_compile %s' % rel, True)
        except py_compile.PyCompileError as e:
            ck.check('py_compile %s' % rel, False, str(e))

    res = compute_all(args.base)

    if args.write_goldens:
        if res['upd']['old-text-mismatch']['old']['fileout'] is not None:
            raise SystemExit('FATAL: old code produced a fileout on the '
                             'mismatch fixture — fixtures are wrong')
        goldens = goldens_from(res)
        with open(GOLDENS, 'wb') as f:
            f.write((json.dumps(goldens, indent=2, sort_keys=True,
                                ensure_ascii=True) + '\n').encode('ascii'))
        print('goldens written to %s (captured from %s)'
              % (os.path.relpath(GOLDENS, ROOT), args.base))
        # capture-time vacuity gate: fixtures must transform under the old code
        for fx in res['trn_fixtures']:
            if fx.get('must_transform') and \
                    res['trn']['old'][fx['id']] == fx['text']:
                raise SystemExit('FATAL: fixture %s is vacuous under old code'
                                 % fx['id'])
        return 0

    if not os.path.exists(GOLDENS):
        raise SystemExit('FATAL: %s missing — run with --write-goldens first'
                         % GOLDENS)
    with open(GOLDENS, 'rb') as f:
        goldens = json.loads(f.read().decode('utf-8'))

    verify(ck, res, goldens)

    print('%d checks, %d failed' % (ck.n, len(ck.failures)))
    if ck.failures:
        print('FAILED: %s' % ', '.join(ck.failures))
        return 1
    print('ALL GREEN')
    return 0


if __name__ == '__main__':
    sys.exit(main())
