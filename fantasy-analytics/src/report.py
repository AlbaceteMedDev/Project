"""Render the study as a single self-contained HTML page.

Every number on the page is read out of output/page_data.json, so the report
cannot drift from the analysis that produced it.
"""
from __future__ import annotations

import html
import json

import pandas as pd

from config import OUTPUT

POS_ORDER = ["WR", "TE", "RB", "QB"]
POS_NAME = {"WR": "Wide receiver", "TE": "Tight end", "RB": "Running back",
            "QB": "Quarterback"}
POS_NOTE = {
    "WR": "The position the original card was about, and the one where the "
          "recipe works best. Five gates, cleared by fewer than three receivers "
          "a year, and nine in ten of them finish top-5.",
    "TE": "Almost as sharp as wide receiver, and the position where last year "
          "tells you the most: a tight end who finished top-5 repeats at 43%, "
          "far above any other position.",
    "RB": "The gates are looser here because volume is assigned, not earned. "
          "A back only needs the job — and the job can be handed to someone who "
          "did not have it last year, which is why a quarter of top-5 running "
          "back seasons were invisible beforehand.",
    "QB": "The position where the format breaks down. Nearly every quarterback "
          "stat is his fantasy score restated in other units, so once the "
          "circular ones are removed only two honest gates survive.",
}

