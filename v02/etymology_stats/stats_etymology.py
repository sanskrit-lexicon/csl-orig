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
            agree_rows.append([a, b, len(common), ag, round(100 * ag / len(common), 1)])
    write_csv('cross_dict_agreement.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'affix_agrees', 'pct'], agree_rows)

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
            root_agree.append([a, b, len(common), ag, round(100 * ag / len(common), 1)])
    write_csv('cross_dict_root_agreement.csv',
              ['dict_a', 'dict_b', 'shared_headwords', 'root_agrees', 'pct'], root_agree)

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
        cap_rows.append([c, n, rs.get('local', 0), rs.get('dhatupatha-join', 0),
                         rs.get('gana-backref', 0), rs.get('empty', 0),
                         round(100 * (n - rs.get('empty', 0)) / max(1, n), 1)])
    write_csv('root_capture.csv',
              ['dict', 'derivations', 'local', 'dhatupatha_join', 'gana_backref',
               'empty', 'pct_with_root'], cap_rows)

    # ---- dashboard ------------------------------------------------------------
    payload = {
        'codes': codes, 'sanskrit': sanskrit,
        'perdict': {c: len(data[c]['rows']) for c in codes},
        'heat': {'affixes': m_aff, 'karakas': [KSENSE[k] for k in KARAKAS],
                 'matrix': matrix, 'rowtot': [mtot[a] for a in m_aff]},
        'entropy': ent[:10],
        'agreement': agree_rows,
        'root_agreement': root_agree,
        'roots': rootc.most_common(15),
        'karaka_dist': [[KSENSE[k]] + [kdist[c].get(k, 0) for c in sanskrit] for k in KARAKAS],
        'capture': cap_rows,
    }
    html = DASHBOARD.replace('/*DATA*/', json.dumps(payload, ensure_ascii=False))
    out = os.path.join(HERE, 'dashboard_etymology.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print("Wrote 8 CSVs + dashboard_etymology.html to {}".format(HERE))
    print("Sanskrit-side dicts (with kāraka):", ", ".join(sanskrit))


DASHBOARD = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cologne etymology — cross-dictionary statistics</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:0 auto;padding:24px;color:#1a1a19;background:#fcfcfb}
 h1{font-size:22px;font-weight:500} h2{font-size:18px;font-weight:500;margin-top:36px;border-top:1px solid #e1e0d9;padding-top:20px}
 p{color:#52514e;line-height:1.6;font-size:14px} .cards{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
 .card{background:#f1efe8;border-radius:8px;padding:10px 14px;min-width:90px}
 .card .n{font-size:24px;font-weight:500} .card .l{font-size:12px;color:#52514e}
 table{border-collapse:collapse;font-size:13px;width:100%} td,th{padding:6px 8px;text-align:left;border-bottom:0.5px solid #e1e0d9}
 th{color:#52514e;font-weight:500} .hm{display:grid;gap:3px;font-size:12px;margin-top:8px}
 .hm div{padding:8px 4px;text-align:center;border-radius:3px} .cw{position:relative;height:340px}
 i{font-style:italic}
</style></head><body>
<h1>Cologne dictionaries — Pāṇinian derivation statistics</h1>
<p>Generated from the <code>*_etymology.tsv</code> extractions. WIL uses the English-prose <code>E.</code> field;
SKD, VCP, Apte, AP, SHS, KRM use Sanskrit-prose kāraka + pratyaya. Only the Sanskrit-side dicts carry a kāraka.</p>
<div class="cards" id="cards"></div>

<h2>Kāraka × pratyaya (Sanskrit-side, pooled)</h2>
<p>Which affix derives a word in which kāraka sense. Darker = more derivations. This grid is impossible from WIL/Apte-English alone — only the Sanskrit dictionaries state the kāraka.</p>
<div id="heat"></div>

<h2>Affix kāraka-spread (entropy)</h2>
<p>How many distinct kāraka senses one affix forms. High = a "generalist" affix (e.g. <i>ac</i>, <i>ka</i>); low = specialised (e.g. <i>lyu</i> → agent only).</p>
<div class="cw"><canvas id="ent" role="img" aria-label="Affix entropy bar chart"></canvas></div>

<h2>Root productivity (Sanskrit-side, pooled)</h2>
<p>Roots with the most derivatives across the Sanskrit dictionaries.</p>
<div class="cw"><canvas id="roots" role="img" aria-label="Most productive roots"></canvas></div>

<h2>Cross-dictionary affix agreement</h2>
<p>For head-words shared by two dictionaries (both giving an affix), how often the affix agrees. The Sanskrit-tradition dicts cluster at 90–100%; Wilson 1832 is the outlier.</p>
<table id="agree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>affix agrees</th><th>%</th></tr></thead><tbody></tbody></table>

<h2>Cross-dictionary root agreement</h2>
<p>For head-words shared by two dictionaries (both giving a root), how often the root agrees. Includes MW, whose etymology is root-attribution + <code>parse=</code> rather than affixes.</p>
<table id="ragree"><thead><tr><th>dict A</th><th>dict B</th><th>shared head-words</th><th>root agrees</th><th>%</th></tr></thead><tbody></tbody></table>

<h2>Root-capture coverage</h2>
<table id="cap"><thead><tr><th>dict</th><th>derivations</th><th>local</th><th>dhātupāṭha-join</th><th>gaṇa-backref</th><th>empty</th><th>% with root</th></tr></thead><tbody></tbody></table>

<script>
const D=/*DATA*/;
const cards=document.getElementById('cards');
D.codes.forEach(c=>cards.insertAdjacentHTML('beforeend',`<div class="card"><div class="n">${D.perdict[c]}</div><div class="l">${c}</div></div>`));

const H=D.heat, max=Math.max(...H.matrix.flat());
function col(v){const t=Math.sqrt(v/max);const a=[230,241,251],b=[24,95,165];return `rgb(${Math.round(a[0]+(b[0]-a[0])*t)},${Math.round(a[1]+(b[1]-a[1])*t)},${Math.round(a[2]+(b[2]-a[2])*t)})`;}
const heat=document.getElementById('heat');
const grid=document.createElement('div');grid.className='hm';
grid.style.gridTemplateColumns=`60px repeat(${H.karakas.length},1fr) 52px`;
grid.insertAdjacentHTML('beforeend','<div></div>'+H.karakas.map(k=>`<div style="color:#52514e">${k}</div>`).join('')+'<div style="color:#52514e">total</div>');
H.affixes.forEach((a,i)=>{
 grid.insertAdjacentHTML('beforeend',`<div style="font-style:italic;text-align:left;align-self:center">${a}</div>`);
 H.matrix[i].forEach(v=>{const t=Math.sqrt(v/max);grid.insertAdjacentHTML('beforeend',`<div style="background:${col(v)};color:${t>0.55?'#fff':'#042C53'}${v===0?';opacity:.4':''}">${v||''}</div>`);});
 grid.insertAdjacentHTML('beforeend',`<div style="color:#52514e;align-self:center">${H.rowtot[i]}</div>`);
});
heat.appendChild(grid);

new Chart(document.getElementById('ent'),{type:'bar',data:{labels:D.entropy.map(e=>e[0]),
 datasets:[{label:'entropy (bits)',data:D.entropy.map(e=>e[1]),backgroundColor:'#2a78d6'}]},
 options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'kāraka-spread entropy (bits)'}}}}});

new Chart(document.getElementById('roots'),{type:'bar',data:{labels:D.roots.map(r=>r[0]),
 datasets:[{label:'derivatives',data:D.roots.map(r=>r[1]),backgroundColor:'#1baf7a'}]},
 options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});

const at=document.querySelector('#agree tbody');
D.agreement.sort((a,b)=>b[2]-a[2]).forEach(r=>at.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}%</td></tr>`));
const rat=document.querySelector('#ragree tbody');
(D.root_agreement||[]).sort((a,b)=>b[2]-a[2]).forEach(r=>rat.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}%</td></tr>`));
const ct=document.querySelector('#cap tbody');
D.capture.forEach(r=>ct.insertAdjacentHTML('beforeend',`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td>${r[5]}</td><td>${r[6]}%</td></tr>`));
</script></body></html>
"""


if __name__ == '__main__':
    main()
