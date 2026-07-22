"""
frame_publisher.py
Owned by: Saarang Agarwal (System Software, Monitoring & Data Management)

Writes the latest annotated frame to a JPEG 'mailbox' file (atomic replace),
throttled to max_fps. The dashboard streams this file as MJPEG.
"""
import os
import time
import cv2


class FramePublisher:
    def __init__(self, out_path: str, max_fps: float = 10.0,
                 width: int = 640, jpeg_quality: int = 70):
        self.out_path = out_path
        self.min_interval = 1.0 / max_fps
        self.width = width
        self.quality = jpeg_quality
        self._last_write = 0.0
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    def publish(self, frame) -> None:
        now = time.time()
        if now - self._last_write < self.min_interval:
            return                              # throttle: dashboard needs ~10fps, not 30
        h, w = frame.shape[:2]
        scale = self.width / float(w)
        small = cv2.resize(frame, (self.width, int(h * scale)))
        ok, jpg = cv2.imencode(".jpg", small,
                               [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        if not ok:
            return
        tmp = self.out_path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(jpg.tobytes())
        try:
            os.replace(tmp, self.out_path)      # atomic swap
        except PermissionError:
            # Windows: reader has the file open this instant — drop this
            # frame, the next one lands in ~100ms. Never crash the detector.
            pass