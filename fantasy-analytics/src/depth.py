"""Where a player sits on his team's depth chart before the season starts.

This project spent its whole life inferring role from last year's box score,
while nflverse published the actual depth chart the entire time. A box score
says what a player did; the depth chart says what the coaching staff currently
intends, which is the one piece of forward-looking information in public data.

Each season file carries snapshots from August through the following March, so
the preseason chart is the last snapshot taken before week one. Files are large
and are reduced to the four fantasy positions and deleted as we go.
"""
from __future__ import annotations

import urllib.request

import pandas as pd

from config import NFLVERSE, OUTPUT, RAW, SEASONS

POS = ["QB", "RB", "WR", "TE"]
OUT = RAW / "depth_preseason.csv"


def _modern(d: pd.DataFrame, season: int) -> pd.DataFrame | None:
    """2025 on: dated snapshots. Take the newest one still inside the preseason."""
    d["dt"] = pd.to_datetime(d["dt"], errors="coerce", utc=True)
    pre = d[(d["dt"] >= f"{season}-07-15") & (d["dt"] < f"{season}-09-12") &
            d["pos_abb"].isin(POS) & d["gsis_id"].notna()]
    if pre.empty:
        return None
    pre = (pre.sort_values("dt")
              .drop_duplicates(["team", "pos_abb", "gsis_id"], keep="last"))
    print(f"  {season}: {len(pre):>5,} rows, chart of {pre['dt'].max().date()}")
    return pre[["gsis_id", "player_name", "team", "pos_abb", "pos_rank"]].rename(
        columns={"gsis_id": "player_id", "pos_abb": "pos", "pos_rank": "depth_rank"})


def _legacy(d: pd.DataFrame, season: int) -> pd.DataFrame | None:
    """2014-2024: one chart per week. Week 1 is the chart the season opened on."""
    pre = d[(d["week"] == 1) & (d["game_type"] == "REG") &
            d["position"].isin(POS) & d["gsis_id"].notna()]
    if pre.empty:
        return None
    pre = pre.drop_duplicates(["club_code", "position", "gsis_id"], keep="first")
    print(f"  {season}: {len(pre):>5,} rows, week 1 chart")
    pre = pre.copy()
    pre["player_name"] = pre["full_name"]
    return pre[["gsis_id", "player_name", "club_code", "position", "depth_team"]].rename(
        columns={"gsis_id": "player_id", "club_code": "team",
                 "position": "pos", "depth_team": "depth_rank"})


def season_snapshot(season: int) -> pd.DataFrame | None:
    """The depth chart a season started on, whichever schema it is published in."""
    tmp = RAW / f"_dc_{season}.csv"
    try:
        urllib.request.urlretrieve(
            f"{NFLVERSE}/depth_charts/depth_charts_{season}.csv", tmp)
    except Exception as ex:
        print(f"  {season}: unavailable ({ex})")
        return None
    try:
        d = pd.read_csv(tmp, low_memory=False)
        out = _modern(d, season) if "dt" in d.columns else _legacy(d, season)
        if out is None:
            print(f"  {season}: no preseason snapshot")
            return None
        out = out.copy()
        out["season"] = season
        return out
    finally:
        tmp.unlink(missing_ok=True)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    frames = [x for s in list(SEASONS) + [max(SEASONS) + 1]
              if (x := season_snapshot(s)) is not None]
    d = pd.concat(frames, ignore_index=True)
    d["depth_rank"] = pd.to_numeric(d["depth_rank"], errors="coerce")
    d.to_csv(OUT, index=False)
    print(f"\nwrote {OUT}  ({len(d):,} player-season rows, "
          f"{d.season.min()}-{d.season.max()})")


if __name__ == "__main__":
    main()
