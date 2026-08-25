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
from config import LAST_SEASON, OUTPUT, TARGET_N
from config import TARGET as TARGET_COL

TARGET = LAST_SEASON + 1

# Medians of the players who jumped into the target tier from outside the prior top 12.
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


# Tier bands as a multiple of the position's own base rate. Absolute bands stop
# meaning the same thing the moment the target moves: 0.25 was a large edge when
# a top-5 quarterback season happened to 9% of the pool, and is barely above the
# field now that a top-8 season happens to 22% of it.
BANDS = [(3.0, "A - target"), (2.0, "B - strong"), (1.3, "D - fringe")]


def tier(prob: float, leap: int, n_leap: int, prev_rank: float, base: float) -> str:
    """How many times the field's own rate this profile is worth."""
    lift = prob / base if base else 0.0
    for mult, name in BANDS:
        if lift >= mult:
            if name == "D - fringe" and prev_rank > 12 and leap >= n_leap - 1:
                return "C - leaper watch"
            return name
    return "E - profile does not support it"


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    # Employment status. A player not on a week-one roster has never finished in
    # the target tier - 0 for roughly 4,500 player-seasons since 2015 - so this
    # overrides whatever his box score says.
    try:
        avail = pd.read_csv(OUTPUT / f"availability_{TARGET}.csv")
        rostered = dict(zip(avail["player_id"], avail["available"]))
        status = dict(zip(avail["player_id"], avail["status"]))
    except FileNotFoundError:
        rostered, status = {}, {}
    pf = model.frame(df)
    gates_by_pos = {p: build_card(gate_pool(df, p), p, TARGET_COL, FAMILIES[p])["rules"]
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
        m.fit(train[f], train[TARGET_COL])
        # the field's own rate at this position, which sets the tier bands
        base = float(train[TARGET_COL].mean())

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
                # The leaper profile describes players who jumped from OUTSIDE
                # the prior top 12. Its bars are deliberately low, so every
                # player who was already top-12 clears all of them and the count says
                # nothing. Only score it for players actually in that lane.
                lhits = (sum(1 for k, v in leap.items() if p[k] >= v)
                         if r["prev_finish"] > 12 else None)
                scored_on = int(p["season"])
            else:
                cleared, missed, lhits = 0, ["no full season to score against"], 0
                scored_on = 0
            pid = r["player_id"]
            on_roster = rostered.get(pid)
            rows.append({
                "position": pos, "player": name, "team": r["team"],
                "roster": ("unrostered" if on_roster is None
                           else status.get(pid, "ACT") if not on_roster else "ACT"),
                "age": round(float(r["age"]), 1), "prob": round(float(r["prob"]), 3),
                "last_finish": int(r["prev_finish"]),
                # What the coaching staff currently intends, as of the August
                # chart. A player listed second almost never finishes near the top.
                "depth_rank": (int(r["depth_rank"])
                               if pd.notna(r.get("depth_rank")) else None),
                "gates_scored_on": scored_on,
                "gates_cleared": cleared, "gates_total": len(gates),
                "leaper_markers": lhits, "leaper_total": len(leap),
                "tier": ("X - not on a roster" if not on_roster
                         else tier(float(r["prob"]), lhits or 0, len(leap),
                                   float(r["prev_finish"]), base)),
                "base_rate": round(base, 4),
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
                      f" leap {'n/a' if pd.isna(r['leaper_markers']) else str(int(r['leaper_markers'])) + '/' + str(r['leaper_total'])} "
                      f" was {pos}{r['last_finish']}{stale}")
    print(f"\nwrote {OUTPUT / f'target_board_{TARGET}.csv'}")


if __name__ == "__main__":
    main()
