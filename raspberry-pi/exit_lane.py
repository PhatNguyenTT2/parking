#!/usr/bin/env python3
"""
Exit Lane Script
Handles vehicle exit process:
1. Wait for RFID card
2. Find entry record from backend
3. Capture image and recognize license plate
4. Compare license plates
5. Delete record and open gate if match
"""
import sys
import time
import signal
from services import RFIDService, CameraService, APIService, GPIOService
from utils.logger import get_logger

logger = get_logger(__name__)

class ExitLane:
    """Exit lane controller"""
    
    def __init__(self):
        logger.info("🚀 Initializing Exit Lane...")
        
        self.rfid_service = RFIDService()
        self.camera_service = CameraService()
        self.api_service = APIService()
        self.gpio_service = GPIOService(lane_type='exit')
        
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ Exit Lane initialized successfully")
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info("⚠️ Shutdown signal received")
        self.stop()
        sys.exit(0)
    
    def calculate_parking_duration(self, entry_time_ms):
        """
        Calculate parking duration
        
        Args:
            entry_time_ms: Entry timestamp in milliseconds
            
        Returns:
            dict: Duration information
        """
        current_time_ms = int(time.time() * 1000)
        duration_ms = current_time_ms - entry_time_ms
        
        duration_seconds = duration_ms // 1000
        duration_minutes = duration_seconds // 60
        duration_hours = duration_minutes // 60
        
        remaining_minutes = duration_minutes % 60
        
        return {
            'milliseconds': duration_ms,
            'seconds': duration_seconds,
            'minutes': duration_minutes,
            'hours': duration_hours,
            'formatted': f"{duration_hours}h {remaining_minutes}m"
        }
    
    def process_exit(self):
        """Process single vehicle exit"""
        logger.info("\n" + "="*60)
        logger.info("🚗 Waiting for vehicle at EXIT lane...")
        logger.info("="*60)
        
        # Step 1: Read RFID card
        logger.info("📍 Step 1: Reading RFID card...")
        card_id = self.rfid_service.wait_for_card()
        
        if not card_id:
            logger.error("❌ Failed to read RFID card")
            self.gpio_service.error_feedback()
            return False
        
        logger.info(f"✅ Card ID: {card_id}")
        self.gpio_service.beep(1)
        
        # Step 2: Find entry record
        logger.info("📍 Step 2: Finding entry record in database...")
        entry_log = self.api_service.find_by_card_id(card_id)
        
        if not entry_log:
            logger.error("❌ No entry record found for this card")
            logger.error("⚠️ Vehicle may have already exited or never entered")
            self.gpio_service.error_feedback()
            return False
        
        entry_plate = entry_log.get('licensePlate')
        entry_time = entry_log.get('entryTime')
        log_id = entry_log.get('id')
        
        logger.info(f"✅ Found entry record:")
        logger.info(f"   - License Plate: {entry_plate}")
        logger.info(f"   - Entry Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry_time/1000))}")
        
        # Step 3: Capture image and recognize license plate
        logger.info("📍 Step 3: Capturing image and recognizing license plate...")
        exit_plate, image_path = self.camera_service.capture_and_recognize('exit')
        
        if not exit_plate:
            logger.error("❌ Failed to recognize license plate")
            logger.warning("⚠️ Manual verification required")
            self.gpio_service.error_feedback()
            return False
        
        logger.info(f"✅ Exit License Plate: {exit_plate}")
        
        # Step 4: Compare license plates
        logger.info("📍 Step 4: Comparing license plates...")
        logger.info(f"   Entry: {entry_plate}")
        logger.info(f"   Exit:  {exit_plate}")
        
        if entry_plate != exit_plate:
            logger.error("❌ LICENSE PLATE MISMATCH!")
            logger.error(f"   Expected: {entry_plate}")
            logger.error(f"   Got:      {exit_plate}")
            logger.error("⚠️ Gate will NOT open - Manual verification required")
            self.gpio_service.error_feedback()
            return False
        
        logger.info("✅ License plates match!")
        
        # Step 5: Calculate parking duration
        duration = self.calculate_parking_duration(entry_time)
        logger.info(f"⏱️ Parking Duration: {duration['formatted']}")
        
        # Step 6: Delete entry record (vehicle exit)
        logger.info("📍 Step 5: Deleting entry record (processing exit)...")
        delete_response = self.api_service.delete_log(log_id)
        
        if not delete_response or not delete_response.get('success'):
            logger.error("❌ Failed to delete entry record")
            logger.warning("⚠️ Gate will still open, but manual cleanup may be needed")
        else:
            logger.info("✅ Entry record deleted successfully")
        
        # Step 7: Open gate
        logger.info("📍 Step 6: Opening gate...")
        self.gpio_service.success_feedback()
        self.gpio_service.open_gate()
        
        # Display summary
        logger.info("\n" + "-"*60)
        logger.info("📊 EXIT SUMMARY:")
        logger.info(f"   License Plate: {entry_plate}")
        logger.info(f"   Card ID: {card_id}")
        logger.info(f"   Entry: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry_time/1000))}")
        logger.info(f"   Exit:  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        logger.info(f"   Duration: {duration['formatted']} ({duration['minutes']} minutes)")
        logger.info("-"*60)
        
        logger.info(f"⏳ Gate will remain open for 5 seconds...")
        time.sleep(5)
        
        self.gpio_service.close_gate()
        logger.info("✅ Gate closed")
        
        logger.info("="*60)
        logger.info("✅ Exit process completed successfully")
        logger.info("="*60 + "\n")
        
        return True
    
    def start(self):
        """Start exit lane loop"""
        logger.info("🚀 Exit Lane started")
        logger.info("Press Ctrl+C to stop\n")
        
        self.running = True
        
        # Process queued requests from offline mode
        self.api_service.process_queued_requests()
        
        while self.running:
            try:
                self.process_exit()
                time.sleep(1)  # Small delay between cycles
                
            except KeyboardInterrupt:
                logger.info("⚠️ Interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                self.gpio_service.error_feedback()
                time.sleep(2)
        
        self.stop()
    
    def stop(self):
        """Stop exit lane and cleanup"""
        logger.info("🛑 Stopping Exit Lane...")
        self.running = False
        
        # Cleanup resources
        self.rfid_service.cleanup()
        self.camera_service.cleanup()
        self.gpio_service.cleanup()
        
        logger.info("✅ Exit Lane stopped")

def main():
    """Main entry point"""
    try:
        exit_lane = ExitLane()
        exit_lane.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
