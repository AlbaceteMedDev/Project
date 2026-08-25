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
          "season is scored by gates that never saw it. Model AUC 0.90, the most "
          "trustworthy board here.",
    "RB": "Volume is assigned, not earned, so the gates are looser and the blind "
          "spot is bigger: 24% of top-5 running back seasons came from players with "
          "no qualifying prior year at all.",
    "TE": "The position where last year tells you the most — a top-5 tight end "
          "repeats 43% of the time — and where the leaper bar is lowest. The only "
          "position whose gates did not degrade out of sample (86% fitted, 88% "
          "held out).",
    "QB": "Only two honest gates survive, because nearly every quarterback stat "
          "restates the fantasy score. AUC 0.68, and the gates fall to a 45% hit "
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
.clean{color:var(--good-ink); font-family:'IBM Plex Mono',monospace; font-size:12px;
  letter-spacing:.06em; text-transform:uppercase; font-weight:600; margin-top:3px}
@media (max-width:640px){
  .row{grid-template-columns:44px minmax(0,1fr); gap:12px}
  .row .cellpips,.row .cellprob{grid-column:2}
  .pnum{font-size:19px; text-align:left}
}
"""


def pips(n: int, total: int, label: str) -> str:
    dots = "".join(f'<span class="pip{" on" if i < n else ""}"></span>'
                   for i in range(total))
    return f'<div class="pips">{dots}</div><div class="piplab">{n}/{total} {e(label)}</div>'


def row(r: pd.Series, pos: str) -> str:
    miss = r["missing"]
    body = (f'<div class="clean">clears every gate</div>' if miss == "-"
            else f'<div class="pmiss">short on <b>{e(miss.lower())}</b></div>')
    return f"""<div class="row">
  <div class="pnum">{r['prob']:.2f}</div>
  <div>
    <div class="pname">{e(r['player'])}</div>
    <div class="pmeta">{e(r['team'])} · age {r['age']:.0f} · was {e(pos)}{int(r[f'{LAST_SEASON}_finish'])}</div>
    {body}
  </div>
  <div class="cellpips">{pips(int(r['gates_cleared']), int(r['gates_total']), 'gates')}</div>
  <div class="cellprob">{pips(int(r['leaper_markers']), int(r['leaper_total']), 'leaper marks')}</div>
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
  <p class="deck">Every player with a qualifying {LAST_SEASON} season, run through the
  positional model and the top-5 gates. No hand-picking — the tiers fall out of the
  numbers.</p>
  <div class="meta">
    <div><b>{sum(counts.values())}</b><span class="label">candidates scored</span></div>
    <div><b>{len(board[board['tier'] < 'E - '])}</b><span class="label">make the board</span></div>
    <div><b>{len(board[board['tier'].str.startswith('A')])}</b><span class="label">in the target tier</span></div>
    <div><b>0.90</b><span class="label">best out-of-sample AUC</span></div>
  </div>
</header>

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
      <p style="margin:8px 0 0"><b>How much of the elite in-season profile his last
      season already looked like.</b> Descriptive, not held out — a miss is a
      question to answer, not a disqualification.</p></div>
    <div class="card pad"><span class="label">Leaper marks</span>
      <p style="margin:8px 0 0"><b>How closely he matches the players who jumped
      into the top 5 from outside the prior top 12.</b> Roughly 40% of all elite
      finishes came from there, so this is the late-round signal.</p></div>
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
    <li><b>Nobody here is a lock.</b> The top score on the whole board is 0.77 —
      three in four of those seasons still missed. The base rate at wide receiver
      is 4.6%, so the very top of this board is a large edge on a small chance.</li>
    <li><b>The pool quietly drops the injured.</b> A player has to log a scoreable
      season to be counted, so 173 receiver-seasons, 138 running backs and 82
      tight ends vanished from the denominator after one qualifying year. Counting
      those as failures, the real receiver base rate is 4.0%, not 4.6% — and every
      probability here is a shade optimistic for the same reason.</li>
    <li><b>It cannot see a job that did not exist yet.</b> Every name needed a
      qualifying {LAST_SEASON} season to be scored. Rookies and players handed a
      role in the offseason are structurally invisible — and they accounted for
      24% of top-5 running back seasons and 16% at quarterback.</li>
    <li><b>Team context is last year's.</b> Anyone who changed teams this offseason
      still carries his old offense's scoring rank and quarterback quality.</li>
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
