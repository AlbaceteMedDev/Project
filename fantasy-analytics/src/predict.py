"""Forward-looking version: what did we know *before* a top-5 season happened?

Every feature here is available in August: last season's production, the
player's age, and last season's context for the team he is on now. Nothing
from the season being predicted is used.

Outputs
  * predictive_cards.json - per-position rule cards and their hit rates
  * model_scores.csv      - leave-one-season-out probabilities for every
                            player-season, so the model is only ever judged on
                            seasons it did not train on
  * coverage.csv          - honest accounting of the top-5 seasons that prior
                            year data could never have flagged (rookies, etc.)
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analyze import (LOWER_IS_BETTER, POOL_RULES, PRETTY, build_card,
                     predictive_frame)
from config import OUTPUT, STUDY_SEASONS

PRETTY.update({
    "prev_pos_rank": "Last year's positional finish",
    "prev_ppg_shrunk": "Last year's PPR per game",
    "prev_target_share": "Last year's target share",
    "prev_targets_pg": "Last year's targets per game",
    "prev_yprr_shrunk": "Last year's yards per route (est., shrunk)",
    "prev_ypt_shrunk": "Last year's yards per target (shrunk)",
    "prev_ypc_shrunk": "Last year's yards per carry (shrunk)",
    "prev_ppg_shrunk": "Last year's PPR per game (shrunk)",
    "prev_ypt_shrunk": "Last year's yards per target",
    "prev_rz_targets_share": "Last year's red-zone target share",
    "prev_snap_pct": "Last year's snap share",
    "prev_wopr": "Last year's WOPR",
    "prev_air_yards_share": "Last year's air-yards share",
    "prev_routes_pg": "Last year's routes per game (est.)",
    "prev_weighted_opps_pg": "Last year's weighted opportunities per game",
    "prev_touches_pg": "Last year's touches per game",
    "prev_opportunity_share": "Last year's opportunity share",
    "prev_i5_carries_share": "Last year's carry share inside the 5",
    "prev_rz_carries_share": "Last year's red-zone carry share",
    "prev_ypc_shrunk": "Last year's yards per carry",
    "prev_rush_att_pg": "Last year's rush attempts per game",
    "prev_rushing_yards": "Last year's rushing yards",
    "prev_epa_per_dropback": "Last year's EPA per dropback",
    "prev_pass_td_rate": "Last year's TD rate",
    "prev_dropbacks": "Last year's dropbacks",
    "prev_games": "Games played last year",
    "newteam_prev_team_scoring_rank": "New team's scoring rank last year",
    "newteam_prev_team_qb_epa_rank": "New team's QB EPA rank last year",
    "newteam_prev_team_ppg": "New team's points per game last year",
    "newteam_prev_team_pass_rate": "New team's pass rate last year",
})

LOWER_IS_BETTER |= {"prev_pos_rank", "newteam_prev_team_scoring_rank",
                    "newteam_prev_team_qb_epa_rank"}

PRED_FAMILIES = {
    "WR": {
        "Prior target volume": ["prev_target_share", "prev_targets_pg", "prev_wopr"],
        "Prior efficiency": ["prev_yprr_shrunk", "prev_ypt_shrunk"],
        "Prior scoring role": ["prev_rz_targets_share", "prev_air_yards_share"],
        "Prior finish": ["prev_pos_rank", "prev_ppg_shrunk"],
        "Landing spot": ["newteam_prev_team_scoring_rank", "newteam_prev_team_ppg"],
        "QB he catches from": ["newteam_prev_team_qb_epa_rank"],
        "Age": ["age"],
    },
    "TE": {
        "Prior target volume": ["prev_target_share", "prev_targets_pg", "prev_wopr"],
        "Prior efficiency": ["prev_yprr_shrunk", "prev_ypt_shrunk"],
        "Prior scoring role": ["prev_rz_targets_share"],
        "Prior finish": ["prev_pos_rank", "prev_ppg_shrunk"],
        "Landing spot": ["newteam_prev_team_scoring_rank", "newteam_prev_team_ppg"],
        "QB he catches from": ["newteam_prev_team_qb_epa_rank"],
        "Field time": ["prev_snap_pct"],
    },
    "RB": {
        "Prior volume": ["prev_weighted_opps_pg", "prev_touches_pg",
                         "prev_opportunity_share"],
        "Prior receiving role": ["prev_target_share", "prev_targets_pg"],
        "Prior goal-line role": ["prev_i5_carries_share", "prev_rz_carries_share"],
        "Prior finish": ["prev_pos_rank", "prev_ppg_shrunk"],
        "Field time": ["prev_snap_pct"],
        "Landing spot": ["newteam_prev_team_scoring_rank", "newteam_prev_team_ppg"],
        "Age": ["age"],
    },
    "QB": {
        "Prior rushing": ["prev_rush_att_pg", "prev_rushing_yards"],
        "Prior efficiency": ["prev_epa_per_dropback", "prev_pass_td_rate"],
        "Prior volume": ["prev_dropbacks", "prev_pass_att_pg"],
        "Prior finish": ["prev_pos_rank", "prev_ppg_shrunk"],
        "Landing spot": ["newteam_prev_team_scoring_rank", "newteam_prev_team_ppg"],
        "Age": ["age"],
    },
}

MODEL_FEATURES = {
    "WR": ["prev_target_share", "prev_yprr_shrunk", "prev_rz_targets_share",
           "prev_air_yards_share", "prev_ppg_shrunk", "prev_snap_pct", "prev_games",
           "age", "newteam_prev_team_scoring_rank", "newteam_prev_team_qb_epa_rank"],
    "TE": ["prev_target_share", "prev_yprr_shrunk", "prev_rz_targets_share",
           "prev_ppg_shrunk", "prev_snap_pct", "prev_games", "age",
           "newteam_prev_team_scoring_rank", "newteam_prev_team_qb_epa_rank"],
    "RB": ["prev_weighted_opps_pg", "prev_opportunity_share", "prev_target_share",
           "prev_rz_carries_share", "prev_snap_pct", "prev_ppg_shrunk", "prev_games",
           "age", "newteam_prev_team_scoring_rank", "newteam_prev_team_ppg"],
    "QB": ["prev_rush_att_pg", "prev_epa_per_dropback", "prev_pass_td_rate",
           "prev_dropbacks", "prev_ppg_shrunk", "prev_games", "age",
           "newteam_prev_team_scoring_rank"],
}


def pred_pool(pf: pd.DataFrame, pos: str) -> pd.DataFrame:
    """Player-seasons whose *prior* year clears the position's volume bar."""
    d = pf[(pf["fantasy_pos"] == pos) & (pf["season"].isin(STUDY_SEASONS))].copy()
    for col, lo in POOL_RULES[pos].items():
        d = d[d[f"prev_{col}"] >= lo]
    return d


