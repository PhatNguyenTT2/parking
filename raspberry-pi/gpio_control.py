#!/usr/bin/env python3
"""
GPIO Control Service cho Raspberry Pi 4
Điều khiển barrier (cổng) qua relay module
"""

import RPi.GPIO as GPIO
import time
import requests

# GPIO Pin Configuration
BARRIER_ENTRY_PIN = 17  # GPIO 17 - Barrier vào
BARRIER_EXIT_PIN = 27   # GPIO 27 - Barrier ra
LED_GREEN_PIN = 22      # GPIO 22 - LED xanh (cho phép vào)
LED_RED_PIN = 23        # GPIO 23 - LED đỏ (không cho vào)

# Backend API
BACKEND_URL = "http://localhost:3001/api/vehicle"

class BarrierController:
    def __init__(self):
        """Initialize GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup output pins
        GPIO.setup(BARRIER_ENTRY_PIN, GPIO.OUT)
        GPIO.setup(BARRIER_EXIT_PIN, GPIO.OUT)
        GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
        GPIO.setup(LED_RED_PIN, GPIO.OUT)
        
        # Initialize all to LOW
        GPIO.output(BARRIER_ENTRY_PIN, GPIO.LOW)
        GPIO.output(BARRIER_EXIT_PIN, GPIO.LOW)
        GPIO.output(LED_GREEN_PIN, GPIO.LOW)
        GPIO.output(LED_RED_PIN, GPIO.LOW)
        
        print("✅ GPIO initialized")
    
    def open_barrier(self, barrier_type="entry", duration=3):
        """
        Open barrier for specified duration
        :param barrier_type: "entry" or "exit"
        :param duration: Time in seconds to keep barrier open
        """
        pin = BARRIER_ENTRY_PIN if barrier_type == "entry" else BARRIER_EXIT_PIN
        
        print(f"🔓 Opening {barrier_type} barrier...")
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(LED_GREEN_PIN, GPIO.HIGH)
        
        time.sleep(duration)
        
        GPIO.output(pin, GPIO.LOW)
        GPIO.output(LED_GREEN_PIN, GPIO.LOW)
        print(f"🔒 Closed {barrier_type} barrier")
    
    def deny_access(self, duration=2):
        """Show red LED to deny access"""
        print("❌ Access denied")
        GPIO.output(LED_RED_PIN, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(LED_RED_PIN, GPIO.LOW)
    
    def check_vehicle_entry(self, license_plate):
        """
        Check if vehicle can enter (not already inside)
        """
        try:
            response = requests.get(f"{BACKEND_URL}/inside")
            if response.status_code == 200:
                data = response.json()
                vehicles_inside = [v['licensePlate'] for v in data.get('vehicles', [])]
                
                if license_plate in vehicles_inside:
                    return False  # Already inside
                return True  # Can enter
        except Exception as e:
            print(f"❌ Backend check failed: {e}")
            return True  # Default allow if backend unavailable
    
    def check_vehicle_exit(self, license_plate):
        """
        Check if vehicle can exit (must have entry record)
        """
        try:
            response = requests.get(f"{BACKEND_URL}/{license_plate}")
            if response.status_code == 200:
                vehicle = response.json()
                if vehicle.get('status') == 'in':
                    return True  # Can exit
                return False  # Not inside
            return False  # No record found
        except Exception as e:
            print(f"❌ Backend check failed: {e}")
            return False  # Default deny if backend unavailable
    
    def handle_vehicle_entry(self, license_plate):
        """
        Handle vehicle entry logic
        """
        print(f"\n🚗 Vehicle entry request: {license_plate}")
        
        if self.check_vehicle_entry(license_plate):
            print("✅ Access granted")
            self.open_barrier("entry", duration=5)
            return True
        else:
            print("❌ Vehicle already inside")
            self.deny_access()
            return False
    
    def handle_vehicle_exit(self, license_plate):
        """
        Handle vehicle exit logic
        """
        print(f"\n🚗 Vehicle exit request: {license_plate}")
        
        if self.check_vehicle_exit(license_plate):
            print("✅ Access granted")
            self.open_barrier("exit", duration=5)
            return True
        else:
            print("❌ No entry record found")
            self.deny_access()
            return False
    
    def test_barriers(self):
        """Test all barriers and LEDs"""
        print("\n🧪 Testing barriers and LEDs...")
        
        print("Testing entry barrier...")
        self.open_barrier("entry", duration=2)
        time.sleep(1)
        
        print("Testing exit barrier...")
        self.open_barrier("exit", duration=2)
        time.sleep(1)
        
        print("Testing deny access...")
        self.deny_access()
        
        print("✅ Test complete")
    
    def cleanup(self):
        """Clean up GPIO"""
        GPIO.cleanup()
        print("✅ GPIO cleaned up")

# Example usage
if __name__ == "__main__":
    print("🚀 Starting Barrier Control Service...")
    
    controller = BarrierController()
    
    try:
        # Run test
        controller.test_barriers()
        
        print("\n" + "="*50)
        print("Service running. Press Ctrl+C to stop")
        print("="*50 + "\n")
        
        # Main loop - wait for camera service to trigger
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping service...")
        controller.cleanup()
        print("✅ Service stopped")
