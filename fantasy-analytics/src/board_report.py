"""Render the target board as a self-contained page, keyed off target_board.csv."""
from __future__ import annotations

import html
import json

import pandas as pd

from config import LAST_SEASON, OUTPUT
from report import CSS, POS_NAME, e, pct

TARGET = LAST_SEASON + 1
POS_ORDER = ["WR", "RB", "TE", "QB"]

TIER_NOTE = {
    "A - target": "One in four or better. The model never saw the season it is "
                  "scoring, and this band is where its hit rate lives.",
    "B - strong": "Between one in eight and one in four. Most will miss — the base "
                  "rate is 5-15% depending on position — but the profile supports "
                  "the bet.",
    "C - leaper watch": "Outside last year's top 12, but matching the profile of "
                        "players who jumped into the top 5 anyway. The late-round lane.",
    "D - fringe": "Enough profile to roster, not enough to target.",
}

POS_NOTE = {
    "WR": "Five gates, ~2.6 receivers a year clear all of them. 90% of those "
          "finished top-5 with thresholds fitted on every season — 78% when each "
          "season is scored by gates that never saw it. Model AUC 0.93 — the most "
          "trustworthy board here, and the only position where a lost season is "
          "scored as its own fact rather than as bad production.",
    "RB": "Volume is assigned, not earned, so the gates are looser and the blind "
          "spot is bigger: 14% of top-5 running back seasons came from players the "
          "last two years could not see at all. Model AUC 0.86.",
    "TE": "The position where last year tells you the most — a top-5 tight end "
          "repeats 43% of the time — and where the leaper bar is lowest. The only "
          "position whose gates did not degrade out of sample (86% fitted, 88% "
          "held out). Model AUC 0.88.",
    "QB": "Only two honest gates survive, because nearly every quarterback stat "
          "restates the fantasy score. AUC 0.71, and the gates fall to a 45% hit "
          "rate out of sample against a 15% base rate. The weakest board here.",
}

EXTRA = """
.tierband{margin:26px 0 0}
.tierhead{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap;
  padding:0 0 8px; border-bottom:2px solid var(--line-strong)}
.tiername{font-family:'Big Shoulders Display',Archivo,sans-serif; font-weight:700;
  font-size:30px; line-height:1; color:var(--mark-ink)}
.tierdesc{color:var(--ink-2); font-size:15px; flex:1 1 320px; max-width:62ch}
.row{display:grid; grid-template-columns:56px minmax(0,1fr) 96px 120px;
  gap:16px; align-items:center; padding:12px 0; border-bottom:1px solid var(--line)}
.row:last-child{border-bottom:0}
.row:hover{background:var(--surface-2)}
.pnum{font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:600;
  text-align:right; letter-spacing:-.02em}
.pname{font-size:17.5px; font-weight:600}
.pmeta{font-family:'IBM Plex Mono',monospace; font-size:11.5px; color:var(--muted);
  letter-spacing:.03em; margin-top:2px}
.pmiss{font-size:13px; color:var(--ink-2); margin-top:3px}
.pmiss b{font-weight:600; color:var(--ink)}
.pips{display:flex; gap:3px; align-items:center}
.pip{width:11px; height:11px; border-radius:2px; background:var(--line-strong)}
.pip.on{background:var(--mark)}
.piplab{font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted);
  letter-spacing:.1em; text-transform:uppercase; margin-top:4px}
.lane{width:100%; border-collapse:collapse; font-size:15px}
.lane td,.lane th{padding:9px 10px}
.lane .grp td{padding-top:18px; font-family:'Big Shoulders Display',Archivo,sans-serif;
  font-size:24px; color:var(--mark-ink); border-bottom:2px solid var(--line-strong);
  text-align:left; font-weight:700}
.lane .lname{text-align:left; font-family:Newsreader,Georgia,serif; font-size:16px}
.lane .lname small{display:block; font-family:'IBM Plex Mono',monospace; font-size:11px;
  color:var(--muted); letter-spacing:.03em}
.lane .base{color:var(--muted)}
.lane .hit{font-weight:600}
.lane .lift{font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--mark-ink);
  font-weight:600}
.picks{display:grid; grid-template-columns:repeat(auto-fit,minmax(208px,1fr));
  gap:24px 26px; margin-top:24px}
.picks .p1{display:grid; grid-template-columns:minmax(0,1fr) 52px; gap:8px;
  padding:7px 0; border-bottom:1px solid var(--line); align-items:baseline}
.picks .p1:last-child{border-bottom:0}
.picks .pn{font-size:15.5px}
.picks .pn small{display:block; font-family:'IBM Plex Mono',monospace; font-size:10.5px;
  color:var(--muted); letter-spacing:.03em}
.picks .pv{font-family:'IBM Plex Mono',monospace; font-size:14px; text-align:right;
  font-variant-numeric:tabular-nums}
.lev{display:grid; grid-template-columns:repeat(auto-fit,minmax(360px,1fr));
  gap:34px 48px; margin-top:26px}
.levpos{min-width:0}
.levhead{display:flex; align-items:baseline; gap:10px; padding-bottom:7px;
  border-bottom:2px solid var(--line-strong); margin-bottom:12px}
.levpos h4{font-family:'Big Shoulders Display',Archivo,sans-serif; font-weight:700;
  font-size:26px; line-height:1; margin:0; color:var(--mark-ink)}
.levauc{font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--muted);
  letter-spacing:.05em; margin-left:auto; white-space:nowrap}
.meter{display:grid; grid-template-columns:minmax(0,1fr) 46px; gap:10px;
  align-items:center; padding:5px 0}
.mlab{font-size:14px; line-height:1.3; min-width:0}
.mlab .yr{font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted);
  letter-spacing:.06em; text-transform:uppercase; margin-left:5px}
.mval{font-family:'IBM Plex Mono',monospace; font-size:13px; text-align:right;
  font-variant-numeric:tabular-nums}
.mtrack{grid-column:1/-1; height:6px; border-radius:3px; background:var(--surface-2);
  border:1px solid var(--line); position:relative; overflow:hidden; margin-top:-2px}
.mfill{position:absolute; inset:0 auto 0 0; background:var(--mark); border-radius:3px}
.mfill.dead{background:var(--line-strong)}
.levnote{font-size:13.5px; color:var(--ink-2); margin:14px 0 0; max-width:46ch}
.deadlist{margin-top:16px; padding-top:12px; border-top:1px dashed var(--line-strong)}
.deadlist .label{display:block; margin-bottom:6px}
.na{font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--muted);
  letter-spacing:.08em; text-transform:uppercase; line-height:1.4}
.clean{color:var(--good-ink); font-family:'IBM Plex Mono',monospace; font-size:12px;
  letter-spacing:.06em; text-transform:uppercase; font-weight:600; margin-top:3px}
@media (max-width:640px){
  .row{grid-template-columns:44px minmax(0,1fr); gap:12px}
  .row .cellpips,.row .cellprob{grid-column:2}
  .pnum{font-size:19px; text-align:left}
}
"""


