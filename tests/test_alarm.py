"""Basic tests for AlarmController (runs without real GPIO via fallback simulation)."""

import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.utils.alarm import AlarmController


def test_trigger_returns_true_first_time():
    alarm = AlarmController(buzzer_pin=18, led_pin=23, relay_pin=24, cooldown_seconds=1)
    assert alarm.trigger() is True


def test_trigger_respects_cooldown():
    alarm = AlarmController(buzzer_pin=18, led_pin=23, relay_pin=24, cooldown_seconds=5)
    assert alarm.trigger() is True
    assert alarm.trigger() is False  # immediate re-trigger should be blocked


def test_trigger_fires_again_after_cooldown():
    alarm = AlarmController(buzzer_pin=18, led_pin=23, relay_pin=24, cooldown_seconds=0.1)
    assert alarm.trigger() is True
    time.sleep(0.2)
    assert alarm.trigger() is True
