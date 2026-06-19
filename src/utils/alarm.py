"""GPIO-based alarm control: buzzer, LED, relay.

Owner module: Embedded Hardware & Device Integration (Dev Tiwari)

NOTE: Jetson.GPIO only works on the actual Jetson board. This module is
written so it can be imported and unit-tested on a dev machine by mocking
GPIO calls — see tests/test_alarm.py.
"""

import time

try:
    import Jetson.GPIO as GPIO

    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class AlarmController:
    """Controls buzzer, LED, and relay outputs on detection events."""

    def __init__(self, buzzer_pin: int, led_pin: int, relay_pin: int, cooldown_seconds: int = 10):
        self.buzzer_pin = buzzer_pin
        self.led_pin = led_pin
        self.relay_pin = relay_pin
        self.cooldown_seconds = cooldown_seconds
        self._last_trigger_time = 0.0

        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup([buzzer_pin, led_pin, relay_pin], GPIO.OUT, initial=GPIO.LOW)

    def trigger(self):
        """Activate buzzer + LED + relay if cooldown has elapsed."""
        now = time.time()
        if now - self._last_trigger_time < self.cooldown_seconds:
            return False  # still in cooldown, skip re-trigger

        self._last_trigger_time = now

        if GPIO_AVAILABLE:
            GPIO.output([self.buzzer_pin, self.led_pin, self.relay_pin], GPIO.HIGH)
        else:
            print("[AlarmController] (simulated) ALARM TRIGGERED — buzzer/LED/relay ON")

        return True

    def reset(self):
        """Turn off all alarm outputs."""
        if GPIO_AVAILABLE:
            GPIO.output([self.buzzer_pin, self.led_pin, self.relay_pin], GPIO.LOW)
        else:
            print("[AlarmController] (simulated) alarm reset — outputs OFF")

    def cleanup(self):
        if GPIO_AVAILABLE:
            GPIO.cleanup()
