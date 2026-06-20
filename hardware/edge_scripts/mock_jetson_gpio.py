# mock_jetson_gpio.py
# A robust, error-handling mock library for NVIDIA Jetson GPIO hardware
# 

BOARD = "BOARD"
BCM = "BCM"
OUT = "OUT"
IN = "IN"
HIGH = 1
LOW = 0

# --- INTERNAL STATE TRACKING ---
# The mock needs to remember what the AI code has done so far
_current_mode = None
_pin_registry = {}  # Tracks which pins are active and their direction {pin: direction}

def setmode(mode):
    global _current_mode
    if mode not in [BOARD, BCM]:
        raise ValueError("[MOCK ERROR] Invalid mode. Must be GPIO.BOARD or GPIO.BCM")
    
    _current_mode = mode
    print(f"[GPIO MOCK] Board mode set to: {mode}")

def setup(pin, direction):
    # Error Check 1: Did they forget to set the board mode first?
    if _current_mode is None:
        raise RuntimeError("[MOCK ERROR] Please set pin numbering mode using GPIO.setmode() first.")
    
    # Error Check 2: Does this pin actually exist on the Jetson Nano?
    if not isinstance(pin, int) or pin < 1 or pin > 40:
        raise ValueError(f"[MOCK ERROR] Invalid channel {pin}. Jetson physical pins are 1-40.")

    # Error Check 3: Did they pass a valid direction?
    if direction not in [OUT, IN]:
        raise ValueError("[MOCK ERROR] Invalid direction. Must use GPIO.OUT or GPIO.IN")

    # If it passes all checks, register the pin
    _pin_registry[pin] = direction
    dir_str = "OUTPUT" if direction == OUT else "INPUT"
    print(f"[GPIO MOCK] Pin {pin} configured as {dir_str}")

def output(pin, state):
    # Error Check 4: Did they try to trigger a pin they never set up?
    if pin not in _pin_registry:
        raise RuntimeError(f"[MOCK ERROR] Channel {pin} has not been set up. Call GPIO.setup() first.")

    # Error Check 5: Are they trying to send voltage OUT of an IN (microphone) pin?
    if _pin_registry[pin] != OUT:
        raise RuntimeError(f"[MOCK ERROR] Channel {pin} is set as an INPUT. Cannot send output voltage.")

    # Error Check 6: Did they pass a valid power state?
    if state not in [HIGH, LOW]:
        raise ValueError("[MOCK ERROR] Invalid output state. Must use GPIO.HIGH or GPIO.LOW")

    # Safe to execute
    status = "HIGH (ON)" if state == HIGH else "LOW (OFF)"
    
    if state == HIGH:
        print(f"\n[HARDWARE TRIGGER] Sending {status} signal to Pin {pin}")
        print("   -> Simulated Relay: ENGAGED")
    else:
        print(f"[HARDWARE TRIGGER] Sending {status} signal to Pin {pin} (System Normal)")

def cleanup():
    global _current_mode
    # Wipe the registry clean
    _pin_registry.clear()
    _current_mode = None
    print("[GPIO MOCK] Cleaning up pins and resetting hardware state.")