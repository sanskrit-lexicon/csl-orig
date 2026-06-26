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


def load_dsg():
    """{slp1: short_en_def} from the vendored DSG json, or {} if absent."""
    p = os.path.join(V02, '..', '..', 'SanskritLexicography', 'RussianTranslation',
                     'research', 'dsg.json')
    p = os.environ.get('DSG_JSON', os.path.normpath(p))
    out = {}
    if os.path.exists(p):
        for e in json.load(open(p, encoding='utf-8')):
            s = e.get('slp1')
            en = (e.get('en') or '').strip()
            if s and en and s not in out:
                short = en[:240].rsplit(' ', 1)[0]
                out[s] = short + ('…' if len(en) > 240 else '')
    return out


def dsg_entry(slp1, defs):
    """{'url':…, 'def':…} for a term, or None."""
    if not slp1:
        return None
    return {'url': DSG_URL.format(slp1), 'def': defs.get(slp1, '')}


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
    ridx = {c: collections.defaultdict(set) for c in rootcodes}
    for c in rootcodes:
        for r in data[c]['rows']:
            if r.get('root'):
                ridx[c][r['headword_slp1']].add(r['root'])
    root_agree = []
    for i, a in enumerate(rootcodes):
        for b in rootcodes[i + 1:]:
            common = set(ridx[a]) & set(ridx[b])
            if not common:
                continue
            ag = sum(1 for h in common if ridx[a][h] & ridx[b][h])
            lo, hi = wilson(ag, len(common))
            root_agree.append([a, b, len(common), ag, round(100 * ag / len(common), 1), lo, hi])
    write_csv('cross_dict_root_agreement.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'root_agrees', 'pct',
               'ci95_low', 'ci95_high'], root_agree)

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
        cap_rows.append([c, n, rs.get('local', 0), rs.get('headword-root', 0),
                         rs.get('nearest-root', 0), rs.get('dhatupatha-join', 0),
                         rs.get('empty', 0),
                         round(100 * (n - rs.get('empty', 0)) / max(1, n), 1)])
    write_csv('root_capture.csv',
              ['dict', 'derivations', 'local', 'headword_root', 'nearest_root',
               'dhatupatha_join', 'empty', 'pct_with_root'], cap_rows)

    # ---- DSG deep-links + definitions for every affix / kāraka shown ----------
    dsg_defs = load_dsg()
    dsg = {}
    for a in set(m_aff) | {e[0] for e in ent[:10]} | set(top_aff):
        dsg['aff:' + a] = dsg_entry(iast_to_slp1(a), dsg_defs)
    for k in KARAKAS:
        dsg['kar:' + KSENSE[k]] = dsg_entry(DSG_KARAKA.get(k), dsg_defs)
    print("DSG definitions wired: {} of {} terms have a gloss".format(
        sum(1 for v in dsg.values() if v and v['def']), len(dsg)))

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
        'dsg': dsg,
    }
    payload['files'] = {code: os.path.basename(rel) for code, rel, _s in DICTS if code in data}
    html = DASHBOARD.replace('/*DATA*/', json.dumps(payload, ensure_ascii=False))
    out = os.path.join(HERE, 'dashboard_etymology.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print("Wrote 8 CSVs + dashboard_etymology.html to {}".format(HERE))
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
</style></head><body>
<h1>Cologne dictionaries — Pāṇinian derivation statistics</h1>
<p>Every chart links to the data behind it. <b>Affix &amp; kāraka labels link to their definition</b> in the
<a href="https://samskrtam.ru/sanskrit-lexicon/dsg/">Dictionary of Sanskrit Grammar</a> (hover for the gloss).
Generated from the <code>*_etymology.tsv</code> extractions across 10 dictionaries.</p>

<h2>Download the data</h2>
<p id="dl-dicts">Per-dictionary derivations (TSV): </p>
<p id="dl-csv">Summary tables (CSV): </p>

<h2>Per-dictionary counts <a class="dl" id="dlcards"></a></h2>
<p>Each card links to that dictionary's full derivation TSV.</p>
<div class="cards" id="cards"></div>

<h2>Kāraka × pratyaya (Sanskrit-side, pooled) <a class="dl" href="karaka_x_affix_matrix.csv">⤓ CSV</a></h2>
<p>Which affix derives a word in which kāraka sense. Darker = more derivations. Row = affix, column = kāraka —
both clickable to their grammar definition. Only the Sanskrit dictionaries state the kāraka.</p>
<div id="heat"></div>

<h2>Affix kāraka-spread (entropy) <a class="dl" href="affix_entropy.csv">⤓ CSV</a></h2>
<p>How many distinct kāraka senses one affix forms. High = a generalist affix; low = specialised
(e.g. <i>lyu</i> → agent only). Click an affix for its definition.</p>
<div class="bars" id="ent"></div>

<h2>Root productivity <a class="dl" href="root_productivity.csv">⤓ CSV</a></h2>
<p id="rootnote">Roots with the most derivatives, pooled across the verbal-root dictionaries.</p>
<div class="bars" id="roots"></div>

<h2>Cross-dictionary affix agreement <a class="dl" href="cross_dict_agreement.csv">⤓ CSV</a></h2>
<p>For head-words shared by two dictionaries (both giving an affix), how often the affix agrees, with 95% CI.
The Sanskrit-tradition dicts cluster at 90–100%; Wilson 1832 is the outlier.</p>
<table id="agree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>affix agrees</th><th>% (95% CI)</th></tr></thead><tbody></tbody></table>

<h2>Cross-dictionary root agreement <a class="dl" href="cross_dict_root_agreement.csv">⤓ CSV</a></h2>
<p>Same, on the root. Includes MW (root-attribution + <code>parse=</code>) and PWG/PW (German "Wurzel").</p>
<table id="ragree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>root agrees</th><th>% (95% CI)</th></tr></thead><tbody></tbody></table>

<h2>Root-capture coverage <a class="dl" href="root_capture.csv">⤓ CSV</a></h2>
<table id="cap"><thead><tr><th>dict</th><th>derivations</th><th>local</th><th>headword-root</th><th>nearest-root</th><th>dhātupāṭha-join</th><th>empty</th><th>% with root</th></tr></thead><tbody></tbody></table>
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
function bars(el,rows,maxv,color,labelKind){
 document.getElementById(el).innerHTML=rows.map(r=>{
  const lab=labelKind?gloss(labelKind,r[0]):`<i>${esc(r[0])}</i>`;
  const w=Math.max(2,100*r[1]/maxv);
  return `<div class="bar"><span>${lab}</span><span class="track" style="width:${w}%;background:${color}"></span><span class="v">${r[1]}</span></div>`;
 }).join('');
}
bars('ent',D.entropy.map(e=>[e[0],e[1]]),Math.max(...D.entropy.map(e=>e[1])),'#2a78d6','aff');
bars('roots',D.roots,Math.max(...D.roots.map(r=>r[1])),'#1baf7a',null);
document.getElementById('rootnote').insertAdjacentHTML('beforeend',
 ` Pool: ${D.prod.join(', ')} (WIL excluded — its "root" is the first etymon, not a dhātu).`);

const ci=r=>`${r[4]}% <span style="color:#888">[${r[5]}–${r[6]}]</span>`;
const at=document.querySelector('#agree tbody');
D.agreement.sort((a,b)=>b[2]-a[2]).forEach(r=>at.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${ci(r)}</td></tr>`));
const rat=document.querySelector('#ragree tbody');
(D.root_agreement||[]).sort((a,b)=>b[2]-a[2]).forEach(r=>rat.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${ci(r)}</td></tr>`));
const ct=document.querySelector('#cap tbody');
D.capture.forEach(r=>ct.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td>${r[5]}</td><td>${r[6]}</td><td>${r[7]}%</td></tr>`));
</script></body></html>
"""


if __name__ == '__main__':
    main()
