"""Render the target board as a self-contained page, keyed off target_board.csv."""
from __future__ import annotations

import html
import json

import pandas as pd

from config import LAST_SEASON, OUTPUT, RAW, TARGET_N
from config import TARGET as TARGET_COL
from report import CSS, POS_NAME, e, pct

TARGET = LAST_SEASON + 1
POS_ORDER = ["WR", "RB", "TE", "QB"]

TIER_NOTE = {k: v.format(N=TARGET_N) for k, v in {
    "A - target": "Three times the rate of the field at this position or better. "
                  "The model never saw the season it is scoring, and this band is "
                  "where its hit rate lives.",
    "B - strong": "Twice the field or better. Most will still miss — a top-{N} "
                  "finish happens to 7-22% of the pool depending on position — but "
                  "the profile supports the bet.",
    "C - leaper watch": "Outside last year's top 12, but matching the profile of "
                        "players who jumped into the top {N} anyway. The late-round lane.",
    "D - fringe": "Above the field but not by much. Enough profile to roster, not "
                  "enough to target.",
}.items()}

POS_SHAPE = {
    "WR": "Five gates, and about two or three receivers a year clear all of them. "
          "The most trustworthy board here.",
    "RB": "Volume is assigned rather than earned, so the gates are looser and the "
          "blind spot is bigger — a share of elite back seasons come from players "
          "the last two years could not see at all.",
    "TE": "The position where last year tells you the most, and where the leaper "
          "bar sits lowest.",
    "QB": "Only two honest gates survive, because nearly every quarterback stat "
          "restates the fantasy score. The weakest board here — though the "
          "preseason depth chart helps more at this position than any other.",
}


def rookie_section() -> str:
    """The class the main model cannot score at all."""
    r = pd.read_csv(OUTPUT / f"rookie_board_{TARGET}.csv")
    cols = []
    for pos in POS_ORDER:
        g = r[r["pos"] == pos].nlargest(5, "raw_prob")
        body = "".join(
            f'<div class="p1"><div class="pn">{e(x.player)}'
            f'<small>{e(str(x.team))} · pick {int(x["pick"])} · '
            f'{pos}{int(x.depth_rank) if pd.notna(x.depth_rank) else "?"} on the chart · '
            f'{x.vacated_share:.0%} vacated</small></div>'
            f'<div class="pv">{x.prob:.2f}{"*" if x.above_tested_range else ""}</div>'
            f'</div>' for _, x in g.iterrows())
        cols.append(f'<div><div class="levhead"><h4>{pos}</h4></div>{body}</div>')
    return f"""<section>
  <hr class="hash">
  <h2>The rookies</h2>
  <p class="sec-intro">A first-year player has no NFL box score, so the main model
  cannot see him and drops him from every table above. He is scored here instead on
  the four things that <i>are</i> knowable in August: where the league drafted him,
  where he sits on his team's depth chart, how much work at his position just left
  the building, and how good the offence around him was. None of it is his own
  production, because he has none.</p>
  <div class="picks">{''.join(cols)}</div>
  <div class="callout"><p><b>Read these more sceptically than anything else here.</b>
  The model separates rookies well — AUC 0.76 at receiver to 0.92 at tight end, and
  it is calibrated by draft round — but elite rookie seasons are rare enough that it
  is fitted on a few dozen of them. Above 0.35 it has three historical observations,
  so scores are published capped at that line and marked with an asterisk. Two of
  those three did hit: Kyle Pitts and Brock Bowers.</p></div>
</section>
"""