def loso_scores(d: pd.DataFrame, feats: list[str], target: str = "top5") -> pd.DataFrame:
    """Leave-one-season-out probabilities - never trained on the year it scores.

    No class weighting. Re-weighting the rare class lifts scores toward 1 and
    destroys their meaning: an earlier version used class_weight="balanced" and
    produced 0.99s whose real top-5 rate was 33%. Plain logistic regression gives
    the same AUC with roughly a quarter of the Brier score, so a published number
    can be read as what it claims to be.
    """
    d = d.dropna(subset=feats + [target]).copy()
    out = []
    for season in sorted(d["season"].unique()):
        tr, te = d[d["season"] != season], d[d["season"] == season]
        if tr[target].sum() < 5 or len(te) == 0:
            continue
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, C=0.5))
        model.fit(tr[feats], tr[target])
        p = model.predict_proba(te[feats])[:, 1]
        chunk = te[["season", "player_id", "player_display_name", "team", "age",
                    "pos_rank", target]].copy()
        chunk["prob"] = p
        out.append(chunk)
    res = pd.concat(out, ignore_index=True)
    res["season_prob_rank"] = res.groupby("season")["prob"].rank(
        ascending=False, method="min").astype(int)
    return res


def full_model(d: pd.DataFrame, feats: list[str], target: str = "top5"):
    d = d.dropna(subset=feats + [target])
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, C=0.5))
    model.fit(d[feats], d[target])
    lr = model.named_steps["logisticregression"]
    coefs = dict(zip(feats, lr.coef_[0].round(3).tolist()))
    return model, coefs


