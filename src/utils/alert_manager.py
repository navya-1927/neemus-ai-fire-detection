"""
alert_manager.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

This is the glue between Mihir's inference output and Dev's GPIO
alarm hardware. It:
  1. Filters detections by confidence threshold.
  2. Debounces: requires N consecutive detecting frames before it
     counts as a real event (avoids one noisy frame triggering an alarm).
  3. Applies a cooldown so a continuously-visible fire doesn't spam
     the buzzer/relay every single frame.
  4. Logs every detection (and whether it triggered an alert) via DBLogger.
  5. Calls an injected `on_alert` callback — this is where Dev's
     GPIO trigger function gets plugged in. Kept as a callback so this
     module has zero hardware dependency and is fully unit-testable.

Expected per-frame input from Mihir's inference module (confirm this
shape with him before wiring in — this is the assumed contract):
    {
        "class_name": "fire" | "smoke",
        "confidence": float,
        "bbox": [x1, y1, x2, y2]   # optional
    }
    or None / [] if nothing detected in that frame.
"""

import time
from collections import deque
from typing import Callable, Optional, List, Dict, Any

from src.utils.db_logger import DBLogger


class AlertManager:
    def __init__(
        self,
        db_logger: DBLogger,
        confidence_threshold: float = 0.6,
        debounce_frames: int = 3,
        alert_cooldown_seconds: float = 30.0,
        on_alert: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.db_logger = db_logger
        self.confidence_threshold = confidence_threshold
        self.debounce_frames = debounce_frames
        self.alert_cooldown_seconds = alert_cooldown_seconds
        self.on_alert = on_alert  # e.g. hardware.gpio_control.trigger_alarm

        self._recent_hits = deque(maxlen=debounce_frames)
        self._last_alert_time: float = 0.0

    def process_frame(self, detections: Optional[List[Dict[str, Any]]]):
        """
        Call this once per frame with the raw detections from the
        inference pipeline (already NMS'd). Returns True if an alert
        was triggered this frame, else False.
        """
        detections = detections or []
        # Keep only detections above threshold and of a known class
        valid = [
            d for d in detections
            if d.get("confidence", 0) >= self.confidence_threshold
            and d.get("class_name") in ("fire", "smoke")
        ]

        # Log every raw detection regardless of alert outcome (alert flag
        # gets filled in after the debounce check below)
        frame_had_hit = len(valid) > 0
        self._recent_hits.append(frame_had_hit)

        debounced_fire = (
            len(self._recent_hits) == self.debounce_frames
            and all(self._recent_hits)
        )

        now = time.time()
        cooling_down = (now - self._last_alert_time) < self.alert_cooldown_seconds
        should_alert = debounced_fire and not cooling_down

        for d in valid:
            self.db_logger.log_detection(
                class_name=d["class_name"],
                confidence=d["confidence"],
                bbox=d.get("bbox"),
                alert_triggered=should_alert,
            )

        if should_alert:
            self._last_alert_time = now
            if self.on_alert:
                # pass the highest-confidence detection as context
                top = max(valid, key=lambda d: d["confidence"])
                self.on_alert(top)
            return True

        return False
