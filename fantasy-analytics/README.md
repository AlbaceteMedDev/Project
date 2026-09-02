# Fantasy football positional blueprints, 2015–2025

What actually separates a top-5 fantasy season from the rest of the position —
computed from eleven seasons of play-by-play rather than asserted.

The starting point was a screenshot of the "overall fantasy WR1s since 2016"
card claiming every WR1 was under 30, had a 25%+ target rate, 2.3+ yards per
route, played on a top-11 scoring offense and caught passes from a top-10 QB in
EPA/dropback. That card is audited here (it goes 7/10 on its own list, and one
of its five rules filters almost nobody), and the same treatment is extended to
all four skill positions in both directions: what a top-5 season *looked like*,
and what was knowable about it *beforehand*.

## Results

### Gates — the bar that ~85% of top-5 seasons cleared

Clearing every gate at a position is rare and it means a lot. Numbers are full
PPR, regular season, 2015–2025.

| Position | Gates | Players clearing all, per season | Hit rate | Lift over base | Share of top-5s caught |
|---|---|---|---|---|---|
| WR | 5 | 2.6 | **90%** | 20.1× | 47% |
| TE | 5 | 2.5 | **86%** | 9.8× | 44% |
| RB | 5 | 5.9 | 54% | 7.8× | 64% |
| QB | 2 | 7.3 | 50% | 3.3× | 73% |

Run `python src/analyze.py` for the rule text, thresholds and per-rule hit rates.

### Prediction — the same question asked in August

