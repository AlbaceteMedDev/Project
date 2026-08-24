"""Run the whole study: download -> dataset -> profile -> predict -> forecast."""
import audit
import build_dataset
import download
import forecast
import predict
import report

for step in (download, build_dataset, __import__("analyze"), predict, audit,
             forecast, report):
    print(f"\n{'=' * 70}\n{step.__name__}\n{'=' * 70}")
    step.main()
