"""
db_logger.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

SQLite logging layer for detection events. Any module (inference loop,
training eval scripts) writes here via log_detection(); the dashboard
reads via get_recent_events()/get_stats().

Schema:
    detections
        id              INTEGER PRIMARY KEY AUTOINCREMENT
        timestamp       TEXT     (ISO 8601, UTC)
        class_name      TEXT     ('fire' | 'smoke')
        confidence      REAL
        bbox_x1         REAL
        bbox_y1         REAL
        bbox_x2         REAL
        bbox_y2         REAL
        alert_triggered INTEGER  (0/1 — did this detection cross the
                                   debounce+threshold logic and fire an alarm?)
        frame_ref       TEXT     (optional path/id of saved frame, nullable)
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional, Iterable

SCHEMA = """
CREATE TABLE IF NOT EXISTS detections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,
    class_name      TEXT NOT NULL CHECK (class_name IN ('fire', 'smoke')),
    confidence      REAL NOT NULL,
    bbox_x1         REAL,
    bbox_y1         REAL,
    bbox_x2         REAL,
    bbox_y2         REAL,
    alert_triggered INTEGER NOT NULL DEFAULT 0,
    frame_ref       TEXT
);
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_alert ON detections(alert_triggered);
"""


class DBLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def log_detection(
        self,
        class_name: str,
        confidence: float,
        bbox: Optional[Iterable[float]] = None,
        alert_triggered: bool = False,
        frame_ref: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> int:
        """Insert one detection event. Returns the new row id."""
        if class_name not in ("fire", "smoke"):
            raise ValueError(f"class_name must be 'fire' or 'smoke', got {class_name!r}")

        ts = timestamp or datetime.now(timezone.utc).isoformat()
        x1, y1, x2, y2 = (list(bbox) + [None] * 4)[:4] if bbox else (None, None, None, None)

        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO detections
                   (timestamp, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    alert_triggered, frame_ref)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ts, class_name, confidence, x1, y1, x2, y2, int(alert_triggered), frame_ref),
            )
            return cur.lastrowid

    def get_recent_events(self, limit: int = 50):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM detections ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_recent_alerts(self, limit: int = 20):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM detections WHERE alert_triggered = 1 ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self):
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) c FROM detections").fetchone()["c"]
            alerts = conn.execute(
                "SELECT COUNT(*) c FROM detections WHERE alert_triggered = 1"
            ).fetchone()["c"]
            by_class = conn.execute(
                "SELECT class_name, COUNT(*) c FROM detections GROUP BY class_name"
            ).fetchall()
            return {
                "total_detections": total,
                "total_alerts": alerts,
                "by_class": {r["class_name"]: r["c"] for r in by_class},
            }


if __name__ == "__main__":
    # Quick manual smoke test: python -m src.utils.db_logger
    logger = DBLogger("data/detections_test.db")
    logger.log_detection("fire", 0.82, bbox=[10, 20, 100, 120], alert_triggered=True)
    logger.log_detection("smoke", 0.45, alert_triggered=False)
    print(logger.get_stats())
    print(logger.get_recent_events(5))