def caveats(board: pd.DataFrame) -> str:
    """Every figure in the limits list, computed from the run that built the page.

    These were prose with numbers typed into it, and they were wrong within a day
    of the target moving from top-5 to top-8 - quoting a 4.6% base rate under a
    table that said 6.7%. Nothing here is remembered.
    """
    import model as M
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = M.frame(df)

    wr = M.pool(pf, "WR")
    wr_base = wr[TARGET_COL].mean()

    # players who logged one qualifying season and never appeared again: they
    # leave the denominator, which flatters every rate on this page
    dropped = {}
    for pos in POS_ORDER:
        d = df[df["fantasy_pos"] == pos]
        last = d.groupby("player_id")["season"].max()
        once = d.groupby("player_id").size() == 1
        gone = ((last < LAST_SEASON) & once).sum()
        dropped[pos] = int(gone)
    wr_adj = wr[TARGET_COL].sum() / (len(wr) + dropped["WR"])

    # how much of the historical target the two-year frame can even reach
    reach = {}
    for pos in POS_ORDER:
        d = pf[(pf["fantasy_pos"] == pos) & pf["season"].between(2016, LAST_SEASON)]
        elite = df[(df["fantasy_pos"] == pos) & df["season"].between(2016, LAST_SEASON)
                   & (df[TARGET_COL] == 1)]
        seen = d[M.qualifies(d, pos)]
        reach[pos] = len(seen.merge(elite[["player_id", "season"]],
                                    on=["player_id", "season"])) / max(len(elite), 1)

    # depth chart separation, measured rather than recalled (frame() already
    # carries depth_rank, so re-merging would only produce suffixed duplicates)
    w = pf[(pf["fantasy_pos"] == "WR") & pf["season"].between(2016, LAST_SEASON)]
    w = w[M.qualifies(w, "WR")]
    d1 = w[w["depth_rank"] == 1][TARGET_COL].mean()
    d2 = w[w["depth_rank"] == 2][TARGET_COL].mean()

    rk = pd.read_csv(OUTPUT / "rookie_scores.csv")
    rk_hits = int(rk[TARGET_COL].sum())

    # availability, measured from the week-one rosters rather than assumed away
    av = pd.read_csv(RAW / "week1_rosters.csv", low_memory=False)
    ah = av[av["season"] <= LAST_SEASON].merge(
        df[["player_id", "season", TARGET_COL]], on=["player_id", "season"], how="left")
    act = ah[ah["status"] == "ACT"][TARGET_COL].fillna(0).mean()
    nonact = int((ah["status"] != "ACT").sum())
    gone = board[board["tier"].str.startswith("X")]
    removed = len(gone)
    examples = ", ".join(gone.nlargest(3, "prob")["player"].tolist())

    return f"""  <ul class="tight">
    <li><b>Nobody here is a lock.</b> The top score on the whole board is
      {board['prob'].max():.2f}, and below the first handful of names the odds fall
      away fast. A top-{TARGET_N} receiving season happens to {wr_base:.1%} of the
      qualifying pool, so the very top of this board is a large edge on a modest
      chance — not a promise.</li>
    <li><b>The pool quietly drops the injured.</b> A player has to log a scoreable
      season to be counted, so {dropped['WR']} receivers, {dropped['RB']} running
      backs and {dropped['TE']} tight ends who managed one qualifying year and never
      another have left the denominator. Counting them as failures puts the real
      receiver base rate at {wr_adj:.1%} rather than {wr_base:.1%}, and every
      probability here is optimistic by roughly that ratio.</li>
    <li><b>Rookies are scored separately, and badly.</b> They have no NFL history,
      so the main model cannot see them at all; a second model scores them on draft
      capital, depth-chart rank, vacated opportunity and offence quality. It works
      — AUC 0.76 to 0.92, and calibrated by round — but it is built on
      {rk_hits} hits in eleven years, and above 0.35 it has three observations
      total. Rookie scores are published capped at that line and flagged, because
      the number above it would be invented.</li>
    <li><b>Two seasons of lookback still miss some of it.</b> The frame can reach
      {min(reach.values()):.0%}–{max(reach.values()):.0%} of past top-{TARGET_N}
      seasons depending on position. The rest belong to players it had no history
      for.</li>
    <li><b>Availability is checked, and it is close to decisive.</b> Every row is
      matched against the published week-one roster. Since 2015, players who opened
      a season on the active list reached the target {act:.1%} of the time; every
      other status — released, reserve, retired, suspended — is <b>0.0%</b> across
      roughly {nonact:,} player-seasons. {removed} players on this board hold no
      {LAST_SEASON + 1} roster spot and are set aside rather than scored, among them
      {examples}. What is still missing is the softer end: a camp injury that has
      not yet moved anyone off the active list is invisible here.</li>
    <li><b>The depth chart is current; everything else is last year's.</b> Each row
      carries the player's rank on his team's August {LAST_SEASON + 1} chart — the only
      forward-looking fact here, and the sharpest. A receiver listed second finishes
      top-{TARGET_N} {d2:.1%} of the time against {d1:.1%} for the one listed first.
      Below the top slot the ordering is loose, especially at receiver where teams
      play three: the {LAST_SEASON + 1} Jaguars list Travis Hunter fourth. Read a low rank as
      a question, not a verdict.</li>
    <li><b>Team context is last year's.</b> Anyone who changed teams this offseason
      still carries his old offence's scoring rank and quarterback quality.</li>
    <li><b>Story lines are not in it, and mostly should not be.</b> A coaching
      change, a move to a better quarterback and a change of team were each tested
      as features. A coaching change made the model worse at every position. Two
      earned a place: a receiver who missed most of last season, and — at
      quarterback only — the depth chart.</li>
  </ul>"""


AUCS: dict[str, float] = {}


