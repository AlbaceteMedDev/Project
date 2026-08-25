"""Scoring the players the main model cannot see.

A rookie has no NFL box score, so the two-year model has nothing to stand on and
drops him entirely. That is a real hole - a first-year player has finished top-8
at his position dozens of times in this window - and it is not unfixable, because
everything that predicts a rookie season is knowable in August:

  draft capital   where the league itself valued him
  landing spot    how much of his team's work at that position just left
  depth chart     what the staff currently intends, per the August chart
  offense         how good the team and the quarterback were last year

None of it is his production, because he has none. All of it is public.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import model as M
from config import LAST_SEASON, OUTPUT, RAW, TARGET, TARGET_N

POS = ["QB", "RB", "WR", "TE"]
# What "opportunity" means at each position, for measuring what a departure left behind.
SHARE = {"WR": "target_share", "TE": "target_share",
         "RB": "opportunity_share", "QB": "dropbacks"}

FEATURES = ["pick", "draft_age", "depth_rank", "vacated_share",
            "returning_top_share", "team_scoring_rank", "team_qb_epa_rank"]

# The highest score this model has enough history to stand behind. Rookie hits
# are rare - six tight ends in eleven years - so above this the fit is
# extrapolating into a region with almost no observations, and a printed 0.61
# would be a number nobody has earned the right to publish. Scores are reported
# capped, with a flag, rather than quietly trusted.
CEILING = 0.35


def draft() -> pd.DataFrame:
    d = pd.read_csv(RAW / "draft_picks.csv", low_memory=False)
    d = d[d["position"].isin(POS) & d["gsis_id"].notna()]
    return (d[["gsis_id", "season", "round", "pick", "team", "position", "age",
               "pfr_player_name", "college"]]
            .rename(columns={"gsis_id": "player_id", "position": "pos",
                             "age": "draft_age", "pfr_player_name": "player"}))


def namekey(s: pd.Series) -> pd.Series:
    """Match on name when ids cannot be trusted - see the join in build()."""
    return (s.astype(str).str.lower()
             .str.replace(r"\b(jr|sr|ii|iii|iv|v)\.?$", "", regex=True)
             .str.replace(r"[^a-z]", "", regex=True))


def team_map(df: pd.DataFrame) -> dict:
    """nflverse draft uses 3-letter club codes that differ from the stats feed."""
    fix = {"LVR": "LV", "LAR": "LA", "KAN": "KC", "NOR": "NO", "SFO": "SF",
           "TAM": "TB", "NWE": "NE", "GNB": "GB", "SDG": "LAC", "STL": "LA",
           "OAK": "LV", "ARZ": "ARI", "BLT": "BAL", "HST": "HOU", "CLV": "CLE",
           "JAC": "JAX", "LVR ": "LV"}
    known = set(df["team"].dropna().unique())
    return {k: v for k, v in fix.items() if v in known}


def landing(df: pd.DataFrame, dc: pd.DataFrame) -> pd.DataFrame:
    """Per team-season-position: how much opportunity walked out the door.

    Vacated share is the fraction of last season's work at that position held by
    players who are not on this season's August depth chart. Returning top share
    is the largest single share still in the building - the man in the way.
    """
    rows = []
    charted = set(zip(dc["player_id"], dc["season"], dc["team"]))
    on_roster = dc.groupby(["season", "team"])["player_id"].apply(set).to_dict()
    for (season, team, pos), g in df.groupby(["season", "team", "fantasy_pos"]):
        col = SHARE[pos]
        nxt = season + 1
        roster = on_roster.get((nxt, team))
        if roster is None:
            continue
        tot = g[col].sum()
        if not tot or pd.isna(tot):
            continue
        gone = g[~g["player_id"].isin(roster)][col].sum()
        stay = g[g["player_id"].isin(roster)][col]
        rows.append(dict(season=nxt, team=team, pos=pos,
                         vacated_share=float(gone / tot),
                         returning_top_share=float(stay.max() / tot) if len(stay) else 0.0))
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    dc = M.depth_chart()
    dcf = pd.read_csv(RAW / "depth_preseason.csv")
    dcf["depth_rank"] = pd.to_numeric(dcf["depth_rank"], errors="coerce")
    dcf = (dcf.sort_values("depth_rank")
              .drop_duplicates(["player_id", "season"], keep="first"))

    d = draft()
    d["team"] = d["team"].replace(team_map(df))
    land = landing(df, dcf)

    # team context from the season before the rookie's
    ctx = (df.dropna(subset=["team"])
             .groupby(["season", "team"])[["team_scoring_rank", "team_qb_epa_rank"]]
             .first().reset_index())
    ctx["season"] = ctx["season"] + 1

    # The current draft class carries placeholder ids (MEN516487) rather than
    # real gsis ids, which arrive once players are on a roster. Every prior class
    # is clean, so ids are used where they work and names fill the gap where they
    # do not - matched within season and team, so a shared surname cannot collide.
    r = d.merge(dcf[["player_id", "season", "depth_rank"]],
                on=["player_id", "season"], how="left")
    miss = r["depth_rank"].isna()
    if miss.any():
        alt = dcf[["player_name", "season", "team", "depth_rank"]].copy()
        alt["k"] = namekey(alt["player_name"])
        alt = alt.drop_duplicates(["k", "season", "team"])[["k", "season", "team", "depth_rank"]]
        fill = (r.loc[miss].assign(k=lambda x: namekey(x["player"]))
                 .merge(alt, on=["k", "season", "team"], how="left")["depth_rank_y"])
        r.loc[miss, "depth_rank"] = fill.values
    r = (r
          .merge(land, on=["season", "team", "pos"], how="left")
          .merge(ctx, on=["season", "team"], how="left"))

    # rookie-season outcome, if the season has been played
    out = df[["player_id", "season", "pos_rank", TARGET, "games"]]
    r = r.merge(out, on=["player_id", "season"], how="left")
    r[TARGET] = r[TARGET].fillna(0)          # never played = did not finish top-N
    return r[r["season"] >= 2015].copy()


def loso(r: pd.DataFrame, pos: str) -> pd.DataFrame:
    d = r[(r["pos"] == pos) & (r["season"] <= LAST_SEASON)].copy()
    out = []
    for s in sorted(d["season"].unique()):
        tr, te = d[d["season"] != s], d[d["season"] == s]
        if tr[TARGET].sum() < 3 or not len(te):
            continue
        m = M.make_model()
        m.fit(tr[FEATURES], tr[TARGET])
        te = te.copy()
        te["prob"] = m.predict_proba(te[FEATURES])[:, 1]
        out.append(te)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def main() -> None:
    r = build()
    print(f"{len(r):,} drafted rookies at fantasy positions, "
          f"{r.season.min()}-{r.season.max()}\n")
    print(f"{'pos':4s} {'n':>5s} {'hit top-'+str(TARGET_N):>12s} {'AUC':>7s} "
          f"{'mean pred':>10s}  calibration by draft round")
    keep = []
    for pos in POS:
        sc = loso(r, pos)
        if sc.empty:
            continue
        auc = roc_auc_score(sc[TARGET], sc["prob"])
        by = []
        for lo, hi, lab in [(1, 1, "r1"), (2, 3, "r2-3"), (4, 7, "r4-7")]:
            g = sc[sc["round"].between(lo, hi)]
            if len(g) >= 15:
                by.append(f"{lab} {g[TARGET].mean():.0%} (pred {g['prob'].mean():.0%})")
        print(f"{pos:4s} {len(sc):>5d} {sc[TARGET].mean():>12.1%} {auc:>7.3f} "
              f"{sc['prob'].mean():>10.1%}  {' · '.join(by)}")
        keep.append(sc)
    pd.concat(keep, ignore_index=True).to_csv(OUTPUT / "rookie_scores.csv", index=False)

    # the class that has not played yet
    up = r[r["season"] == LAST_SEASON + 1]
    print(f"\n\n{LAST_SEASON + 1} ROOKIES, scored\n")
    rows = []
    for pos in POS:
        tr = r[(r["pos"] == pos) & (r["season"] <= LAST_SEASON)]
        te = up[up["pos"] == pos]
        if tr[TARGET].sum() < 3 or te.empty:
            continue
        m = M.make_model()
        m.fit(tr[FEATURES], tr[TARGET])
        te = te.copy()
        te["raw_prob"] = m.predict_proba(te[FEATURES])[:, 1]
        te["above_tested_range"] = te["raw_prob"] > CEILING
        te["prob"] = te["raw_prob"].clip(upper=CEILING)
        rows.append(te)
        print(f"  {pos}")
        for _, x in te.nlargest(5, "raw_prob").iterrows():
            dr = f"{pos}{int(x.depth_rank)}" if pd.notna(x.depth_rank) else "unlisted"
            cap = " (capped, above tested range)" if x.above_tested_range else ""
            print(f"    {x.player[:22]:23s} {x.team:4s} p={x.prob:.3f}  "
                  f"pick {int(x['pick']):>3d}  {dr:>8s}  "
                  f"vacated {x.vacated_share:.0%}{cap}")
    pd.concat(rows, ignore_index=True).to_csv(
        OUTPUT / f"rookie_board_{LAST_SEASON + 1}.csv", index=False)
    print(f"\nwrote {OUTPUT / f'rookie_board_{LAST_SEASON + 1}.csv'}")


if __name__ == "__main__":
    main()
