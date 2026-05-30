#!/usr/bin/env python3
"""Encoding guard for csl-orig canonical dictionary sources.

Checks each canonical per-dict source `v02/<dict>/<dict>.txt` (the file the
generation pipeline / hw.py consumes) and fails if it:
  * begins with a UTF-8 BOM (EF BB BF), or
  * is not decodable as UTF-8.

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

bad_bom, bad_utf8 = [], []
for name, p in files:
    with open(p, 'rb') as f:
        data = f.read()
    if data[:3] == b'\xef\xbb\xbf':
        bad_bom.append(name)
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        bad_utf8.append(name)

print(f'checked {len(files)} canonical dict sources under v02/')
fail = False
if bad_bom:
    fail = True
    print(f'FAIL: UTF-8 BOM found in: {", ".join(bad_bom)}')
if bad_utf8:
    fail = True
    print(f'FAIL: invalid UTF-8 in: {", ".join(bad_utf8)}')
if fail:
    sys.exit(1)
print('OK: no BOM, all valid UTF-8')
