"""
GPIO Pin Configuration for Raspberry Pi
Using BCM pin numbering
"""

# Entry Lane Pins
ENTRY_GATE_PIN = 17          # Servo motor for entry gate
ENTRY_GREEN_LED = 27         # Success LED
ENTRY_RED_LED = 22           # Error LED
ENTRY_BUZZER = 23            # Buzzer for alerts

# Exit Lane Pins
EXIT_GATE_PIN = 18           # Servo motor for exit gate
EXIT_GREEN_LED = 24          # Success LED
EXIT_RED_LED = 25            # Error LED
EXIT_BUZZER = 8              # Buzzer for alerts

# RFID Reader Pins (SPI)
RFID_RST_PIN = 25            # Reset pin
RFID_IRQ_PIN = 24            # Interrupt pin (optional)

# Camera
CAMERA_ID = 0                # USB camera index (0 = default)

# Servo Motor Settings
SERVO_FREQUENCY = 50         # Hz
SERVO_OPEN_ANGLE = 90        # Degrees (gate open position)
SERVO_CLOSE_ANGLE = 0        # Degrees (gate closed position)
