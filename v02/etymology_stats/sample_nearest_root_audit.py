#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a deterministic audit sample for nearest-root etymology captures."""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
V02 = HERE.parent
DEFAULT_OUTPUT = HERE / 'nearest_root_audit_sample.csv'

AUDIT_FIELDS = [
    'dict',
    'L_id',
    'headword',
    'headword_slp1',
    'root',
    'root_slp1',
    'karaka',
    'karaka_sense',
    'affix',
    'affix_slp1',
    'context',
    'audit_status',
    'auditor_notes',
]


def iter_nearest_root_rows(v02_dir):
    for path in sorted(v02_dir.glob('*/*_etymology.jsonl')):
        dict_code = path.name.split('_', 1)[0].upper()
        with path.open(encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as err:
                    raise ValueError("{}:{}: {}".format(path, line_no, err)) from err
                if row.get('root_source') == 'nearest-root':
                    row['dict'] = dict_code
                    yield row


def choose_sample(rows_by_dict, per_dict, seed):
    rng = random.Random(seed)
    sample = []
    for dict_code in sorted(rows_by_dict):
        rows = sorted(
            rows_by_dict[dict_code],
            key=lambda r: (r.get('L_id') or '', r.get('headword_slp1') or '',
                           r.get('root_slp1') or '', r.get('context') or ''),
        )
        if len(rows) <= per_dict:
            picked = rows
        else:
            picked = rng.sample(rows, per_dict)
            picked.sort(key=lambda r: (r.get('L_id') or '', r.get('headword_slp1') or '',
                                       r.get('root_slp1') or '', r.get('context') or ''))
        sample.extend(picked)
    return sample


def audit_row(row):
    return {
        field: row.get(field, '')
        for field in AUDIT_FIELDS
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--per-dict', type=int, default=25,
                        help='maximum nearest-root rows to sample from each dictionary')
    parser.add_argument('--seed', type=int, default=20260626,
                        help='random seed for deterministic sampling')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT),
                        help='CSV path to write')
    args = parser.parse_args()

    rows_by_dict = defaultdict(list)
    for row in iter_nearest_root_rows(V02):
        rows_by_dict[row['dict']].append(row)

    sample = choose_sample(rows_by_dict, args.per_dict, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=AUDIT_FIELDS)
        writer.writeheader()
        writer.writerows(audit_row(row) for row in sample)

    counts = Counter({dict_code: len(rows) for dict_code, rows in rows_by_dict.items()})
    print('nearest-root rows:', ', '.join(
        '{}={}'.format(dict_code, counts[dict_code]) for dict_code in sorted(counts)))
    print('sample rows written: {} -> {}'.format(len(sample), output))


if __name__ == '__main__':
    main()
