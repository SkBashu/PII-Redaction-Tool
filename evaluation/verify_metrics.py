"""Independently recompute the aggregate metrics recorded by evaluate.py.

Run after ``py evaluate.py``. This verifier deliberately does not infer true
negatives from characters, tokens, whitespace, or unlabeled spans.
"""

from __future__ import annotations

import json
from pathlib import Path


REPORT_FILE = Path("evaluation_report.json")


def safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
    overall = report["overall"]
    tp, fp, fn = (overall[key] for key in ("tp", "fp", "fn"))

    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    coverage = safe_divide(tp, tp + fp + fn)

    expected = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "coverage": round(coverage, 4),
    }
    actual = {key: overall.get(key) for key in expected}
    if actual != expected:
        raise SystemExit(f"Metric mismatch: expected {expected}, report has {actual}")
    if overall.get("tn") is not None or overall.get("accuracy") is not None:
        raise SystemExit("TN/accuracy must remain undefined for this benchmark")

    print("Verified metrics:")
    print(f"TP = {tp}; FP = {fp}; FN = {fn}; TN = NOT DEFINED")
    for key, value in expected.items():
        print(f"{key.title()} = {value:.4f}")


if __name__ == "__main__":
    main()
