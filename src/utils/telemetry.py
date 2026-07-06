"""
telemetry.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

Measures FPS in the inference loop and publishes system health to a JSON
file once per second. The dashboard (separate process) reads that file.
On Jetson: uses jetson-stats (jtop) for GPU temp. On dev machines: psutil.
"""
import json
import os
import time

try:
    from jtop import jtop          # Jetson only
    HAS_JTOP = True
except ImportError:
    HAS_JTOP = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class TelemetryReporter:
    def __init__(self, out_path: str = "data/telemetry.json",
                 interval_s: float = 1.0):
        self.out_path = out_path
        self.interval = interval_s
        self._frames = 0
        self._window_start = time.time()
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        self._jetson = None
        if HAS_JTOP:
            try:
                self._jetson = jtop()
                self._jetson.start()
            except Exception:
                self._jetson = None   # jtop service not running — degrade gracefully

    def tick(self) -> None:
        """Call exactly once per processed frame."""
        self._frames += 1
        now = time.time()
        elapsed = now - self._window_start
        if elapsed >= self.interval:
            self._publish(fps=self._frames / elapsed)
            self._frames = 0
            self._window_start = now

    def _system_stats(self) -> dict:
        if self._jetson is not None and self._jetson.ok():
            s = self._jetson.stats
            return {"gpu_temp_c": s.get("Temp GPU"),
                    "mem_used_pct": None,
                    "cpu_pct": None,
                    "source": "jetson"}
        if HAS_PSUTIL:
            return {"gpu_temp_c": None,
                    "mem_used_pct": psutil.virtual_memory().percent,
                    "cpu_pct": psutil.cpu_percent(),
                    "source": "psutil"}
        return {"gpu_temp_c": None, "mem_used_pct": None,
                "cpu_pct": None, "source": "none"}

    def _publish(self, fps: float) -> None:
        data = {"timestamp": time.time(), "fps": round(fps, 1)}
        data.update(self._system_stats())
        tmp = self.out_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, self.out_path)   # atomic swap — reader never sees a half-written file