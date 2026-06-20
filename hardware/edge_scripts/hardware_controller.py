
import mock_jetson_gpio as GPIO

ALARM_PIN = 23

def initialize_hardware():
    """Sets up the board. Mihir calls this once at boot."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ALARM_PIN, GPIO.OUT)
    print("[HARDWARE] System initialized and ready.")

def trigger_fire_protocol():
    """Turns on the alarms. Mihir calls this when he sees fire."""
    GPIO.output(ALARM_PIN, GPIO.HIGH)

def reset_alarms():
    """Turns off alarms."""
    GPIO.output(ALARM_PIN, GPIO.LOW)