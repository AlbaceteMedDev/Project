"""How a player finished the season, not just what he totalled.

A season total is a single number, so a receiver who scored evenly all year and
one who was a WR40 through October and a WR8 after it are the same row. The
second player is the one who becomes a top-5 finisher, and this project threw
that distinction away by aggregating to season level before ever looking.

Builds a late-window view from the weekly files - the last six games a player
actually played - and asks whether it says anything the season total does not.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import OUTPUT, RAW, SEASONS

WINDOW = 6      # games at the end of the year that define "how he finished"
MIN_GAMES = 6   # below this there is no meaningful split


def weekly() -> pd.DataFrame:
    """Regular-season weekly rows for the four fantasy positions."""
    frames = []
    for s in SEASONS:
        f = RAW / f"stats_{s}.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f, low_memory=False)
        d = d[(d["season_type"] == "REG") &
              d["position"].isin(["QB", "RB", "WR", "TE", "FB", "HB"])]
        frames.append(d[["player_id", "player_display_name", "position", "season",
                         "week", "team", "fantasy_points_ppr", "targets",
                         "target_share", "carries"]])
    w = pd.concat(frames, ignore_index=True)
    w["position"] = w["position"].replace({"FB": "RB", "HB": "RB"})
    # a player traded mid-year keeps one row per week, which is what we want
    return w.sort_values(["player_id", "season", "week"])


def splits(w: pd.DataFrame) -> pd.DataFrame:
    """Per player-season: full-year rate, the last six games, and the gap."""
    rows = []
    for (pid, season), g in w.groupby(["player_id", "season"], sort=False):
        g = g[g["fantasy_points_ppr"].notna()]
        n = len(g)
        if n < MIN_GAMES:
            continue
        late, early = g.tail(WINDOW), g.head(max(1, n - WINDOW))
        rows.append(dict(
            player_id=pid, season=season, pos=g["position"].iat[0],
            player=g["player_display_name"].iat[0], gp=n,
            ppg=g["fantasy_points_ppr"].mean(),
            late_ppg=late["fantasy_points_ppr"].mean(),
            early_ppg=early["fantasy_points_ppr"].mean(),
            late_tgt_share=late["target_share"].mean(),
            tgt_share=g["target_share"].mean(),
        ))
    d = pd.DataFrame(rows)
    d["ramp"] = d["late_ppg"] - d["early_ppg"]
    d["tgt_ramp"] = d["late_tgt_share"] - d["tgt_share"]
    # Where he ranked on each basis, within his position and season. The point of
    # the late rank is that it is often nowhere near the season rank.
    for col, out in [("ppg", "rank_ppg"), ("late_ppg", "rank_late")]:
        d[out] = (d.groupby(["season", "pos"])[col]
                    .rank(ascending=False, method="min").astype(int))
    return d


def main() -> None:
    d = splits(weekly())
    d.to_csv(OUTPUT / "trajectory.csv", index=False)
    print(f"{len(d)} player-seasons with a late-window split\n")
    print("Biggest late-season risers, all positions, 2016 on "
          "(season rank -> last-six-games rank):\n")
    top = d[(d["season"] >= 2016) & (d["gp"] >= 10)].copy()
    top["jump"] = top["rank_ppg"] - top["rank_late"]
    for _, r in top.nlargest(15, "jump").iterrows():
        print(f"  {r.season}  {r.player[:24]:25s} {r.pos:3s} "
              f"{r.pos}{r.rank_ppg:>3d} -> {r.pos}{r.rank_late:<3d} "
              f"({r.early_ppg:>5.1f} -> {r.late_ppg:>5.1f} ppg)")
    print(f"\nwrote {OUTPUT / 'trajectory.csv'}")


if __name__ == "__main__":
    main()