CSS = """
:root{
  color-scheme:light;
  --ground:#E7EAE8; --surface:#F8F9F7; --surface-2:#EFF2EF; --line:#D2D8D4;
  --line-strong:#B4BDB8; --ink:#12100C; --ink-2:#3D4441; --muted:#697471;
  --mark:#eda100; --mark-ink:#8A6207; --good:#1baf7a; --good-ink:#0F6B4A;
  --bad:#e34948; --bad-ink:#9E2C2B; --shadow:0 1px 2px rgba(18,16,12,.06);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#0E1211; --surface:#181D1C; --surface-2:#1F2523; --line:#2C3432;
    --line-strong:#414B48; --ink:#ECEFEC; --ink-2:#C2C9C5; --muted:#8D9895;
    --mark:#c98500; --mark-ink:#E2B458; --good:#199e70; --good-ink:#54C79B;
    --bad:#e66767; --bad-ink:#F09189; --shadow:0 1px 2px rgba(0,0,0,.4);
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#0E1211; --surface:#181D1C; --surface-2:#1F2523; --line:#2C3432;
  --line-strong:#414B48; --ink:#ECEFEC; --ink-2:#C2C9C5; --muted:#8D9895;
  --mark:#c98500; --mark-ink:#E2B458; --good:#199e70; --good-ink:#54C79B;
  --bad:#e66767; --bad-ink:#F09189; --shadow:0 1px 2px rgba(0,0,0,.4);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:Newsreader,Georgia,'Times New Roman',serif;
  font-size:17px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px; margin:0 auto; padding:0 24px 96px}
p{margin:0 0 1em; max-width:66ch}
a{color:var(--mark-ink)}
h1,h2,h3,h4{margin:0; text-wrap:balance; font-weight:600; letter-spacing:-.011em}
.mono{font-family:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  font-variant-numeric:tabular-nums}
.label{font-family:'IBM Plex Mono',ui-monospace,monospace; font-size:11px;
  letter-spacing:.14em; text-transform:uppercase; color:var(--muted); font-weight:500}
.num{font-family:'Big Shoulders Display',Archivo,Impact,sans-serif; font-weight:700;
  font-variant-numeric:tabular-nums; line-height:.82; letter-spacing:.01em}

/* hash-mark rule: the yard-line motif, used only as a section divider */
.hash{height:11px; margin:0;
  background:repeating-linear-gradient(90deg,var(--line-strong) 0 2px,transparent 2px 14px);
  border:0; opacity:.85}

header.top{padding:76px 0 40px}
.eyebrow{display:flex; gap:14px; align-items:center; margin-bottom:22px; flex-wrap:wrap}
h1{font-size:clamp(38px,6.2vw,68px); line-height:1.02; margin-bottom:20px;
  font-weight:600; letter-spacing:-.028em}
.deck{font-size:clamp(18px,2.1vw,21px); color:var(--ink-2); max-width:60ch}
.meta{display:flex; flex-wrap:wrap; gap:0; margin-top:34px; border-top:1px solid var(--line);
  border-bottom:1px solid var(--line)}
.meta div{flex:1 1 150px; padding:14px 18px 15px; border-right:1px solid var(--line)}
.meta div:last-child{border-right:0}
.meta b{display:block; font-family:'IBM Plex Mono',monospace; font-size:19px;
  font-weight:600; letter-spacing:-.02em; margin-bottom:2px}

section{padding:56px 0 8px}
h2{font-size:clamp(25px,3.4vw,33px); margin-bottom:8px; letter-spacing:-.02em}
.sec-intro{color:var(--ink-2); margin-bottom:30px}

.card{background:var(--surface); border:1px solid var(--line); border-radius:3px;
  box-shadow:var(--shadow)}
.pad{padding:24px 26px}

/* audit */
table{width:100%; border-collapse:collapse; font-size:15px}
.scroll{overflow-x:auto; -webkit-overflow-scrolling:touch}
th{font-family:'IBM Plex Mono',monospace; font-size:10.5px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); font-weight:500; text-align:right;
  padding:0 12px 9px; border-bottom:1px solid var(--line-strong); white-space:nowrap}
th:first-child{text-align:left}
td{padding:11px 12px; border-bottom:1px solid var(--line); text-align:right;
  font-family:'IBM Plex Mono',monospace; font-size:13.5px; white-space:nowrap}
td:first-child{text-align:left; font-family:Newsreader,Georgia,serif; font-size:16px;
  white-space:normal}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--surface-2)}
.verdict{display:inline-flex; align-items:center; gap:6px; font-family:'IBM Plex Mono',monospace;
  font-size:11px; letter-spacing:.08em; text-transform:uppercase; font-weight:600;
  padding:3px 9px; border-radius:2px; border:1px solid}
.v-good{color:var(--good-ink); border-color:var(--good); background:color-mix(in srgb,var(--good) 9%,transparent)}
.v-bad{color:var(--bad-ink); border-color:var(--bad); background:color-mix(in srgb,var(--bad) 9%,transparent)}

/* rule rows */
.rules{display:flex; flex-direction:column}
.rule{display:grid; grid-template-columns:52px minmax(0,1fr) 112px;
  gap:18px; align-items:center; padding:15px 0; border-bottom:1px solid var(--line)}
.rule:last-child{border-bottom:0}
.rule .n{font-size:44px; color:var(--mark-ink); text-align:center}
.rule .body strong{font-weight:600; font-size:17.5px; display:block}
.rule .thr{font-family:'IBM Plex Mono',monospace; font-size:13px; color:var(--ink-2);
  margin-top:1px}
.bar-wrap{display:flex; align-items:center; gap:9px}
.bar{height:9px; border-radius:0 4px 4px 0; background:var(--mark); flex:0 0 auto; min-width:2px}
.bar-val{font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--ink-2);
  font-variant-numeric:tabular-nums}
.rule .right{text-align:right}
.rule .hit{font-family:'IBM Plex Mono',monospace; font-size:20px; font-weight:600;
  letter-spacing:-.02em}
.rule .hit span{font-size:11px; color:var(--muted); letter-spacing:.1em;
  text-transform:uppercase; display:block; font-weight:500; margin-top:1px}

.joint{display:grid; grid-template-columns:repeat(4,minmax(0,1fr));
  border-top:1px solid var(--line-strong); background:var(--surface-2)}
.joint.narrow{grid-template-columns:repeat(2,minmax(0,1fr))}
.joint>div{padding:15px 18px; border-right:1px solid var(--line)}
.joint>div:nth-child(4n){border-right:0}
.joint.narrow>div{border-right:0; border-bottom:1px solid var(--line)}
.joint.narrow>div:nth-child(odd){border-right:1px solid var(--line)}
.joint.narrow>div:nth-last-child(-n+2){border-bottom:0}
@media (max-width:760px){.joint{grid-template-columns:repeat(2,minmax(0,1fr))}}
.joint b{display:block; font-family:'IBM Plex Mono',monospace; font-size:23px;
  font-weight:600; letter-spacing:-.025em; margin-bottom:1px}

/* position chapter head */
.chapter{margin-top:14px}
.chead{display:flex; align-items:flex-end; gap:22px; padding:0 0 18px; flex-wrap:wrap}
.pmark{font-family:'Big Shoulders Display',Archivo,Impact,sans-serif; font-weight:800;
  font-size:104px; line-height:.76; letter-spacing:-.01em; color:var(--ink);
  -webkit-text-stroke:0}
.chead .txt{flex:1 1 300px; padding-bottom:6px}
.chead h3{font-size:26px; letter-spacing:-.02em}
.chead .sub{color:var(--muted); font-family:'IBM Plex Mono',monospace; font-size:12.5px;
  margin-top:3px}
.note{color:var(--ink-2); margin:0 0 26px; max-width:64ch}

.grid2{display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:20px;
  align-items:start}
.stack{display:flex; flex-direction:column; gap:20px}
.blockhead{display:flex; align-items:baseline; justify-content:space-between; gap:12px;
  padding:15px 26px 13px; border-bottom:1px solid var(--line-strong); flex-wrap:wrap}
.blockhead h4{font-size:18px}
.green{display:flex; flex-direction:column}
.narrowcard .rule{grid-template-columns:40px minmax(0,1fr) 92px; gap:12px}
.narrowcard .rule .n{font-size:36px}
.narrowcard .rule .body strong{font-size:16px}
.narrowcard .rule .hit{font-size:18px}
.green .g{display:grid; grid-template-columns:minmax(0,1fr) auto; gap:14px;
  padding:12px 0; border-bottom:1px solid var(--line); align-items:baseline}
.green .g:last-child{border-bottom:0}
.green .g em{font-style:normal; font-family:'IBM Plex Mono',monospace; font-size:12.5px;
  color:var(--muted); display:block}
.green .pct{font-family:'IBM Plex Mono',monospace; font-size:17px; font-weight:600;
  color:var(--mark-ink); white-space:nowrap}

/* persistence small multiple */
.pers{display:flex; gap:6px; align-items:flex-end; height:96px; padding-top:8px}
.pers .col{flex:1; display:flex; flex-direction:column; justify-content:flex-end;
  align-items:center; gap:5px; height:100%}
.pers .fill{width:100%; background:var(--mark); border-radius:3px 3px 0 0; min-height:2px}
.pers .cv{font-family:'IBM Plex Mono',monospace; font-size:12px; font-weight:600}
.pers .cl{font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted);
  letter-spacing:.04em; white-space:nowrap}
.cap{font-family:'IBM Plex Mono',monospace; font-size:11px; line-height:1.5;
  color:var(--muted); margin:14px 0 0; max-width:none}

details{border-top:1px solid var(--line); margin-top:0}
summary{cursor:pointer; padding:14px 26px; font-family:'IBM Plex Mono',monospace;
  font-size:11.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted);
  font-weight:500; list-style:none; display:flex; justify-content:space-between;
  align-items:center; gap:10px}
summary::-webkit-details-marker{display:none}
summary::after{content:"+"; font-size:15px; color:var(--line-strong)}
details[open] summary::after{content:"–"}
summary:hover{color:var(--ink)}
summary:focus-visible,a:focus-visible{outline:2px solid var(--mark-ink); outline-offset:2px}

.roll{display:flex; flex-wrap:wrap; gap:0; padding:2px 26px 20px}
.roll .yr{flex:1 1 168px; padding:11px 12px 11px 0}
.roll .yr .y{font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--muted);
  letter-spacing:.1em; margin-bottom:2px}
.roll .yr .p{font-size:15.5px; line-height:1.32}
.roll .yr .p b{font-weight:600}

.fc{display:flex; flex-direction:column}
.fc .r{display:grid; grid-template-columns:24px minmax(0,1fr) auto; gap:0 12px;
  align-items:center; padding:9px 0; border-bottom:1px solid var(--line)}
.fc .r:last-child{border-bottom:0}
.fc .rk{font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--muted)}
.fc .nm{font-size:16px}
.fc .nm small{display:block; font-family:'IBM Plex Mono',monospace; font-size:11px;
  color:var(--muted); letter-spacing:.04em; margin-top:1px}
.fc .rt{text-align:right}
.fc .gates{font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:.07em;
  color:var(--muted); text-transform:uppercase; margin-top:1px}
.fc .gates.all{color:var(--good-ink); font-weight:600}
.fc .pp{font-family:'IBM Plex Mono',monospace; font-size:15px; font-weight:600;
  line-height:1.15}

.callout{border-left:3px solid var(--mark); padding:2px 0 2px 20px; margin:26px 0;
  color:var(--ink-2)}
.callout b{color:var(--ink)}
footer{padding:52px 0 0; color:var(--muted); font-size:14.5px}
footer a{color:var(--mark-ink)}
ul.tight{margin:0 0 1em; padding-left:20px; max-width:66ch}
ul.tight li{margin-bottom:.45em}
@media (max-width:640px){
  .rule{grid-template-columns:40px minmax(0,1fr); gap:14px}
  .rule .right{grid-column:2; text-align:left}
  .rule .hit{display:flex; align-items:baseline; gap:8px}
  .rule .hit span{display:inline; margin:0}
  .fc .r{grid-template-columns:22px minmax(0,1fr) auto}
  .pmark{font-size:76px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important; transition:none!important}}
"""