def disagreement_section() -> str:
    """The one cut on this board that is not just a list of good players."""
    v = json.loads((OUTPUT / "disagreement.json").read_text())
    by = {b["pos"]: b for b in v["backtest"]}

    rows = []
    for pos in POS_ORDER:
        b = by[pos]
        rows.append(f'<tr class="grp"><td colspan="4">{pos}</td></tr>')
        base = b["rows"][0]
        for r in b["rows"]:
            if r["threshold"] is None:
                lab, sub = "Every one of them", "the whole lane, unfiltered"
                cls = "base"
            else:
                lab = f'Model says {r["threshold"]:.2f} or better'
                sub = f'{r["per_season"]:.1f} players a year'
                cls = "hit"
            lift = r["hit5"] / base["hit5"] if base["hit5"] else 0
            liftx = "" if r["threshold"] is None else f' <span class="lift">{lift:.0f}×</span>'
            rows.append(
                f'<tr><td class="lname">{e(lab)}<small>{e(sub)}</small></td>'
                f'<td class="{cls}">{pct(r["hit5"])}{liftx}</td>'
                f'<td class="{cls}">{pct(r["hit12"])}</td>'
                f'<td class="base">{r["n"]}</td></tr>')

    cols = []
    for pos in POS_ORDER:
        picks = [x for x in v["upcoming"] if x["pos"] == pos]
        body = "".join(
            f'<div class="p1"><div class="pn">{e(x["player"])}'
            f'<small>{e(x["team"])} · {x["age"]:.0f} · was {pos}{x["prior"]}, '
            f'{x["last_games"]} gm</small></div>'
            f'<div class="pv">{x["prob"]:.2f}</div></div>' for x in picks) or \
            '<p class="levnote">Nobody clears the bar this year.</p>'
        cols.append(f'<div><div class="levhead"><h4>{pos}</h4></div>{body}</div>')

    return f"""<section>
  <hr class="hash">
  <h2>Where the model disagrees with last season</h2>
  <p class="sec-intro">Everything above is ordered by probability, which puts the
  best players on top. This cut asks the opposite question: among players whose
  <b>last season finished outside the top 12</b>, which ones does the model still
  rate highly anyway? Those two facts pull against each other, and where they
  conflict is the only place on this page the model says something the previous
  season does not.</p>
  <div class="scroll"><table class="lane">
    <thead><tr><th style="text-align:left">Among players who finished outside the
      top 12 last year…</th><th>Top-5</th><th>Top-12</th><th>n</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
  <div class="callout"><p><b>This is the sharpest thing on the page.</b> A receiver
  coming off a season outside the top 12 finishes top-5 about 2% of the time. The
  ones this model rates at 0.20 or better did it <b>37% of the time</b> — roughly
  two players a year, over eleven seasons. Tight end is the exception and the
  numbers there wobble with the threshold, which is what a sample of nine looks
  like; treat the TE row as unproven.</p></div>
  <h3 style="font-size:20px; margin:38px 0 4px">{v['target']}: who clears it</h3>
  <p class="sec-intro" style="margin-bottom:0">Everyone rated {v['floor']:.2f} or
  better whose {v['target'] - 1} finish was outside the top 12.</p>
  <div class="picks">{''.join(cols)}</div>
</section>
"""


