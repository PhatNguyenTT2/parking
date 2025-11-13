#!/usr/bin/env python3
"""
Main Parking System Integration
Tích hợp Camera + OCR + GPIO + Backend
"""

import cv2
import time
import sys
import os
from camera_ocr_service import ParkingCameraService

# Try import GPIO, fallback if not on Raspberry Pi
try:
    from gpio_control import BarrierController
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("⚠️  GPIO not available (not running on Raspberry Pi)")

class ParkingSystem:
    def __init__(self, entry_camera_id=0, exit_camera_id=1, enable_gpio=True):
        """
        Initialize complete parking system
        """
        print("🚀 Initializing Parking System...")
        
        # Initialize cameras
        self.entry_service = ParkingCameraService(
            camera_index=entry_camera_id, 
            camera_type="entry"
        )
        print("✅ Entry camera initialized")
        
        self.exit_service = ParkingCameraService(
            camera_index=exit_camera_id, 
            camera_type="exit"
        )
        print("✅ Exit camera initialized")
        
        # Initialize GPIO if available and enabled
        self.gpio_enabled = GPIO_AVAILABLE and enable_gpio
        if self.gpio_enabled:
            self.barrier = BarrierController()
            print("✅ Barrier controller initialized")
        else:
            self.barrier = None
            print("⚠️  Barrier controller disabled")
        
        print("✅ Parking System ready!\n")
    
    def handle_entry(self):
        """Process vehicle entry"""
        print("\n" + "="*60)
        print("🚗 VEHICLE ENTRY DETECTED")
        print("="*60)
        
        # Process image and OCR
        result = self.entry_service.process_vehicle()
        
        if result and result.get('success'):
            license_plate = result['vehicle']['licensePlate']
            print(f"✅ Vehicle registered: {license_plate}")
            
            # Open barrier if GPIO available
            if self.barrier:
                self.barrier.handle_vehicle_entry(license_plate)
            
            return True
        else:
            print("❌ Vehicle registration failed")
            if self.barrier:
                self.barrier.deny_access()
            return False
    
    def handle_exit(self):
        """Process vehicle exit"""
        print("\n" + "="*60)
        print("🚗 VEHICLE EXIT DETECTED")
        print("="*60)
        
        # Process image and OCR
        result = self.exit_service.process_vehicle()
        
        if result and result.get('allowed'):
            license_plate = result['vehicle']['licensePlate']
            print(f"✅ Vehicle exit approved: {license_plate}")
            
            # Open barrier if GPIO available
            if self.barrier:
                self.barrier.handle_vehicle_exit(license_plate)
            
            return True
        else:
            print("❌ Vehicle exit denied")
            if self.barrier:
                self.barrier.deny_access()
            return False
    
    def run_demo_mode(self):
        """Run system in demo mode (manual trigger)"""
        print("\n" + "="*60)
        print("DEMO MODE")
        print("="*60)
        print("Commands:")
        print("  'e' - Process entry")
        print("  'x' - Process exit")
        print("  't' - Test barriers")
        print("  'q' - Quit")
        print("="*60 + "\n")
        
        try:
            while True:
                cmd = input("\nEnter command: ").strip().lower()
                
                if cmd == 'e':
                    self.handle_entry()
                elif cmd == 'x':
                    self.handle_exit()
                elif cmd == 't' and self.barrier:
                    self.barrier.test_barriers()
                elif cmd == 'q':
                    break
                else:
                    print("❌ Invalid command")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping demo mode...")
    
    def run_auto_mode(self):
        """
        Run system in auto mode (with motion sensors/buttons)
        TODO: Implement actual trigger mechanism
        """
        print("\n" + "="*60)
        print("AUTO MODE")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        try:
            while True:
                # TODO: Replace with actual trigger
                # - Motion sensor
                # - IR beam break
                # - Pressure pad
                # - Button press
                
                time.sleep(1)
                
                # Simulate random triggers for demo
                # In production, remove this and use real triggers
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping auto mode...")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        
        self.entry_service.cleanup()
        self.exit_service.cleanup()
        
        if self.barrier:
            self.barrier.cleanup()
        
        print("✅ Cleanup complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parking Management System')
    parser.add_argument('--mode', choices=['demo', 'auto'], default='demo',
                       help='Run mode: demo (manual) or auto (with triggers)')
    parser.add_argument('--entry-cam', type=int, default=0,
                       help='Entry camera index (default: 0)')
    parser.add_argument('--exit-cam', type=int, default=1,
                       help='Exit camera index (default: 1)')
    parser.add_argument('--no-gpio', action='store_true',
                       help='Disable GPIO control (for testing on PC)')
    
    args = parser.parse_args()
    
    # Initialize system
    system = ParkingSystem(
        entry_camera_id=args.entry_cam,
        exit_camera_id=args.exit_cam,
        enable_gpio=not args.no_gpio
    )
    
    try:
        # Run selected mode
        if args.mode == 'demo':
            system.run_demo_mode()
        else:
            system.run_auto_mode()
            
    finally:
        system.cleanup()

if __name__ == "__main__":
    main()
