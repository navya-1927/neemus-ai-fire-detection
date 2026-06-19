"""SQLite-based logging for detection events.

Owner module: System Software, Monitoring & Data Management (Saarang Agarwal)
"""

import sqlite3
from datetime import datetime
from pathlib import Path


class DetectionLogger:
    """Logs fire/smoke detection events to a local SQLite database."""

    def __init__(self, db_path: str = "logs/detections.sqlite3"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    class_label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    bbox_x1 REAL, bbox_y1 REAL, bbox_x2 REAL, bbox_y2 REAL,
                    alarm_triggered INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def log_detection(
        self,
        class_label: str,
        confidence: float,
        bbox: tuple,
        alarm_triggered: bool = False,
    ):
        """Insert a single detection event.

        Args:
            class_label: "flame" or "smoke"
            confidence: model confidence score (0-1)
            bbox: (x1, y1, x2, y2) bounding box coordinates
            alarm_triggered: whether this detection fired the alarm
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO detections
                (timestamp, class_label, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, alarm_triggered)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    class_label,
                    confidence,
                    *bbox,
                    int(alarm_triggered),
                ),
            )