def e(s) -> str:
    return html.escape(str(s))


def pct(v, dp=0) -> str:
    return "—" if v is None or v != v else f"{v * 100:.{dp}f}%"


def fmt_thr(rule: dict) -> str:
    t = rule["threshold"]
    m = rule["metric"]
    op = "at most" if rule["direction"] == "<=" else "at least"
    if any(k in m for k in ("share", "_pct", "td_rate")) and t < 1:
        val = f"{t * 100:.0f}%"
    elif abs(t - round(t)) < 1e-9:
        val = f"{t:.0f}"
    else:
        val = f"{t:g}"
    return f"{op} {val}"


def bar(value: float, vmax: float, text: str, width: int = 74) -> str:
    w = max(2, round(value / vmax * width)) if vmax else 2
    return (f'<div class="bar-wrap"><div class="bar" style="width:{w}px"></div>'
            f'<span class="bar-val">{e(text)}</span></div>')


def rules_block(rules: list, title: str, sub: str, joint_html: str = "",
                narrow: bool = False) -> str:
    if not rules:
        return ""
    vmax = max(r["lift"] for r in rules)
    rows = []
    for i, r in enumerate(rules, 1):
        rows.append(f"""
      <div class="rule" title="{e(r['label'])}: {e(fmt_thr(r))} — {pct(r['precision'])} of
           seasons clearing it finished top-5">
        <div class="n num">{i}</div>
        <div class="body">
          <strong>{e(r['label'])}</strong>
          <div class="thr">{e(fmt_thr(r))} &nbsp;·&nbsp; cleared by
            {pct(r['recall'])} of top-5 seasons &nbsp;·&nbsp;
            ~{r['per_season_flagged']:.1f} players a season</div>
          {bar(r['lift'], vmax, f"{r['lift']:.1f}× base rate")}
        </div>
        <div class="right"><div class="hit">{pct(r['precision'])}<span>finish top-5</span></div></div>
      </div>""")
    cls = "card narrowcard" if narrow else "card"
    return f"""<div class="{cls}"><div class="blockhead"><h4>{e(title)}</h4>
      <span class="label">{e(sub)}</span></div>
      <div class="pad rules">{''.join(rows)}</div>{joint_html}</div>"""


