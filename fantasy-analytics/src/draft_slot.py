"""Which seat in a 10-team snake is worth the most.

The question is not "who is good", it is what the snake geometry does to a
particular shape of value curve. Pick 1 gets picks 1, 20, 21, 40; pick 10 gets
10, 11, 30, 31. Whether that trade is good depends entirely on how steeply value
falls off at the top of the board, which changes year to year.

Two boards are simulated, because they answer different questions:

  perfect   everyone drafts in true final-value order. Isolates the geometry:
            given how the season actually turned out, which seat was best?
  market    everyone drafts by last season's finish, which is roughly how a
            real room orders its board. Adds the market's mistakes back in.

Scored on full PPR with a double flex: QB, RB, RB, WR, WR, TE, FLEX, FLEX,
where flex is RB/WR/TE. Every team's score is its best legal eight by actual
season points, chosen from the whole roster - so depth is worth something, as
it is in a real league where players miss time.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import OUTPUT

TEAMS = 10
ROUNDS = 14
STARTERS = dict(QB=1, RB=2, WR=2, TE=1)
FLEX = 2
FLEX_POS = ("RB", "WR", "TE")
# Caps stop the simulation drafting six quarterbacks; they are the roster shapes
# a competent room actually builds.
CAPS = dict(QB=2, TE=2, RB=6, WR=7)


def snake(teams: int, rounds: int) -> list[int]:
    order = []
    for r in range(rounds):
        seats = range(teams) if r % 2 == 0 else range(teams - 1, -1, -1)
        order.extend(seats)
    return order


# A real room does not draft the board in order. Each pick is sampled from the
# best few still available, which is what reaches and positional runs look like
# from the outside. Without this the simulation is deterministic - one outcome
# per season, ten observations per seat - and every seat difference it reports
# is noise.
REACH = 4.0
_POS = ("QB", "RB", "WR", "TE")


def draft(pos_idx: np.ndarray, rng: np.random.Generator) -> list[np.ndarray]:
    """Best available with reach noise, subject to positional caps.

    The board arrives pre-sorted by value, so "best available" is just the
    lowest surviving index. Caps are checked with a table lookup rather than a
    Python loop over every undrafted player, which is the difference between
    this finishing and not.
    """
    caps = np.array([CAPS[p] for p in _POS])
    counts = np.zeros((TEAMS, 4), int)
    taken = np.zeros(len(pos_idx), bool)
    rosters = [[] for _ in range(TEAMS)]
    for seat in snake(TEAMS, ROUNDS):
        room = counts[seat] < caps
        avail = np.flatnonzero(~taken & room[pos_idx])
        if not avail.size:
            continue
        w = np.exp(-np.arange(min(avail.size, 40)) / REACH)
        i = int(rng.choice(avail[: w.size], p=w / w.sum()))
        taken[i] = True
        rosters[seat].append(i)
        counts[seat, pos_idx[i]] += 1
    return [np.array(r) for r in rosters]


def lineup(points: np.ndarray, pos_idx: np.ndarray, idx: np.ndarray) -> float:
    """Best legal eight: fill the fixed slots, then flex from what is left."""
    idx = idx[np.argsort(-points[idx])]
    p = pos_idx[idx]
    used = np.zeros(len(idx), bool)
    total = 0.0
    for slot, n in STARTERS.items():
        k = _POS.index(slot)
        where = np.flatnonzero((p == k) & ~used)[:n]
        used[where] = True
        total += points[idx[where]].sum()
    flexible = np.flatnonzero(np.isin(p, FLEX_IDX) & ~used)[:FLEX]
    return float(total + points[idx[flexible]].sum())


FLEX_IDX = np.array([_POS.index(p) for p in FLEX_POS])


def vor(points: pd.Series, pos: pd.Series) -> pd.Series:
    """Value over the last man who would start. See project_points.add_vor."""
    order = points.sort_values(ascending=False).index
    ranked_pos = pos.loc[order]
    starting: set = set()
    for p, n in STARTERS.items():
        starting.update(order[(ranked_pos == p).values][: n * TEAMS])
    rest = order[np.isin(ranked_pos.values, FLEX_POS) & ~np.isin(order, list(starting))]
    starting.update(rest[: FLEX * TEAMS])
    base = {}
    for p in STARTERS:
        bench = [i for i in order if pos.loc[i] == p and i not in starting]
        base[p] = float(points.loc[bench[0]]) if bench else 0.0
    return points - pos.map(base)


def season_board(df: pd.DataFrame, season: int, how: str) -> pd.DataFrame | None:
    """The room's board, ordered by value over replacement rather than by points.

    Ordering on raw points would have every team spend its early picks on
    quarterbacks, who score most and are worth least, and the seat comparison
    would be measuring a mistake nobody makes.
    """
    cur = df[(df["season"] == season) &
             df["fantasy_pos"].isin(_POS)].reset_index(drop=True)
    if how == "perfect":
        key = vor(cur["fantasy_points_ppr"], cur["fantasy_pos"])
    else:
        prev = (df[df["season"] == season - 1][["player_id", "fantasy_points_ppr"]]
                .rename(columns={"fantasy_points_ppr": "prior"}))
        cur = cur.merge(prev, on="player_id", how="left")
        # a player with no track record goes to the back of a real room's board
        key = vor(cur["prior"].fillna(0.0), cur["fantasy_pos"])
    b = cur.copy()
    b["_k"] = key
    b = b.sort_values("_k", ascending=False).reset_index(drop=True)
    return b if len(b) >= TEAMS * ROUNDS else None


def simulate(board: pd.DataFrame, points_col: str, sims: int,
             rng: np.random.Generator, tag, noise: dict | None = None) -> list[dict]:
    """Draft on the board's order; score on what the players actually do.

    When `noise` is given the season is re-rolled each simulation - every
    player's outcome is his projection plus a draw from that position's observed
    projection error. Without it the only randomness is the draft order, and the
    standard errors come out around a point, which is a lie: the projections
    themselves miss by forty to sixty points a man.
    """
    points = board[points_col].to_numpy(float)
    pos_idx = board["fantasy_pos"].map({p: i for i, p in enumerate(_POS)}).to_numpy()
    sd = (np.array([noise[p] for p in _POS])[pos_idx]
          if noise else None)
    rows = []
    for _ in range(sims):
        outcome = points if sd is None else np.maximum(
            0.0, points + rng.normal(0.0, sd))
        scores = [lineup(outcome, pos_idx, r) for r in draft(pos_idx, rng)]
        place = pd.Series(scores).rank(ascending=False, method="min")
        for seat in range(TEAMS):
            rows.append(dict(**tag, seat=seat + 1, points=scores[seat],
                             place=int(place[seat])))
    return rows


def run(how: str, sims: int = 150, seed: int = 0) -> pd.DataFrame:
    df = pd.read_csv(OUTPUT / "player_seasons.csv", low_memory=False)
    rng = np.random.default_rng(seed)
    rows = []
    for season in range(2016, int(df["season"].max()) + 1):
        b = season_board(df, season, how)
        if b is not None:
            rows += simulate(b, "fantasy_points_ppr", sims, rng, dict(season=season))
    return pd.DataFrame(rows)


def upcoming_board(sims: int = 1200, seed: int = 1) -> pd.DataFrame:
    """The seat question for the season that has not happened yet.

    Scored on projected points rather than actual ones, which is the right
    currency for a decision made before the season: it asks which seat the
    shape of *this* board rewards, not which seat got lucky.
    """
    from config import LAST_SEASON
    b = pd.read_csv(OUTPUT / f"projected_points_{LAST_SEASON + 1}.csv")
    b = b[b["fantasy_pos"].isin(_POS)].copy()
    b["_k"] = vor(b["proj"], b["fantasy_pos"])
    b = b.sort_values("_k", ascending=False).reset_index(drop=True)
    # spread of the projection's own errors, measured leave-one-season-out
    noise = {"QB": 76.0, "RB": 70.0, "WR": 60.0, "TE": 47.0}
    rng = np.random.default_rng(seed)
    return pd.DataFrame(simulate(b, "proj", sims, rng,
                                 dict(season=LAST_SEASON + 1), noise=noise))


def report(r: pd.DataFrame, title: str, n_indep: int) -> None:
    print(f"\n{'=' * 74}\n{title}\n{'=' * 74}")
    print(f"{'seat':>4} {'mean pts':>10} {'vs field':>9} {'std err':>8} "
          f"{'top-3':>7} {'last-3':>7}")
    mean_all = r["points"].mean()
    for seat, x in r.groupby("seat"):
        se = x["points"].std(ddof=1) / np.sqrt(n_indep)
        print(f"{seat:>4} {x['points'].mean():>10.0f} "
              f"{x['points'].mean() - mean_all:>+9.0f} {se:>8.0f} "
              f"{(x['place'] <= 3).mean():>6.0%} {(x['place'] >= 8).mean():>7.0%}")


def main() -> None:
    for how in ("perfect", "market"):
        r = run(how)
        report(r, f"{how.upper()} BOARD  -  {r.season.nunique()} seasons, {TEAMS}-team "
                  f"snake, {ROUNDS} rounds, full PPR, double flex", r.season.nunique())
        r.to_csv(OUTPUT / f"draft_slot_{how}.csv", index=False)
    u = upcoming_board()
    report(u, f"PROJECTED {int(u.season.iloc[0])} BOARD  -  "
              f"{len(u) // TEAMS:,} simulated drafts, scored on projected points",
           len(u) // TEAMS)
    u.to_csv(OUTPUT / "draft_slot_upcoming.csv", index=False)
    print(f"\nwrote {OUTPUT / 'draft_slot_*.csv'}")


if __name__ == "__main__":
    main()
