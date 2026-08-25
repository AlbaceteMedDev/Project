"""Who is actually on a roster, which the box score cannot tell you.

The board spent its life scoring players who had retired, been released, or were
sitting on injured reserve, because production data has no opinion about whether
a man is employed. nflverse publishes week-one rosters with a status field, and
the status is close to decisive: across 2021-2025, not one fantasy-position
player who opened a season on anything other than the active list finished top-8.

Two traps, both of which caught me before I checked:

  Rookie codes look like injuries. Every 2026 player carrying R09 is a member of
  that year's draft class, so it reads as an unsigned-draftee designation, not a
  season-ending one. It is scored as neutral rather than disqualifying.

  Codes are not stable across years. Only the coarse status - ACT, RES, RET, CUT
  - is validated here, because the fine-grained abbreviations turn over and
  several in the current file have three observations in five prior seasons.

And one the roster file cannot fix on its own: it lags. Stefon Diggs is WR2 on
Washington's 24 August depth chart and absent from the week-one roster entirely,
along with twelve others an earlier version of this module struck off the board.
Employment is therefore the union of the two sources - a player on either is
employed - and only someone missing from both is set aside.
"""
from __future__ import annotations

import urllib.request

import pandas as pd

from config import LAST_SEASON, NFLVERSE, OUTPUT, RAW, TARGET

POS = ["QB", "RB", "WR", "TE", "FB", "HB"]
OUT = RAW / "week1_rosters.csv"
SEASONS = range(2015, LAST_SEASON + 2)


def fetch() -> pd.DataFrame:
    if OUT.exists():
        return pd.read_csv(OUT, low_memory=False)
    frames = []
    for s in SEASONS:
        tmp = RAW / f"_rw_{s}.csv"
        try:
            urllib.request.urlretrieve(
                f"{NFLVERSE}/weekly_rosters/roster_weekly_{s}.csv", tmp)
        except Exception as ex:
            print(f"  {s}: unavailable ({ex})")
            continue
        try:
            d = pd.read_csv(tmp, low_memory=False)
            d = d[(d["week"] == 1) & (d["game_type"] == "REG") &
                  d["position"].isin(POS)]
            frames.append(d[["season", "gsis_id", "full_name", "position", "team",
                             "status", "status_description_abbr"]])
            print(f"  {s}: {len(d):>5,} rows")
        finally:
            tmp.unlink(missing_ok=True)
    r = pd.concat(frames, ignore_index=True).rename(columns={"gsis_id": "player_id"})
    r.to_csv(OUT, index=False)
    return r


def rookie_codes(r: pd.DataFrame, season: int) -> set[str]:
    """Status codes held only by that season's draft class - not season-ending."""
    try:
        d = pd.read_csv(RAW / "draft_picks.csv", low_memory=False)
    except FileNotFoundError:
        return set()
    names = set(d[d["season"] == season]["pfr_player_name"].dropna())
    cur = r[(r["season"] == season) & (r["status"] != "ACT")]
    out = set()
    for code, g in cur.groupby("status_description_abbr"):
        if len(g) >= 3 and g["full_name"].isin(names).all():
            out.add(code)
    return out


def charted(season: int) -> set[str]:
    """Everyone on a recent depth chart - the dated, and fresher, of the two feeds."""
    d = pd.read_csv(RAW / "depth_preseason.csv")
    return set(d[d["season"] == season]["player_id"].dropna())


def main() -> None:
    r = fetch()
    ps = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    hist = r[r["season"] <= LAST_SEASON].merge(
        ps[["player_id", "season", "games", TARGET]],
        on=["player_id", "season"], how="left")
    hist["played"] = hist["games"].notna()

    print("\nWhat a week-one status was worth, by season played "
          f"({hist.season.min()}-{hist.season.max()}):\n")
    print(f"{'status':8s} {'n':>6s} {'played':>8s} {'median gm':>10s} "
          f"{'reached the target':>19s}")
    for st, g in hist.groupby("status"):
        if len(g) < 20:
            continue
        print(f"{st:8s} {len(g):>6d} {g['played'].mean():>8.0%} "
              f"{g['games'].median() if g['played'].any() else 0:>10.0f} "
              f"{g[TARGET].fillna(0).mean():>19.1%}")

    nxt = LAST_SEASON + 1
    cur = r[r["season"] == nxt]
    ok = rookie_codes(r, nxt)
    if ok:
        print(f"\nTreated as neutral for {nxt} (held only by that draft class): "
              f"{', '.join(sorted(ok))}")
    chart = charted(nxt)
    cur = cur.assign(
        available=lambda d: (d["status"] == "ACT")
                            | d["status_description_abbr"].isin(ok)
                            | d["player_id"].isin(chart))
    # players the roster feed never mentions but a current chart does
    extra = pd.DataFrame({"player_id": sorted(chart - set(cur["player_id"]))})
    if len(extra):
        extra = extra.assign(full_name=None, position=None, team=None,
                             status="CHART", status_description_abbr=None,
                             available=True)
        cur = pd.concat([cur, extra], ignore_index=True)
        print(f"\n{len(extra)} players are on a {nxt} depth chart but absent from "
              f"the roster feed; the chart is dated and the roster file is not, "
              f"so they count as employed.")
    cur[["player_id", "full_name", "position", "team", "status",
         "status_description_abbr", "available"]].to_csv(
        OUTPUT / f"availability_{nxt}.csv", index=False)
    print(f"\n{nxt}: {cur['available'].sum():,} of {len(cur):,} fantasy-position "
          f"players available; {(~cur['available']).sum()} are not.")
    print(f"wrote {OUTPUT / f'availability_{nxt}.csv'}")


if __name__ == "__main__":
    main()
