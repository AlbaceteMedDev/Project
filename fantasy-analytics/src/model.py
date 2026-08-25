"""The predictive frame and model.

Two design choices here exist because the first version got them wrong.

*Two years of history, not one.* A single prior season has no memory, so a
receiver who was elite in year N-2 and hurt in year N-1 scores like a scrub.
Adding year N-2 lifts receiver AUC from 0.901 to 0.929 and tight end from
0.848 to 0.866.

*Entry on either year.* The original pool required the prior season to clear a
volume floor, which silently deleted exactly the players the market cares most
about - a WR6 who played four games, a QB5 who played seven. Letting year N-2
qualify a player instead raises quarterback AUC from 0.664 to 0.710 and lifts
the share of top-5 seasons the model can even reach to 86-94%.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analyze import POOL_RULES
from config import LAST_SEASON, OUTPUT

# Everything carried forward from a past season onto the season being predicted.
CARRY = [
    "target_share", "yprr_shrunk", "rz_targets_share", "air_yards_share",
    "ppg_shrunk", "snap_pct", "games", "targets_pg", "wopr", "weighted_opps_pg",
    "opportunity_share", "rz_carries_share", "touches_pg", "rush_att_pg",
    "epa_per_dropback", "pass_td_rate", "dropbacks", "pos_rank",
    "yards_per_target", "routes_pg", "targets", "touches", "attempts",
]
TEAM_CTX = ["team_ppg", "team_scoring_rank", "team_qb_epa_rank"]

FEATURES = {
    "WR": ["target_share", "yprr_shrunk", "rz_targets_share", "air_yards_share",
           "ppg_shrunk", "snap_pct", "games"],
    "TE": ["target_share", "yprr_shrunk", "rz_targets_share", "ppg_shrunk",
           "snap_pct", "games"],
    "RB": ["weighted_opps_pg", "opportunity_share", "target_share",
           "rz_carries_share", "snap_pct", "ppg_shrunk", "games"],
    "QB": ["rush_att_pg", "epa_per_dropback", "pass_td_rate", "dropbacks",
           "ppg_shrunk", "games"],
}


def _lag(df: pd.DataFrame, k: int, tag: str) -> pd.DataFrame:
    c = df[["player_id", "season"] + CARRY].copy()
    c["season"] = c["season"] + k
    return c.rename(columns={x: f"{tag}_{x}" for x in CARRY})


def frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per player-season, carrying the two seasons before it."""
    base = df[["player_id", "player_display_name", "fantasy_pos", "team", "season",
               "age", "top5", "pos_rank"]].copy()
    out = (base.merge(_lag(df, 1, "p1"), on=["player_id", "season"], how="left")
                .merge(_lag(df, 2, "p2"), on=["player_id", "season"], how="left"))
    tp = (df.dropna(subset=["team"]).groupby(["season", "team"])[TEAM_CTX]
            .first().reset_index())
    tp["season"] = tp["season"] + 1
    return out.merge(tp.rename(columns={c: f"nt_{c}" for c in TEAM_CTX}),
                     on=["season", "team"], how="left")


def qualifies(d: pd.DataFrame, pos: str) -> np.ndarray:
    """Either of the last two seasons clearing the volume floor lets a player in."""
    ok1 = np.ones(len(d), bool)
    ok2 = np.ones(len(d), bool)
    for col, lo in POOL_RULES[pos].items():
        ok1 &= (d[f"p1_{col}"] >= lo).fillna(False).values
        ok2 &= (d[f"p2_{col}"] >= lo).fillna(False).values
    return ok1 | ok2


def features(pos: str) -> list[str]:
    return ([f"p1_{x}" for x in FEATURES[pos]] + [f"p2_{x}" for x in FEATURES[pos]]
            + ["age", "nt_team_scoring_rank", "nt_team_qb_epa_rank"])


def make_model():
    """No class weighting - it inflates scores and destroys their calibration."""
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                         LogisticRegression(max_iter=3000, C=0.5))


def pool(pf: pd.DataFrame, pos: str) -> pd.DataFrame:
    d = pf[(pf["fantasy_pos"] == pos) & pf["season"].between(2016, LAST_SEASON)].copy()
    return d[qualifies(d, pos)].dropna(subset=["age", "top5"])


def loso(d: pd.DataFrame, pos: str) -> pd.DataFrame:
    """Leave-one-season-out scores: never trained on the season it predicts."""
    f = features(pos)
    out = []
    for season in sorted(d["season"].unique()):
        tr, te = d[d["season"] != season], d[d["season"] == season]
        if tr["top5"].sum() < 5 or not len(te):
            continue
        m = make_model()
        m.fit(tr[f], tr["top5"])
        chunk = te[["season", "player_id", "player_display_name", "team", "age",
                    "pos_rank", "top5"]].copy()
        chunk["prob"] = m.predict_proba(te[f])[:, 1]
        out.append(chunk)
    res = pd.concat(out, ignore_index=True)
    res["season_prob_rank"] = res.groupby("season")["prob"].rank(
        ascending=False, method="min").astype(int)
    return res


def upcoming(df: pd.DataFrame, pos: str) -> pd.DataFrame:
    """Feature rows for a season that has not been played yet."""
    target = LAST_SEASON + 1
    ident = (df[df["season"].isin([LAST_SEASON, LAST_SEASON - 1])]
             .sort_values("season")
             .drop_duplicates("player_id", keep="last")
             [["player_id", "player_display_name", "fantasy_pos", "team", "age",
               "season", "pos_rank"]].copy())
    ident["age"] = ident["age"] + (target - ident["season"])
    ident["prev_finish"] = ident["pos_rank"]
    ident["season"] = target
    out = (ident.merge(_lag(df, 1, "p1"), on=["player_id", "season"], how="left")
                .merge(_lag(df, 2, "p2"), on=["player_id", "season"], how="left"))
    tp = (df[df["season"] == LAST_SEASON].dropna(subset=["team"])
            .groupby("team")[TEAM_CTX].first().reset_index())
    out = out.merge(tp.rename(columns={c: f"nt_{c}" for c in TEAM_CTX}),
                    on="team", how="left")
    out = out[out["fantasy_pos"] == pos]
    return out[qualifies(out, pos)].dropna(subset=["age"])
