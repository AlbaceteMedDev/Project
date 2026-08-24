"""Shared configuration for the fantasy football positional-archetype study."""
from pathlib import Path

# Seasons analysed. 2014 is loaded only to supply prior-year inputs for 2015.
FIRST_PRIOR_SEASON = 2014
FIRST_SEASON = 2015
LAST_SEASON = 2025

SEASONS = list(range(FIRST_PRIOR_SEASON, LAST_SEASON + 1))
STUDY_SEASONS = list(range(FIRST_SEASON, LAST_SEASON + 1))

POSITIONS = ["QB", "RB", "WR", "TE"]
# nflverse position codes that map onto a fantasy position
POSITION_MAP = {"QB": "QB", "RB": "RB", "HB": "RB", "FB": "RB", "WR": "WR", "TE": "TE"}

# Games in a regular season, by year (17-game seasons start in 2021).
def season_games(season: int) -> int:
    return 17 if season >= 2021 else 16

ROOT = Path(__file__).resolve().parent.parent
RAW = Path("/tmp/claude-0/-home-user-Project/69846014-c8fa-518b-ba8e-200c8dd7bd5b/scratchpad/raw")
DATA = ROOT / "data"
OUTPUT = ROOT / "output"

NFLVERSE = "https://github.com/nflverse/nflverse-data/releases/download"

# Minimum volume for a player-season to be treated as a real fantasy asset.
MIN_GAMES = 4
QB_MIN_DROPBACKS = 200   # qualifier for the EPA/dropback leaderboard
