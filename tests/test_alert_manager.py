import os
import tempfile
import time
import pytest

from src.utils.db_logger import DBLogger
from src.utils.alert_manager import AlertManager


@pytest.fixture
def manager():
    tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_db.close()
    logger = DBLogger(tmp_db.name)
    alerts = []
    mgr = AlertManager(
        db_logger=logger,
        confidence_threshold=0.6,
        debounce_frames=3,
        alert_cooldown_seconds=1,  # short for tests
        on_alert=lambda d: alerts.append(d),
    )
    mgr._test_alerts = alerts  # stash for assertions
    yield mgr
    os.unlink(tmp_db.name)


def fire_hit(conf=0.8):
    return [{"class_name": "fire", "confidence": conf, "bbox": [0, 0, 10, 10]}]


def test_no_alert_below_threshold(manager):
    for _ in range(5):
        triggered = manager.process_frame([{"class_name": "fire", "confidence": 0.3}])
        assert triggered is False
    assert manager._test_alerts == []


def test_no_alert_single_frame(manager):
    assert manager.process_frame(fire_hit()) is False
    assert manager.process_frame(None) is False  # breaks the debounce streak


def test_alert_after_debounce_frames(manager):
    assert manager.process_frame(fire_hit()) is False
    assert manager.process_frame(fire_hit()) is False
    assert manager.process_frame(fire_hit()) is True  # 3rd consecutive -> alert
    assert len(manager._test_alerts) == 1


def test_cooldown_suppresses_repeat_alert(manager):
    for _ in range(3):
        manager.process_frame(fire_hit())
    assert len(manager._test_alerts) == 1

    # Immediately continuing to detect fire should NOT re-trigger
    # within the cooldown window
    manager.process_frame(fire_hit())
    assert len(manager._test_alerts) == 1

    time.sleep(1.1)  # let cooldown (1s in fixture) expire
    for _ in range(3):
        manager.process_frame(fire_hit())
    assert len(manager._test_alerts) == 2


def test_empty_detections_never_alert(manager):
    for _ in range(10):
        assert manager.process_frame([]) is False
    assert manager._test_alerts == []
