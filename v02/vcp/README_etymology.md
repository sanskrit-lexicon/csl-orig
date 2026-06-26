# VCP Pāṇinian derivation extractor

VCP (Vācaspatyam) has **no `<ab>E.</ab>` block** — its derivations are stated in
Sanskrit prose (`kf--BAve lyuw`, `jiDAtoH karmmaRi yat`). They are mined by the
shared SKD/VCP extractor, which lives in the SKD folder:

```sh
cd ../skd && python analyze_sktdict_etymology.py ../vcp/vcp.txt
```

→ writes [`vcp_etymology.tsv`](vcp_etymology.tsv) (committed) and
`vcp_etymology.jsonl` (git-ignored) here.

Full documentation, column list, the WIL/Apte vs SKD/VCP comparison, the kāraka
layer, and use cases:
[`../skd/README_etymology.md`](../skd/README_etymology.md).
