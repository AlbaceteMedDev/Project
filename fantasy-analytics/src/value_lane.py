"""The part of the board that is worth anything.

Sorting by raw probability puts the best players on top, which is both correct
and useless - you already know Ja'Marr Chase is good, and you will pay for him.
The question a draft actually asks is narrower: among players nobody is paying
up for, does the model know anything?

Three nested lanes, each one stripping out more of what the market has already
priced:

    all         every scored candidate
    cheap       no top-12 finish last season
    strict      no top-12 finish in EITHER of the last two seasons

The strict lane is the honest test. Everybody in it has been, recently and
publicly, not a star.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import model as M
from config import LAST_SEASON, OUTPUT

POS = ["WR", "RB", "TE", "QB"]
TAKE = 3  # how many the model is allowed to pick per season per lane


def lanes(r: pd.DataFrame) -> dict[str, pd.Series]:
    """Boolean masks, loosest first. NaN means he did not play - also not a star."""
    p1 = (r["p1_pos_rank"] > 12) | r["p1_pos_rank"].isna()
    p2 = (r["p2_pos_rank"] > 12) | r["p2_pos_rank"].isna()
    return {"all": pd.Series(True, index=r.index), "cheap": p1, "strict": p1 & p2}


def backtest(df: pd.DataFrame, pf: pd.DataFrame) -> list[dict]:
    top12 = df[["player_id", "season", "top12"]]
    out = []
    for pos in POS:
        d = M.pool(pf, pos)
        r = M.loso(d, pos)
        r = (r.merge(d[["player_id", "season", "p1_pos_rank", "p2_pos_rank"]],
                     on=["player_id", "season"], how="left")
              .merge(top12, on=["player_id", "season"], how="left"))
        for name, mask in lanes(r).items():
            g = r[mask].copy()
            g["rk"] = g.groupby("season")["prob"].rank(ascending=False, method="first")
            picks = g[g["rk"] <= TAKE]
            out.append(dict(
                pos=pos, lane=name, n_per_season=round(g.groupby("season").size().mean()),
                base5=g["top5"].mean(), hit5=picks["top5"].mean(),
                base12=g["top12"].mean(), hit12=picks["top12"].mean(),
                # the names it actually produced, so the claim is checkable
                picks=[dict(season=int(x.season), player=x.player_display_name,
                            rank=int(x.pos_rank), hit5=bool(x.top5), hit12=bool(x.top12))
                       for _, x in picks.sort_values(["season", "rk"]).iterrows()]))
    return out


def upcoming_lane(df: pd.DataFrame, pf: pd.DataFrame) -> list[dict]:
    """The strict lane for the season that has not happened yet."""
    recent = (df[df["season"].isin([LAST_SEASON - 1, LAST_SEASON])]
                .groupby("player_id")["pos_rank"].min().rename("best_recent").reset_index())
    out = []
    for pos in POS:
        d = M.pool(pf, pos)
        f = M.features(pos)
        m = M.make_model()
        m.fit(d[f], d["top5"])
        up = M.upcoming(df, pos).copy()
        up["prob"] = m.predict_proba(up[f])[:, 1]
        up = up.merge(recent, on="player_id", how="left")
        lane = up[(up["best_recent"] > 12) | up["best_recent"].isna()]
        for _, x in lane.sort_values("prob", ascending=False).head(7).iterrows():
            out.append(dict(pos=pos, player=x.player_display_name, team=str(x.team),
                            age=round(float(x.age), 1), prob=float(x.prob),
                            best_recent=(int(x.best_recent)
                                         if pd.notna(x.best_recent) else None),
                            last_games=(int(x.p1_games) if pd.notna(x.p1_games) else 0)))
    return out


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = M.frame(df)
    data = dict(take=TAKE, target=LAST_SEASON + 1,
                backtest=backtest(df, pf), upcoming=upcoming_lane(df, pf))
    (OUTPUT / "value_lane.json").write_text(json.dumps(data, indent=1))

    print(f"{'pos':4s} {'lane':8s} {'n/yr':>5s} {'base top5':>10s} {'picks':>7s} "
          f"{'base top12':>11s} {'picks':>7s}")
    for row in data["backtest"]:
        print(f"{row['pos']:4s} {row['lane']:8s} {row['n_per_season']:>5d} "
              f"{row['base5']:>10.1%} {row['hit5']:>7.1%} "
              f"{row['base12']:>11.1%} {row['hit12']:>7.1%}")
    print(f"\nwrote {OUTPUT / 'value_lane.json'}")


if __name__ == "__main__":
    main()