Inputs restricted to the prior season plus what is settled in the offseason
(age, team, that team's prior-year context). The model is a logistic regression
scored **leave-one-season-out**, so no season is ever predicted by a model that
trained on it.

| Position | Out-of-sample AUC | Preseason top-10 catches | Top-5 finishes reachable at all |
|---|---|---|---|
| WR | **0.922** | 66% of top-5s | 94% |
| TE | 0.881 | 70% | 88% |
| RB | 0.860 | 60% | 86% |
| QB | **0.710** | 66% | 88% |

Those figures are the two-year model. The first version looked back one season
and required that season to clear a volume floor, which deleted exactly the
players the market cares about — a WR6 who played four games, a QB5 who played
seven. Two fixes, both measured:

- **Two years of history rather than one** lifts WR AUC 0.901 → 0.929 and the
  share of top-5 finishers inside a preseason top-10 list from 59% to 75%.
- **Entry on either of the last two seasons** lifts QB AUC 0.664 → 0.710 and RB
  0.837 → 0.860, and raises reachable top-5 seasons to 86–94%.

### What survived a check

Every headline was fitted on all eleven seasons at once, so each was re-derived
under conditions that could break it (`python src/audit_robustness.py`).

| Position | Gates fitted on all 11 | Refitted leave-one-season-out | Base rate |
|---|---|---|---|
| WR | 90% | **78%** | 4.5% |
| TE | 86% | **88%** | 8.8% |
| RB | 54% | 54% | 6.9% |
| QB | 50% | 45% | 14.9% |

- **The receiver card was flattering itself.** 78% is still 17x the base rate, but
  the published 90% was partly the thresholds having seen the answer. Tight end did
  not degrade at all.
- **Scoring format barely matters.** Half-PPR keeps 89-93% of the same top-5
  finishers, standard keeps 82-85%, quarterback is identical in all three.
- **One threshold is soft.** Refitting eleven times, the receiver target bar never
  moves off 9.0 — but *routes per game* survives into the card in only 4 of 11
  refits. It is the gate the route estimate handles worst.
- **The pool drops the injured.** 173 receiver-seasons, 138 backs and 82 tight ends
  vanish from the denominator after one qualifying year. Counting those as failures
  moves the receiver base rate from 4.6% to 4.0%.
- **A real error, found and fixed.** The model used balanced class weights, which
  lifts scores toward 1 and strips them of meaning — an earlier target board
  published 0.99s whose actual top-5 rate was 33%. Removing the weighting gives the
  same AUC at roughly a quarter of the Brier score. Hand-picking the feature list
  did *not* inflate anything: selecting features inside each training fold returns
  the same AUCs.

### Findings worth the trouble

1. **"Under 30" is not a rule.** 89% of the qualifying WR pool is already under
   30. It has a lift of 1.0× — it removes nobody. Age carries an AUC of 0.512
   for WR top-5 finishes, which is a coin flip.
2. **Target share and route efficiency are the two real WR rules**, at 6.6× and
   6.3× lift respectively. The team-context rules the card leans on are worth
   about 2×.
3. **QB is the position where the recipe breaks down.** Almost every QB stat is
   a restatement of the fantasy score itself; strip those out and only two
   honest gates survive. Out-of-sample AUC of 0.68 is far below the other three.
   Prior-year *rushing* volume is the one durable non-circular signal.
4. **Elite finishes barely repeat.** A top-5 finish last year means a 24–43%
   chance of repeating. Finish 25th or worse and it is 1–3%.
5. **A quarter of top-5 RB seasons were unreachable** from prior-year data —
   rookies and role changes. Prior-year metrics cannot see a backfield that has
   not happened yet.

## Method

`Data` — nflverse public releases: weekly player stats, play-by-play,
PFR snap counts, and the player master file. 2014 is loaded only to supply
prior-year inputs for 2015.

`Scoring` — full PPR, regular season totals. Positional finish is the rank of
total PPR points within position within season. The computed WR1 list for
2016–2025 reproduces the source card's ten players exactly.

`Pools` — a player-season counts if it clears a rosterability floor
(WR: 8 games and 30 targets; TE: 8 and 20; RB: 8 games and 50 touches;
QB: 8 games and 200 attempts). Base rates are quoted against these pools, not
against every player who took a snap.

`Thresholds` — for each metric the engine finds the loosest bar that still keeps
85% of top-5 seasons above it (a *gate*), and separately the bar that maximises
hit rate given it flags at least 15 seasons (a *green flag*). One metric per
family makes the card, so five rules measure five different things rather than
five flavours of target share.

`Rules that do not survive` — a candidate rule is rejected if its lift is below
1.35×, and reported separately as decoration if it is at or below 1.25×. Metrics
that restate the fantasy score (a QB's team points, his TD rate) are flagged
circular and kept out of the cards.

`Rate stats are shrunk` — yards per route, per target, per carry and PPR per
game are regressed toward the positional mean by sample size (empirical Bayes,
prior weight 150 routes / 30 targets / 40 carries / 4 games). Without this a
tight end with 157 routes and a 3.6 YPRR spike outranks a 680-route starter.

### One honest caveat about yards per route

Public data has no route counts. Routes are estimated as offensive snap share ×
team dropbacks, per game. That estimate runs roughly 10–20% below charted route
totals, because receivers who leave the field on run downs run routes on a
higher share of dropbacks than their overall snap share implies — so the yards
per route figures here read 10–20% *above* PFF's. Every rule is therefore also
expressed as "how many players clear this per season", which is unaffected by
the bias. The audit scores the card's 2.3 threshold both as stated and at a
PFF-equivalent 2.5.

## Layout

```
src/download.py       fetch the nflverse releases
src/build_dataset.py  season-level player + team dataset
src/analyze.py        gates, green flags, vacuous-rule detection
src/model.py          two-year predictive frame and the model itself
src/predict.py        prior-year model, leave-one-season-out scoring
src/audit.py          score the viral WR1 card against the record
src/audit_robustness.py  adversarial checks on this project's own claims
src/target_board.py   score every returning candidate, tier the board
src/report.py         render the study as a page
src/board_report.py   render the target board as a page
src/run_all.py        all of the above in order

output/player_seasons.csv     5,832 player-seasons, every metric
output/profile_cards.json     in-season gates and green flags
output/predictive_cards.json  preseason rules, model, persistence, coverage
output/viral_rule_audit.csv   the screenshot's five rules, scored
output/model_scores.csv       leave-one-season-out probabilities
output/forecast_2026.csv      upcoming-season shortlists
output/target_board_2026.csv  every candidate, gates cleared, tier
```

## Running it

```bash
pip install -r requirements.txt
python src/run_all.py     # ~5 minutes, downloads ~350MB on first run
```

Set `RAW` in `src/config.py` to choose where raw data is cached.

## Limits

Eleven seasons give 55 top-5 finishes per position. Thresholds are fitted on
that sample, so the gate values carry real uncertainty even though the *ranking*
of which metrics matter is stable. The model is validated out-of-sample by
season; the gate thresholds are descriptive and are not. Forecast rows carry
each player's most recent team, so anyone who changed teams in the offseason
needs his landing-spot inputs re-pointed by hand.
