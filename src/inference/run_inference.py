"""Real-time fire/smoke detection inference pipeline.

Owner module: AI Model Optimization & Edge Inference (Mihir S. Joshi)
Pipeline stages (per technical proposal):
    Frame Capture -> Pre-processing -> AI Inference -> Post-processing (NMS)
    -> Confidence check -> Alarm trigger or loop

This is a scaffold stub. Fill in load_model() and the inference call once
the trained/exported model (.engine / .onnx) is available in models/.
"""

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))  # repo root

from src.utils.config import load_config
from src.utils.logger import DetectionLogger
from src.utils.alarm import AlarmController

import cv2


def load_model(weights_path: str):
    """Load the detection model (TensorRT engine, ONNX, or .pt depending on stage).

    TODO: implement once model export is ready (Phase 3 — Embedded Deployment).
    For TensorRT: load .engine via pycuda/tensorrt runtime.
    For dev-machine testing: can load a .pt via ultralytics YOLO() as a stand-in.
    """
    raise NotImplementedError(
        f"Model loading not yet implemented. Expected weights at: {weights_path}"
    )


def preprocess_frame(frame, input_size: int):
    """Resize + normalize a BGR frame for model input."""
    resized = cv2.resize(frame, (input_size, input_size))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype("float32") / 255.0
    return normalized


def run(config_path: str):
    config = load_config(config_path)

    cam_cfg = config["camera"]
    model_cfg = config["model"]
    alarm_cfg = config["alarm"]

    logger = DetectionLogger(config["logging"]["db_path"])
    alarm = AlarmController(
        buzzer_pin=alarm_cfg["buzzer_gpio_pin"],
        led_pin=alarm_cfg["led_gpio_pin"],
        relay_pin=alarm_cfg["relay_gpio_pin"],
        cooldown_seconds=alarm_cfg["trigger_cooldown_seconds"],
    )

    cap = cv2.VideoCapture(cam_cfg["source"])
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera source: {cam_cfg['source']}")

    print("Starting inference loop. Press Ctrl+C to stop.")
    print("NOTE: model loading is not yet implemented — this loop currently "
          "just exercises capture + preprocessing for pipeline testing.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame capture failed, stopping.")
                break

            _ = preprocess_frame(frame, model_cfg["input_size"])

            # TODO once model is ready:
            # detections = model_infer(model, processed_frame)
            # for det in detections:
            #     if det.confidence > model_cfg["confidence_threshold"]:
            #         alarm.trigger()
            #         logger.log_detection(det.label, det.confidence, det.bbox, alarm_triggered=True)

    except KeyboardInterrupt:
        print("\nStopping inference loop.")
    finally:
        cap.release()
        alarm.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fire detection inference pipeline.")
    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to YAML config file (default: config/default.yaml)",
    )
    args = parser.parse_args()
    run(args.config)
