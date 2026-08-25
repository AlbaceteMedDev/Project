"""Adversarial checks on the study's own claims.

Every headline number in this project was produced by fitting on all eleven
seasons at once. That is fine for description and wrong for prediction, so the
checks here re-derive the same claims under conditions that could break them:
thresholds fitted without seeing the season they are scored on, a pool that does
not quietly drop players who got hurt, and scoring formats other than full PPR.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(__file__.rsplit("/", 1)[0]))

from analyze import FAMILIES, POOL_RULES, build_card, pool
from config import OUTPUT, STUDY_SEASONS
from predict import MODEL_FEATURES, pred_pool, predictive_frame

df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)


def hr(title: str) -> None:
    print(f"\n{'=' * 92}\n{title}\n{'=' * 92}")


# ---------------------------------------------------------------- check 1
def gates_out_of_sample() -> None:
    """Refit the gates without the season being scored, then score it."""
    hr("CHECK 1 — gates, refitted leave-one-season-out")
    print("The published hit rates come from thresholds fitted on all 11 seasons "
          "including\nthe one they score. Here each season is scored by gates fitted "
          "only on the other 10.\n")
    print(f"{'pos':4s} {'in-sample hit':>14s} {'out-of-sample hit':>18s} "
          f"{'drop':>7s} {'flagged':>9s} {'caught':>8s}")
    for pos in ["WR", "TE", "RB", "QB"]:
        full = pool(df, pos)
        ins = build_card(full, pos, "top5", FAMILIES[pos])["joint"]
        hits = flagged = elite_caught = elite_total = 0
        for season in STUDY_SEASONS:
            train = full[full["season"] != season]
            test = full[full["season"] == season]
            if not len(test):
                continue
            card = build_card(train, pos, "top5", FAMILIES[pos])
            mask = pd.Series(True, index=test.index)
            for r in card["rules"]:
                col = test[r["metric"]]
                m = (col <= r["threshold"]) if r["direction"] == "<=" else (col >= r["threshold"])
                mask &= m.fillna(False)
            flagged += int(mask.sum())
            hits += int((mask & (test["top5"] == 1)).sum())
            elite_caught += int((mask & (test["top5"] == 1)).sum())
            elite_total += int((test["top5"] == 1).sum())
        oos = hits / flagged if flagged else np.nan
        print(f"{pos:4s} {ins['precision']:>13.0%} {oos:>17.0%} "
              f"{ins['precision'] - oos:>+6.0%} {flagged:>9d} "
              f"{elite_caught / elite_total:>7.0%}")


# ---------------------------------------------------------------- check 2
def survivorship() -> None:
    """The predictive pool silently drops anyone who did not play year N."""
    hr("CHECK 2 — survivorship in the predictive pool")
    print("pred_pool inner-joins year N to year N-1, so a player who missed all of "
          "year N\nnever appears. That inflates every rate below. Re-scored counting "
          "a lost season\nas a failed one:\n")
    pf = predictive_frame(df)
    print(f"{'pos':4s} {'joined pool':>12s} {'+ vanished':>11s} "
          f"{'base rate (joined)':>19s} {'base rate (honest)':>19s}")
    for pos in ["WR", "TE", "RB", "QB"]:
        d = pred_pool(pf, pos)
        # everyone who qualified in year N-1 and could have been scored in year N
        elig = df[(df["fantasy_pos"] == pos) & (df["season"].isin(
            [s - 1 for s in STUDY_SEASONS]))].copy()
        for col, lo in POOL_RULES[pos].items():
            elig = elig[elig[col] >= lo]
        elig["next"] = elig["season"] + 1
        elig = elig[elig["next"].isin(STUDY_SEASONS)]
        joined = set(zip(d["player_id"], d["season"]))
        elig["appeared"] = [(p, s) in joined for p, s in
                            zip(elig["player_id"], elig["next"])]
        vanished = int((~elig["appeared"]).sum())
        honest = d["top5"].sum() / (len(d) + vanished)
        print(f"{pos:4s} {len(d):>12d} {vanished:>11d} "
              f"{d['top5'].mean():>18.1%} {honest:>18.1%}")
    print("\nA vanished season is a player who cleared the volume bar one year and "
          "then did\nnot play enough to be scored the next. Those are mostly "
          "injuries and lost jobs —\nreal outcomes for anyone holding the player.")


# ---------------------------------------------------------------- check 3
def scoring_formats() -> None:
    """Do the gates describe half-PPR and standard leagues too?"""
    hr("CHECK 3 — does any of this survive a different scoring format?")
    d = df.copy()
    d["fp_half"] = d["fantasy_points_ppr"] - 0.5 * d["receptions"]
    d["fp_std"] = d["fantasy_points_ppr"] - 1.0 * d["receptions"]
    print(f"{'pos':4s} {'format':8s} {'top-5 overlap with full PPR':>30s}")
    for pos in ["WR", "TE", "RB", "QB"]:
        base = set()
        for fmt in ["fantasy_points_ppr", "fp_half", "fp_std"]:
            sub = d[(d["fantasy_pos"] == pos) & d["season"].isin(STUDY_SEASONS)].copy()
            sub["rk"] = sub.groupby("season")[fmt].rank(ascending=False, method="min")
            top = set(zip(sub.loc[sub["rk"] <= 5, "player_id"],
                          sub.loc[sub["rk"] <= 5, "season"]))
            if fmt == "fantasy_points_ppr":
                base = top
                continue
            name = "half-PPR" if fmt == "fp_half" else "standard"
            print(f"{pos:4s} {name:8s} {len(top & base)}/{len(base)} "
                  f"({len(top & base) / len(base):.0%})")


# ---------------------------------------------------------------- check 4
def threshold_stability() -> None:
    """How much does each gate value move if one season is removed?"""
    hr("CHECK 4 — how stable are the threshold values themselves?")
    print("Each gate refitted 11 times, each time dropping one season.\n")
    for pos in ["WR", "TE", "RB", "QB"]:
        full = pool(df, pos)
        published = {r["metric"]: r["threshold"]
                     for r in build_card(full, pos, "top5", FAMILIES[pos])["rules"]}
        spread: dict[str, list] = {m: [] for m in published}
        chosen: dict[str, int] = {m: 0 for m in published}
        for season in STUDY_SEASONS:
            card = build_card(full[full["season"] != season], pos, "top5", FAMILIES[pos])
            for r in card["rules"]:
                if r["metric"] in spread:
                    spread[r["metric"]].append(r["threshold"])
                    chosen[r["metric"]] += 1
        print(f"  {pos}")
        for m, vals in spread.items():
            if not vals:
                print(f"    {m:32s} published {published[m]:<8g} "
                      f"— dropped from the card in every refit")
                continue
            print(f"    {m:32s} published {published[m]:<8g} "
                  f"refits {min(vals):g}–{max(vals):g}  "
                  f"kept in {chosen[m]}/{len(STUDY_SEASONS)} refits")


if __name__ == "__main__":
    gates_out_of_sample()
    survivorship()
    scoring_formats()
    threshold_stability()
