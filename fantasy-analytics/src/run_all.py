"""Run the whole study: download -> dataset -> profile -> predict -> forecast -> board."""
import audit
import build_dataset
import download
import forecast
import predict
import board_report
import report
import target_board

for step in (download, build_dataset, __import__("analyze"), predict, audit,
             forecast, report, target_board, board_report):
    print(f"\n{'=' * 70}\n{step.__name__}\n{'=' * 70}")
    step.main()
