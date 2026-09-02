"""Find the statistical bar that top-5 fantasy seasons clear, per position.

Two questions are answered separately, because they are not the same question:

  PROFILE   - what did a top-5 season look like *while it was happening*?
              (this is what the popular "5 rules" graphics actually show)
  PREDICT   - what did we know *before* the season about players who then
              finished top-5? Inputs are prior-year production plus things
              settled in the offseason (age, team, draft capital).

For every candidate metric the engine picks the loosest threshold that still
keeps a target share of top-5 seasons above it, then reports how often a
player clearing that bar actually finished top-5 (precision) and how much
that beats the base rate (lift).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from config import OUTPUT, STUDY_SEASONS, TARGET

# Higher is better unless the metric is listed here (ranks: lower is better).
LOWER_IS_BETTER = {"team_scoring_rank", "team_qb_epa_rank", "age", "team_pace_rank"}

POOL_RULES = {
    "WR": dict(games=8, targets=30),
    "TE": dict(games=8, targets=20),
    "RB": dict(games=8, touches=50),
    "QB": dict(games=8, attempts=200),
}

# Candidate metrics grouped into families. The card takes the best metric from
# each family so the five rules measure five different things.
FAMILIES = {
    "WR": {
        "Target volume": ["target_share", "targets_pg", "wopr"],
        "Route efficiency": ["yprr_shrunk", "ypt_shrunk"],
        "Scoring role": ["rz_targets_share", "air_yards_share"],
        "Offense quality": ["team_scoring_rank", "team_ppg"],
        "QB quality": ["team_qb_epa_rank"],
        "Field time": ["snap_pct", "routes_pg"],
        "Age / profile": ["age", "exp"],
    },
    "TE": {
        "Target volume": ["target_share", "targets_pg", "wopr"],
        "Route efficiency": ["yprr_shrunk", "ypt_shrunk"],
        "Scoring role": ["rz_targets_share"],
        "Offense quality": ["team_scoring_rank", "team_ppg"],
        "QB quality": ["team_qb_epa_rank"],
        "Field time": ["snap_pct", "routes_pg"],
        "Age / profile": ["age", "exp"],
    },
    "RB": {
        "Total volume": ["weighted_opps_pg", "touches_pg", "opportunity_share"],
        "Passing-game role": ["target_share", "targets_pg"],
        "Goal-line role": ["i5_carries_share", "rz_carries_share"],
        "Field time": ["snap_pct"],
        "Efficiency": ["ypc_shrunk", "ypt_shrunk"],
        "Offense quality": ["team_scoring_rank", "team_ppg"],
        "Age / profile": ["age", "exp"],
    },
    "QB": {
        "Rushing volume": ["rush_att_pg", "rushing_yards"],
        "Rushing scores": ["rushing_tds"],
        "Passing efficiency": ["epa_per_dropback"],
        "Dropback volume": ["dropbacks", "pass_att_pg"],
        "Passing scoring rate": ["pass_td_rate"],
        "Offense quality": ["team_scoring_rank", "team_ppg"],
        "Age / profile": ["age", "exp"],
    },
}

# Metrics that are partly a restatement of the fantasy score itself. They are
# still reported, but flagged so nobody mistakes them for independent evidence.
CIRCULAR = {
    # a QB's fantasy score is largely his passing box score restated
    "QB": {"team_ppg", "team_scoring_rank", "pass_td_rate"},
    "WR": {"receiving_epa"},
    "TE": {"receiving_epa"},
    "RB": set(),
}

PRETTY = {
    "target_share": "Target share", "targets_pg": "Targets per game",
    "wopr": "WOPR (weighted opportunity)", "yprr_est": "Yards per route (est.)",
    "yards_per_target": "Yards per target", "rz_targets_share": "Red-zone target share",
    "air_yards_share": "Air-yards share", "team_scoring_rank": "Team scoring rank",
    "team_ppg": "Team points per game", "team_qb_epa_rank": "QB rank in EPA/dropback",
    "snap_pct": "Snap share", "routes_pg": "Routes per game (est.)", "age": "Age",
    "exp": "Seasons of experience", "weighted_opps_pg": "Weighted opportunities per game",
    "touches_pg": "Touches per game", "opportunity_share": "Team opportunity share",
    "i5_carries_share": "Carry share inside the 5",
    "rz_carries_share": "Red-zone carry share", "yards_per_carry": "Yards per carry",
    "rush_att_pg": "Rush attempts per game", "rushing_yards": "Rushing yards",
    "epa_per_dropback": "EPA per dropback", "pass_td_rate": "TD rate per attempt",
    "dropbacks": "Dropbacks", "pass_att_pg": "Pass attempts per game", "rushing_tds": "Rushing TDs",
    "rush_share": "Rush share", "receiving_epa": "Receiving EPA",
    "yprr_shrunk": "Yards per route (est., shrunk)",
    "ypt_shrunk": "Yards per target (shrunk)",
    "ypc_shrunk": "Yards per carry (shrunk)",
    "ppg_shrunk": "PPR per game (shrunk)",
}


def pool(df: pd.DataFrame, pos: str) -> pd.DataFrame:
    d = df[(df["fantasy_pos"] == pos) & (df["season"].isin(STUDY_SEASONS))]
    for col, lo in POOL_RULES[pos].items():
        d = d[d[col] >= lo]
    return d.copy()


def auc(y: np.ndarray, x: np.ndarray) -> float:
    m = ~pd.isna(x)
    y, x = y[m], x[m]
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 < 3 or n0 < 3:
        return np.nan
    r = pd.Series(x).rank().values
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def nice_round(v: float, metric: str) -> float:
    """Round a threshold to a number a human would actually say out loud."""
    if metric in {"team_scoring_rank", "team_qb_epa_rank", "exp"}:
        return float(int(round(v)))
    if metric in {"dropbacks", "rushing_yards"}:
        return float(int(round(v / 25.0) * 25))
    if abs(v) >= 20:
        return round(v, 0)
    if abs(v) >= 3:
        return round(v * 2) / 2
    if metric in {"target_share", "snap_pct", "air_yards_share", "rz_targets_share",
                  "i5_carries_share", "rz_carries_share", "opportunity_share",
                  "rush_share", "pass_td_rate"}:
        return round(v, 2)
    return round(v, 2)


def evaluate(d: pd.DataFrame, metric: str, thr: float, target: str) -> dict:
    lower = metric in LOWER_IS_BETTER
    x = d[metric]
    flag = (x <= thr) if lower else (x >= thr)
    flag = flag.fillna(False)
    y = d[target].astype(bool)
    n_flag = int(flag.sum())
    hits = int((flag & y).sum())
    base = float(y.mean())
    n_seasons = d["season"].nunique()
    return {
        "metric": metric, "label": PRETTY.get(metric, metric),
        "direction": "<=" if lower else ">=", "threshold": float(thr),
        "n_flagged": n_flag, "hits": hits,
        "per_season_flagged": n_flag / n_seasons if n_seasons else np.nan,
        "precision": hits / n_flag if n_flag else np.nan,
        "recall": hits / int(y.sum()) if y.sum() else np.nan,
        "base_rate": base,
        "lift": (hits / n_flag) / base if n_flag and base else np.nan,
    }


def best_threshold(d: pd.DataFrame, metric: str, target: str,
                   min_recall: float = 0.85) -> dict:
    """Loosest bar that still keeps `min_recall` of the elite seasons above it."""
    lower = metric in LOWER_IS_BETTER
    elite = d.loc[d[target] == 1, metric].dropna()
    if len(elite) < 5:
        return {}
    q = min_recall if lower else 1 - min_recall
    raw = float(np.quantile(elite, q))
    thr = nice_round(raw, metric)
    res = evaluate(d, metric, thr, target)
    # A rounded bar can drop below the recall target; step back one notch if so.
    if res["recall"] < min_recall - 0.05:
        step = 0.01 if abs(thr) < 3 else (0.5 if abs(thr) < 20 else 1.0)
        thr = thr + step if lower else thr - step
        res = evaluate(d, metric, nice_round(thr, metric), target)
    res["raw_quantile"] = raw
    res["auc"] = auc(d[target].values, d[metric].values)
    return res


MIN_LIFT = 1.35     # below this a "rule" barely narrows the field
VACUOUS_LIFT = 1.25  # at or below this it is decoration, not a filter


def scan_threshold(d: pd.DataFrame, metric: str, target: str,
                   min_flagged: int = 15) -> dict:
    """The bar that maximises hit rate, not the bar everyone clears.

    `best_threshold` answers "what floor did nearly every elite season clear?".
    This answers the opposite question: "what bar, once cleared, most often
    means a top-5 finish?" - subject to flagging enough seasons to be real.
    """
    lower = metric in LOWER_IS_BETTER
    x = d[metric].dropna()
    if len(x) < 50:
        return {}
    qs = np.linspace(0.50, 0.995, 60) if not lower else np.linspace(0.005, 0.50, 60)
    best = None
    for q in qs:
        thr = nice_round(float(np.quantile(x, q)), metric)
        r = evaluate(d, metric, thr, target)
        if r["n_flagged"] < min_flagged:
            continue
        if best is None or (r["precision"] or 0) > (best["precision"] or 0):
            best = r
    if best:
        best["auc"] = auc(d[target].values, d[metric].values)
    return best or {}


def build_card(d: pd.DataFrame, pos: str, target: str, families: dict,
               min_recall: float = 0.85, n_rules: int = 5,
               drop_circular: bool = True) -> dict:
    """Pick one metric per family, keep the `n_rules` most discriminating.

    Rules that almost everyone already passes are rejected rather than padded
    into the card - a filter that removes nobody is not a finding.
    """
    picks = []
    for fam, metrics in families.items():
        scored = []
        for m in metrics:
            if m not in d.columns:
                continue
            r = best_threshold(d, m, target, min_recall)
            if not r:
                continue
            r["family"] = fam
            r["circular"] = m in CIRCULAR.get(pos, set())
            scored.append(r)
        if scored:
            scored.sort(key=lambda r: -(r["lift"] if not np.isnan(r["lift"]) else 0))
            picks.append(scored[0])
    picks.sort(key=lambda r: -(r["lift"] if not np.isnan(r["lift"]) else 0))

    vacuous = [r for r in picks if not np.isnan(r["lift"]) and r["lift"] <= VACUOUS_LIFT]
    eligible = [r for r in picks
                if not (drop_circular and r["circular"])
                and not np.isnan(r["lift"]) and r["lift"] >= MIN_LIFT]
    rules = eligible[:n_rules]

    mask = pd.Series(True, index=d.index)
    for r in rules:
        col = d[r["metric"]]
        m = (col <= r["threshold"]) if r["direction"] == "<=" else (col >= r["threshold"])
        mask &= m.fillna(False)
    y = d[target].astype(bool)
    n_flag = int(mask.sum())
    hits = int((mask & y).sum())
    base = float(y.mean())
    n_seasons = d["season"].nunique()
    joint = {
        "n_pool": int(len(d)), "n_elite": int(y.sum()), "base_rate": base,
        "n_flagged": n_flag, "hits": hits, "n_seasons": int(n_seasons),
        "per_season_flagged": n_flag / n_seasons if n_seasons else np.nan,
        "precision": hits / n_flag if n_flag else np.nan,
        "recall": hits / int(y.sum()) if y.sum() else np.nan,
        "lift": (hits / n_flag) / base if n_flag and base else np.nan,
    }
    # Green flags: the strongest single signals, regardless of how many elite
    # seasons they miss. One per family again, so they measure different things.
    greens = []
    for fam, metrics in families.items():
        cands = []
        for m in metrics:
            if m not in d.columns or (drop_circular and m in CIRCULAR.get(pos, set())):
                continue
            g = scan_threshold(d, m, target)
            if g:
                g["family"] = fam
                cands.append(g)
        if cands:
            cands.sort(key=lambda r: -(r["precision"] or 0))
            greens.append(cands[0])
    greens.sort(key=lambda r: -(r["precision"] or 0))

    return {"rules": rules, "green_flags": greens[:5], "all_candidates": picks,
            "vacuous": vacuous, "joint": joint,
            "flagged_index": d.index[mask].tolist()}


def predictive_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Join each player-season to the season *before* it.

    Prior-year player production is carried forward as `prev_*`. Team and QB
    context is taken from the year-N team's year-N-1 season, which is what an
    analyst actually knows in August.
    """
    keep = [c for c in df.columns if c not in
            {"player_display_name", "fantasy_pos", "team", "birth_date", "gsis_id"}]
    prev = df[["player_id", "season"] + [c for c in keep if c != "player_id"
                                         and c != "season"]].copy()
    prev["season"] = prev["season"] + 1
    prev = prev.rename(columns={c: f"prev_{c}" for c in prev.columns
                                if c not in {"player_id", "season"}})
    out = df.merge(prev, on=["player_id", "season"], how="inner")

    team_cols = ["team_ppg", "team_scoring_rank", "team_qb_epa_rank", "team_pass_rate",
                 "team_plays", "team_dropbacks"]
    team_prev = (df.dropna(subset=["team"])
                   .groupby(["season", "team"])[team_cols].first().reset_index())
    team_prev["season"] = team_prev["season"] + 1
    team_prev = team_prev.rename(columns={c: f"newteam_prev_{c}" for c in team_cols})
    out = out.merge(team_prev, on=["season", "team"], how="left")
    return out


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    results, rows = {}, []

    for pos in ["QB", "RB", "WR", "TE"]:
        d = pool(df, pos)
        prof = build_card(d, pos, TARGET, FAMILIES[pos])
        prof1 = build_card(d, pos, "top1", FAMILIES[pos], min_recall=0.8)
        flagged = d.loc[prof["flagged_index"]]
        results[pos] = {
            "pool": {"n": int(len(d)), "seasons": sorted(d["season"].unique().tolist()),
                     "rule": POOL_RULES[pos]},
            "profile_top5": prof, "profile_top1": prof1,
            "flagged_seasons": flagged[[
                "season", "player_display_name", "team", "pos_rank",
                "fantasy_points_ppr"]].sort_values(["season", "pos_rank"]).to_dict("records"),
            "elite_seasons": d[d[TARGET] == 1][[
                "season", "player_display_name", "team", "pos_rank",
                "fantasy_points_ppr"]].sort_values(["season", "pos_rank"]).to_dict("records"),
        }
        for r in prof["all_candidates"]:
            rows.append({"position": pos, "mode": "profile_top5", **r})

    OUTPUT.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT / "thresholds_profile.csv", index=False)
    with open(OUTPUT / "profile_cards.json", "w") as fh:
        json.dump(results, fh, indent=2, default=str)

    for pos in ["QB", "RB", "WR", "TE"]:
        j = results[pos]["profile_top5"]["joint"]
        print(f"\n### {pos}  pool={j['n_pool']}  top5={j['n_elite']}  "
              f"base={j['base_rate']:.1%}")
        for r in results[pos]["profile_top5"]["rules"]:
            print(f"   {r['label']:32s} {r['direction']} {r['threshold']:<8g} "
                  f"recall={r['recall']:.0%}  hit={r['precision']:.0%}  "
                  f"lift={r['lift']:.1f}x{'  [circular]' if r['circular'] else ''}")
        print(f"   ALL {len(results[pos]['profile_top5']['rules'])} GATES -> "
              f"{j['n_flagged']} seasons flagged, {j['hits']} were top-5 "
              f"({j['precision']:.0%} hit rate, {j['lift']:.1f}x base, "
              f"catches {j['recall']:.0%} of top-5s, "
              f"~{j['per_season_flagged']:.1f} players a season)")
        print("   green flags (clear this and you are probably top-5):")
        for g in results[pos]["profile_top5"]["green_flags"]:
            print(f"     {g['label']:32s} {g['direction']} {g['threshold']:<8g} "
                  f"hit={g['precision']:.0%}  lift={g['lift']:.1f}x  "
                  f"~{g['per_season_flagged']:.1f}/season  "
                  f"(catches {g['recall']:.0%} of top-5s)")
        vac = results[pos]["profile_top5"]["vacuous"]
        if vac:
            print("   sounds strict, filters almost nobody: " +
                  "; ".join(f"{v['label']} {v['direction']} {v['threshold']:g} "
                            f"({v['lift']:.1f}x)" for v in vac))


if __name__ == "__main__":
    main()