LEV_ORDER = ["WR", "RB", "TE", "QB"]
# AUC 0.50 is a coin flip and nothing below it means anything, so the bar starts
# just under it rather than at zero - a scale from 0 would make every indicator
# look strong.
LEV_LO, LEV_HI = 0.45, 0.95


def meter(label: str, tag: str, auc: float) -> str:
    w = max(0.0, min(1.0, (auc - LEV_LO) / (LEV_HI - LEV_LO))) * 100
    dead = " dead" if auc < 0.60 else ""
    yr = f'<span class="yr">{e(tag)}</span>' if tag else ""
    return (f'<div class="meter"><div class="mlab">{e(label)}{yr}</div>'
            f'<div class="mval">{auc:.3f}</div>'
            f'<div class="mtrack"><div class="mfill{dead}" style="width:{w:.1f}%">'
            f'</div></div></div>')


def leverage_section() -> str:
    """Rank the indicators the only way that survives contact with a new season."""
    lev = pd.read_csv(OUTPUT / "leverage.csv")
    cols = []
    for pos in LEV_ORDER:
        g = lev[lev["pos"] == pos].sort_values("solo", ascending=False)
        live, dead = g[g["solo"] >= 0.60].head(7), g[g["solo"] < 0.60]
        bars = []
        for _, x in live.iterrows():
            name = x["label"].replace(" ()", "")
            tag = ""
            for suffix in (" (last yr)", " (two yrs ago)"):
                if name.endswith(suffix):
                    name, tag = name[: -len(suffix)], suffix.strip(" ()")
            bars.append(meter(name, tag, x["solo"]))
        names = ", ".join(sorted({x["label"].replace(" ()", "")
                                  .replace(" (last yr)", "").replace(" (two yrs ago)", "")
                                  for _, x in dead.iterrows()}))
        cols.append(f"""<div class="levpos">
          <div class="levhead"><h4>{pos}</h4>
            <span class="levauc">full model {g['auc_base'].iat[0]:.3f} · n={g['n'].iat[0]}</span></div>
          {''.join(bars)}
          <div class="deadlist"><span class="label">No signal on its own</span>
            <p class="levnote">{e(names)}</p></div>
        </div>""")
    return f"""<section>
  <hr class="hash">
  <h2>What actually predicts it</h2>
  <p class="sec-intro">Every indicator, scored alone, leave-one-season-out. The
  number is the area under the ROC curve — 0.50 is a coin flip, 0.90 means that
  given one top-5 season and one that was not, the indicator ranks them correctly
  nine times in ten. This is the honest ranking: in-sample lift flatters anything
  that correlates with volume, and out of sample most of it does not survive.</p>
  <div class="lev">{''.join(cols)}</div>
  <div class="grid2" style="margin-top:36px">
    <div class="card pad"><span class="label">The uncomfortable finding</span>
      <p style="margin:8px 0 0">The strongest single indicator at three of four
      positions is <b>last year's points per game</b>. Not an efficiency metric, not
      a usage rate — the fantasy score itself. Everything else on this page earns its
      place by telling you <i>which</i> good season was real: target share and yards
      per route separate a receiver who earned his points from one who caught six
      touchdowns on forty targets.</p></div>
    <div class="card pad"><span class="label">Tested and rejected</span>
      <p style="margin:8px 0 0">A coaching change, a move to a better quarterback,
      a team change and a player's draft round were all tested as features. Adding
      a <b>coaching change made the model worse at every position</b> (QB 0.710 →
      0.696). A quarterback upgrade was worth nothing once the box score was known.
      Two survived: a receiver who <b>missed most of last season</b> (0.922 → 0.929,
      now in the model) and a <b>quarterback changing teams</b> (0.710 → 0.737, left
      out — next year's roster is not in this data).</p>
      <p style="margin:12px 0 0"><b>Also rejected: how he finished.</b> Season
      totals hide whether a player was steady or surging, so the last six games of
      each prior season were rebuilt from the weekly files and tested. They add
      nothing at any position — WR 0.929 → 0.928, TE 0.881 → 0.862 with all five
      late-window features. "He finished strong" is a story, not a signal.</p></div>
  </div>
</section>
"""