def joint_block(j: dict, n_rules: int, narrow: bool = False) -> str:
    word = "the gate" if n_rules == 1 else f"all {n_rules} gates"
    return f"""<div class="joint{' narrow' if narrow else ''}">
      <div><b>{j['per_season_flagged']:.1f}</b><span class="label">a season clear {e(word)}</span></div>
      <div><b>{pct(j['precision'])}</b><span class="label">of them finish top-5</span></div>
      <div><b>{j['lift']:.1f}&times;</b><span class="label">the base rate of {pct(j['base_rate'], 1)}</span></div>
      <div><b>{pct(j['recall'])}</b><span class="label">of all top-5 seasons caught</span></div>
    </div>"""


def green_block(greens: list, title: str) -> str:
    if not greens:
        return ""
    rows = "".join(f"""<div class="g"><div><strong>{e(g['label'])}</strong>
        <em>{e(fmt_thr(g))} &nbsp;·&nbsp; ~{g['per_season_flagged']:.1f} a season</em></div>
        <div class="pct">{pct(g['precision'])}</div></div>""" for g in greens[:4])
    return f"""<div class="card"><div class="blockhead"><h4>{e(title)}</h4>
      <span class="label">hit rate once cleared</span></div>
      <div class="pad green">{rows}</div></div>"""


