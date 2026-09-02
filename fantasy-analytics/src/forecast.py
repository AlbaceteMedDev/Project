"""Apply the rules and the model to the upcoming season.

Prior year = the most recent completed season. Team context is that team's
most recent season. Rosters move in the offseason, so a player who changed
teams carries his old team's context here - the landing-spot inputs need to be
re-pointed by hand once depth charts settle.
"""
from __future__ import annotations

import json

import pandas as pd

from analyze import POOL_RULES
from config import LAST_SEASON, OUTPUT
from predict import (MODEL_FEATURES, PRED_FAMILIES, build_card, full_model,
                     pred_pool, predictive_frame)

TARGET_SEASON = LAST_SEASON + 1


def upcoming_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Build year-N feature rows for a season that has not been played yet."""
    prev = df[df["season"] == LAST_SEASON].copy()
    carry = [c for c in prev.columns if c not in
             {"player_id", "season", "player_display_name", "fantasy_pos", "team",
              "birth_date", "gsis_id"}]
    out = pd.concat([
        prev[["player_id", "player_display_name", "fantasy_pos", "team"]]
            .reset_index(drop=True),
        prev[carry].reset_index(drop=True).add_prefix("prev_"),
        pd.DataFrame({"season": TARGET_SEASON, "age": prev["age"].values + 1.0}),
    ], axis=1)

    team_cols = ["team_ppg", "team_scoring_rank", "team_qb_epa_rank",
                 "team_pass_rate", "team_plays", "team_dropbacks"]
    tprev = (df[df["season"] == LAST_SEASON].dropna(subset=["team"])
               .groupby("team")[team_cols].first().reset_index()
               .rename(columns={c: f"newteam_prev_{c}" for c in team_cols}))
    return out.merge(tprev, on="team", how="left")


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = predictive_frame(df)
    upcoming = upcoming_frame(df)

    out_rows, summary = [], {}
    for pos in ["QB", "RB", "WR", "TE"]:
        train = pred_pool(pf, pos)
        card = build_card(train, pos, "top5", PRED_FAMILIES[pos], min_recall=0.80)
        feats = MODEL_FEATURES[pos]
        model, coefs = full_model(train, feats)

        cand = upcoming[upcoming["fantasy_pos"] == pos].copy()
        for col, lo in POOL_RULES[pos].items():
            cand = cand[cand[f"prev_{col}"] >= lo]
        cand = cand.dropna(subset=feats)
        cand["prob"] = model.predict_proba(cand[feats])[:, 1]

        passes, detail = pd.Series(True, index=cand.index), {}
        for rule in card["rules"]:
            col = cand[rule["metric"]]
            m = (col <= rule["threshold"]) if rule["direction"] == "<=" \
                else (col >= rule["threshold"])
            m = m.fillna(False)
            detail[rule["metric"]] = m
            passes &= m
        n_rules = len(card["rules"])
        cand["rules_passed"] = sum(detail.values()) if detail else 0
        cand["n_rules"] = n_rules
        cand["passes_all"] = passes
        cand = cand.sort_values("prob", ascending=False)
        cand["rank"] = range(1, len(cand) + 1)

        summary[pos] = {
            "n_candidates": int(len(cand)),
            "n_rules": n_rules,
            "n_passing_all_rules": int(passes.sum()),
            "green_flags": [{k: g[k] for k in
                             ("label", "metric", "direction", "threshold",
                              "precision", "lift", "per_season_flagged")}
                            for g in card["green_flags"]],
            "rules": [{k: r[k] for k in
                       ("label", "metric", "direction", "threshold", "precision",
                        "recall", "lift")} for r in card["rules"]],
            "model_coefficients": coefs,
            "shortlist": cand.head(15)[
                ["rank", "player_display_name", "team", "age", "prob",
                 "rules_passed", "n_rules", "passes_all", "prev_pos_rank",
                 "prev_ppg_ppr"]
            ].round(3).to_dict("records"),
        }
        keep = ["season", "fantasy_pos", "player_display_name", "team", "age", "prob",
                "rank", "rules_passed", "n_rules", "passes_all", "prev_pos_rank",
                "prev_ppg_ppr"]
        out_rows.append(cand[keep])

    pd.concat(out_rows, ignore_index=True).to_csv(
        OUTPUT / f"forecast_{TARGET_SEASON}.csv", index=False)
    with open(OUTPUT / f"forecast_{TARGET_SEASON}.json", "w") as fh:
        json.dump(summary, fh, indent=2, default=str)

    for pos in ["QB", "RB", "WR", "TE"]:
        s = summary[pos]
        gate_txt = ("the 1 gate rule" if s["n_rules"] == 1
                    else f"all {s['n_rules']} gate rules")
        print(f"\n### {pos} {TARGET_SEASON} - {s['n_candidates']} returning "
              f"candidates, {s['n_passing_all_rules']} clear {gate_txt}")
        for r in s["shortlist"][:10]:
            flag = ("ALL" if r["passes_all"]
                    else f"{r['rules_passed']}/{s['n_rules']}")
            print(f"   {r['rank']:>2d}. {r['player_display_name']:22s} {r['team']:4s} "
                  f"age {r['age']:.1f}  p={r['prob']:.2f}  {flag:>5s}  "
                  f"(was {pos}{int(r['prev_pos_rank'])})")


if __name__ == "__main__":
    main()
