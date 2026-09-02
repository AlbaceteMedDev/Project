"""Build the season-level player/team dataset used by the archetype study.

Sources (all nflverse public releases):
  * stats_player_week_{season}.csv  - weekly box-score + efficiency stats
  * play_by_play_{season}.parquet   - team context, QB EPA, red-zone usage
  * snap_counts_{season}.csv.gz     - snap share (and the route estimate)
  * players.csv                     - birth dates, draft capital, id crosswalk

Output: output/player_seasons.csv - one row per player-season with every
metric the threshold search is allowed to look at.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import (DATA, MIN_GAMES, OUTPUT, POSITION_MAP, QB_MIN_DROPBACKS,
                    RAW, SEASONS, season_games)

PBP_COLS = [
    "game_id", "season", "season_type", "week", "posteam", "home_team", "away_team",
    "home_score", "away_score", "play_type", "qb_dropback", "qb_scramble", "sack",
    "pass_attempt", "rush_attempt", "yardline_100", "passer_player_id",
    "rusher_player_id", "receiver_player_id", "qb_epa", "touchdown", "two_point_attempt",
]


def load_players() -> pd.DataFrame:
    p = pd.read_csv(RAW / "players.csv", low_memory=False)
    keep = ["gsis_id", "pfr_id", "display_name", "birth_date", "draft_year",
            "draft_round", "draft_pick", "rookie_season", "height", "weight"]
    p = p[[c for c in keep if c in p.columns]].copy()
    p["birth_date"] = pd.to_datetime(p["birth_date"], errors="coerce")
    return p


def pbp_season(season: int) -> pd.DataFrame:
    df = pd.read_parquet(RAW / f"pbp_{season}.parquet", columns=PBP_COLS)
    return df[df["season_type"] == "REG"].copy()


def team_context(pbp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-game and per-season team offensive context."""
    # Final score of each game, from the team's own perspective.
    games = pbp.drop_duplicates("game_id")[
        ["game_id", "home_team", "away_team", "home_score", "away_score"]]
    home = games.rename(columns={"home_team": "team", "home_score": "points_for",
                                 "away_score": "points_against"})[
        ["game_id", "team", "points_for", "points_against"]]
    away = games.rename(columns={"away_team": "team", "away_score": "points_for",
                                 "home_score": "points_against"})[
        ["game_id", "team", "points_for", "points_against"]]
    scores = pd.concat([home, away], ignore_index=True)

    off = pbp[pbp["posteam"].notna()]
    per_game = off.groupby(["game_id", "posteam"]).agg(
        dropbacks=("qb_dropback", "sum"),
        team_pass_att=("pass_attempt", "sum"),
        team_rush_att=("rush_attempt", "sum"),
        plays=("play_type", lambda s: s.isin(["pass", "run"]).sum()),
    ).reset_index().rename(columns={"posteam": "team"})
    per_game = per_game.merge(scores, on=["game_id", "team"], how="left")
    per_game["week"] = per_game["game_id"].str.split("_").str[1].astype(int)

    season_tot = per_game.groupby("team").agg(
        team_games=("game_id", "nunique"),
        team_dropbacks=("dropbacks", "sum"),
        team_points=("points_for", "sum"),
        team_plays=("plays", "sum"),
        team_pass_att_pbp=("team_pass_att", "sum"),
        team_rush_att_pbp=("team_rush_att", "sum"),
    ).reset_index()
    season_tot["team_ppg"] = season_tot["team_points"] / season_tot["team_games"]
    season_tot["team_pass_rate"] = (
        season_tot["team_dropbacks"] /
        (season_tot["team_dropbacks"] + season_tot["team_rush_att_pbp"]))
    season_tot["team_scoring_rank"] = season_tot["team_ppg"].rank(
        ascending=False, method="min").astype(int)
    season_tot["team_pace_rank"] = season_tot["team_plays"].rank(
        ascending=False, method="min").astype(int)
    return per_game, season_tot


