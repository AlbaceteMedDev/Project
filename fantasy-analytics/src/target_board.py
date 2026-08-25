"""Score every candidate for the upcoming season and tier the board.

Rows come from the two-year model in model.py, so a player who was elite two
seasons ago and hurt last season still gets scored - that class of player is
exactly what a one-year model deletes and the market does not.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import model
from analyze import FAMILIES, POOL_RULES, build_card, pool as gate_pool
from config import LAST_SEASON, OUTPUT

TARGET = LAST_SEASON + 1

# Medians of the players who jumped into the top 5 from outside the prior top 12.
LEAPER = {
    "WR": dict(target_share=.236, yprr_shrunk=2.072, air_yards_share=.331,
               snap_pct=.833, targets_pg=8.154),
    "TE": dict(target_share=.148, yprr_shrunk=1.376, rz_targets_share=.123,
               snap_pct=.632, targets_pg=4.867),
    "RB": dict(opportunity_share=.258, snap_pct=.566, target_share=.082,
               rz_carries_share=.403, touches_pg=15.308),
    "QB": dict(rush_att_pg=3.475, epa_per_dropback=.025, dropbacks=501.5,
               ppg_shrunk=14.636),
}


def tier(prob: float, leap: int, n_leap: int, prev_rank: float) -> str:
    """Bands are absolute probabilities, so 0.25 means the same thing everywhere:
    about one season in four with this profile finished top-5. Base rates differ
    by position, so an identical score is a much larger edge at receiver.
    """
    if prob >= 0.25:
        return "A - target"
    if prob >= 0.12:
        return "B - strong"
    if prob >= 0.06:
        if prev_rank > 12 and leap >= n_leap - 1:
            return "C - leaper watch"
        return "D - fringe"
    return "E - profile does not support it"


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = model.frame(df)
    gates_by_pos = {p: build_card(gate_pool(df, p), p, "top5", FAMILIES[p])["rules"]
                    for p in ["QB", "RB", "WR", "TE"]}
    # Gates describe a full season, so score them on the most recent season that
    # actually cleared the volume floor - not on a four-game injury year that
    # happens to be the latest row.
    def qualifying_seasons(pos: str) -> pd.DataFrame:
        d = df[df["fantasy_pos"] == pos].copy()
        for col, lo in POOL_RULES[pos].items():
            d = d[d[col] >= lo]
        return d.sort_values("season").drop_duplicates("player_id", keep="last")

    rows = []
    for pos in ["QB", "RB", "WR", "TE"]:
        train = model.pool(pf, pos)
        m = model.make_model()
        f = model.features(pos)
        m.fit(train[f], train["top5"])

        cand = model.upcoming(df, pos).copy()
        cand["prob"] = m.predict_proba(cand[f])[:, 1]
        leap = LEAPER[pos]
        gates = gates_by_pos[pos]
        recent = qualifying_seasons(pos).set_index("player_id")

        for _, r in cand.iterrows():
            name = r["player_display_name"]
            p = recent.loc[r["player_id"]] if r["player_id"] in recent.index else None
            if p is not None:
                cleared = sum(
                    bool((p[g["metric"]] <= g["threshold"]) if g["direction"] == "<="
                         else (p[g["metric"]] >= g["threshold"])) for g in gates)
                missed = [g["label"] for g in gates
                          if not ((p[g["metric"]] <= g["threshold"])
                                  if g["direction"] == "<="
                                  else (p[g["metric"]] >= g["threshold"]))]
                lhits = sum(1 for k, v in leap.items() if p[k] >= v)
                scored_on = int(p["season"])
            else:
                cleared, missed, lhits = 0, ["no full season to score against"], 0
                scored_on = 0
            rows.append({
                "position": pos, "player": name, "team": r["team"],
                "age": round(float(r["age"]), 1), "prob": round(float(r["prob"]), 3),
                "last_finish": int(r["prev_finish"]),
                "gates_scored_on": scored_on,
                "gates_cleared": cleared, "gates_total": len(gates),
                "leaper_markers": lhits, "leaper_total": len(leap),
                "tier": tier(float(r["prob"]), lhits, len(leap),
                             float(r["prev_finish"])),
                "missing": "; ".join(missed) or "-",
            })

    board = pd.DataFrame(rows).sort_values(
        ["position", "tier", "prob"], ascending=[True, True, False])
    board.to_csv(OUTPUT / f"target_board_{TARGET}.csv", index=False)

    for pos in ["WR", "RB", "TE", "QB"]:
        b = board[board["position"] == pos]
        keep = b[b["tier"] < "E - "]
        print(f"\n{'=' * 112}\n{pos} — {len(b)} candidates scored, {len(keep)} on the board")
        for t, grp in keep.groupby("tier"):
            print(f"\n  {t}")
            for _, r in grp.iterrows():
                stale = ("" if r["gates_scored_on"] == LAST_SEASON
                         else f"  [gates from {int(r['gates_scored_on'])}]")
                print(f"    {r['player'][:24]:25s} {r['team']:4s} {r['age']:>4.1f} "
                      f"p={r['prob']:.2f}  gates {r['gates_cleared']}/{r['gates_total']} "
                      f" leap {r['leaper_markers']}/{r['leaper_total']} "
                      f" was {pos}{r['last_finish']}{stale}")
    print(f"\nwrote {OUTPUT / f'target_board_{TARGET}.csv'}")


if __name__ == "__main__":
    main()
