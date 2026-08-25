"""Which indicators actually carry the weight, measured out of sample.

The cards in the report rank rules by in-sample lift, which flatters anything
correlated with volume. This ranks them the only way that means anything for a
decision you have not made yet: leave-one-season-out AUC, once alone and once
as the marginal loss from deleting the feature out of the full model.

It also tests the situational variables the change study turned up - a lost
season, a coaching change, a quarterback upgrade, proven career peak - to see
whether they add anything the box score does not already say.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import model as M
from config import LAST_SEASON, OUTPUT

df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
POS = ["QB", "RB", "WR", "TE"]

# Human labels, so the output reads as findings rather than column names.
LABEL = {
    "target_share": "target share", "yprr_shrunk": "yards per route (shrunk)",
    "rz_targets_share": "red-zone target share", "air_yards_share": "air yards share",
    "ppg_shrunk": "points per game (shrunk)", "snap_pct": "snap rate",
    "games": "games played", "targets_pg": "targets per game", "wopr": "WOPR",
    "weighted_opps_pg": "weighted opportunities/gm", "opportunity_share": "opportunity share",
    "rz_carries_share": "red-zone carry share", "touches_pg": "touches per game",
    "rush_att_pg": "rush attempts per game", "epa_per_dropback": "EPA per dropback",
    "pass_td_rate": "pass TD rate", "dropbacks": "dropbacks", "pos_rank": "positional finish",
    "yards_per_target": "yards per target", "routes_pg": "routes per game",
    "age": "age", "nt_team_scoring_rank": "team scoring rank",
    "nt_team_qb_epa_rank": "team QB EPA rank",
    "best_rank_prior": "career-best finish so far", "yrs_since_top12": "years since a top-12",
    "chg_team": "changed teams", "chg_coach": "changed head coach",
    "qb_epa_gain": "moved to a better QB room",
    "qb_trend": "own team QB play improving", "p1_missed": "missed most of last year",
    "missed": "missed most of last year",
    "draft_round": "draft round", "career_seasons": "seasons in the league",
}


def coach_table() -> pd.DataFrame:
    from change_effects import coach_table as ct
    return ct()


def augment(pf: pd.DataFrame) -> pd.DataFrame:
    """Add the situational variables to the standard two-year frame."""
    out = pf.copy()

    # proven peak: the best finish anywhere before the season being predicted
    hist = df[["player_id", "season", "pos_rank", "top12"]].sort_values("season")
    best, since = [], []
    prior = {}
    for pid, g in hist.groupby("player_id"):
        run_best, last12 = np.inf, np.nan
        for _, r in g.iterrows():
            prior[(pid, r["season"] + 1)] = (run_best, last12)
            run_best = min(run_best, r["pos_rank"])
            if r["top12"] == 1:
                last12 = r["season"]
    key = list(zip(out["player_id"], out["season"]))
    vals = [prior.get(k, (np.nan, np.nan)) for k in key]
    out["best_rank_prior"] = [v[0] if np.isfinite(v[0]) else np.nan for v in vals]
    out["yrs_since_top12"] = [out["season"].iat[i] - v[1] if pd.notna(v[1]) else 99
                              for i, v in enumerate(vals)]

    # team and coach continuity
    tm = df[["player_id", "season", "team"]].copy()
    tm["season"] = tm["season"] + 1
    out = out.merge(tm.rename(columns={"team": "p1_team"}),
                    on=["player_id", "season"], how="left")
    out["chg_team"] = (out["team"] != out["p1_team"]).astype(float)
    out.loc[out["p1_team"].isna(), "chg_team"] = np.nan

    co = coach_table()
    cur = co.rename(columns={"coach": "coach_now"})
    prv = co.copy(); prv["season"] = prv["season"] + 1
    prv = prv.rename(columns={"coach": "coach_prev"})
    out = (out.merge(cur, on=["season", "team"], how="left")
              .merge(prv, on=["season", "team"], how="left"))
    out["chg_coach"] = (out["coach_now"] != out["coach_prev"]).astype(float)
    out.loc[out["coach_prev"].isna() | out["coach_now"].isna(), "chg_coach"] = np.nan

    # Quarterback context moving in the player's favour. nt_team_qb_epa_rank is
    # already the current team's rank in the season just played, so a "gain" has
    # to come from somewhere else: either he moved to a better room, or his own
    # team's quarterback play improved year over year. Rank 1 is best, so a
    # falling rank number is a gain.
    q = df[df["fantasy_pos"] == "QB"].dropna(subset=["team"])
    idx = q.groupby(["season", "team"])["dropbacks"].idxmax()
    qe = q.loc[idx, ["season", "team", "team_qb_epa_rank"]]

    lag1 = qe.copy(); lag1["season"] += 1
    lag1 = lag1.rename(columns={"team_qb_epa_rank": "qb_rank_t1"})
    lag2 = qe.copy(); lag2["season"] += 2
    lag2 = lag2.rename(columns={"team_qb_epa_rank": "qb_rank_t2"})
    out = (out.merge(lag1, on=["season", "team"], how="left")
              .merge(lag2, on=["season", "team"], how="left"))
    # the room he is leaving, scored in the same season as the one he joins
    old_room = lag1.rename(columns={"team": "p1_team", "qb_rank_t1": "qb_rank_old"})
    out = out.merge(old_room, on=["season", "p1_team"], how="left")

    out["qb_epa_gain"] = (out["qb_rank_old"] - out["qb_rank_t1"]).fillna(0.0)
    out["qb_trend"] = out["qb_rank_t2"] - out["qb_rank_t1"]

    # p1_missed now ships inside model.frame(); do not add a second copy.
    dr = df[["player_id", "draft_round", "exp"]].drop_duplicates("player_id")
    out = out.merge(dr, on="player_id", how="left")
    out["draft_round"] = out["draft_round"].fillna(8)
    out["career_seasons"] = out["season"] - (out["season"] - out["exp"])
    return out


EXTRA = ["best_rank_prior", "yrs_since_top12", "chg_team", "chg_coach",
         "qb_epa_gain", "qb_trend", "p1_missed", "draft_round"]


def loso_auc(d: pd.DataFrame, feats: list[str]) -> float:
    """AUC where every season is scored by a model that never saw it."""
    y, p = [], []
    for s in sorted(d["season"].unique()):
        tr, te = d[d["season"] != s], d[d["season"] == s]
        if tr["top5"].sum() < 5 or te["top5"].nunique() < 1 or not len(te):
            continue
        m = M.make_model()
        m.fit(tr[feats], tr["top5"])
        y.append(te["top5"].values)
        p.append(m.predict_proba(te[feats])[:, 1])
    y, p = np.concatenate(y), np.concatenate(p)
    return roc_auc_score(y, p) if len(np.unique(y)) > 1 else np.nan


def run() -> pd.DataFrame:
    pf = augment(M.frame(df))
    rows = []
    for pos in POS:
        d = pf[(pf["fantasy_pos"] == pos) & pf["season"].between(2016, LAST_SEASON)].copy()
        d = d[M.qualifies(d, pos)].dropna(subset=["age", "top5"])
        base = M.features(pos)
        full = base + [f for f in EXTRA if f not in base]
        auc_full = loso_auc(d, full)
        auc_base = loso_auc(d, base)
        print(f"\n{'=' * 92}\n{pos}  —  n={len(d)}, top-5 seasons={int(d['top5'].sum())}, "
              f"base rate={d['top5'].mean():.1%}")
        print(f"      published model AUC {auc_base:.3f}   "
              f"with situational features {auc_full:.3f}\n{'=' * 92}")
        print(f"{'indicator':32s} {'alone':>8s} {'marginal':>10s}  {'reading':<28s}")
        for f in full:
            solo = loso_auc(d, [f])
            drop = loso_auc(d, [x for x in full if x != f])
            marg = auc_full - drop
            name = LABEL.get(f.replace("p1_", "").replace("p2_", ""), f)
            tag = "last yr" if f.startswith("p1_") else ("two yrs ago" if f.startswith("p2_") else "")
            rows.append(dict(pos=pos, feature=f, label=f"{name} ({tag})".strip(),
                             solo=solo, marginal=marg,
                             auc_base=auc_base, auc_full=auc_full, n=len(d)))
        r = pd.DataFrame([x for x in rows if x["pos"] == pos]).sort_values(
            "solo", ascending=False)
        for _, x in r.iterrows():
            read = ("carries it alone" if x.solo >= 0.75 else
                    "real on its own" if x.solo >= 0.65 else
                    "weak alone" if x.solo >= 0.55 else "no signal alone")
            if x.marginal >= 0.005:
                read += ", and unique"
            elif x.marginal <= -0.002:
                read += ", model is better without it"
            print(f"{x.label[:31]:32s} {x.solo:>8.3f} {x.marginal:>+10.4f}  {read:<28s}")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = run()
    out.to_csv(OUTPUT / "leverage.csv", index=False)
    print(f"\nwrote {OUTPUT / 'leverage.csv'}")