def qb_leaderboard(pbp: pd.DataFrame) -> pd.DataFrame:
    """EPA per dropback for every passer, plus the league rank among qualifiers."""
    db = pbp[(pbp["qb_dropback"] == 1) & pbp["passer_player_id"].notna()]
    lb = db.groupby("passer_player_id").agg(
        qb_dropbacks=("qb_epa", "size"),
        qb_epa_total=("qb_epa", "sum"),
        qb_team=("posteam", lambda s: s.mode().iat[0] if len(s.mode()) else None),
    ).reset_index().rename(columns={"passer_player_id": "player_id"})
    lb["epa_per_dropback"] = lb["qb_epa_total"] / lb["qb_dropbacks"]
    qual = lb["qb_dropbacks"] >= QB_MIN_DROPBACKS
    lb["qb_epa_rank"] = np.nan
    lb.loc[qual, "qb_epa_rank"] = lb.loc[qual, "epa_per_dropback"].rank(
        ascending=False, method="min")
    lb["qb_qualified"] = qual
    return lb


def team_primary_qb(lb: pd.DataFrame) -> pd.DataFrame:
    """The QB who took the most dropbacks for each team, and how good he was."""
    idx = lb.groupby("qb_team")["qb_dropbacks"].idxmax()
    tq = lb.loc[idx, ["qb_team", "player_id", "epa_per_dropback", "qb_epa_rank",
                      "qb_dropbacks"]]
    return tq.rename(columns={
        "qb_team": "team", "player_id": "team_qb_id",
        "epa_per_dropback": "team_qb_epa_per_db", "qb_epa_rank": "team_qb_epa_rank",
        "qb_dropbacks": "team_qb_dropbacks"})


