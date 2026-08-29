#!/usr/bin/env python3
"""Encoding guard for csl-orig canonical dictionary sources.

Checks each canonical per-dict source `v02/<dict>/<dict>.txt` (the file the
generation pipeline / hw.py consumes) and fails if it:
  * begins with a UTF-8 BOM (EF BB BF),
  * is not decodable as UTF-8, or
  * uses the `<L>…<LEND>` entry format but `<L>` and `<LEND>` counts do not
    balance, or has zero `<LEND>` lines at all (catches missing/duplicated
    `<LEND>` and the hidden-first-`<L>` case without needing the full XML
    build).

Rationale: a stray UTF-8 BOM on line 1 once surfaced only as a cryptic
`hw.py` `init_entries Error 2` and reached origin before detection
(see csl-pywork#50/#51). This catches that whole class pre-merge.

Scope note: only canonical `<dict>/<dict>.txt` files are checked. Auxiliary
/intermediate files (e.g. `*/update/*_ansi.txt`) are deliberately *not*
checked — some are intentionally in non-UTF-8 encodings. NFC normalization is
also not enforced (some sources legitimately are not NFC).

Run from anywhere: `python scripts/check_encoding.py`.

Pre-commit (`--staged`) mode validates the STAGED blobs (`git show :v02/...`),
never the worktree bytes, so a partial `git add -p` staging cannot commit
content that was never checked. If a canonical `v02/<dict>/<dict>.txt` is
absent from the index (deleted/renamed away without an ack), that is a
failure — not a silent skip.
"""
import os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'v02')
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STAGED = False
args = sys.argv[1:]
if args and args[0] == '--staged':
    STAGED = True
    args = args[1:]


def staged_bytes(relpath):
    """Return the staged blob bytes for relpath, or (None, error_message)."""
    try:
        r = subprocess.run(['git', 'show', ':' + relpath], cwd=REPO_ROOT,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        return None, str(e)
    if r.returncode != 0:
        return None, r.stderr.decode('utf-8', 'replace').strip()
    return r.stdout, None


files = []
bad_missing = []   # canonical sources missing from the index (staged mode only)
if args:
    # Pre-commit mode: filenames of staged files are passed as arguments.
    # Derive the unique dict names from paths like v02/<dict>/... and check
    # only those dicts' canonical <dict>.txt files.
    dicts_to_check: set[str] = set()
    for p in args:
        parts = p.replace('\\', '/').split('/')
        # Expect at least  v02 / <dict> / ...
        if len(parts) >= 2 and parts[0] == 'v02' and parts[1]:
            dicts_to_check.add(parts[1])
    for d in sorted(dicts_to_check):
        rel = f'v02/{d}/{d}.txt'                # canonical source: v02/<dict>/<dict>.txt
        if STAGED:
            data, err = staged_bytes(rel)
            if err is not None:
                bad_missing.append(f'{d} ({rel} not in the index: {err})')
                continue
            files.append((d, rel, data))
        else:
            p = os.path.join(ROOT, d, d + '.txt')
            if os.path.exists(p):
                files.append((d, p, None))
else:
    # CI / scan-all mode (GHA workflow, or manual run with no arguments).
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        p = os.path.join(dd, d + '.txt')        # canonical source: v02/<dict>/<dict>.txt
        if os.path.exists(p):
            files.append((d, p, None))

bad_bom, bad_utf8, bad_struct = [], [], []
for name, p, data in files:
    if data is None:
        with open(p, 'rb') as f:
            data = f.read()
    if data[:3] == b'\xef\xbb\xbf':
        bad_bom.append(name)
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        bad_utf8.append(name)
        continue
    # Structural balance: every canonical source uses the <L>...<LEND> format,
    # so a file with zero <LEND> lines is itself a defect, and entry-starts
    # must match entry-ends.
    nL = nLEND = 0
    for line in text.split('\n'):
        if line.startswith('<LEND>'):
            nLEND += 1
        elif line.startswith('<L>'):
            nL += 1
    if nLEND == 0:
        bad_struct.append(f'{name} (zero <LEND> lines; <L>={nL})')
    elif nL != nLEND:
        bad_struct.append(f'{name} (<L>={nL}, <LEND>={nLEND})')

print(f'checked {len(files)} canonical dict sources under v02/')
fail = False
if bad_missing:
    fail = True
    print(f'FAIL: canonical source missing from the index in: {"; ".join(bad_missing)}')
if bad_bom:
    fail = True
    print(f'FAIL: UTF-8 BOM found in: {", ".join(bad_bom)}')
if bad_utf8:
    fail = True
    print(f'FAIL: invalid UTF-8 in: {", ".join(bad_utf8)}')
if bad_struct:
    fail = True
    print(f'FAIL: <L>/<LEND> structural defect in: {"; ".join(bad_struct)}')
if fail:
    sys.exit(1)
print('OK: no BOM, valid UTF-8, balanced <L>/<LEND>')
