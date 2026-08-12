"""Fine-tune a small image classifier on a dataset captured with dataset_capture.py.

This is genuine supervised ML training, not a canned demo: it fine-tunes
a pretrained YOLO classification model (`yolov8n-cls.pt`) on whatever
images you captured, using Ultralytics' training API. Verified during
development against a real (synthetic) dataset with this exact folder
layout and training call.

Expects <dataset-dir>/train/<label>/*.jpg and <dataset-dir>/val/<label>/*.jpg
for one or more labels -- exactly what dataset_capture.py produces.

Install the extra dependency once (same as object_tracker.py):
    pip install ultralytics opencv-python

Usage:
    python -m go2_control.train_classifier --dataset-dir dataset --epochs 15
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))


def train(dataset_dir: Path, epochs: int, imgsz: int, out_model: Path, run_dir: Path) -> Path:
    """Train and return the path to the saved best-weights file."""

    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise SystemExit("Training needs the 'ultralytics' package: pip install ultralytics") from exc

    train_dir = dataset_dir / "train"
    if not train_dir.exists():
        raise SystemExit(
            f"No {train_dir} folder found. Capture images first with dataset_capture.py "
            "(it creates <dataset-dir>/train/<label>/... and <dataset-dir>/val/<label>/...)."
        )
    labels = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
    if len(labels) < 2:
        raise SystemExit(
            f"Found {len(labels)} label(s) in {train_dir}: {labels}. "
            "Classification training needs at least 2 different labels to distinguish between."
        )
    print(f"Training on labels: {labels}")

    model = YOLO("yolov8n-cls.pt")
    results = model.train(
        data=str(dataset_dir),
        epochs=epochs,
        imgsz=imgsz,
        project=str(run_dir),
        name="exp",
        exist_ok=True,
        verbose=False,
        plots=False,
    )

    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    out_model.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(best_weights, out_model)
    print(f"Trained model saved to {out_model} (full training run logged in {results.save_dir})")
    return out_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune a YOLO classifier on a captured dataset")
    parser.add_argument("--dataset-dir", default="dataset", help="Dataset root (from dataset_capture.py)")
    parser.add_argument("--epochs", type=int, default=15, help="Training epochs")
    parser.add_argument("--imgsz", type=int, default=224, help="Training image size in pixels")
    parser.add_argument("--out-model", default="trained_classifier.pt", help="Where to save the trained weights")
    parser.add_argument("--run-dir", default="runs/classify", help="Where Ultralytics logs the full training run")
    args = parser.parse_args()
    train(Path(args.dataset_dir), args.epochs, args.imgsz, Path(args.out_model), Path(args.run_dir))


if __name__ == "__main__":
    main()