def pips(n: int, total: int, label: str) -> str:
    dots = "".join(f'<span class="pip{" on" if i < n else ""}"></span>'
                   for i in range(total))
    return f'<div class="pips">{dots}</div><div class="piplab">{n}/{total} {e(label)}</div>'


def row(r: pd.Series, pos: str) -> str:
    miss = r["missing"]
    leapcell = (pips(int(r["leaper_markers"]), int(r["leaper_total"]), "leaper marks")
                if pd.notna(r["leaper_markers"])
                # Leaper marks only mean something for players coming from
                # outside the prior top 12. Say which, not what he is.
                else f'<div class="na">top 12 in {LAST_SEASON}</div>')
    stale = ("" if r["gates_scored_on"] == LAST_SEASON
             else " · no full season to score" if not r["gates_scored_on"]
             else f" · gates from {int(r['gates_scored_on'])}")
    body = (f'<div class="clean">clears every gate</div>' if miss == "-"
            else f'<div class="pmiss">short on <b>{e(miss.lower())}</b></div>')
    return f"""<div class="row">
  <div class="pnum">{r['prob']:.2f}</div>
  <div>
    <div class="pname">{e(r['player'])}</div>
    <div class="pmeta">{e(r['team'])} · age {r['age']:.0f} · was {e(pos)}{int(r['last_finish'])}{stale}</div>
    {body}
  </div>
  <div class="cellpips">{pips(int(r['gates_cleared']), int(r['gates_total']), 'gates')}</div>
  <div class="cellprob">{leapcell}</div>
</div>"""


