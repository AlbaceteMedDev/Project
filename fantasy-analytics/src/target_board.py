"""Score every returning player for the upcoming season against the position's gates.

Produces one row per candidate: how many in-season gates his prior year cleared,
how many leaper markers he matches, and the model's probability. That is the
whole draft board - no hand-picking.
"""
from __future__ import annotations

import json

import pandas as pd

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


def tier(gates_cleared: int, n_gates: int, leap: int, n_leap: int,
         prob: float, prev_rank: float) -> str:
    """Tier on the model first, because it is the instrument validated out of
    sample. Gate counts are descriptive and were never held out, so they sharpen
    a tier rather than set it - a player can miss a gate on a metric the route
    estimate handles badly and still be the best bet on the board.
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
    prof = json.load(open(OUTPUT / "profile_cards.json"))
    fc = pd.read_csv(OUTPUT / f"forecast_{TARGET}.csv")
    prev = df[df["season"] == LAST_SEASON].set_index("player_display_name")
    prev = prev[~prev.index.duplicated(keep="first")]

    rows = []
    for pos in ["QB", "RB", "WR", "TE"]:
        gates = prof[pos]["profile_top5"]["rules"]
        leap = LEAPER[pos]
        for _, r in fc[fc["fantasy_pos"] == pos].iterrows():
            name = r["player_display_name"]
            if name not in prev.index:
                continue
            p = prev.loc[name]
            cleared, missed = 0, []
            for g in gates:
                v = p[g["metric"]]
                ok = (v <= g["threshold"]) if g["direction"] == "<=" else (v >= g["threshold"])
                cleared += bool(ok)
                if not ok:
                    missed.append(g["label"])
            lhits = sum(1 for k, v in leap.items() if p[k] >= v)
            rows.append({
                "position": pos, "player": name, "team": r["team"],
                "age": round(float(r["age"]), 1), "prob": round(float(r["prob"]), 3),
                f"{LAST_SEASON}_finish": int(r["prev_pos_rank"]),
                "gates_cleared": cleared, "gates_total": len(gates),
                "leaper_markers": lhits, "leaper_total": len(leap),
                "tier": tier(cleared, len(gates), lhits, len(leap),
                             float(r["prob"]), float(r["prev_pos_rank"])),
                "missing": "; ".join(missed) or "-",
            })

    board = pd.DataFrame(rows).sort_values(
        ["position", "tier", "prob"], ascending=[True, True, False])
    board.to_csv(OUTPUT / f"target_board_{TARGET}.csv", index=False)

    for pos in ["WR", "TE", "RB", "QB"]:
        b = board[board["position"] == pos]
        keep = b[(b["tier"] < "E") | (b["prob"] >= 0.45)]
        print(f"\n{'=' * 118}\n{pos} — {len(b)} returning candidates, "
              f"{len(keep)} with a usable profile\n{'=' * 118}")
        for t, grp in keep.groupby("tier"):
            print(f"\n  {t}")
            for _, r in grp.iterrows():
                print(f"    {r['player'][:24]:25s} {r['team']:4s} {r['age']:>4.1f}  "
                      f"p={r['prob']:.2f}  gates {r['gates_cleared']}/{r['gates_total']}  "
                      f"leap {r['leaper_markers']}/{r['leaper_total']}  "
                      f"was {pos}{r[f'{LAST_SEASON}_finish']:<3d} "
                      f"| missing: {r['missing'][:58]}")
    print(f"\nwrote {OUTPUT / f'target_board_{TARGET}.csv'}")


if __name__ == "__main__":
    main()
