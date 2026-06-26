#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stats_etymology.py  --  cross-dictionary statistics + dashboard over the
etymology TSVs produced by the WIL and SKD/VCP analysers.

Covers every dictionary that has a `<dict>_etymology.tsv`:
  * WIL              — English-prose `<ab>E.</ab>` style  (no kāraka)
  * SKD, VCP, AP90, AP, SHS, KRM — Sanskrit-prose kāraka+pratyaya style

Emits CSV summaries + one self-contained HTML dashboard (Chart.js from CDN):
  affix_frequency.csv · karaka_distribution.csv · karaka_x_affix_matrix.csv ·
  group_distribution.csv · affix_entropy.csv · cross_dict_agreement.csv ·
  root_productivity.csv · root_capture.csv · dashboard_etymology.html

    python stats_etymology.py            # auto-detects sibling dict TSVs
"""
import os, sys, csv, json, math, collections

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
V02 = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(V02, 'wil'))
try:
    import analyze_wil_etymology as wil      # affix table: realized surface + function
    wil.load_affix_base()
except Exception:
    wil = None

# dict code -> (relative tsv path, style). Sanskrit-side dicts carry a kāraka.
DICTS = [
    ('WIL',  'wil/wil_etymology.tsv',   'english'),
    ('SKD',  'skd/skd_etymology.tsv',   'sanskrit'),
    ('VCP',  'vcp/vcp_etymology.tsv',   'sanskrit'),
    ('Apte', 'ap90/ap90_etymology.tsv', 'sanskrit'),   # Apte 1890 = the Apte representative
    ('AP',   'ap/ap_etymology.tsv',     'sanskrit'),
    ('SHS',  'shs/shs_etymology.tsv',   'sanskrit'),
    ('KRM',  'krm/krm_etymology.tsv',   'sanskrit'),
    ('MW',   'mw/mw_etymology.tsv',     'mw'),          # root-attribution + parse=
    ('PWG',  'pwg/pwg_etymology.tsv',   'german'),       # "Von {#src#}" derivation
    ('PW',   'pw/pw_etymology.tsv',     'german'),
]
KARAKAS = ['BAve', 'karaRe', 'karmaRi', 'kartari', 'aDikaraRe', 'apAdAne', 'sampradAne']
KSENSE = {'BAve': 'bhāve', 'karaRe': 'karaṇe', 'karmaRi': 'karmaṇi',
          'kartari': 'kartari', 'aDikaraRe': 'adhikaraṇe', 'apAdAne': 'apādāne',
          'sampradAne': 'sampradāne'}


def load():
    data = {}
    for code, rel, style in DICTS:
        p = os.path.join(V02, rel)
        if not os.path.exists(p):
            continue
        rows = list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))
        if style == 'german':       # normalise "source"(is_root) -> root column
            for r in rows:
                if r.get('is_root') == 'True':
                    r['root'], r['root_slp1'] = r.get('source'), r.get('source_slp1')
        data[code] = {'style': style, 'rows': rows,
                      'aff': [r for r in rows if r.get('affix')]}
    return data


# --- DSG (Dictionary of Sanskrit Grammar) deep-links + definitions ----------
# Reuses the vendored dsg.json (K.V. Abhyankar's DSG, ~4400 terms, EN+RU senses,
# keyed by SLP1) from SanskritLexicography; deep-links to samskrtam.ru.
DSG_URL = 'https://samskrtam.ru/sanskrit-lexicon/dsg/#t-{}'
DSG_KARAKA = {'BAve': 'BAva', 'karaRe': 'karaRa', 'karmaRi': 'karman',
              'kartari': 'kartf', 'aDikaraRe': 'aDikaraRa', 'apAdAne': 'apAdAna',
              'sampradAne': 'sampradAna'}
try:
    from indic_transliteration import sanscript
    def iast_to_slp1(s):
        return sanscript.transliterate(s, sanscript.IAST, sanscript.SLP1)
except Exception:
    def iast_to_slp1(s):
        return s


def _short(s, n=240):
    s = (s or '').strip()
    return (s[:n].rsplit(' ', 1)[0] + '…') if len(s) > n else s


def load_dsg():
    """{slp1: {'en':…, 'ru':…}} from the vendored DSG json, or {} if absent."""
    p = os.path.join(V02, '..', '..', 'SanskritLexicography', 'RussianTranslation',
                     'research', 'dsg.json')
    p = os.environ.get('DSG_JSON', os.path.normpath(p))
    out = {}
    if os.path.exists(p):
        for e in json.load(open(p, encoding='utf-8')):
            s = e.get('slp1')
            if s and s not in out and (e.get('en') or e.get('ru')):
                out[s] = {'en': _short(e.get('en')), 'ru': _short(e.get('ru'), 200)}
    return out


def dsg_entry(slp1, defs):
    """{'url':…, 'def':…, 'ru':…} for a term, or None."""
    if not slp1:
        return None
    d = defs.get(slp1, {})
    return {'url': DSG_URL.format(slp1), 'def': d.get('en', ''), 'ru': d.get('ru', '')}


# Whitney's Roots (1885) per-root deep-links, via the WhitneyRoots crosswalk.
WHITNEY_URL = 'https://samskrtam.ru/whitney-roots/{}'


def load_whitney():
    """{root_iast: url} from WhitneyRoots/crosswalk/roots.csv (855 roots)."""
    p = os.path.join(V02, '..', '..', 'WhitneyRoots', 'crosswalk', 'roots.csv')
    p = os.environ.get('WHITNEY_ROOTS', os.path.normpath(p))
    out = {}
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding='utf-8')):
            ia, url = r.get('root_iast'), r.get('warnemyr_url')
            if ia and url and ia not in out:
                out[ia] = WHITNEY_URL.format(url)
    return out


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a binomial proportion, as percentages."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(100 * (centre - half) / d, 1), round(100 * (centre + half) / d, 1))


def write_csv(name, header, rows):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    data = load()
    if not data:
        print("No *_etymology.tsv found under {} — run the analysers first.".format(V02))
        return
    codes = list(data)
    print("Loaded:", ", ".join("{} ({})".format(c, len(data[c]['rows'])) for c in codes))
    sanskrit = [c for c in codes if data[c]['style'] == 'sanskrit']

    affcodes = [c for c in codes if data[c]['aff']]   # dicts that tag affixes

    # 1. affix frequency per dict ------------------------------------------------
    afreq = {c: collections.Counter(r['affix'] for r in data[c]['aff']) for c in affcodes}
    all_affixes = collections.Counter()
    for c in affcodes:
        all_affixes.update(afreq[c])
    top_aff = [a for a, _ in all_affixes.most_common(15)]
    write_csv('affix_frequency.csv', ['affix'] + affcodes,
              [[a] + [afreq[c].get(a, 0) for c in affcodes] for a in top_aff])

    # 2. kāraka distribution (sanskrit-side) ------------------------------------
    kdist = {c: collections.Counter(r['karaka'] for r in data[c]['aff']) for c in sanskrit}
    write_csv('karaka_distribution.csv', ['karaka', 'sense'] + sanskrit,
              [[k, KSENSE[k]] + [kdist[c].get(k, 0) for c in sanskrit] for k in KARAKAS])

    # 3. kāraka × affix matrix (all sanskrit dicts pooled) -----------------------
    pool = [r for c in sanskrit for r in data[c]['aff']]
    mtot = collections.Counter(r['affix'] for r in pool)
    m_aff = [a for a, _ in mtot.most_common(10)]
    cell = collections.Counter((r['affix'], r['karaka']) for r in pool)
    matrix = [[cell.get((a, k), 0) for k in KARAKAS] for a in m_aff]
    write_csv('karaka_x_affix_matrix.csv', ['affix'] + [KSENSE[k] for k in KARAKAS],
              [[a] + row for a, row in zip(m_aff, matrix)])

    # 4. teaching-group distribution per dict ------------------------------------
    groups = sorted({r['group'] for c in affcodes for r in data[c]['aff'] if r.get('group')})
    gdist = {c: collections.Counter(r.get('group') for r in data[c]['aff']) for c in affcodes}
    write_csv('group_distribution.csv', ['group'] + affcodes,
              [[g] + [gdist[c].get(g, 0) for c in affcodes] for g in groups])

    # 5. affix kāraka-spread entropy (sanskrit pool) -----------------------------
    byaff = collections.defaultdict(collections.Counter)
    for r in pool:
        byaff[r['affix']][r['karaka']] += 1
    ent = []
    for a, c in byaff.items():
        tot = sum(c.values())
        if tot < 30:
            continue
        H = -sum((v / tot) * math.log2(v / tot) for v in c.values())
        ent.append((a, round(H, 3), tot))
    ent.sort(key=lambda x: -x[1])
    write_csv('affix_entropy.csv', ['affix', 'entropy_bits', 'n'], ent)

    # 6a. cross-dict AFFIX agreement (headword_slp1 sharing an affix) ------------
    idx = {c: collections.defaultdict(set) for c in affcodes}
    for c in affcodes:
        for r in data[c]['aff']:
            idx[c][r['headword_slp1']].add(r['affix'])
    agree_rows = []
    for i, a in enumerate(affcodes):
        for b in affcodes[i + 1:]:
            common = set(idx[a]) & set(idx[b])
            if not common:
                continue
            ag = sum(1 for h in common if idx[a][h] & idx[b][h])
            lo, hi = wilson(ag, len(common))
            agree_rows.append([a, b, len(common), ag, round(100 * ag / len(common), 1), lo, hi])
    write_csv('cross_dict_agreement.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'affix_agrees', 'pct',
               'ci95_low', 'ci95_high'], agree_rows)

    # 6b. cross-dict ROOT agreement (incl. MW, which gives root not affix) -------
    rootcodes = [c for c in codes if any(r.get('root') for r in data[c]['rows'])]
    def root_index(strict):
        ix = {c: collections.defaultdict(set) for c in rootcodes}
        for c in rootcodes:
            for r in data[c]['rows']:
                if r.get('root') and not (strict and r.get('root_source') == 'nearest-root'):
                    ix[c][r['headword_slp1']].add(r['root'])
        return ix

    def agree_table(ix):
        out = []
        for i, a in enumerate(rootcodes):
            for b in rootcodes[i + 1:]:
                common = set(ix[a]) & set(ix[b])
                if not common:
                    continue
                ag = sum(1 for h in common if ix[a][h] & ix[b][h])
                lo, hi = wilson(ag, len(common))
                out.append([a, b, len(common), ag, round(100 * ag / len(common), 1), lo, hi])
        return out

    root_agree = agree_table(root_index(False))
    write_csv('cross_dict_root_agreement.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'root_agrees', 'pct',
               'ci95_low', 'ci95_high'], root_agree)
    write_csv('cross_dict_root_agreement_strict.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'root_agrees', 'pct',
               'ci95_low', 'ci95_high'], agree_table(root_index(True)))

    # 7. root productivity (verbal-root dicts only: sanskrit-side + MW) ----------
    # WIL is excluded: its "root" is the first etymon (often a prefix), not a dhātu.
    prodcodes = [c for c in rootcodes if data[c]['style'] != 'english']
    rootc = collections.Counter(
        r['root'] for c in prodcodes for r in data[c]['rows'] if r.get('root'))
    write_csv('root_productivity.csv', ['root', 'derivatives'], rootc.most_common(20))

    # 8. root-capture breakdown (sanskrit-side; WIL has no root_source) -----------
    cap_rows = []
    for c in sanskrit:
        rs = collections.Counter(r.get('root_source') or 'empty' for r in data[c]['rows'])
        n = len(data[c]['rows'])
        rooted = n - rs.get('empty', 0)
        # strict = high-precision subset: drop the ~66-75% nearest-root tier
        strict = rooted - rs.get('nearest-root', 0)
        cap_rows.append([c, n, rs.get('local', 0), rs.get('headword-root', 0),
                         rs.get('nearest-root', 0), rs.get('dhatupatha-join', 0),
                         rs.get('oracle-join', 0), rs.get('llm-pass', 0),
                         rs.get('empty', 0),
                         round(100 * rooted / max(1, n), 1),
                         round(100 * strict / max(1, n), 1)])
    write_csv('root_capture.csv',
              ['dict', 'derivations', 'local', 'headword_root', 'nearest_root',
               'dhatupatha_join', 'oracle_join', 'llm_pass', 'empty',
               'pct_with_root', 'pct_strict'], cap_rows)

    # ---- DSG deep-links + definitions for every affix / kāraka shown ----------
    dsg_defs = load_dsg()
    dsg = {}
    for a in set(m_aff) | {e[0] for e in ent[:10]} | set(top_aff):
        dsg['aff:' + a] = dsg_entry(iast_to_slp1(a), dsg_defs)
    for k in KARAKAS:
        dsg['kar:' + KSENSE[k]] = dsg_entry(DSG_KARAKA.get(k), dsg_defs)
    print("DSG definitions wired: {} of {} terms have a gloss".format(
        sum(1 for v in dsg.values() if v and v['def']), len(dsg)))

    # ---- Whitney's Roots deep-links for the productivity chart -----------------
    whit_all = load_whitney()
    whitney = {r[0]: whit_all[r[0]] for r in rootc.most_common(15) if r[0] in whit_all}
    print("Whitney root links: {} of top-15 roots linked".format(len(whitney)))

    # ---- legend: Sanskrit affix -> IAST surface suffix · English · Russian ----
    legend = []
    for a in m_aff + [e[0] for e in ent[:10]]:
        if any(row[0] == a for row in legend):
            continue
        slp1 = iast_to_slp1(a)
        rec = wil.AFFIXES.get(a) if wil else None
        surface = '-' + rec[0] if rec and rec[0] else ('∅' if rec else '')
        func = rec[2] if rec else ''
        ru = dsg_defs.get(slp1, {}).get('ru', '')
        legend.append([a, surface, func, ru, DSG_URL.format(slp1)])

    # ---- dashboard ------------------------------------------------------------
    payload = {
        'codes': codes, 'sanskrit': sanskrit, 'prod': prodcodes,
        'perdict': {c: len(data[c]['rows']) for c in codes},
        'heat': {'affixes': m_aff, 'karakas': [KSENSE[k] for k in KARAKAS],
                 'matrix': matrix, 'rowtot': [mtot[a] for a in m_aff]},
        'entropy': ent[:10],
        'agreement': agree_rows,
        'root_agreement': root_agree,
        'roots': rootc.most_common(15),
        'karaka_dist': [[KSENSE[k]] + [kdist[c].get(k, 0) for c in sanskrit] for k in KARAKAS],
        'capture': cap_rows,
        'dsg': dsg, 'legend': legend, 'whitney': whitney,
    }
    payload['files'] = {code: os.path.basename(rel) for code, rel, _s in DICTS if code in data}
    html = DASHBOARD.replace('/*DATA*/', json.dumps(payload, ensure_ascii=False))
    out = os.path.join(HERE, 'dashboard_etymology.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print("Wrote 9 CSVs + dashboard_etymology.html to {}".format(HERE))
    print("Sanskrit-side dicts (with kāraka):", ", ".join(sanskrit))


DASHBOARD = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cologne etymology — cross-dictionary statistics</title>
<style>
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:1020px;margin:0 auto;padding:24px;color:#1a1a19;background:#fcfcfb}
 h1{font-size:22px;font-weight:500} h2{font-size:18px;font-weight:500;margin-top:34px;border-top:1px solid #e1e0d9;padding-top:18px}
 p{color:#52514e;line-height:1.6;font-size:14px} a{color:#185fa5}
 .dl{font-size:12px;font-weight:400;margin-left:10px}
 .cards{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
 .card{background:#f1efe8;border-radius:8px;padding:10px 14px;min-width:84px;text-decoration:none;color:inherit;display:block}
 .card:hover{background:#e7e4d8} .card .n{font-size:22px;font-weight:500} .card .l{font-size:12px;color:#185fa5}
 table{border-collapse:collapse;font-size:13px;width:100%} td,th{padding:6px 8px;text-align:left;border-bottom:0.5px solid #e1e0d9}
 th{color:#52514e;font-weight:500}
 .hm{display:grid;gap:3px;font-size:12px;margin-top:8px} .hm>div{padding:8px 4px;text-align:center;border-radius:3px}
 .hm a{color:inherit;text-decoration:none;cursor:pointer}
 .gloss{border-bottom:1px dotted #888;cursor:help;text-decoration:none;color:inherit;font-style:italic}
 .bars{display:flex;flex-direction:column;gap:4px;margin-top:8px}
 .bar{display:grid;grid-template-columns:74px 1fr 56px;align-items:center;gap:8px;font-size:13px}
 .bar .track{height:18px;border-radius:3px} .bar .v{color:#52514e;font-variant-numeric:tabular-nums}
 .src{font-size:12px;color:#888;margin:14px 0 4px} code{background:#f1efe8;padding:1px 4px;border-radius:3px}
 .read{font-size:13px;background:#eef4ec;border-left:3px solid #1baf7a;border-radius:0 6px 6px 0;padding:8px 12px;margin:8px 0}
 .read b{color:#0f6e56} .read .ex{display:block;margin-top:4px}
 .cant{font-size:13px;color:#7a3b1d;background:#faece7;border-left:3px solid #d85a30;border-radius:0 6px 6px 0;padding:8px 12px;margin:8px 0}
</style></head><body>
<h1>Cologne dictionaries — Pāṇinian derivation statistics</h1>
<p>Every chart links to the data behind it. <b>Affix &amp; kāraka labels link to their definition</b> in the
<a href="https://samskrtam.ru/sanskrit-lexicon/dsg/">Dictionary of Sanskrit Grammar</a> (hover for the gloss).
Generated from the <code>*_etymology.tsv</code> extractions across 10 dictionaries.</p>

<h2>What we see</h2>
<p><b>Kāraka is a fingerprint of each dictionary's purpose.</b> Overall <i>bhāve</i> (action / abstract noun)
dominates, but <b>KRM inverts this</b> — <i>kartari</i> 227 ≫ <i>bhāve</i> 30 — because the Kṛdanta-rūpa-mālā is
built around agent-derivatives. The kāraka mix tells you what a dictionary is <i>for</i>.</p>
<p><b>The kāraka × pratyaya grid is textbook-clean Pāṇini.</b> <i>lyuṭ</i> → bhāve + karaṇe (the <code>-ana</code>
action / instrument nouns); <i>kta</i> spreads across bhāve / karmaṇi / kartari — exactly the past participle's
three readings; <i>ghañ</i> → bhāve; <i>lyu</i> is pure kartari.</p>
<p><b>Affix polysemy is quantified by entropy.</b> Generalists (<i>ḍa</i>, <i>anīyar</i>, <i>ac</i> ≈ 2 bits) form
almost any kāraka; specialists (<i>lyu</i> 0.33, <i>ṣṭran</i>, <i>aṅ</i>) do one job — directly pedagogical.</p>
<p><b>Root productivity follows corpus frequency</b> (<i>kṛ</i> ≫ <i>bhū</i> > <i>i</i>, <i>dhā</i>, <i>gam</i>),
and <b>the traditions agree</b>: <span id="hl"></span> A cascade of root-recovery tiers — local citation, KRM's
head-word-is-the-root, a cross-dict oracle (incl. KRM's 60k-form paradigm), and a DeepSeek pass over the
residual, every fill validated against the canonical dhātu list — lifts the empty-root tail to near-complete
(VCP 20 → 97 %, SHS → 95 %).</p>

<h2>Download the data</h2>
<p id="dl-dicts">Per-dictionary derivations (TSV): </p>
<p id="dl-csv">Summary tables (CSV): </p>

<h2>Per-dictionary counts <a class="dl" id="dlcards"></a></h2>
<p>Each card links to that dictionary's full derivation TSV.</p>
<div class="cards" id="cards"></div>

<h2>Kāraka × pratyaya (Sanskrit-side, pooled) <a class="dl" href="karaka_x_affix_matrix.csv">⤓ CSV</a></h2>
<p>Each <b>row</b> is a primary affix (pratyaya); each <b>column</b> is a kāraka — the grammatical role the
derived word plays in its root's action (the doer, the instrument, the object, or the bare action itself).
A <b>cell</b> counts how many extracted derivations, pooled across the six Sanskrit-prose dictionaries, use
that affix in that kāraka sense; darker means more. The <b>row total</b> on the right is the affix's overall
frequency, so reading along a row shows how one affix divides its labour across senses, and reading down a
column shows which affixes compete to express one relation. This grid exists <i>only</i> because the
Sanskrit-side dictionaries spell the kāraka out in the entry (<code>BAve GaY</code> = "in the bhāva sense,
affix ghañ"); WIL, MW and the German dictionaries never state it, so they contribute nothing here. Row and
column labels link to their definition in the Dictionary of Sanskrit Grammar.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① The <i>lyuṭ</i> × <i>bhāve</i> cell (1005) — ghañ-style action nouns in <code>-ana</code> are formed in the "the act of" sense ~1000× (e.g. <i>karaṇa</i> "doing"); it is lyuṭ's single commonest job.</span>
<span class="ex">② The <i>kta</i> row lights three columns at once (bhāve · karmaṇi · kartari) — the past participle is read as the action, the object, or the agent by context (<i>kṛta</i> = "the doing / the deed / the doer").</span></div>
<div class="cant"><b>Can't tell you:</b> this is a population view — it counts attestations of an affix-in-a-kāraka, not whether a <i>particular</i> word is unambiguous (a form like <i>gata</i> legitimately sits in two cells). And it cannot compare the English/German dicts, which are blank by construction, not by absence of derivation.</div>
<div id="heat"></div>

<h2>Affix kāraka-spread (entropy) <a class="dl" href="affix_entropy.csv">⤓ CSV</a></h2>
<p>Each bar is the <b>Shannon entropy</b>, in bits, of one affix's distribution across the seven kārakas —
a single number answering "how many different jobs does this affix do?" Zero bits means the affix only ever
forms one kāraka (a pure specialist); the theoretical maximum (~2.8 bits) would mean it spreads perfectly
evenly over all seven. High-entropy affixes are <b>semantic generalists</b> — the affix alone tells you almost
nothing about the meaning, so you must read the gloss; low-entropy affixes are <b>specialists</b> that pin the
sense by themselves. The entropy is computed only over the Sanskrit-side derivations that carry a kāraka, so
the count it rests on (the <code>n</code> column in the CSV) matters as much as the bits. Affix labels link to
their full grammar definition.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>lyu</i> at 0.33 bits is a pure specialist — see it and you know the word is an agent (kartari): <i>kāraka</i> "doer".</span>
<span class="ex">② <i>ac</i> at 1.84 bits over n=411 is a generalist — the bare affix predicts almost nothing; <i>-a</i> nouns can be agent, action, object or instrument, so you must consult the entry.</span></div>
<div class="cant"><b>Can't tell you:</b> entropy measures <i>spread</i>, not productivity or correctness — a rare affix with two even senses outscores a hugely productive affix that has one dominant sense plus a long tail. Always read it next to <code>n</code> and the heatmap; a high bar on a tiny <code>n</code> is noise.</div>
<div class="bars" id="ent"></div>

<h2>Root productivity <a class="dl" href="root_productivity.csv">⤓ CSV</a></h2>
<p>Each bar counts how many <b>distinct derived words</b> trace back to that root across the verbal-root
dictionaries (the Sanskrit-side dicts + MW + PWG/PW; WIL is excluded because its "root" is the first etymon,
often a prefix). It is a measure of <b>derivational fertility</b> — which roots seed the most vocabulary in the
recorded lexicon. The ranking tracks corpus frequency closely but is not the same thing: it counts dictionary
<i>head-words</i>, not running corpus tokens. <b>Click any root to open its full entry</b> — paradigms,
attested forms and primary derivatives — in Whitney's <i>The Roots, Verb-Forms and Primary Derivatives of the
Sanskrit Language</i> (1885) on samskrtam.ru.</p>
<p id="rootnote" style="font-size:13px;color:#888"></p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>kṛ</i> "do / make" tops the list — the most fertile root in the language, seeding <i>kṛta, karaṇa, kartṛ, kārya, kriyā…</i>; click it to see the whole Whitney paradigm.</span>
<span class="ex">② <i>i</i> "go" ranks near the top despite being a single short vowel — the oldest, shortest roots are disproportionately productive, a real signal about the age-vs-fertility relationship.</span></div>
<div class="cant"><b>Can't tell you:</b> the counts are inflated by <i>coverage</i>, not only real productivity — a root recorded in more of the ten dictionaries accrues more derivatives, and two homonymous roots (e.g. the two √vid "know" / "find") may be merged into one bar. It is a lexicon count, never a corpus frequency.</div>
<div class="bars" id="roots"></div>

<h2>Cross-dictionary affix agreement <a class="dl" href="cross_dict_agreement.csv">⤓ CSV</a></h2>
<p>Take every head-word that <b>two</b> dictionaries both analyse with an affix, and ask: do they choose the
<i>same</i> affix? The percentage is the share that agree; the bracket is the <b>95% Wilson confidence
interval</b>, which widens sharply when only a few head-words are shared. This is a direct test of whether two
lexicographic traditions reconstruct the same Pāṇinian derivation for the same word — a consistency check that
no single dictionary can give you. Rows are sorted by the number of shared head-words, so the most evidentially
solid comparisons sit at the top.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>Apte↔AP</i> 100% [97.9–100] over 178 shared head-words — the two Apte editions are essentially identical, exactly the sanity check you'd want.</span>
<span class="ex">② <i>WIL↔SKD</i> 22.9% [14.6–34.0] — Wilson and the Śabdakalpadruma pick the same affix barely a fifth of the time, and the interval tops out at 34%, below every Sanskrit-side pair, so the gap is real, not small-sample noise.</span></div>
<div class="cant"><b>Can't tell you:</b> it scores only head-words that <i>both</i> dicts root with an affix — it is silent on coverage gaps (a word one dict omits never enters the comparison), and a tidy 100% over n=5 is weak evidence. Always read the CI and the shared-count together.</div>
<table id="agree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>affix agrees</th><th>% (95% CI)</th></tr></thead><tbody></tbody></table>

<h2>Cross-dictionary root agreement <a class="dl" href="cross_dict_root_agreement.csv">⤓ CSV</a></h2>
<p>The same comparison, but on the <b>root</b> instead of the affix — so it can include the dictionaries that
attribute a root without naming a pratyaya: MW (via its <code>√</code> notation and <code>parse=</code> field)
and the German PWG/PW (via "Wurzel" / "von"). Root agreement runs lower than affix agreement, but that is a
measurement artefact, not real disagreement: the same root is written in different transliterations and
homonym conventions across traditions, so a "miss" is often two spellings of one dhātu, not a genuine dispute.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>PWG↔PW</i> ~93% — the two German Petersburg dictionaries, same school, agree on the root almost always.</span>
<span class="ex">② <i>MW↔PWG</i> ~65% — the English √-tradition and the German Wurzel-tradition independently land on the same root for two-thirds of shared head-words, a strong cross-tradition validation given the script differences.</span></div>
<div class="cant"><b>Can't tell you:</b> a low cell here may be a transliteration/homonym mismatch rather than a real conflict; treat root agreement as a <i>lower bound</i> on true agreement, and the affix table above as the cleaner signal.</div>
<table id="ragree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>root agrees</th><th>% (95% CI)</th></tr></thead><tbody></tbody></table>

<h2>Affix legend (Sanskrit → surface · function · Russian)</h2>
<p>The Sanskrit affix names (<i>ghañ</i>, <i>lyuṭ</i>…) are opaque until you strip their mute markers
(anubandhas). This table gives, for each affix shown above: its <b>IAST surface suffix</b> — what actually
attaches to the stem once the markers fall away — its <b>English function</b>, and the <b>Russian gloss</b>
from the Dictionary of Sanskrit Grammar. The affix name links to its full DSG entry. Use it as a key while
reading the heatmap and entropy charts.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>ghañ</i> → <code>-a</code>, "action/result noun" — drop the <i>gh</i> and <i>ñ</i> markers and the affix is just <code>-a</code>; it makes a bhāva noun (<i>pāka</i> "cooking").</span>
<span class="ex">② <i>lyuṭ</i> → <code>-ana</code> — the <i>l</i> and <i>ṭ</i> are mute; the real suffix is <code>-ana</code> (<i>gamana</i> "going").</span></div>
<div class="cant"><b>Can't tell you:</b> the surface is the affix <i>in isolation</i> — sandhi and root-gradation reshape the actual word (<i>kṛ</i> + lyuṭ → <i>karaṇa</i>, not <i>kṛ-ana</i>). The legend names the building block, not the finished form.</div>
<table id="legend"><thead><tr><th>affix</th><th>surface</th><th>English function</th><th>Russian (DSG)</th></tr></thead><tbody></tbody></table>

<h2>Root-capture coverage <a class="dl" href="root_capture.csv">⤓ CSV</a></h2>
<p>Not every extracted derivation comes with its root sitting beside it; this table shows, per dictionary,
<b>how</b> the root was recovered, tier by tier. <i>local</i> = the root sat next to the derivation marker;
<i>headword-root</i> = the dictionary is organised by root so the head-word <i>is</i> the dhātu;
<i>nearest-root</i> = the nearest known dhātu in a citation context; <i>dhātupāṭha-join</i> and
<i>oracle-join</i> = filled by look-up against the canonical dhātu list and the cross-dictionary root oracle.
The final column is the share of derivations that ended up with <i>a</i> root.</p>
<div class="read"><b>Read it:</b>
<span class="ex">① <i>KRM</i> is 100%, entirely via <i>headword-root</i> — it is a root dictionary, so every derivation's root is just the entry head-word.</span>
<span class="ex">② <i>VCP</i> reaches 97% as a stack: 2263 local + 532 nearest-root + 363 oracle-join + 361 DeepSeek llm-pass, leaving only 117 empty — read the row left-to-right to see each tier's contribution.</span></div>
<div class="cant"><b>Can't tell you:</b> the percentage is "has <i>a</i> root", not "has the <i>correct</i> root" — the nearest-root and oracle tiers are dhātu-list-validated but not hand-checked. Sample them with <code>sample_nearest_root_audit.py</code> before trusting a single fill.</div>
<table id="cap"><thead><tr><th>dict</th><th>derivations</th><th>local</th><th>headword-root</th><th>nearest-root</th><th>dhātupāṭha-join</th><th>oracle-join</th><th>llm-pass</th><th>empty</th><th>% rooted</th><th>% strict</th></tr></thead><tbody></tbody></table>
<p style="font-size:13px;color:#888"><b>% strict</b> drops the <i>nearest-root</i> tier (the one sub-~100% tier, ~66–75% precise) to leave a near-100%-precision subset — the column to cite for headline tables. Filter the TSVs by <code>root_source != nearest-root</code> to reproduce it.</p>
<p class="src">DSG definitions © K. V. Abhyankar, <i>A Dictionary of Sanskrit Grammar</i>, via
<a href="https://samskrtam.ru/sanskrit-lexicon/dsg/">samskrtam.ru</a>. Data + code:
<a href="https://github.com/sanskrit-lexicon/csl-orig/tree/master/v02/etymology_stats">csl-orig/v02/etymology_stats</a>.</p>

<script>
const D=/*DATA*/;
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
// affix / kāraka label -> DSG link + tooltip
function gloss(kind,label){const e=D.dsg&&D.dsg[kind+':'+label];
 if(e&&e.url){const t=e.def?` title="${esc(e.def)}"`:'';return `<a class="gloss" href="${e.url}"${t}>${esc(label)}</a>`;}
 return `<i>${esc(label)}</i>`;}
const CSVS=['karaka_x_affix_matrix','affix_entropy','affix_frequency','karaka_distribution','group_distribution','cross_dict_agreement','cross_dict_root_agreement','root_productivity','root_capture'];

// download links
document.getElementById('dl-dicts').insertAdjacentHTML('beforeend',
 D.codes.map(c=>`<a href="${D.files[c]}">${c}</a>`).join(' · '));
document.getElementById('dl-csv').insertAdjacentHTML('beforeend',
 CSVS.map(f=>`<a href="${f}.csv">${f}</a>`).join(' · '));

// cards -> per-dict TSV
const cards=document.getElementById('cards');
D.codes.forEach(c=>cards.insertAdjacentHTML('beforeend',
 `<a class="card" href="${D.files[c]}"><div class="n">${D.perdict[c].toLocaleString()}</div><div class="l">${c} ⤓</div></a>`));

// heatmap
const H=D.heat, max=Math.max(...H.matrix.flat());
function col(v){const t=Math.sqrt(v/max);const a=[230,241,251],b=[24,95,165];return `rgb(${Math.round(a[0]+(b[0]-a[0])*t)},${Math.round(a[1]+(b[1]-a[1])*t)},${Math.round(a[2]+(b[2]-a[2])*t)})`;}
const grid=document.createElement('div');grid.className='hm';
grid.style.gridTemplateColumns=`66px repeat(${H.karakas.length},1fr) 52px`;
grid.insertAdjacentHTML('beforeend','<div></div>'+H.karakas.map(k=>`<div style="color:#52514e;font-size:11px">${gloss('kar',k)}</div>`).join('')+'<div style="color:#52514e">total</div>');
H.affixes.forEach((a,i)=>{
 grid.insertAdjacentHTML('beforeend',`<div style="text-align:left;align-self:center">${gloss('aff',a)}</div>`);
 H.matrix[i].forEach((v,j)=>{const t=Math.sqrt(v/max);
  grid.insertAdjacentHTML('beforeend',`<div title="${esc(a)} × ${esc(H.karakas[j])} = ${v} derivations" style="background:${col(v)};color:${t>0.55?'#fff':'#042C53'}${v===0?';opacity:.4':''}">${v||''}</div>`);});
 grid.insertAdjacentHTML('beforeend',`<div style="color:#52514e;align-self:center">${H.rowtot[i]}</div>`);
});
document.getElementById('heat').appendChild(grid);

// HTML bar lists (clickable, data in the DOM)
function bars(el,rows,maxv,color,labelKind,whit){
 document.getElementById(el).innerHTML=rows.map(r=>{
  let lab;
  if(labelKind) lab=gloss(labelKind,r[0]);
  else if(whit&&whit[r[0]]) lab=`<a class="gloss" style="font-style:normal" href="${whit[r[0]]}" title="open √${esc(r[0])} in Whitney's Roots (1885)">${esc(r[0])}</a>`;
  else lab=`<i>${esc(r[0])}</i>`;
  const w=Math.max(2,100*r[1]/maxv);
  return `<div class="bar"><span>${lab}</span><span class="track" style="width:${w}%;background:${color}"></span><span class="v">${r[1]}</span></div>`;
 }).join('');
}
bars('ent',D.entropy.map(e=>[e[0],e[1]]),Math.max(...D.entropy.map(e=>e[1])),'#2a78d6','aff');
bars('roots',D.roots,Math.max(...D.roots.map(r=>r[1])),'#1baf7a',null,D.whitney);
document.getElementById('rootnote').insertAdjacentHTML('beforeend',
 ` Pool: ${D.prod.join(', ')} (WIL excluded — its "root" is the first etymon, not a dhātu).`);

const ci=r=>`${r[4]}% <span style="color:#888">[${r[5]}–${r[6]}]</span>`;
const at=document.querySelector('#agree tbody');
D.agreement.sort((a,b)=>b[2]-a[2]).forEach(r=>at.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${ci(r)}</td></tr>`));
const rat=document.querySelector('#ragree tbody');
(D.root_agreement||[]).sort((a,b)=>b[2]-a[2]).forEach(r=>rat.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${ci(r)}</td></tr>`));
const ct=document.querySelector('#cap tbody');
D.capture.forEach(r=>ct.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td>${r[5]}</td><td>${r[6]}</td><td>${r[7]}</td><td>${r[8]}</td><td>${r[9]}%</td><td style="font-weight:500">${r[10]}%</td></tr>`));

// affix legend (surface · function · Russian), affix links to DSG
const lt=document.querySelector('#legend tbody');
(D.legend||[]).forEach(r=>lt.insertAdjacentHTML('beforeend',
 `<tr><td><a class="gloss" href="${r[4]}" style="font-style:normal">${esc(r[0])}</a></td><td><code>${esc(r[1])}</code></td><td>${esc(r[2])}</td><td style="color:#52514e">${esc(r[3])}</td></tr>`));

// headline agreement numbers, injected live
const f=(a,b)=>{const r=(D.agreement||[]).find(x=>(x[0]==a&&x[1]==b)||(x[0]==b&&x[1]==a));return r?`${r[4]}% [${r[5]}–${r[6]}]`:'';};
const hl=document.getElementById('hl');
if(hl)hl.innerHTML=`SKD↔VCP ${f('SKD','VCP')} affix agreement vs Wilson↔SKD ${f('WIL','SKD')} — the Sanskrit-tradition block is internally consistent while Wilson 1832 is the disjoint outlier.`;
</script></body></html>
"""


if __name__ == '__main__':
    main()
