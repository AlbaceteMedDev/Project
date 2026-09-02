"""Audit the viral "5 rules for WR1s" card against the actual record.

The card claims every overall WR1 since 2016 was: under 30, 25%+ target rate,
2.3+ yards per route, on a top-11 scoring offense, with a top-10 QB by
EPA/dropback. Each rule is scored two ways:

  recall    - share of WR1 (and top-5) seasons that actually cleared it
  base rate - share of the *whole* WR pool that clears it anyway

A rule with high recall and a high base rate is not insight, it is a filter
that removes almost nobody.
"""
from __future__ import annotations

import json

import pandas as pd

from analyze import pool
from config import OUTPUT

# yprr_est runs above PFF-charted YPRR because estimated routes are
# conservative; 2.3 PFF maps to roughly 2.5 in these units. Both are scored.
VIRAL_RULES = [
    ("Under 30 years old", "age", "<=", 29.99),
    ("25%+ target share", "target_share", ">=", 0.25),
    ("2.3+ yards per route (as stated)", "yprr_est", ">=", 2.30),
    ("2.5+ yards per route (PFF-equivalent)", "yprr_est", ">=", 2.50),
    ("Top-11 scoring offense", "team_scoring_rank", "<=", 11),
    ("Top-10 QB in EPA/dropback", "team_qb_epa_rank", "<=", 10),
]
CARD = [r for r in VIRAL_RULES if r[0] != "2.5+ yards per route (PFF-equivalent)"]


def apply_rule(d: pd.DataFrame, col: str, op: str, thr: float) -> pd.Series:
    s = (d[col] <= thr) if op == "<=" else (d[col] >= thr)
    return s.fillna(False)


def main() -> None:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    wr = pool(df, "WR")
    wr = wr[wr["season"] >= 2016]          # the card's own window
    wr1 = wr[wr["pos_rank"] == 1]
    top5 = wr[wr["top5"] == 1]

    rows = []
    for label, col, op, thr in VIRAL_RULES:
        m_all = apply_rule(wr, col, op, thr)
        rows.append({
            "rule": label, "metric": col, "op": op, "threshold": thr,
            "wr1_pass": int(apply_rule(wr1, col, op, thr).sum()), "wr1_n": len(wr1),
            "top5_pass": int(apply_rule(top5, col, op, thr).sum()), "top5_n": len(top5),
            "pool_pass_rate": float(m_all.mean()),
            "precision": float(wr.loc[m_all, "top5"].mean()),
            "lift": float(wr.loc[m_all, "top5"].mean() / wr["top5"].mean()),
        })
    audit = pd.DataFrame(rows)

    joint = pd.Series(True, index=wr.index)
    for _, col, op, thr in CARD:
        joint &= apply_rule(wr, col, op, thr)
    joint_stats = {
        "n_pool": int(len(wr)), "n_wr1": int(len(wr1)), "n_top5": int(len(top5)),
        "first_season": int(wr["season"].min()), "last_season": int(wr["season"].max()),
        "n_flagged": int(joint.sum()),
        "n_top5_flagged": int(wr.loc[joint, "top5"].sum()),
        "n_wr1_flagged": int((wr.loc[joint, "pos_rank"] == 1).sum()),
        "precision_top5": float(wr.loc[joint, "top5"].mean()),
        "recall_top5": float(wr.loc[joint, "top5"].sum() / wr["top5"].sum()),
        "recall_wr1": float((wr.loc[joint, "pos_rank"] == 1).sum() / len(wr1)),
        "base_rate": float(wr["top5"].mean()),
    }

    # Which WR1 seasons the card would have missed, and why.
    misses = []
    for _, r in wr1.iterrows():
        failed = [label for label, col, op, thr in CARD
                  if not apply_rule(pd.DataFrame([r]), col, op, thr).iloc[0]]
        if failed:
            misses.append({"season": int(r["season"]),
                           "player": r["player_display_name"],
                           "failed": failed})

    audit.to_csv(OUTPUT / "viral_rule_audit.csv", index=False)
    with open(OUTPUT / "viral_rule_audit.json", "w") as fh:
        json.dump({"rules": rows, "joint": joint_stats, "wr1_misses": misses},
                  fh, indent=2, default=str)

    print(f"WR pool 2016-2025: {len(wr)} seasons | {len(wr1)} WR1s | "
          f"{len(top5)} top-5 seasons | base rate {joint_stats['base_rate']:.1%}\n")
    print(f"{'rule':42s} {'WR1s':>7s} {'top-5':>8s} {'pool':>7s} {'hit':>6s} {'lift':>6s}")
    for r in rows:
        print(f"{r['rule']:42s} {r['wr1_pass']:>3d}/{r['wr1_n']:<3d} "
              f"{r['top5_pass']:>3d}/{r['top5_n']:<4d} {r['pool_pass_rate']:>6.0%} "
              f"{r['precision']:>6.0%} {r['lift']:>5.1f}x")
    print(f"\nAll five together: {joint_stats['n_flagged']} seasons flagged, "
          f"{joint_stats['n_top5_flagged']} were top-5 "
          f"({joint_stats['precision_top5']:.0%} hit rate), "
          f"catching {joint_stats['recall_wr1']:.0%} of WR1s and "
          f"{joint_stats['recall_top5']:.0%} of top-5 seasons")
    print("\nWR1 seasons the card would have missed:")
    for m in misses:
        print(f"  {m['season']} {m['player']:20s} failed: {'; '.join(m['failed'])}")


if __name__ == "__main__":
    main()
