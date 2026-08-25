"""Run the whole study: download -> dataset -> gates -> predict -> board.

target_board.py supersedes the old forecast.py: it uses the two-year model in
model.py, which scores players a one-year lookback deletes.
"""
import audit
import build_dataset
import download
import predict
import board_report
import report
import rookies
import target_board
import disagreement

for step in (download, build_dataset, __import__("analyze"), predict, audit,
             report, target_board, rookies, disagreement, board_report):
    print(f"\n{'=' * 70}\n{step.__name__}\n{'=' * 70}")
    step.main()
