#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
root_norm.py  --  shared root-form normalization, consumed by every etymology
extractor. Loads root_norm.tsv (built by build_root_normalization.py) and folds a
surface-variant root onto its dhātupāṭha citation form (sada -> sad). A root with
no mapping is returned unchanged. Single owner so the three extractors normalize
identically.
"""
import os
import csv

_MAP = {}
_LOADED = False


def load(path=None):
    global _LOADED
    p = path or os.environ.get('ROOT_NORM') or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'root_norm.tsv')
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
            v, c = r.get('variant_slp1'), r.get('canonical_slp1')
            if v and c:
                _MAP[v] = c
    _LOADED = True
    return len(_MAP)


def canon(slp1):
    """Return the canonical citation-form SLP1 root for a (possibly variant) root."""
    if not _LOADED:
        load()
    return _MAP.get(slp1, slp1) if slp1 else slp1
