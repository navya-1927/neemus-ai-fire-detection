"""
dashboard/app.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

Minimal Flask dashboard: live status, recent events, recent alerts.
Run with:
    python -m src.dashboard.app --config config/default.yaml

This is an MVP — no auth, local network only. Fine for a Jetson on a
LAN; do NOT expose this port to the open internet as-is.
"""

import argparse
import json
import os
import time
from flask import Flask, jsonify, render_template_string, render_template, Response
from src.utils.config_loader import load_config
from src.utils.db_logger import DBLogger

TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Neemus Fire Detection — Monitor</title>
  <meta http-equiv="refresh" content="{{ refresh }}">
  <style>
    body { font-family: sans-serif; margin: 2rem; background: #111; color: #eee; }
    h1 { color: #ff5533; }
    table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
    th, td { border: 1px solid #333; padding: 6px 10px; text-align: left; }
    th { background: #222; }
    .alert-row { background: #3a1414; }
    .stats { display: flex; gap: 2rem; margin-top: 1rem; }
    .stat-box { background: #1c1c1c; padding: 1rem; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>🔥 Fire Detection Monitor</h1>
  <div class="stats">
  <div class="stat-box"><b>Detector</b><br>
      <span style="color: {{ '#4caf50' if telemetry.status == 'ONLINE' else '#ff5533' }}">
        {{ telemetry.status }}</span></div>
    <div class="stat-box"><b>FPS</b><br>{{ telemetry.fps if telemetry.fps else '—' }}</div>
    <div class="stat-box"><b>Total detections</b><br>{{ stats.total_detections }}</div>
    <div class="stat-box"><b>Total alerts</b><br>{{ stats.total_alerts }}</div>
    <div class="stat-box"><b>By class</b><br>{{ stats.by_class }}</div>
  </div>
<h2>Live feed</h2>
  <img src="/video_feed" width="640" style="border:1px solid #333; border-radius:6px;">
  <h2>Recent events</h2>
  <table>
    <tr><th>ID</th><th>Time (UTC)</th><th>Class</th><th>Confidence</th><th>Alert?</th></tr>
    {% for e in events %}
    <tr class="{{ 'alert-row' if e.alert_triggered else '' }}">
      <td>{{ e.id }}</td><td>{{ e.timestamp }}</td><td>{{ e.class_name }}</td>
      <td>{{ '%.2f' | format(e.confidence) }}</td><td>{{ 'YES' if e.alert_triggered else '-' }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


def create_app(config_path: str = "config/default.yaml") -> Flask:
    cfg = load_config(config_path)
    db = DBLogger(cfg["logging"]["db_path"])
    refresh = cfg["dashboard"].get("refresh_seconds", 5)

    app = Flask(__name__)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0   # dev mode: never cache static files
    def read_telemetry():
        path = "data/telemetry.json"
        try:
            with open(path) as f:
                t = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"status": "OFFLINE", "fps": None}
        age = time.time() - t.get("timestamp", 0)
        t["status"] = "ONLINE" if age < 5 else "OFFLINE"
        return t
    @app.route("/")
    def index():
        return app.send_static_file("dashboard.html")
    @app.route("/classic")
    def classic():
        # the original server-rendered dashboard, kept as a fallback
        return render_template_string(
            TEMPLATE,
            stats=db.get_stats(),
            events=db.get_recent_events(50),
            refresh=refresh,
            telemetry=read_telemetry(),
        )
    @app.route("/api/stats")
    def api_stats():
        return jsonify(db.get_stats())

    @app.route("/api/events")
    def api_events():
        return jsonify(db.get_recent_events(100))

    @app.route("/api/alerts")
    def api_alerts():
        return jsonify(db.get_recent_alerts(50))
    @app.route("/api/telemetry")
    def api_telemetry():
        return jsonify(read_telemetry())
    @app.route("/api/discards")
    def api_discards():
        return jsonify(db.get_recent_discards(50))
    @app.route("/video_feed")
    def video_feed():
        frame_path = cfg["dashboard"]["live_frame_path"]

        def generate():
            while True:
                try:
                    with open(frame_path, "rb") as f:
                        jpg = f.read()
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")
                except (FileNotFoundError, PermissionError):
                    pass
                time.sleep(0.1)

        return Response(generate(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")

    return app        # ← exit door: nothing below this ever runs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    app = create_app(args.config)
    app.run(host=cfg["dashboard"]["host"], port=cfg["dashboard"]["port"])