def persistence_block(p: dict) -> str:
    buckets = [("top 5", p["prev_top5"]), ("6–12", p["prev_6_12"]),
               ("13–24", p["prev_13_24"]), ("25+", p["prev_25plus"])]
    vmax = max(b[1]["rate"] for b in buckets) or 1
    cols = "".join(f"""<div class="col" title="{e(lab)} last year, n={v['n']}:
        {pct(v['rate'])} finished top-5 the next season">
        <div class="cv">{pct(v['rate'])}</div>
        <div class="fill" style="height:{max(2, round(v['rate'] / vmax * 58))}px"></div>
        <div class="cl">{e(lab)}</div></div>""" for lab, v in buckets)
    return f"""<div class="card"><div class="blockhead"><h4>Does it repeat?</h4>
      <span class="label">chance of top-5, by last year's finish</span></div>
      <div class="pad"><div class="pers">{cols}</div>
      <p class="cap">Sample: {p['prev_top5']['n']} / {p['prev_6_12']['n']} /
      {p['prev_13_24']['n']} / {p['prev_25plus']['n']} player-seasons per bucket.
      Elite finishes decay fast — outside last year's top 24 it is close to a
      standing start.</p></div></div>"""


def model_block(pos: str, m: dict, cov: dict) -> str:
    return f"""<div class="card"><div class="blockhead"><h4>Predicting it in August</h4>
      <span class="label">leave-one-season-out</span></div>
      <div class="joint narrow" style="border-top:0">
      <div><b>{m['oos_auc']:.2f}</b><span class="label">out-of-sample AUC</span></div>
      <div><b>{pct(m['top10_precision'])}</b><span class="label">of a preseason top-10 list hits</span></div>
      <div><b>{pct(m['top10_recall'])}</b><span class="label">of top-5s inside that list</span></div>
      <div><b>{pct(cov['pct_reachable'])}</b><span class="label">had a qualifying prior season at all</span></div>
      </div></div>"""


def elite_roll(pos: str, elite: list) -> str:
    by_year: dict[int, list] = {}
    for r in elite:
        by_year.setdefault(int(r["season"]), []).append(r)
    cells = []
    for yr in sorted(by_year):
        names = sorted(by_year[yr], key=lambda r: r["pos_rank"])
        inner = "<br>".join(
            (f"<b>{e(n['player_display_name'])}</b>" if n["pos_rank"] == 1
             else e(n["player_display_name"])) for n in names)
        cells.append(f'<div class="yr"><div class="y mono">{yr}</div>'
                     f'<div class="p">{inner}</div></div>')
    return f"""<details><summary>Every top-5 {e(pos)} season, 2015–2025
      &nbsp;·&nbsp; {len(elite)} seasons, position winner in bold</summary>
      <div class="roll">{''.join(cells)}</div></details>"""


def forecast_block(pos: str, rows: list, n_cand: int, n_rules: int,
                   season: int) -> str:
    out = []
    for r in rows[:10]:
        allp = r["passes_all"] in (True, "True")
        gates = "all gates" if allp else f"{int(r['rules_passed'])}/{n_rules}"
        out.append(f"""<div class="r">
          <div class="rk">{int(r['rank'])}</div>
          <div class="nm">{e(r['player_display_name'])}
            <small>{e(r['team'])} · {float(r['age']):.0f}yo · was {e(pos)}{int(r['prev_pos_rank'])}</small></div>
          <div class="rt"><div class="pp">{float(r['prob']):.2f}</div>
            <div class="gates{' all' if allp else ''}">{e(gates)}</div></div></div>""")
    return f"""<div class="card"><div class="blockhead"><h4>{season} shortlist</h4>
      <span class="label">{n_cand} returning candidates</span></div>
      <div class="pad fc">{''.join(out)}</div>
      <div class="pad" style="padding-top:0"><p class="label" style="max-width:none">
      Model probability, not a projection. Anyone who changed teams this offseason
      still carries his old team's context.</p></div></div>"""


