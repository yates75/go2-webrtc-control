"""Fit a small, transparent linear policy from recorded follow demonstrations.

Takes the CSV produced by record_demo.py (center_x, center_y, box_w,
box_h -> forward_mps, turn_rps) and fits a linear regression via
least-squares (numpy only, no ML framework needed -- this is intentional:
the resulting model is a small matrix of numbers a student can read and
reason about, not a black box). Reports mean absolute error on a held-out
slice of the data so a class can discuss over/underfitting on a tiny
dataset.

follow.py can then drive using this learned policy (--policy flag)
instead of, or compared against, its hand-coded proportional controller.

Usage:
    python -m go2_control.train_follow_policy --data follow_demo.csv --out-policy follow_policy.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))

FEATURE_NAMES = ["center_x", "center_y", "box_w", "box_h", "bias"]
TARGET_NAMES = ["forward_mps", "turn_rps"]


def _load_rows(data_csv: Path) -> tuple[np.ndarray, np.ndarray]:
    with data_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if len(rows) < 5:
        raise SystemExit(f"Only {len(rows)} rows in {data_csv} -- record more demonstration data first.")

    features = np.array(
        [[float(r["center_x"]), float(r["center_y"]), float(r["box_w"]), float(r["box_h"]), 1.0] for r in rows]
    )
    targets = np.array([[float(r["forward_mps"]), float(r["turn_rps"])] for r in rows])
    return features, targets


def train(data_csv: Path, out_policy: Path, val_fraction: float = 0.2) -> Path:
    features, targets = _load_rows(data_csv)

    rng = np.random.default_rng(0)
    order = rng.permutation(len(features))
    split = max(1, int(len(order) * (1 - val_fraction)))
    train_idx, val_idx = order[:split], order[split:]

    coefficients, *_ = np.linalg.lstsq(features[train_idx], targets[train_idx], rcond=None)

    if len(val_idx) > 0:
        predictions = features[val_idx] @ coefficients
        mae = np.abs(predictions - targets[val_idx]).mean(axis=0)
        print(f"Held-out MAE: forward={mae[0]:.3f} m/s, turn={mae[1]:.3f} rps (n={len(val_idx)})")
    else:
        print("Not enough rows for a held-out split -- trained on all data, no generalization estimate.")

    policy = {
        "feature_names": FEATURE_NAMES,
        "target_names": TARGET_NAMES,
        "coefficients": coefficients.tolist(),
        "note": "predicted = [center_x, center_y, box_w, box_h, 1.0] @ coefficients -> [forward_mps, turn_rps]",
    }
    out_policy.parent.mkdir(parents=True, exist_ok=True)
    out_policy.write_text(json.dumps(policy, indent=2))
    print(f"Saved policy to {out_policy}")
    return out_policy


def main() -> None:
    parser = argparse.ArgumentParser(description="Fit a linear follow-policy from recorded demonstrations")
    parser.add_argument("--data", default="follow_demo.csv", help="CSV from record_demo.py")
    parser.add_argument("--out-policy", default="follow_policy.json", help="Where to save the fitted policy")
    parser.add_argument("--val-fraction", type=float, default=0.2, help="Fraction of rows held out for evaluation")
    args = parser.parse_args()
    train(Path(args.data), Path(args.out_policy), args.val_fraction)


if __name__ == "__main__":
    main()