def pos_notes() -> dict[str, str]:
    """Model quality per position, measured now rather than remembered."""
    import model as M
    from sklearn.metrics import roc_auc_score
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = M.frame(df)
    out = {}
    for pos in POS_ORDER:
        d = M.pool(pf, pos)
        r = M.loso(d, pos)
        auc = roc_auc_score(r[TARGET_COL], r["prob"])
        AUCS[pos] = auc
        out[pos] = (f"{POS_SHAPE[pos]} A top-{TARGET_N} finish happens to "
                    f"{r[TARGET_COL].mean():.1%} of the qualifying pool in a given year; "
                    f"the model separates them at AUC {auc:.2f} out of sample, over "
                    f"{len(r):,} scored player-seasons.")
    return out


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
    # The headline sentence is built from the table rather than typed underneath it,
    # so it cannot disagree with the numbers directly above it.
    wr = by["WR"]["rows"]
    base = wr[0]
    best = max(wr[1:], key=lambda r: r["hit5"]) if len(wr) > 1 else base
    wr_line = (f'A receiver coming off a season outside the top 12 finishes '
               f'top-{TARGET_N} {base["hit5"]:.0%} of the time. The ones this model '
               f'rates at {best["threshold"]:.2f} or better did it '
               f'<b>{best["hit5"]:.0%} of the time</b> — about '
               f'{best["per_season"]:.0f} a year, across eleven seasons.')

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
  <div class="callout"><p><b>This is the sharpest thing on the page.</b> {wr_line}
  Tight end is the exception and the numbers there move around with the threshold,
  which is what a sample this size looks like; treat the TE rows as unproven.</p></div>
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
  given one top-{TARGET_N} season and one that was not, the indicator ranks them correctly
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
    dr = r.get("depth_rank")
    depth = ("" if pd.isna(dr) else f' · {pos}{int(dr)} on the chart')
    stale = ("" if r["gates_scored_on"] == LAST_SEASON
             else " · no full season to score" if not r["gates_scored_on"]
             else f" · gates from {int(r['gates_scored_on'])}")
    if pd.notna(dr) and int(dr) > 1:
        body = (f'<div class="pmiss"><b>Listed {pos}{int(dr)} on the August depth '
                f'chart.</b> Players listed second finish top-{TARGET_N} roughly 1% of the '
                f'time.</div>')
    else:
        body = ""
    body += (f'<div class="clean">clears every gate</div>' if miss == "-"
            else f'<div class="pmiss">short on <b>{e(miss.lower())}</b></div>')
    return f"""<div class="row">
  <div class="pnum">{r['prob']:.2f}</div>
  <div>
    <div class="pname">{e(r['player'])}</div>
    <div class="pmeta">{e(r['team'])} · age {r['age']:.0f} · was {e(pos)}{int(r['last_finish'])}{depth}{stale}</div>
    {body}
  </div>
  <div class="cellpips">{pips(int(r['gates_cleared']), int(r['gates_total']), 'gates')}</div>
  <div class="cellprob">{leapcell}</div>
</div>"""


def build(board: pd.DataFrame, counts: dict) -> str:
    POS_NOTE = pos_notes()
    best_auc = max(AUCS.values())
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
  seasons, run through the positional model and the top-{TARGET_N} gates. No hand-picking —
  the tiers fall out of the numbers.</p>
  <div class="meta">
    <div><b>{sum(counts.values())}</b><span class="label">candidates scored</span></div>
    <div><b>{len(board[board['tier'] < 'E - '])}</b><span class="label">make the board</span></div>
    <div><b>{len(board[board['tier'].str.startswith('A')])}</b><span class="label">in the target tier</span></div>
    <div><b>{best_auc:.2f}</b><span class="label">best out-of-sample AUC</span></div>
  </div>
</header>

{disagreement_section()}

{rookie_section()}

{leverage_section()}

<section>
  <h2>How to read a row</h2>
  <p class="sec-intro">Three numbers, and they answer different questions.</p>
  <div class="grid2">
    <div class="card pad"><span class="label">The big number</span>
      <p style="margin:8px 0 0"><b>Probability of a top-{TARGET_N} finish</b>, from a model
      scored leave-one-season-out — every season predicted by a version that never
      trained on it. It is calibrated: across eleven seasons, players scored near
      0.30 finished top-{TARGET_N} about 30% of the time. This is the only figure here
      validated out of sample, so it sets the tier.</p></div>
    <div class="card pad"><span class="label">Gates</span>
      <p style="margin:8px 0 0"><b>How much of the elite in-season profile his most
      recent played season looked like.</b> Descriptive, not held out — a miss is a
      question to answer, not a disqualification. A player who missed last season is
      scored on the one before, and the row says so.</p></div>
    <div class="card pad"><span class="label">Leaper marks</span>
      <p style="margin:8px 0 0"><b>How closely he matches the players who jumped
      into the top {TARGET_N} from outside the prior top 12.</b> Roughly 40% of all elite
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
{caveats(board)}
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