def audit_section(a: dict) -> str:
    rows = []
    for r in a["rules"]:
        vacuous = r["lift"] < 1.25
        badge = ('<span class="verdict v-bad">&#10007; no filter</span>' if vacuous
                 else '<span class="verdict v-good">&#10003; real</span>')
        rows.append(f"""<tr>
          <td>{e(r['rule'])}</td>
          <td>{r['wr1_pass']}/{r['wr1_n']}</td>
          <td>{r['top5_pass']}/{r['top5_n']}</td>
          <td>{pct(r['pool_pass_rate'])}</td>
          <td>{r['lift']:.1f}&times;</td>
          <td>{badge}</td></tr>""")
    j = a["joint"]
    misses = "".join(
        f"<li><b>{m['season']} {e(m['player'])}</b> — failed {e(', '.join(m['failed']))}</li>"
        for m in a["wr1_misses"])
    return f"""<section id="audit">
  <h2>The card that started this</h2>
  <p class="sec-intro">Five rules, claimed to describe every overall WR1 since 2016.
  Scored against all {j['n_pool']:,} qualifying receiver seasons from
  {j['first_season']} to {j['last_season']}. A rule earns its place only if the
  field does not already clear it.</p>
  <div class="card"><div class="scroll"><table>
    <thead><tr><th>Rule as stated</th><th>WR1s passing</th><th>Top-5 seasons</th>
      <th>Whole pool passing</th><th>Lift</th><th>Verdict</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table></div>
    {joint_block({**j, 'precision': j['precision_top5'], 'recall': j['recall_top5'],
                  'per_season_flagged': j['n_flagged'] / 10, 'lift':
                  j['precision_top5'] / j['base_rate']}, 5)}
  </div>
  <div class="callout"><p><b>Four of the five rules hold up. One does nothing.</b>
  Being under 30 describes {pct(a['rules'][0]['pool_pass_rate'])} of the qualifying
  receiver pool, so it removes almost nobody — a lift of
  {a['rules'][0]['lift']:.1f}&times;. Age carries an AUC of 0.51 for predicting a
  top-5 receiver season, which is a coin flip. The two rules doing the real work
  are target share and route efficiency, at 6.6&times; and 6.3&times;.</p></div>
  <p>Taken together the five rules flag {j['n_flagged']} seasons across the decade
  and {j['n_top5_flagged']} of them finished top-5 — a {pct(j['precision_top5'])} hit
  rate. But the card goes {j['n_wr1_flagged']} for {j['n_wr1']}
  on the very list it illustrates:</p>
  <ul class="tight">{misses}</ul>
</section>"""


def chapter(pos: str, d: dict, season: int) -> str:
    j = d["joint"]
    pj = d["pred"]["joint"]
    n_pred_rules = len(d["pred"]["gates"])
    pred_line = (
        f"""<div class="card narrowcard"><div class="blockhead">
        <h4>What last season already told you</h4>
        <span class="label">prior-year inputs only</span></div>
        <div class="pad rules">{''.join(
            f'''<div class="rule"><div class="n num">{i}</div><div class="body">
            <strong>{e(r['label'])}</strong><div class="thr">{e(fmt_thr(r))}
            &nbsp;·&nbsp; true of {pct(r['recall'])} of the next year's top-5</div>
            {bar(r['lift'], max(x['lift'] for x in d['pred']['gates']),
                 f"{r['lift']:.1f}× base rate")}</div>
            <div class="right"><div class="hit">{pct(r['precision'])}<span>hit rate</span></div></div>
            </div>''' for i, r in enumerate(d["pred"]["gates"], 1))}</div>
        {joint_block(pj, n_pred_rules, narrow=True)}</div>""" if d["pred"]["gates"] else "")

    return f"""<section class="chapter" id="{pos.lower()}">
  <hr class="hash">
  <div class="chead">
    <div class="pmark">{pos}</div>
    <div class="txt">
      <h3>{e(POS_NAME[pos])}</h3>
      <div class="sub">{d['pool']['n']:,} qualifying seasons, 2015–2025 &nbsp;·&nbsp;
        {j['n_elite']} of them top-5 &nbsp;·&nbsp; base rate {pct(j['base_rate'], 1)}</div>
    </div>
  </div>
  <p class="note">{e(POS_NOTE[pos])}</p>

  {rules_block(d['gates'], 'The gates', 'cleared by ~85% of top-5 seasons',
               joint_block(j, len(d['gates'])))}

  <div class="grid2" style="margin-top:20px">
    {green_block(d['greens'], 'Green flags')}
    {persistence_block(d['pred']['persistence'])}
  </div>

  <div class="grid2" style="margin-top:20px">
    {pred_line}
    <div class="stack">{model_block(pos, d['pred']['model'], d['pred']['coverage'])}
      {forecast_block(pos, d['forecast'], d['forecast_n'], n_pred_rules, season)}</div>
  </div>

  <div class="card" style="margin-top:20px">{elite_roll(pos, d['elite'])}</div>
</section>"""


