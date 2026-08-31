"""Expected fantasy points for the upcoming season, not just a hit probability.

The board model answers "will he finish top-8", which is the right question for
targeting and the wrong one for choosing a draft seat. Seat value depends on the
shape of the whole value curve - how far the drop is from pick 1 to pick 10, and
whether it is steeper than the drop from 10 to 20 - so it needs points.

Same features and the same leave-one-season-out discipline as the classifier;
only the target changes, to full-PPR season total. Players who missed time are
predicted at the points they would score, injuries included, because that is
what a drafted player actually returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import model as M
from config import LAST_SEASON, OUTPUT
from draft_slot import FLEX, FLEX_POS, STARTERS, TEAMS

TARGET_COL = "fantasy_points_ppr"


def regressor():
    return make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                         Ridge(alpha=5.0))


def frame_with_points(df: pd.DataFrame) -> pd.DataFrame:
    pf = M.frame(df)
    return pf.merge(df[["player_id", "season", TARGET_COL]],
                    on=["player_id", "season"], how="left")


def loso(d: pd.DataFrame, feats: list[str]) -> pd.DataFrame:
    out = []
    for s in sorted(d["season"].unique()):
        tr, te = d[d["season"] != s], d[d["season"] == s]
        if len(tr) < 50 or not len(te):
            continue
        m = regressor()
        m.fit(tr[feats], tr[TARGET_COL])
        te = te.copy()
        te["proj"] = m.predict(te[feats])
        out.append(te)
    return pd.concat(out, ignore_index=True)


def add_vor(d: pd.DataFrame) -> pd.DataFrame:
    """Points over the last man who would start, position by position.

    Raw points are the wrong currency in a one-quarterback league: the QB1 and
    the QB10 occupy the same single roster slot, so a quarterback is worth only
    his margin over the one you could have had for nothing. Ranking on raw
    points drafts twelve quarterbacks in two rounds.

    Replacement level is derived rather than assumed - fill the fixed slots, let
    the best remaining RB/WR/TE take the flex spots, and the best player still
    not starting anywhere sets the baseline for his position.
    """
    d = d.sort_values("proj", ascending=False).reset_index(drop=True)
    starting: set[int] = set()
    for pos, n in STARTERS.items():
        starting.update(d.index[d["fantasy_pos"] == pos][: n * TEAMS])
    flexible = d.index[d["fantasy_pos"].isin(FLEX_POS) & ~d.index.isin(starting)]
    starting.update(flexible[: FLEX * TEAMS])

    base = {}
    for pos in STARTERS:
        bench = d[(d["fantasy_pos"] == pos) & ~d.index.isin(starting)]
        base[pos] = float(bench["proj"].iloc[0]) if len(bench) else 0.0
    d["replacement"] = d["fantasy_pos"].map(base)
    d["vor"] = d["proj"] - d["replacement"]
    print("\nreplacement level (last starter), 10 teams, double flex:")
    print("  " + " · ".join(f"{p} {v:.0f}" for p, v in base.items()))
    return d


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    pf = frame_with_points(df)

    print(f"{'pos':4s} {'n':>5s} {'corr':>7s} {'MAE':>7s} {'mean actual':>12s} "
          f"{'mean proj':>10s}")
    projections = []
    for pos in ["QB", "RB", "WR", "TE"]:
        f = M.features(pos)
        d = pf[(pf["fantasy_pos"] == pos) & pf["season"].between(2016, LAST_SEASON)]
        d = d[M.qualifies(d, pos)].dropna(subset=["age", TARGET_COL])
        sc = loso(d, f)
        corr = np.corrcoef(sc["proj"], sc[TARGET_COL])[0, 1]
        mae = (sc["proj"] - sc[TARGET_COL]).abs().mean()
        print(f"{pos:4s} {len(sc):>5d} {corr:>7.3f} {mae:>7.1f} "
              f"{sc[TARGET_COL].mean():>12.0f} {sc['proj'].mean():>10.0f}")

        m = regressor()
        m.fit(d[f], d[TARGET_COL])
        up = M.upcoming(df, pos).copy()
        up["proj"] = m.predict(up[f])
        projections.append(up[["player_id", "player_display_name", "team",
                               "fantasy_pos", "age", "proj", "depth_rank"]])

    out = pd.concat(projections, ignore_index=True)
    # employment: a player on nobody's roster is not draftable
    try:
        av = pd.read_csv(OUTPUT / f"availability_{LAST_SEASON + 1}.csv")
        ok = set(av[av["available"]]["player_id"])
        before = len(out)
        out = out[out["player_id"].isin(ok)]
        print(f"\ndropped {before - len(out)} players with no "
              f"{LAST_SEASON + 1} roster spot")
    except FileNotFoundError:
        pass

    out = add_vor(out).sort_values("vor", ascending=False).reset_index(drop=True)
    out.to_csv(OUTPUT / f"projected_points_{LAST_SEASON + 1}.csv", index=False)
    print(f"\nTop 24 of the projected {LAST_SEASON + 1} board:\n")
    for i, r in out.head(24).iterrows():
        print(f"  {i + 1:>2}. {r.player_display_name[:22]:23s} "
              f"{r.fantasy_pos:3s} {str(r.team):4s} {r.proj:>6.0f} pts  "
              f"VOR {r.vor:>+6.0f}")
    print(f"\nwrote {OUTPUT / f'projected_points_{LAST_SEASON + 1}.csv'}")


if __name__ == "__main__":
    main()
