# csl-orig Correction Manual

_Created: 11-07-2026 · Last updated: 11-07-2026_

The self-contained operator manual for changing dictionary text in csl-orig —
the canonical source-text store for all 45 CDSL dictionaries and the root of
the correction dependency graph. It distills the full 8-stage discipline, the
local safety hooks, and the **delivery split**: upstream maintainers commit
directly; **everyone else (agents and downstream contributors) queues
corrections and ships ONE consolidated PR roughly monthly — never direct
pushes, never streams of small PRs.** The deep reference (worked tutorial,
full tooling table, evidence links) remains the canonical
[csl-corrections/docs/correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md);
this manual is the csl-orig-resident operator view.

Companion metadoc: [docs/CORRECTION_MANUAL.meta.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/docs/CORRECTION_MANUAL.meta.md).

---

## 1. Cheat-sheet — one correction, eight stages

```bash
# layout: csl-orig / csl-pywork / csl-websanlexicon / csl-corrections
#         as siblings under one parent ($BASE/cologne/ convention)

# 0. PREFLIGHT (old issues): search csl-corrections CFR + batch history for the
#    same dict/L-number/headword — 'No change'/rejected/deferred = STOP (§3.0)

# 1. snapshot
cp $BASE/cologne/csl-orig/v02/<dict>/<dict>.txt temp_<dict>_0.txt

# 2. apply (line-addressed change file: 'NNN old …' / 'NNN new …'; ins/del too)
python updateByLine.py temp_<dict>_0.txt change_<dict>_in.txt temp_<dict>_1.txt

# 3. promote
cp temp_<dict>_1.txt $BASE/cologne/csl-orig/v02/<dict>/<dict>.txt

# 4. regenerate      (watch for: "All records parsed by ET")
cd $BASE/cologne/csl-pywork/v02 && sh generate_dict.sh <dict> ../../<dict>

# 5. XML-validate against the DTD
sh xmlchk_xampp.sh <dict>

# 6. audit trail (equal line counts; use diff_to_changes.py if lines added/removed)
python diff_to_changes_dict.py temp_<dict>_0.txt temp_<dict>_1.txt change_<dict>_N.txt

# 7. DELIVER — two different worlds:
#    maintainers (Jim/Dhaval): paired direct commits to csl-orig + csl-corrections
#    agents/contributors:      park in the correction queue (/cologne-correction-queue)
#                               → ONE consolidated PR ~monthly (/cologne-batch-pr)

# 8. public refresh: cron-driven redo_xampp_selective.sh on the server — not your step
```

Local safety net (install once per clone): `sh scripts/install-hooks.sh` —
the pre-commit hook then runs the encoding guard + a `generate_dict.sh`
smoke-test on every staged `v02/` file (§4).

## 2. Data-flow diagram

```
GitHub issue (dictionary repo: MWS, PWG, AP90, …)   ← where corrections start
│    §3.0 CFR/batch-history preflight (was it already decided?)
▼
change file  (NNN old / NNN new, ; comments)         ← the auditable edit unit
│    updateByLine.py over a snapshot
▼
v02/<dict>/<dict>.txt   ★ THE CANONICAL TEXT — 45 dicts, everything downstream
│                          derives from this file
│    generate_dict.sh   (csl-pywork: orig/ → pywork/ → web/ → downloads/;
│                        make_xml.py "All records parsed by ET")
│    xmlchk_xampp.sh    (xmllint --valid against the DTD)
▼
csl-corrections/batch_YYYYMMDD/dictionaries/<dict>/  ← audit trail
│    change_<dict>_N.txt + readme.txt  (generated AFTER the edit — the change
│    files are records, not pipeline inputs)
▼
DELIVERY
├─ maintainer pattern: paired direct commits (csl-orig + csl-corrections,
│    cross-referenced messages — Dhaval's "DC DD Month YYYY" commits)
└─ agent/contributor pattern: correction queue → ONE batched PR ~monthly
     (the load-bearing no-noise rule: csl-orig is the dependency-graph root;
      unvalidated or noisy writes ripple into every reader-facing surface)
▼
public artefacts: Cologne site, zips, Stardict, JSON, SQLite
     (cron: redo_xampp_selective.sh picks up new commits)
```

## 3. The stages, with the judgment calls

### 3.0 Preflight — has this correction already been decided?