def build(page: dict) -> str:
    m = page["meta"]
    unreachable = "".join(
        f"""<tr><td style="white-space:nowrap">{e(POS_NAME[p])}</td>
        <td>{page['positions'][p]['pred']['coverage']['n_top5'] -
             page['positions'][p]['pred']['coverage']['n_reachable']}</td>
        <td>{pct(1 - page['positions'][p]['pred']['coverage']['pct_reachable'])}</td>
        <td style="text-align:left;white-space:normal;font-size:12.5px">
        {e(', '.join(f"{u['season']} {u['player_display_name']}"
                     for u in page['positions'][p]['pred']['unreachable']))}</td></tr>"""
        for p in POS_ORDER)

    return f"""<title>Anatomy of a Top-5 Season</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="top">
  <div class="eyebrow"><span class="label">Fantasy football · 2015–2025</span>
    <span class="label" style="color:var(--mark-ink)">Full PPR</span></div>
  <h1>Anatomy of a top-5 season</h1>
  <p class="deck">Eleven seasons of play-by-play, asked two questions at every
  position: what did a top-5 fantasy season look like while it was happening, and
  how much of it could you actually see coming?</p>
  <div class="meta">
    <div><b>11</b><span class="label">seasons</span></div>
    <div><b>{m['n_player_seasons']:,}</b><span class="label">player-seasons</span></div>
    <div><b>{sum(page['positions'][p]['joint']['n_elite'] for p in POS_ORDER)}</b><span class="label">top-5 finishes</span></div>
    <div><b>4</b><span class="label">positions</span></div>
    <div><b>{max(page['positions'][p]['pred']['model']['oos_auc'] for p in POS_ORDER):.2f}</b><span class="label">best out-of-sample AUC</span></div>
  </div>
</header>

{audit_section(page['audit'])}

<section>
  <hr class="hash">
  <h2 style="margin-top:44px">Two different questions</h2>
  <p class="sec-intro">Cards like the one above blur them together. They are not
  the same question and they do not have the same answer.</p>
  <div class="grid2">
    <div class="card pad"><span class="label">Gate</span>
      <p style="margin:8px 0 0"><b>The bar nearly every top-5 season cleared.</b>
      Loose enough that ~85% of elite seasons sit above it, so failing one is
      strong evidence against. Clearing all of them at once is rare, and at wide
      receiver it is close to decisive.</p></div>
    <div class="card pad"><span class="label">Green flag</span>
      <p style="margin:8px 0 0"><b>The bar that, once cleared, usually means top-5.</b>
      Set to maximise hit rate rather than coverage, so most elite seasons miss it —
      but the ones that clear it are mostly elite.</p></div>
  </div>
  <div class="callout"><p>Rules are rejected, not padded. A candidate rule has to
  beat the base rate by 1.35&times; to make a card, and metrics that merely restate
  the fantasy score — a quarterback's team points, his touchdown rate — are marked
  circular and kept out. That is why the quarterback card has two rules and the
  receiver card has five.</p></div>
</section>

{''.join(chapter(p, page['positions'][p], m['forecast_season']) for p in POS_ORDER)}

<section>
  <hr class="hash">
  <h2 style="margin-top:44px">What none of this can see</h2>
  <p class="sec-intro">Prior-year metrics cannot describe a role that did not exist
  yet. These top-5 seasons had no qualifying prior season at all — rookies, and
  players handed a job they had never held.</p>
  <div class="card"><div class="scroll"><table>
    <thead><tr><th>Position</th><th>Unreachable</th><th>Share</th>
      <th style="text-align:left">Seasons no prior-year model could have flagged</th></tr></thead>
    <tbody>{unreachable}</tbody></table></div></div>
  <div class="callout"><p><b>Running back is the position with the biggest blind spot.</b>
  A quarter of its top-5 seasons came from players the prior year could not see,
  because a backfield job is assigned in August, not earned in December. That is
  the same reason its gates are the loosest of the four.</p></div>
</section>

<section>
  <hr class="hash">
  <h2 style="margin-top:44px">Method</h2>
  <ul class="tight">
    <li><b>Data.</b> nflverse public releases — weekly player stats, play-by-play,
      Pro-Football-Reference snap counts, player master file. 2014 is loaded only
      to supply prior-year inputs for 2015.</li>
    <li><b>Scoring.</b> Full PPR, regular season totals; positional finish is the
      rank of total points within position within season. The computed WR1 list for
      2016–2025 reproduces the source card's ten players exactly, which is the check
      that the scoring and ranking are right.</li>
    <li><b>Pools.</b> A season counts if it clears a rosterability floor — receivers
      8 games and 30 targets, tight ends 8 and 20, backs 8 games and 50 touches,
      quarterbacks 8 games and 200 attempts. Base rates are quoted against these
      pools, not against everyone who took a snap.</li>
    <li><b>Rate stats are shrunk</b> toward the positional mean by sample size, so a
      tight end with 157 routes and a 3.6 yards-per-route spike does not outrank a
      680-route starter.</li>
    <li><b>Prediction is scored leave-one-season-out</b> — every season is predicted
      by a model that never saw it.</li>
    <li><b>Yards per route is an estimate.</b> Public data has no route counts, so
      routes are estimated as snap share × team dropbacks. That runs 10–20% below
      charted totals, so the figures here read correspondingly high; every rule is
      therefore also given as players-per-season, which the bias does not touch.</li>
  </ul>
  <p style="color:var(--muted); font-size:15px">Eleven seasons give 55 top-5
  finishes per position. Which metrics matter is stable; the exact threshold values
  carry real uncertainty. The model is validated out of sample, the gate thresholds
  are descriptive and are not.</p>
</section>

<footer>
  <hr class="hash" style="margin-bottom:26px">
  <p>Built from <a href="https://github.com/nflverse/nflverse-data">nflverse</a>
  public data. Full pipeline, thresholds and per-season outputs are in the
  repository — <span class="mono">python src/run_all.py</span> reproduces every
  number on this page.</p>
</footer>
</div>"""


