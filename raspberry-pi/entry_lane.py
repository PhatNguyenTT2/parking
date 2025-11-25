#!/usr/bin/env python3
"""
Entry Lane Script
Handles vehicle entry process:
1. Wait for RFID card
2. Capture image and recognize license plate
3. Send data to backend
4. Open gate if successful
"""
import sys
import time
import signal
from services import RFIDService, CameraService, APIService, GPIOService
from utils.logger import get_logger

logger = get_logger(__name__)

class EntryLane:
    """Entry lane controller"""
    
    def __init__(self):
        logger.info("🚀 Initializing Entry Lane...")
        
        self.rfid_service = RFIDService()
        self.camera_service = CameraService()
        self.api_service = APIService()
        self.gpio_service = GPIOService(lane_type='entry')
        
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ Entry Lane initialized successfully")
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        logger.info("⚠️ Shutdown signal received")
        self.stop()
        sys.exit(0)
    
    def process_entry(self):
        """Process single vehicle entry"""
        logger.info("\n" + "="*60)
        logger.info("🚗 Waiting for vehicle at ENTRY lane...")
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
        
        # Step 2: Capture image and recognize license plate
        logger.info("📍 Step 2: Capturing image and recognizing license plate...")
        license_plate, image_path = self.camera_service.capture_and_recognize('entry')
        
        if not license_plate:
            logger.error("❌ Failed to recognize license plate")
            self.gpio_service.error_feedback()
            return False
        
        logger.info(f"✅ License Plate: {license_plate}")
        
        # Step 3: Send to backend
        logger.info("📍 Step 3: Sending data to backend...")
        response = self.api_service.record_entry(license_plate, card_id, image_path)
        
        if not response:
            logger.error("❌ Failed to record entry in backend")
            self.gpio_service.error_feedback()
            return False
        
        # Check response
        if not response.get('success'):
            error = response.get('error', {})
            error_code = error.get('code')
            error_msg = error.get('message', 'Unknown error')
            
            logger.error(f"❌ Backend error: {error_msg}")
            
            if error_code == 'CARD_IN_USE':
                logger.warning("⚠️ This card is already in use!")
                self.gpio_service.error_feedback()
            else:
                self.gpio_service.error_feedback()
            
            return False
        
        logger.info("✅ Entry recorded successfully")
        
        # Step 4: Open gate
        logger.info("📍 Step 4: Opening gate...")
        self.gpio_service.success_feedback()
        self.gpio_service.open_gate()
        
        logger.info(f"⏳ Gate will remain open for 5 seconds...")
        time.sleep(5)
        
        self.gpio_service.close_gate()
        logger.info("✅ Gate closed")
        
        logger.info("="*60)
        logger.info("✅ Entry process completed successfully")
        logger.info("="*60 + "\n")
        
        return True
    
    def start(self):
        """Start entry lane loop"""
        logger.info("🚀 Entry Lane started")
        logger.info("Press Ctrl+C to stop\n")
        
        self.running = True
        
        # Process queued requests from offline mode
        self.api_service.process_queued_requests()
        
        while self.running:
            try:
                self.process_entry()
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
        """Stop entry lane and cleanup"""
        logger.info("🛑 Stopping Entry Lane...")
        self.running = False
        
        # Cleanup resources
        self.rfid_service.cleanup()
        self.camera_service.cleanup()
        self.gpio_service.cleanup()
        
        logger.info("✅ Entry Lane stopped")

def main():
    """Main entry point"""
    try:
        entry_lane = EntryLane()
        entry_lane.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