def build(board: pd.DataFrame, counts: dict) -> str:
    secs = []
    for pos in POS_ORDER:
        b = board[board["position"] == pos]
        b = b[b["tier"] < "E - "]
        bands = []
        for t in ["A - target", "B - strong", "C - leaper watch", "D - fringe"]:
            grp = b[b["tier"] == t]
            if not len(grp):
                continue
            bands.append(f"""<div class="tierband">
              <div class="tierhead"><div class="tiername">{e(t.split(' - ')[1].title())}</div>
              <div class="tierdesc">{e(TIER_NOTE[t])}</div></div>
              {''.join(row(r, pos) for _, r in grp.iterrows())}</div>""")
        secs.append(f"""<section class="chapter" id="{pos.lower()}">
          <hr class="hash">
          <div class="chead"><div class="pmark">{pos}</div>
            <div class="txt"><h3>{e(POS_NAME[pos])}</h3>
            <div class="sub">{counts[pos]} returning candidates scored · {len(b)} make the board</div></div>
          </div>
          <p class="note">{e(POS_NOTE[pos])}</p>
          {''.join(bands)}
        </section>""")

    return f"""<title>2026 Draft Target Board</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap">
<style>{CSS}{EXTRA}</style>
<div class="wrap">
<header class="top">
  <div class="eyebrow"><span class="label">{TARGET} season · full PPR</span>
    <span class="label" style="color:var(--mark-ink)">Every returning candidate, scored</span></div>
  <h1>Draft target board</h1>
  <p class="deck">Every player who cleared a volume floor in either of the last two
  seasons, run through the positional model and the top-5 gates. No hand-picking —
  the tiers fall out of the numbers.</p>
  <div class="meta">
    <div><b>{sum(counts.values())}</b><span class="label">candidates scored</span></div>
    <div><b>{len(board[board['tier'] < 'E - '])}</b><span class="label">make the board</span></div>
    <div><b>{len(board[board['tier'].str.startswith('A')])}</b><span class="label">in the target tier</span></div>
    <div><b>0.93</b><span class="label">best out-of-sample AUC</span></div>
  </div>
</header>

{disagreement_section()}

{leverage_section()}

<section>
  <h2>How to read a row</h2>
  <p class="sec-intro">Three numbers, and they answer different questions.</p>
  <div class="grid2">
    <div class="card pad"><span class="label">The big number</span>
      <p style="margin:8px 0 0"><b>Probability of a top-5 finish</b>, from a model
      scored leave-one-season-out — every season predicted by a version that never
      trained on it. It is calibrated: across eleven seasons, players scored near
      0.30 finished top-5 about 30% of the time. This is the only figure here
      validated out of sample, so it sets the tier.</p></div>
    <div class="card pad"><span class="label">Gates</span>
      <p style="margin:8px 0 0"><b>How much of the elite in-season profile his most
      recent played season looked like.</b> Descriptive, not held out — a miss is a
      question to answer, not a disqualification. A player who missed last season is
      scored on the one before, and the row says so.</p></div>
    <div class="card pad"><span class="label">Leaper marks</span>
      <p style="margin:8px 0 0"><b>How closely he matches the players who jumped
      into the top 5 from outside the prior top 12.</b> Roughly 40% of all elite
      finishes came from there, so this is the late-round signal. It is shown only
      for players in that lane — the bars sit at the leapers' own medians, so anyone
      who was already top-12 clears all of them and the count would mean nothing.</p></div>
    <div class="card pad"><span class="label">What is missing</span>
      <p style="margin:8px 0 0">The specific gates his prior year failed. Read it as
      the thesis you are buying: something has to change for that line to clear.</p></div>
  </div>
  <div class="callout"><p><b>The route estimate is the one metric to discount.</b>
  Public data has no route counts, so routes come from snap share × team dropbacks.
  Receivers who leave the field on run downs — Nacua and Smith-Njigba most
  obviously — run routes on a far higher share of dropbacks than their snap share
  implies, so a "routes per game" miss on that kind of player is usually the proxy
  failing, not the player.</p></div>
</section>

{''.join(secs)}

<section>
  <hr class="hash">
  <h2 style="margin-top:44px">Before you use it</h2>
  <ul class="tight">
    <li><b>Nobody here is a lock.</b> The top score on the whole board is
      {board['prob'].max():.2f} — even that one misses roughly one year in ten, and
      below the first handful of names the odds fall away fast. The base rate at
      wide receiver is 4.6%, so the very top of this board is a large edge on a
      small chance.</li>
    <li><b>The pool quietly drops the injured.</b> A player has to log a scoreable
      season to be counted, so 173 receiver-seasons, 138 running backs and 82
      tight ends vanished from the denominator after one qualifying year. Counting
      those as failures, the real receiver base rate is 4.0%, not 4.6% — and every
      probability here is a shade optimistic for the same reason.</li>
    <li><b>It cannot see a job that did not exist yet.</b> Rookies have no NFL
      history to score and are structurally invisible. Two seasons of lookback
      closed most of the injury gap — 86–94% of past top-5 seasons are now
      reachable — but a first-year player never will be.</li>
    <li><b>It cannot see availability.</b> Suspensions, holdouts and training-camp
      injuries are not in the data. Anyone facing league discipline or rehabbing an
      injury is scored as though he plays a full season, which is exactly when this
      board is most wrong.</li>
    <li><b>Team context is last year's.</b> Anyone who changed teams this offseason
      still carries his old offense's scoring rank and quarterback quality.</li>
    <li><b>Story lines are not in it, and mostly should not be.</b> A coaching
      change, a move to a better quarterback and a change of team were each tested
      as model features. A coaching change made the model <i>worse</i> at every
      position. The one narrative that earned a place is a receiver who missed most
      of last season, which the box-score features over-punish on their own.</li>
    <li><b>Efficiency does not rescue a small role.</b> 176 receiver-seasons had a
      prior year under a 15% target share and 50% snaps. None finished top-5 the
      next year. None finished top-12.</li>
  </ul>
</section>

<footer>
  <hr class="hash" style="margin-bottom:26px">
  <p>Built from <a href="https://github.com/nflverse/nflverse-data">nflverse</a>
  play-by-play, 2015–{LAST_SEASON}. Method, thresholds and the full pipeline are in
  the repository; <span class="mono">python src/target_board.py</span> regenerates
  every row on this page.</p>
</footer>
</div>"""


def main() -> None:
    board = pd.read_csv(OUTPUT / f"target_board_{TARGET}.csv")
    counts = board.groupby("position").size().to_dict()
    out = OUTPUT / "target_board.html"
    out.write_text(build(board, counts), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
