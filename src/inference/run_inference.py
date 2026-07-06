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
from src.utils.db_logger import DBLogger
from src.utils.alarm import AlarmController
from src.utils.alert_manager import AlertManager
from src.utils.telemetry import TelemetryReporter
from src.utils.frame_publisher import FramePublisher
import cv2


def load_model(weights_path: str):
    """Load the trained YOLO model (.pt for dev machine)."""
    from ultralytics import YOLO
    return YOLO(weights_path)



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
    det_cfg = config["detection"]
    alarm_cfg = config["alarm"]

    logger = DBLogger(config["logging"]["db_path"])
    alarm = AlarmController(
        buzzer_pin=alarm_cfg["buzzer_gpio_pin"],
        led_pin=alarm_cfg["led_gpio_pin"],
        relay_pin=alarm_cfg["relay_gpio_pin"],
        cooldown_seconds=0,    
    )
    alert_mgr = AlertManager(
        db_logger=logger,
        confidence_threshold=det_cfg["confidence_threshold"],
        debounce_frames=det_cfg["debounce_frames"],
        alert_cooldown_seconds=det_cfg["alert_cooldown_seconds"],
        on_alert=lambda top: alarm.trigger(),
    )    

    cap = cv2.VideoCapture(cam_cfg["source"])
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera source: {cam_cfg['source']}")
    model = load_model(model_cfg["weights_path"])
    telemetry = TelemetryReporter()
    publisher = FramePublisher(config["dashboard"]["live_frame_path"])
    print("Starting inference loop. Press Ctrl+C to stop.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame capture failed, stopping.")
                break

            results = model(
                frame,
                imgsz=model_cfg["input_size"],
                conf=det_cfg["confidence_threshold"],
                verbose=False,
            )

            detections = [
                {
                    "class_name": det_cfg["classes"][int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy[0].tolist(),
                }
                for box in results[0].boxes
            ]
            alert_mgr.process_frame(detections)
            annotated = results[0].plot()
            publisher.publish(annotated)
            cv2.imshow("NEEMUS Fire Detection (press q to quit)", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            telemetry.tick()
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
