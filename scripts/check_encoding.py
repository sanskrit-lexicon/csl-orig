#!/usr/bin/env python3
"""Encoding guard for csl-orig canonical dictionary sources.

Checks each canonical per-dict source `v02/<dict>/<dict>.txt` (the file the
generation pipeline / hw.py consumes) and fails if it:
  * begins with a UTF-8 BOM (EF BB BF),
  * is not decodable as UTF-8, or
  * uses the `<L>…<LEND>` entry format but `<L>` and `<LEND>` counts do not
    balance (catches missing/duplicated `<LEND>` and the hidden-first-`<L>`
    case without needing the full XML build).

Rationale: a stray UTF-8 BOM on line 1 once surfaced only as a cryptic
`hw.py` `init_entries Error 2` and reached origin before detection
(see csl-pywork#50/#51). This catches that whole class pre-merge.

Scope note: only canonical `<dict>/<dict>.txt` files are checked. Auxiliary
/intermediate files (e.g. `*/update/*_ansi.txt`) are deliberately *not*
checked — some are intentionally in non-UTF-8 encodings. NFC normalization is
also not enforced (some sources legitimately are not NFC).

Run from anywhere: `python scripts/check_encoding.py`.
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'v02')

files = []
for d in sorted(os.listdir(ROOT)):
    dd = os.path.join(ROOT, d)
    if not os.path.isdir(dd):
        continue
    p = os.path.join(dd, d + '.txt')          # canonical source: v02/<dict>/<dict>.txt
    if os.path.exists(p):
        files.append((d, p))

bad_bom, bad_utf8, bad_struct = [], [], []
for name, p in files:
    with open(p, 'rb') as f:
        data = f.read()
    if data[:3] == b'\xef\xbb\xbf':
        bad_bom.append(name)
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        bad_utf8.append(name)
        continue
    # Structural balance: in <L>...<LEND> formats, entry-starts must match entry-ends.
    nL = nLEND = 0
    for line in text.split('\n'):
        if line.startswith('<LEND>'):
            nLEND += 1
        elif line.startswith('<L>'):
            nL += 1
    if nLEND and nL != nLEND:
        bad_struct.append(f'{name} (<L>={nL}, <LEND>={nLEND})')

print(f'checked {len(files)} canonical dict sources under v02/')
fail = False
if bad_bom:
    fail = True
    print(f'FAIL: UTF-8 BOM found in: {", ".join(bad_bom)}')
if bad_utf8:
    fail = True
    print(f'FAIL: invalid UTF-8 in: {", ".join(bad_utf8)}')
if bad_struct:
    fail = True
    print(f'FAIL: <L>/<LEND> imbalance in: {"; ".join(bad_struct)}')
if fail:
    sys.exit(1)
print('OK: no BOM, valid UTF-8, balanced <L>/<LEND>')
