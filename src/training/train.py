"""Training script for the flame/smoke detection model.

Owner module: Dataset Engineering, AI Training & Validation (Navya B. Kommuri)

Uses Ultralytics YOLOv8-Nano with transfer learning from COCO pretrained
weights, per the technical proposal's AI Algorithm Pipeline (page 6-7).

Usage:
    python src/training/train.py --data config/dataset.yaml --epochs 100
"""

import argparse

# from ultralytics import YOLO  # uncomment once ultralytics is installed


def train(data_yaml: str, epochs: int, img_size: int, base_model: str):
    """Train a YOLOv8-Nano model on the fire/smoke dataset.

    Args:
        data_yaml: path to a YOLO-format dataset YAML (train/val/test splits,
                    class names: flame, smoke)
        epochs: number of training epochs
        img_size: input resolution (proposal specifies 416)
        base_model: pretrained checkpoint to start from (e.g. 'yolov8n.pt')
    """
    print(
        f"[stub] Would train {base_model} on {data_yaml} "
        f"for {epochs} epochs at {img_size}px."
    )
    print("TODO: replace with actual Ultralytics training call once dataset is ready, e.g.:")
    print("    model = YOLO(base_model)")
    print("    model.train(data=data_yaml, epochs=epochs, imgsz=img_size)")

    # Example real implementation:
    # model = YOLO(base_model)
    # results = model.train(data=data_yaml, epochs=epochs, imgsz=img_size)
    # return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the fire/smoke detection model.")
    parser.add_argument("--data", default="config/dataset.yaml", help="Path to dataset YAML")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--img-size", type=int, default=416)
    parser.add_argument("--base-model", default="yolov8n.pt")
    args = parser.parse_args()

    train(args.data, args.epochs, args.img_size, args.base_model)
