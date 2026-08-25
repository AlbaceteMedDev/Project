"""Where the model and last season's box score disagree.

Sorting the board by probability puts the best players on top, which you already
knew. Filtering it by last year's finish rank produces bad starters, which is
worse than useless - a tight end who finished 18th is cheap because he is not
good, and the model correctly says so.

The cut that means something is the intersection: a player whose LAST SEASON was
outside the top 12, whom the model nonetheless rates highly in absolute terms.
That is a small list - one to three players a position per year - and it is where
the instrument is saying something the previous season does not.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import model as M
from config import LAST_SEASON, OUTPUT, TARGET, TARGET_N

POS = ["WR", "RB", "TE", "QB"]
STEPS = [0.10, 0.15, 0.20, 0.25]
# Below this the list stops being players you would actually draft.
FLOOR = 0.15


def behind(r: pd.DataFrame) -> pd.Series:
    """Last season outside the top 12 - a season not played counts."""
    return (r["p1_pos_rank"] > 12) | r["p1_pos_rank"].isna()


def backtest(df: pd.DataFrame, pf: pd.DataFrame) -> list[dict]:
    top12 = df[["player_id", "season", "top12"]]
    out = []
    for pos in POS:
        d = M.pool(pf, pos)
        r = (M.loso(d, pos)
              .merge(d[["player_id", "season", "p1_pos_rank"]],
                     on=["player_id", "season"], how="left")
              .merge(top12, on=["player_id", "season"], how="left"))
        lane = r[behind(r)]
        seasons = r["season"].nunique()
        rows = [dict(threshold=None, n=len(lane), per_season=len(lane) / seasons,
                     hit5=lane[TARGET].mean(), hit12=lane["top12"].mean())]
        for th in STEPS:
            g = lane[lane["prob"] >= th]
            if len(g) < 8:      # below this the cell is a rounding error
                continue
            rows.append(dict(threshold=th, n=len(g), per_season=len(g) / seasons,
                             hit5=g[TARGET].mean(), hit12=g["top12"].mean()))
        picked = lane[lane["prob"] >= FLOOR].sort_values(["season", "prob"],
                                                         ascending=[True, False])
        out.append(dict(pos=pos, rows=rows, floor=FLOOR,
                        names=[dict(season=int(x.season), player=x.player_display_name,
                                    prob=round(float(x.prob), 2),
                                    prior=int(x.p1_pos_rank) if pd.notna(x.p1_pos_rank) else None,
                                    rank=int(x.pos_rank), hit5=bool(x[TARGET]))
                               for _, x in picked.iterrows()]))
    return out


def upcoming(df: pd.DataFrame, pf: pd.DataFrame) -> list[dict]:
    out = []
    for pos in POS:
        d = M.pool(pf, pos)
        f = M.features(pos)
        m = M.make_model()
        m.fit(d[f], d[TARGET])
        up = M.upcoming(df, pos).copy()
        up["prob"] = m.predict_proba(up[f])[:, 1]
        g = up[(up["prev_finish"] > 12) & (up["prob"] >= FLOOR)]
        for _, x in g.sort_values("prob", ascending=False).iterrows():
            out.append(dict(pos=pos, player=x.player_display_name, team=str(x.team),
                            age=round(float(x.age), 1), prob=float(x.prob),
                            prior=int(x.prev_finish),
                            last_games=int(x.p1_games) if pd.notna(x.p1_games) else 0))
    return out


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = M.frame(df)
    data = dict(floor=FLOOR, target=LAST_SEASON + 1,
                backtest=backtest(df, pf), upcoming=upcoming(df, pf))
    (OUTPUT / "disagreement.json").write_text(json.dumps(data, indent=1))

    for b in data["backtest"]:
        print(f"\n{b['pos']}")
        for r in b["rows"]:
            lab = "any (base rate)" if r["threshold"] is None else f">= {r['threshold']:.2f}"
            print(f"   {lab:16s} {r['per_season']:>5.1f}/yr  "
                  f"top-{TARGET_N} {r['hit5']:>6.1%}  top-12 {r['hit12']:>6.1%}")
    print(f"\nwrote {OUTPUT / 'disagreement.json'}")


if __name__ == "__main__":
    main()
