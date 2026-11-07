_Created: 26-06-2026 · Last updated: 05-09-2026_

# VCP Pāṇinian derivation extractor

VCP (Vācaspatyam) has **no `<ab>E.</ab>` block** — its derivations are stated in
Sanskrit prose (`kf--BAve lyuw`, `jiDAtoH karmmaRi yat`). They are mined by the
shared SKD/VCP extractor, which lives in the SKD folder:

```sh
cd ../skd && python analyze_sktdict_etymology.py ../vcp/vcp.txt
```

→ writes [`vcp_etymology.tsv`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/vcp/vcp_etymology.tsv) (committed) and
`vcp_etymology.jsonl` (git-ignored) here.

Full documentation, column list, the WIL/Apte vs SKD/VCP comparison, the kāraka
layer, and use cases:
[`../skd/README_etymology.md`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/skd/README_etymology.md).

_Dr. Mārcis Gasūns_
