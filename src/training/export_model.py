"""Model optimization & export pipeline: PyTorch -> ONNX -> TensorRT (.engine).

Owner module: AI Model Optimization & Edge Inference (Mihir S. Joshi)

Steps per proposal (page 6):
    1. Quantization: FP32 -> INT8 (4x size reduction)
    2. Pruning of low-weight neurons
    3. Export to ONNX, then TensorRT/.engine for Jetson deployment

Usage:
    python src/training/export_model.py --weights models/yolov8n_fire.pt --format engine
"""

import argparse


def export_model(weights_path: str, export_format: str, int8: bool):
    """Export a trained model to an edge-deployable format.

    Args:
        weights_path: path to trained .pt checkpoint
        export_format: 'onnx' or 'engine' (TensorRT)
        int8: whether to apply INT8 quantization during export
    """
    print(f"[stub] Would export {weights_path} -> format={export_format}, int8={int8}")
    print("TODO: implement with Ultralytics export, e.g.:")
    print("    from ultralytics import YOLO")
    print("    model = YOLO(weights_path)")
    print(f"    model.export(format='{export_format}', int8={int8})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export/optimize the trained model for edge deployment.")
    parser.add_argument("--weights", required=True, help="Path to trained .pt weights")
    parser.add_argument("--format", default="engine", choices=["onnx", "engine", "tflite"])
    parser.add_argument("--int8", action="store_true", help="Apply INT8 quantization")
    args = parser.parse_args()

    export_model(args.weights, args.format, args.int8)
