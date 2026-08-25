"""Fetch the nflverse releases the study runs on.

Everything here is public data published by the nflverse project. Files land in
the directory named by config.RAW and are skipped if already present.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

from config import NFLVERSE, RAW, SEASONS

FILES = [("players/players.csv", "players.csv"),
         ("draft_picks/draft_picks.csv", "draft_picks.csv")]
for _s in SEASONS:
    FILES += [
        (f"stats_player/stats_player_week_{_s}.csv", f"stats_{_s}.csv"),
        (f"snap_counts/snap_counts_{_s}.csv.gz", f"snaps_{_s}.csv.gz"),
        (f"pbp/play_by_play_{_s}.parquet", f"pbp_{_s}.parquet"),
    ]


def fetch(remote: str, local: Path) -> None:
    if local.exists() and local.stat().st_size > 0:
        return
    url = f"{NFLVERSE}/{remote}"
    print(f"  {url}")
    urllib.request.urlretrieve(url, local)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for remote, name in FILES:
        fetch(remote, RAW / name)
    # Depth charts ship one large file per season in two different schemas, so
    # they are fetched and reduced by their own module rather than copied whole.
    if not (RAW / "depth_preseason.csv").exists():
        import depth
        depth.main()
    print(f"raw data ready in {RAW}")


if __name__ == "__main__":
    main()