def coverage(df: pd.DataFrame, pf: pd.DataFrame, pos: str) -> dict:
    """How many top-5 seasons were even reachable from prior-year data?"""
    elite = df[(df["fantasy_pos"] == pos) & (df["season"].isin(STUDY_SEASONS)) &
               (df["top5"] == 1)]
    reachable = pred_pool(pf, pos)
    key = set(zip(reachable["player_id"], reachable["season"]))
    elite = elite.copy()
    elite["in_prior_pool"] = [
        (p, s) in key for p, s in zip(elite["player_id"], elite["season"])]
    missed = elite[~elite["in_prior_pool"]]
    return {
        "n_top5": int(len(elite)),
        "n_reachable": int(elite["in_prior_pool"].sum()),
        "pct_reachable": float(elite["in_prior_pool"].mean()),
        "unreachable": missed[["season", "player_display_name", "team", "pos_rank",
                               "exp"]].sort_values("season").to_dict("records"),
    }


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = predictive_frame(df)

    results, score_frames, cov_rows = {}, [], []
    for pos in ["QB", "RB", "WR", "TE"]:
        d = pred_pool(pf, pos)
        card = build_card(d, pos, "top5", PRED_FAMILIES[pos], min_recall=0.80)

        feats = MODEL_FEATURES[pos]
        scores = loso_scores(d, feats)
        scores["position"] = pos
        auc_oos = roc_auc_score(scores["top5"], scores["prob"])
        model, coefs = full_model(d, feats)

        # How often is a top-5 finisher inside the model's preseason top 5/10?
        hit5 = scores[scores["season_prob_rank"] <= 5]
        hit10 = scores[scores["season_prob_rank"] <= 10]
        cov = coverage(df, pf, pos)
        cov_rows.append({"position": pos, **{k: v for k, v in cov.items()
                                             if k != "unreachable"}})

        # Persistence: does last year's top-5 finish repeat?
        prev5 = d[d["prev_pos_rank"] <= 5]
        prev12 = d[(d["prev_pos_rank"] > 5) & (d["prev_pos_rank"] <= 12)]
        prev24 = d[(d["prev_pos_rank"] > 12) & (d["prev_pos_rank"] <= 24)]
        rest = d[d["prev_pos_rank"] > 24]

        results[pos] = {
            "pool": {"n": int(len(d)), "base_rate": float(d["top5"].mean())},
            "card": card,
            "model": {
                "features": feats, "coefficients": coefs,
                "oos_auc": float(auc_oos),
                "top5_precision": float(hit5["top5"].mean()),
                "top5_recall": float(hit5["top5"].sum() / d["top5"].sum()),
                "top10_precision": float(hit10["top5"].mean()),
                "top10_recall": float(hit10["top5"].sum() / d["top5"].sum()),
            },
            "persistence": {
                "prev_top5": {"n": int(len(prev5)), "rate": float(prev5["top5"].mean())},
                "prev_6_12": {"n": int(len(prev12)), "rate": float(prev12["top5"].mean())},
                "prev_13_24": {"n": int(len(prev24)), "rate": float(prev24["top5"].mean())},
                "prev_25plus": {"n": int(len(rest)), "rate": float(rest["top5"].mean())},
            },
            "coverage": cov,
        }
        score_frames.append(scores)

    pd.concat(score_frames, ignore_index=True).to_csv(
        OUTPUT / "model_scores.csv", index=False)
    pd.DataFrame(cov_rows).to_csv(OUTPUT / "coverage.csv", index=False)
    with open(OUTPUT / "predictive_cards.json", "w") as fh:
        json.dump(results, fh, indent=2, default=str)

    for pos in ["QB", "RB", "WR", "TE"]:
        r = results[pos]
        j = r["card"]["joint"]
        print(f"\n### {pos}  returning pool={r['pool']['n']}  "
              f"base rate of a top-5 finish={r['pool']['base_rate']:.1%}")
        for rule in r["card"]["rules"]:
            print(f"   {rule['label']:38s} {rule['direction']} {rule['threshold']:<7g} "
                  f"catches {rule['recall']:.0%} of top-5s | {rule['precision']:.0%} hit")
        print(f"   ALL {len(r['card']['rules'])} GATES -> {j['n_flagged']} flagged, "
              f"{j['hits']} top-5 "
              f"({j['precision']:.0%} hit, {j['lift']:.1f}x base, "
              f"{j['recall']:.0%} of top-5s caught)")
        if r["card"]["green_flags"]:
            print("   preseason green flags:")
            for g in r["card"]["green_flags"][:4]:
                print(f"     {g['label']:44s} {g['direction']} {g['threshold']:<7g} "
                      f"{g['precision']:.0%} hit | {g['lift']:.1f}x | "
                      f"~{g['per_season_flagged']:.1f}/season")
        m = r["model"]
        print(f"   model: out-of-sample AUC={m['oos_auc']:.3f} | preseason top-5 list "
              f"hits {m['top5_precision']:.0%} | top-10 list catches "
              f"{m['top10_recall']:.0%} of top-5 finishers")
        p = r["persistence"]
        print(f"   repeat rates: was top-5 -> {p['prev_top5']['rate']:.0%} | "
              f"6-12 -> {p['prev_6_12']['rate']:.0%} | 13-24 -> "
              f"{p['prev_13_24']['rate']:.0%} | 25+ -> {p['prev_25plus']['rate']:.0%}")
        c = r["coverage"]
        print(f"   reachable at all: {c['n_reachable']}/{c['n_top5']} "
              f"({c['pct_reachable']:.0%}) had a qualifying prior season")


if __name__ == "__main__":
    main()