Before applying **any** old correction issue: search the csl-corrections CFR
registry + batch history for the same dictionary, L-number, headword, old
text, new text. `No change` / rejected / deferred = **do not patch** unless a
maintainer explicitly reopens it. Then decide the representation: a **plain
replacement**, or the **inline correction layer**
`{{old->new||YYYYMMDD|author|issue|}}` that preserves the original reading
(use the layer when the original text has scholarly value — record the
decision in the batch readme).

### 3.1–3.3 Snapshot → apply → promote

The snapshot is the diff base for the audit trail — keep it until stage 6.
`updateByLine.py` applies line-addressed `old`/`new`/`ins`/`del` directives
(hand-editing works but leaves no record — don't). **Re-pull and re-snapshot
if any time passed**: line numbers shift the moment someone else's correction
lands (§5). Promotion is a plain `cp` over the canonical file — from this
moment the pipeline sees your edit.

### 3.4–3.5 Regenerate → validate

`generate_dict.sh <dict> ../../<dict>` rebuilds the full installation in four
sub-stages (orig → pywork → web → execute; details in the
[canonical doc §4.4](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md)).
The ET parse failing loudly is the point — it catches broken tags.
`xmlchk_xampp.sh <dict>` adds the DTD validation xmllint pass; ET-parse
success alone is necessary but not sufficient (§5 on missing xmllint).

### 3.6 Audit trail

`diff_to_changes_dict.py before after change_<dict>_N.txt` — positional
pairing, so **equal line counts required**; if your edit added/removed lines
use `diff_to_changes.py` (no `_dict`). The output lands in
`csl-corrections/batch_YYYYMMDD/dictionaries/<dict>/` with a `readme.txt`
recording commands run + the §3.0 decisions.

### 3.7 Delivery — the load-bearing split

**Upstream maintainers** (Jim Funderburk, Dhaval Patel) commit directly to
csl-orig — that is the canonical pattern this repo's history shows
(`DC 10 July 2026`-style commits referencing csl-corrections issues), always
paired with the csl-corrections audit commit.

**Agents and downstream contributors never push directly.** The org rule
(org-root CLAUDE.md, restated here because it is the reason this manual
exists): prepare + XML-validate locally, park each correction in the queue
with **`/cologne-correction-queue`**, and ship everything accumulated as
**ONE consolidated PR at most ~monthly** with **`/cologne-batch-pr`**. No
streams of small PRs, no bot comments — csl-orig is the root of the
dependency graph and noise here multiplies across every dictionary's XML and
every reader-facing site. (Doc-only PRs like the one that added this manual
are the sanctioned exception — they touch no `v02/` text.)

### 3.8 Public refresh

Cron on the live server (`redo_xampp_selective.sh`, marker file
`v02/.xampp_last_run`) picks up new commits and refreshes the site plus the
Stardict/JSON mirrors. Not an operator step unless you run a server.

## 4. The local safety layer (this repo's own tooling)

| Piece | What it does |
|---|---|
| [scripts/install-hooks.sh](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/install-hooks.sh) | One-time per clone: wires `hooks/pre-commit` into git |
| [hooks/pre-commit](https://github.com/sanskrit-lexicon/csl-orig/blob/main/hooks/pre-commit) | On staged `v02/` files: encoding guard + full `generate_dict.sh` smoke-test (fails on red output; hard-blocks if csl-pywork isn't a sibling) |
| [scripts/check_encoding.py](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_encoding.py) | BOM / invalid-UTF-8 / `<L>`↔`<LEND>` balance check on canonical `<dict>.txt` files (aux files deliberately excluded — some are legitimately non-UTF-8). Born from the BOM postmortem (csl-pywork #50/#51) |
| [scripts/check_generate_dict.sh](https://github.com/sanskrit-lexicon/csl-orig/blob/main/scripts/check_generate_dict.sh) | The hook's second stage: per staged dict, run the pipeline and fail on ANSI-red lines |

Layout notes: [v02/](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v02)
= the live corpus (45 dictionary dirs, each `<dict>.txt` + auxiliary files);
[v00/](https://github.com/sanskrit-lexicon/csl-orig/tree/main/v00) = a legacy
remnant (`updateDistinctData.sh`);
[reorg/](https://github.com/sanskrit-lexicon/csl-orig/tree/main/reorg) = the
historical scripts of the one-time v01→v02 reorganization. Neither is part of
the correction workflow.

## 5. Symptom → cause → cure

| Symptom | Cause | Cure |
|---|---|---|
| `hw.py: init_entries Error 2. Not expecting <LEND>` on AP90/MW/BUR | Pre-existing `<LEND>` markers in those dicts' intro sections — not your edit | Ignore for content-only changes; on production the pre-built hw.txt absorbs it |
| Cryptic `hw.py` failure after a bulk edit | UTF-8 BOM written by an editor/`utf-8-sig` | Never `utf-8-sig`; `scripts/check_encoding.py` (and the hook) catches it pre-commit |
| `diff_to_changes_dict.py: files have different number of lines` | Your edit added/removed lines; the `_dict` variant pairs positionally | Use `diff_to_changes.py` |
| Change file applies to the wrong lines | Someone else's correction landed between your snapshot and apply | `git pull`, re-snapshot, rebuild the change file (§3.1) |
| `xmllint: command not found` | xmllint not installed locally | Install libxml2-utils/GnuWin32; ET-parse success is not a full substitute |
| `python3: command not found` in Git Bash | Pipeline scripts call `python3` literally; Windows exposes `python` | Shim it: a `/tmp/pybin/python3` wrapper on PATH (canonical doc §8) |
| CRLF warnings on `git add` | Windows line-ending normalization; `.gitattributes` already handles `*.txt` | Informational — let it through; don't fight autocrlf |
| Hand-edit inside `<outdir>/pywork/` or `web/` disappears | `generate_dict.sh` regenerates from scratch | Move the edit upstream (csl-pywork / csl-websanlexicon) |
| Tempted to open a small PR "just for this one fix" | The no-noise rule exists precisely for this | Queue it (`/cologne-correction-queue`); it ships in the monthly batch |
| Old issue's fix seems obvious but the CFR says `No change` | The proposal was already adjudicated | Stop; only a maintainer reopens decisions (§3.0) |
| Pre-commit hook blocks with "csl-pywork not found" | Sibling layout not in place | Clone csl-pywork beside csl-orig (§1 layout) |

## 6. Glossary

| Term | Meaning |
|---|---|
| canonical text | `v02/<dict>/<dict>.txt` — the one file per dictionary everything derives from |
| change file | Line-addressed edit record: `NNN old …` / `NNN new …` (+ `ins`/`del`), `;` comments |
| audit trail | The AFTER-the-fact change file + readme in `csl-corrections/batch_YYYYMMDD/…` — a record, never a pipeline input |
| CFR | csl-corrections' correction-form registry — the adjudication history checked in the §3.0 preflight |
| correction layer | `{{old->new||YYYYMMDD|author|issue|}}` — inline representation preserving the original reading |
| batched PR | The agent delivery unit: everything queued, ONE consolidated PR ~monthly |
| promote | Copying the corrected temp file over the canonical `<dict>.txt` |
| `printchange.txt` | Per-dict record of intentional divergences from the printed book (print errors only — not for markup fixes) |
| L-number / metaline | `<L>…<pc>…<k1>…<k2>…` — the stable entry id + header line the audit tools track |
| ET parse | `make_xml.py`'s ElementTree pass ("All records parsed by ET") — the first structural gate |

## 7. Maintainer appendix

- **Invariants:** the canonical file only changes through the workflow;
  every csl-orig text commit has a paired csl-corrections audit commit
  (cross-referenced messages); XML validation precedes any commit; the
  agent lane is queue → monthly batch, without exception for "tiny" fixes.
- **Who may do what:** direct commits = Jim/Dhaval (their pattern, visible
  throughout `git log`); everyone else = the batched-PR lane; doc-only
  changes (like this manual) = normal PR, no `v02/` contact.
- **Correction-type routing** (full table in the
  [canonical doc §7](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md)):
  markup/text fixes → this workflow; print errors → also `printchange.txt`;
  link targets → the per-dict `lsfix2.py` pipeline; headword normalization →
  hwnorm1/2; display bugs → csl-websanlexicon; pipeline bugs → csl-pywork.
- **Observed state** (11-07-2026): the hooks are opt-in (`install-hooks.sh`)
  — a fresh clone has no safety net until it is run; `v00/` and `reorg/`
  are historical and unlabelled as such in-tree (this manual is now the
  label). No script defects found — the tooling here is deliberately
  minimal, with the heavy machinery living in csl-pywork.
- **Issue taxonomy:** tooling-repo taxonomy — see
  [CLAUDE.md](https://github.com/sanskrit-lexicon/csl-orig/blob/main/CLAUDE.md);
  correction issues are normally filed on the **dictionary's own repo**, not
  here (2,733 closed issues here are largely the historical intake).

---

_Dr. Mārcis Gasūns_