def red_zone_usage(pbp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-player red-zone / inside-10 / inside-5 opportunity counts and team totals."""
    off = pbp[pbp["posteam"].notna()].copy()
    off["rz"] = off["yardline_100"] <= 20
    off["i10"] = off["yardline_100"] <= 10
    off["i5"] = off["yardline_100"] <= 5

    tgt = off[(off["pass_attempt"] == 1) & off["receiver_player_id"].notna()]
    car = off[(off["rush_attempt"] == 1) & off["rusher_player_id"].notna()]

    p_t = tgt.groupby("receiver_player_id").agg(
        rz_targets=("rz", "sum"), i10_targets=("i10", "sum"),
        i5_targets=("i5", "sum")).reset_index().rename(
        columns={"receiver_player_id": "player_id"})
    p_c = car.groupby("rusher_player_id").agg(
        rz_carries=("rz", "sum"), i10_carries=("i10", "sum"),
        i5_carries=("i5", "sum")).reset_index().rename(
        columns={"rusher_player_id": "player_id"})
    player = p_t.merge(p_c, on="player_id", how="outer").fillna(0)

    t_t = tgt.groupby("posteam").agg(
        team_rz_targets=("rz", "sum"), team_i10_targets=("i10", "sum"),
        team_i5_targets=("i5", "sum")).reset_index().rename(
        columns={"posteam": "team"})
    t_c = car.groupby("posteam").agg(
        team_rz_carries=("rz", "sum"), team_i10_carries=("i10", "sum"),
        team_i5_carries=("i5", "sum")).reset_index().rename(
        columns={"posteam": "team"})
    team = t_t.merge(t_c, on="team", how="outer").fillna(0)
    return player, team


def weekly_stats(season: int) -> pd.DataFrame:
    df = pd.read_csv(RAW / f"stats_{season}.csv", low_memory=False)
    df = df[df["season_type"] == "REG"].copy()
    df["fantasy_pos"] = df["position"].map(POSITION_MAP)
    return df[df["fantasy_pos"].notna()]


def snap_shares(season: int, per_game_team: pd.DataFrame,
                players: pd.DataFrame) -> pd.DataFrame:
    """Snap share and an estimate of routes run.

    Public data has no route counts, so routes are estimated as the player's
    offensive snap share in a game multiplied by the team's dropbacks in that
    game. That equals "pass snaps if the player were on the field for a
    representative share of dropbacks" and tracks charted route totals closely.
    """
    s = pd.read_csv(RAW / f"snaps_{season}.csv.gz", low_memory=False)
    s = s[s["game_type"] == "REG"]
    s = s.merge(per_game_team[["game_id", "team", "dropbacks"]],
                on=["game_id", "team"], how="left")
    s["routes_est"] = s["offense_pct"] * s["dropbacks"]
    xwalk = players[["pfr_id", "gsis_id"]].dropna().drop_duplicates("pfr_id")
    s = s.merge(xwalk, left_on="pfr_player_id", right_on="pfr_id", how="left")
    out = s.dropna(subset=["gsis_id"]).groupby("gsis_id").agg(
        snap_games=("offense_snaps", "size"),
        offense_snaps=("offense_snaps", "sum"),
        snap_pct=("offense_pct", "mean"),
        routes_est=("routes_est", "sum"),
    ).reset_index().rename(columns={"gsis_id": "player_id"})
    return out


def build_season(season: int, players: pd.DataFrame) -> pd.DataFrame:
    pbp = pbp_season(season)
    per_game_team, team_season = team_context(pbp)
    lb = qb_leaderboard(pbp)
    tq = team_primary_qb(lb)
    rz_player, rz_team = red_zone_usage(pbp)
    wk = weekly_stats(season)

    # ---- team weekly usage totals, so shares respect games actually played ----
    team_week = wk.groupby(["team", "week"]).agg(
        tw_targets=("targets", "sum"),
        tw_carries=("carries", "sum"),
        tw_air_yards=("receiving_air_yards", "sum"),
    ).reset_index()
    wk = wk.merge(team_week, on=["team", "week"], how="left")

    num = ["completions", "attempts", "passing_yards", "passing_tds",
           "passing_interceptions", "sacks_suffered", "passing_epa", "carries",
           "rushing_yards", "rushing_tds", "rushing_epa", "receptions", "targets",
           "receiving_yards", "receiving_tds", "receiving_air_yards", "receiving_epa",
           "receiving_first_downs", "rushing_first_downs", "fantasy_points_ppr",
           "fantasy_points", "tw_targets", "tw_carries", "tw_air_yards"]
    num = [c for c in num if c in wk.columns]
    agg = {c: "sum" for c in num}
    agg.update({"week": "size"})
    ssn = wk.groupby(["player_id", "player_display_name", "fantasy_pos"]).agg(
        **{c: (c, "sum") for c in num}, games=("week", "size")).reset_index()

    # primary team = team with the most games played
    prim = (wk.groupby(["player_id", "team"]).size().reset_index(name="n")
              .sort_values("n", ascending=False).drop_duplicates("player_id"))
    ssn = ssn.merge(prim[["player_id", "team"]], on="player_id", how="left")
    ssn["season"] = season

    # ---- usage shares ----
    ssn["target_share"] = ssn["targets"] / ssn["tw_targets"].replace(0, np.nan)
    ssn["rush_share"] = ssn["carries"] / ssn["tw_carries"].replace(0, np.nan)
    ssn["air_yards_share"] = (ssn["receiving_air_yards"] /
                              ssn["tw_air_yards"].replace(0, np.nan))
    ssn["wopr"] = 1.5 * ssn["target_share"] + 0.7 * ssn["air_yards_share"]
    ssn["opportunity_share"] = ((ssn["targets"] + ssn["carries"]) /
                                (ssn["tw_targets"] + ssn["tw_carries"]).replace(0, np.nan))

    # ---- rate stats ----
    ssn["ppg_ppr"] = ssn["fantasy_points_ppr"] / ssn["games"]
    ssn["yards_per_target"] = ssn["receiving_yards"] / ssn["targets"].replace(0, np.nan)
    ssn["yards_per_carry"] = ssn["rushing_yards"] / ssn["carries"].replace(0, np.nan)
    ssn["touches"] = ssn["carries"] + ssn["receptions"]
    ssn["touches_pg"] = ssn["touches"] / ssn["games"]
    ssn["targets_pg"] = ssn["targets"] / ssn["games"]
    ssn["carries_pg"] = ssn["carries"] / ssn["games"]
    ssn["rush_att_pg"] = ssn["carries"] / ssn["games"]
    ssn["pass_att_pg"] = ssn["attempts"] / ssn["games"]
    ssn["weighted_opps_pg"] = (ssn["carries"] + 2 * ssn["targets"]) / ssn["games"]
    ssn["total_tds"] = ssn["rushing_tds"] + ssn["receiving_tds"]
    ssn["yards_from_scrimmage"] = ssn["rushing_yards"] + ssn["receiving_yards"]
    ssn["scrimmage_ypg"] = ssn["yards_from_scrimmage"] / ssn["games"]
    ssn["dropbacks"] = ssn["attempts"] + ssn["sacks_suffered"]
    ssn["epa_per_dropback"] = ssn["passing_epa"] / ssn["dropbacks"].replace(0, np.nan)
    ssn["pass_td_rate"] = ssn["passing_tds"] / ssn["attempts"].replace(0, np.nan)

    # ---- snaps and routes ----
    snaps = snap_shares(season, per_game_team, players)
    ssn = ssn.merge(snaps, on="player_id", how="left")
    ssn["yprr_est"] = ssn["receiving_yards"] / ssn["routes_est"].replace(0, np.nan)
    ssn["routes_pg"] = ssn["routes_est"] / ssn["games"]

    # ---- red zone ----
    ssn = ssn.merge(rz_player, on="player_id", how="left")
    ssn = ssn.merge(rz_team, on="team", how="left")
    for a, b in [("rz_targets", "team_rz_targets"), ("i10_targets", "team_i10_targets"),
                 ("i5_carries", "team_i5_carries"), ("rz_carries", "team_rz_carries")]:
        ssn[f"{a}_share"] = ssn[a] / ssn[b].replace(0, np.nan)

    # ---- team + QB context ----
    ssn = ssn.merge(team_season, on="team", how="left")
    ssn = ssn.merge(tq, on="team", how="left")
    ssn = ssn.merge(lb[["player_id", "qb_epa_rank", "qb_qualified"]],
                    on="player_id", how="left")

    # ---- age on Sept 1 of the season ----
    ssn = ssn.merge(players[["gsis_id", "birth_date", "draft_year", "draft_round",
                             "draft_pick", "rookie_season", "height", "weight"]],
                    left_on="player_id", right_on="gsis_id", how="left")
    ref = pd.Timestamp(f"{season}-09-01")
    ssn["age"] = (ref - ssn["birth_date"]).dt.days / 365.25
    ssn["exp"] = season - ssn["rookie_season"]
    ssn["games_share"] = ssn["games"] / season_games(season)
    return ssn



# Prior weights for empirical-Bayes shrinkage of rate stats, in units of the
# rate's own denominator. A player with K routes gets pulled halfway to the
# positional mean, which stops 150-route efficiency spikes from reading as skill.
SHRINK_K = {"yprr": 150, "ypt": 30, "ypc": 40, "ppg": 4}


def add_shrunk_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Regress each rate stat toward its positional mean by sample size."""
    specs = [("yprr_shrunk", "receiving_yards", "routes_est", "yprr", "yprr_est"),
             ("ypt_shrunk", "receiving_yards", "targets", "ypt", "yards_per_target"),
             ("ypc_shrunk", "rushing_yards", "carries", "ypc", "yards_per_carry"),
             ("ppg_shrunk", "fantasy_points_ppr", "games", "ppg", "ppg_ppr")]
    for out, num, den, key, raw in specs:
        k = SHRINK_K[key]
        mu = df.groupby("fantasy_pos").apply(
            lambda g: g[num].sum() / g[den].sum() if g[den].sum() else np.nan,
            include_groups=False)
        prior = df["fantasy_pos"].map(mu)
        df[out] = (df[num] + k * prior) / (df[den] + k)
        df.loc[df[den].isna(), out] = np.nan
    return df


def main() -> None:
    players = load_players()
    frames = []
    for season in SEASONS:
        print(f"  building {season} ...", flush=True)
        frames.append(build_season(season, players))
    df = pd.concat(frames, ignore_index=True)
    df = add_shrunk_rates(df)

    # ---- positional finish ranks (full PPR, regular season totals) ----
    df["pos_rank"] = df.groupby(["season", "fantasy_pos"])["fantasy_points_ppr"].rank(
        ascending=False, method="min")
    ppg_pool = df[df["games"] >= 8]
    df["pos_rank_ppg"] = ppg_pool.groupby(["season", "fantasy_pos"])["ppg_ppr"].rank(
        ascending=False, method="min")
    for n in (1, 3, 5, 8, 12, 24):
        df[f"top{n}"] = (df["pos_rank"] <= n).astype(int)

    df = df[df["games"] >= MIN_GAMES].copy()
    OUTPUT.mkdir(exist_ok=True)
    df.to_csv(OUTPUT / "player_seasons.csv", index=False)
    print(f"wrote {len(df):,} player-seasons -> {OUTPUT / 'player_seasons.csv'}")


if __name__ == "__main__":
    main()
