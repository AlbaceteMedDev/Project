"""What a bad season, and what a change in situation, actually does to next year.

The predictive model treats a season as a bag of numbers. It cannot tell a
receiver who tore an ACL in week four from one who lost his job to a rookie,
and it does not know when a player changed teams, quarterbacks or coaches. This
asks what those distinctions are worth.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import OUTPUT, RAW

df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
POS = ["QB", "RB", "WR", "TE"]
# The usage stat that defines "role" at each position.
ROLE = {"WR": "target_share", "TE": "target_share",
        "RB": "opportunity_share", "QB": "dropbacks"}


def hr(t: str) -> None:
    print(f"\n{'=' * 96}\n{t}\n{'=' * 96}")


def pairs() -> pd.DataFrame:
    """Every player-season joined to the one after it, whether or not it exists."""
    a = df[["player_id", "player_display_name", "fantasy_pos", "season", "team",
            "pos_rank", "games", "ppg_shrunk", "age", "exp", "top5", "top12",
            "target_share", "opportunity_share", "dropbacks", "snap_pct"]].copy()
    b = a.copy()
    b["season"] = b["season"] - 1
    b = b.rename(columns={c: f"n_{c}" for c in b.columns
                          if c not in ("player_id", "season")})
    return a.merge(b, on=["player_id", "season"], how="left")


def coach_table() -> pd.DataFrame:
    g = pd.read_csv(RAW / "games.csv", low_memory=False)
    g = g[g["game_type"].isin(["REG"])] if "game_type" in g else g
    home = g[["season", "home_team", "home_coach"]].rename(
        columns={"home_team": "team", "home_coach": "coach"})
    away = g[["season", "away_team", "away_coach"]].rename(
        columns={"away_team": "team", "away_coach": "coach"})
    both = pd.concat([home, away], ignore_index=True).dropna()
    # the coach who led the most games that season
    return (both.groupby(["season", "team"])["coach"]
                .agg(lambda s: s.mode().iat[0]).reset_index())


def team_qb() -> pd.DataFrame:
    q = df[df["fantasy_pos"] == "QB"].dropna(subset=["team"])
    idx = q.groupby(["season", "team"])["dropbacks"].idxmax()
    return q.loc[idx, ["season", "team", "player_id", "epa_per_dropback"]].rename(
        columns={"player_id": "qb_id", "epa_per_dropback": "qb_epa"})


# --------------------------------------------------------------- study A
def bounce_back(p: pd.DataFrame) -> None:
    hr("A — a down year is not one thing. What caused it decides what happens next.")
    print("Players who finished top-12 at their position, then fell outside the top 24\n"
          "the following year. Split by why, and scored on the year after that.\n")
    print(f"{'pos':4s} {'cause of the down year':26s} {'n':>4s} "
          f"{'top-5 next':>11s} {'top-12 next':>12s} {'median rank':>12s}")
    for pos in POS:
        d = p[(p["fantasy_pos"] == pos) & (p["pos_rank"] <= 12)].copy()
        role = ROLE[pos]
        # the down year is season N+1 relative to the top-12 year
        d = d[d["n_pos_rank"].isna() | (d["n_pos_rank"] > 24)]
        d["role_drop"] = 1 - (d[f"n_{role}"] / d[role])
        def cause(r):
            if pd.isna(r["n_pos_rank"]) or r["n_games"] < 12:
                return "injury / missed time"
            if r["role_drop"] >= 0.25:
                return "role taken away"
            return "role kept, output fell"
        d["cause"] = d.apply(cause, axis=1)
        # outcome is the season after the down year
        nxt = df[["player_id", "season", "pos_rank", "top5", "top12"]].copy()
        nxt["season"] = nxt["season"] - 2
        nxt = nxt.rename(columns={"pos_rank": "y2_rank", "top5": "y2_top5",
                                  "top12": "y2_top12"})
        d = d.merge(nxt, on=["player_id", "season"], how="left")
        for c in ["injury / missed time", "role taken away", "role kept, output fell"]:
            g = d[d["cause"] == c]
            if len(g) < 5:
                continue
            print(f"{pos:4s} {c:26s} {len(g):>4d} "
                  f"{g['y2_top5'].fillna(0).mean():>10.0%} "
                  f"{g['y2_top12'].fillna(0).mean():>11.0%} "
                  f"{g['y2_rank'].median():>12.0f}")
    print("\nA rank of NaN means he did not post a qualifying season at all; those\n"
          "count as failures, not as missing data.")


# --------------------------------------------------------------- study B
def rookie_year(p: pd.DataFrame) -> None:
    hr("B — does a bad rookie season mean anything?")
    print("Every player whose first qualifying season came at experience 0, bucketed\n"
          "by where he finished, then followed for three years.\n")
    print(f"{'pos':4s} {'rookie finish':16s} {'n':>4s} {'ever top-5 by yr 4':>19s} "
          f"{'ever top-12':>12s} {'best rank (median)':>19s}")
    for pos in POS:
        r = df[(df["fantasy_pos"] == pos) & (df["exp"] == 0) &
               (df["season"] <= 2022)].copy()
        for lo, hi, lab in [(1, 12, "top 12"), (13, 24, "13-24"),
                            (25, 48, "25-48"), (49, 999, "49+")]:
            g = r[(r["pos_rank"] >= lo) & (r["pos_rank"] <= hi)]
            if len(g) < 5:
                continue
            best, t5, t12 = [], [], []
            for _, row in g.iterrows():
                fut = df[(df["player_id"] == row["player_id"]) &
                         (df["season"] > row["season"]) &
                         (df["season"] <= row["season"] + 3) &
                         (df["fantasy_pos"] == pos)]
                best.append(fut["pos_rank"].min() if len(fut) else np.nan)
                t5.append(int((fut["top5"] == 1).any()) if len(fut) else 0)
                t12.append(int((fut["top12"] == 1).any()) if len(fut) else 0)
            print(f"{pos:4s} {lab:16s} {len(g):>4d} {np.mean(t5):>18.0%} "
                  f"{np.mean(t12):>11.0%} {np.nanmedian(best):>19.0f}")
        print()


# --------------------------------------------------------------- study C/D/E
def situation_changes(p: pd.DataFrame) -> None:
    hr("C/D/E — changing teams, coaches and quarterbacks")
    coaches = coach_table()
    qbs = team_qb()

    d = p.dropna(subset=["n_pos_rank", "team", "n_team"]).copy()
    d["changed_team"] = d["team"] != d["n_team"]

    d = d.merge(coaches.rename(columns={"coach": "coach_now"}),
                left_on=["season", "team"], right_on=["season", "team"], how="left")
    nxt_c = coaches.copy()
    nxt_c["season"] = nxt_c["season"] - 1
    d = d.merge(nxt_c.rename(columns={"coach": "coach_next", "team": "n_team"}),
                on=["season", "n_team"], how="left")
    d["changed_coach"] = (d["coach_now"] != d["coach_next"]) & d["coach_next"].notna()

    d = d.merge(qbs.rename(columns={"qb_id": "qb_now", "qb_epa": "qb_epa_now"}),
                on=["season", "team"], how="left")
    nq = qbs.copy()
    nq["season"] = nq["season"] - 1
    d = d.merge(nq.rename(columns={"qb_id": "qb_next", "qb_epa": "qb_epa_next",
                                   "team": "n_team"}),
                on=["season", "n_team"], how="left")
    d["changed_qb"] = (d["qb_now"] != d["qb_next"]) & d["qb_next"].notna()
    d["qb_upgrade"] = d["qb_epa_next"] - d["qb_epa_now"]

    d["moved"] = d["n_pos_rank"] - d["pos_rank"]   # positive = got worse

    print("Effect on next-season finish, among players who were top-24 the year before.")
    print("'Rank change' is negative when a player improved.\n")
    for pos in POS:
        s = d[(d["fantasy_pos"] == pos) & (d["pos_rank"] <= 24)]
        if len(s) < 30:
            continue
        print(f"  {pos}  (n={len(s)})")
        for label, mask in [
            ("stayed put", ~s["changed_team"]),
            ("changed teams", s["changed_team"]),
            ("same coach", ~s["changed_coach"]),
            ("new head coach", s["changed_coach"]),
        ]:
            g = s[mask]
            if len(g) < 8:
                continue
            print(f"    {label:18s} n={len(g):>3d}  rank change {g['moved'].median():>+5.0f}  "
                  f"top-5 next {g['n_top5'].mean():>4.0%}  top-12 next {g['n_top12'].mean():>4.0%}")
        if pos in ("WR", "TE"):
            for label, mask in [
                ("same QB", ~s["changed_qb"]),
                ("new QB, worse", s["changed_qb"] & (s["qb_upgrade"] < -0.02)),
                ("new QB, similar", s["changed_qb"] & s["qb_upgrade"].between(-0.02, 0.02)),
                ("new QB, better", s["changed_qb"] & (s["qb_upgrade"] > 0.02)),
            ]:
                g = s[mask]
                if len(g) < 8:
                    continue
                print(f"    {label:18s} n={len(g):>3d}  rank change {g['moved'].median():>+5.0f}  "
                      f"top-5 next {g['n_top5'].mean():>4.0%}  top-12 next {g['n_top12'].mean():>4.0%}")
        print()


if __name__ == "__main__":
    p = pairs()
    bounce_back(p)
    rookie_year(p)
    situation_changes(p)
