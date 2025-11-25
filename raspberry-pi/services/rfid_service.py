"""
RFID Reader Service
Handles RFID card reading using MFRC522
"""
import time
try:
    from mfrc522 import SimpleMFRC522
    RFID_AVAILABLE = True
except ImportError:
    RFID_AVAILABLE = False

from config.settings import RFID_READ_TIMEOUT, RFID_MAX_RETRIES
from utils.logger import get_logger
from utils.validators import validate_card_id

logger = get_logger(__name__)

class RFIDService:
    """Service to handle RFID card reading"""
    
    def __init__(self):
        if not RFID_AVAILABLE:
            logger.warning("⚠️ MFRC522 library not available. Running in simulation mode.")
            self.reader = None
        else:
            try:
                self.reader = SimpleMFRC522()
                logger.info("✅ RFID Reader initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize RFID Reader: {e}")
                self.reader = None
    
    def read_card(self, timeout=RFID_READ_TIMEOUT):
        """
        Read RFID card with timeout and retry logic
        
        Args:
            timeout: Maximum time to wait for card (seconds)
            
        Returns:
            str: Card ID if successful, None if failed
        """
        if not self.reader:
            # Simulation mode for testing
            logger.warning("⚠️ RFID Reader not available, using simulation")
            time.sleep(1)
            return "1234567890"  # Test card ID
        
        logger.info(f"🔍 Waiting for RFID card (timeout: {timeout}s)...")
        
        start_time = time.time()
        retry_count = 0
        
        while retry_count < RFID_MAX_RETRIES:
            try:
                # Try to read card
                card_id, text = self.reader.read_no_block()
                
                if card_id:
                    card_id_str = str(card_id)
                    
                    if validate_card_id(card_id_str):
                        logger.info(f"✅ Valid card detected: {card_id_str}")
                        return card_id_str
                    else:
                        logger.warning(f"⚠️ Invalid card ID format: {card_id_str}")
                
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"⏱️ Card read timeout after {timeout}s")
                    return None
                
                time.sleep(0.1)  # Small delay to prevent CPU overload
                
            except KeyboardInterrupt:
                logger.warning("⚠️ RFID read interrupted by user")
                raise
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ RFID read error (attempt {retry_count}/{RFID_MAX_RETRIES}): {e}")
                time.sleep(0.5)
        
        logger.error("❌ Failed to read RFID card after max retries")
        return None
    
    def wait_for_card(self):
        """
        Wait indefinitely until a card is detected
        Useful for entry lane where we wait for user
        
        Returns:
            str: Card ID
        """
        if not self.reader:
            # Simulation mode
            logger.warning("⚠️ RFID Reader not available, using simulation")
            time.sleep(2)
            return "1234567890"
        
        logger.info("🔍 Waiting for RFID card (blocking mode)...")
        
        while True:
            try:
                card_id, text = self.reader.read()
                card_id_str = str(card_id)
                
                if validate_card_id(card_id_str):
                    logger.info(f"✅ Valid card detected: {card_id_str}")
                    return card_id_str
                else:
                    logger.warning(f"⚠️ Invalid card ID, please try again")
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.warning("⚠️ RFID read interrupted by user")
                raise
            except Exception as e:
                logger.error(f"❌ RFID read error: {e}")
                time.sleep(0.5)
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            if self.reader:
                # MFRC522 library handles cleanup automatically
                logger.info("✅ RFID Reader cleanup completed")
        except Exception as e:
            logger.error(f"❌ RFID cleanup error: {e}")