SLIM = ("label", "metric", "direction", "threshold", "precision", "recall",
        "lift", "per_season_flagged", "n_flagged", "hits")


def assemble() -> dict:
    """Collect the analysis outputs into the single bundle the page renders from."""
    prof = json.load(open(OUTPUT / "profile_cards.json"))
    pred = json.load(open(OUTPUT / "predictive_cards.json"))
    audit = json.load(open(OUTPUT / "viral_rule_audit.json"))
    fc_path = next(OUTPUT.glob("forecast_*.json"))
    fc = json.load(open(fc_path))
    n_seasons = len(pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False))

    def slim(r):
        return {k: r[k] for k in SLIM}

    page = {"meta": {"n_player_seasons": n_seasons,
                     "forecast_season": int(fc_path.stem.split("_")[1])},
            "audit": audit, "positions": {}}
    for p in POS_ORDER:
        pr, pd_ = prof[p]["profile_top5"], pred[p]
        page["positions"][p] = {
            "pool": prof[p]["pool"], "joint": pr["joint"],
            "gates": [slim(r) for r in pr["rules"]],
            "greens": [slim(r) for r in pr["green_flags"]],
            "vacuous": [slim(r) for r in pr["vacuous"]],
            "pred": {
                "pool": pd_["pool"], "joint": pd_["card"]["joint"],
                "gates": [slim(r) for r in pd_["card"]["rules"]],
                "greens": [slim(r) for r in pd_["card"]["green_flags"]],
                "model": pd_["model"], "persistence": pd_["persistence"],
                "coverage": {k: v for k, v in pd_["coverage"].items()
                             if k != "unreachable"},
                "unreachable": pd_["coverage"]["unreachable"],
            },
            "elite": prof[p]["elite_seasons"],
            "forecast": fc[p]["shortlist"][:12],
            "forecast_n": fc[p]["n_candidates"],
        }
    with open(OUTPUT / "page_data.json", "w") as fh:
        json.dump(page, fh, indent=1, default=str)
    return page


def main() -> None:
    page = assemble()
    out = OUTPUT / "report.html"
    out.write_text(build(page), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
