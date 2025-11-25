"""
API Service
Handles communication with backend API
"""
import requests
import time
from config.settings import BACKEND_URL, API_TIMEOUT, MAX_RETRIES, ENABLE_OFFLINE_QUEUE
from utils.logger import get_logger
from utils.queue_manager import QueueManager

logger = get_logger(__name__)

class APIService:
    """Service to handle API communication with backend"""
    
    def __init__(self, enable_queue=ENABLE_OFFLINE_QUEUE):
        self.base_url = BACKEND_URL
        self.timeout = API_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.queue_manager = QueueManager() if enable_queue else None
        
        logger.info(f"✅ API Service initialized (base URL: {self.base_url})")
    
    def _make_request(self, method, endpoint, data=None, files=None):
        """
        Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (relative to base URL)
            data: Request data
            files: Files to upload
            
        Returns:
            dict: Response data or None if failed
        """
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                logger.info(f"🌐 {method} {url}")
                
                if method == 'GET':
                    response = requests.get(
                        url,
                        params=data,
                        timeout=self.timeout
                    )
                elif method == 'POST':
                    response = requests.post(
                        url,
                        json=data,
                        files=files,
                        timeout=self.timeout
                    )
                elif method == 'DELETE':
                    response = requests.delete(
                        url,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check response status
                if response.status_code in [200, 201]:
                    logger.info(f"✅ API request successful: {response.status_code}")
                    return response.json()
                
                elif response.status_code == 404:
                    logger.warning(f"⚠️ Resource not found: {url}")
                    return None
                
                elif response.status_code == 409:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Conflict')
                    logger.warning(f"⚠️ Conflict: {error_msg}")
                    return error_data
                
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Bad request')
                    logger.error(f"❌ Bad request: {error_msg}")
                    return error_data
                
                else:
                    logger.error(f"❌ API error: {response.status_code} - {response.text}")
                    retry_count += 1
                    time.sleep(1)
                
            except requests.exceptions.ConnectionError as e:
                retry_count += 1
                logger.error(f"❌ Connection error (attempt {retry_count}/{self.max_retries}): {e}")
                
                # Queue request if offline mode enabled and max retries reached
                if self.queue_manager and retry_count >= self.max_retries:
                    logger.info("💾 Queueing request for later")
                    self.queue_manager.add_request(method, endpoint, data, files)
                
                time.sleep(2)
                
            except requests.exceptions.Timeout as e:
                retry_count += 1
                logger.error(f"❌ Request timeout (attempt {retry_count}/{self.max_retries}): {e}")
                time.sleep(1)
                
            except Exception as e:
                retry_count += 1
                logger.error(f"❌ Request error (attempt {retry_count}/{self.max_retries}): {e}")
                time.sleep(1)
        
        logger.error(f"❌ Failed to complete request after {self.max_retries} retries")
        return None
    
    def record_entry(self, license_plate, card_id, image_path=None):
        """
        Record vehicle entry
        
        Args:
            license_plate: License plate number
            card_id: RFID card ID
            image_path: Path to entry image
            
        Returns:
            dict: Response data
        """
        data = {
            'licensePlate': license_plate,
            'cardId': card_id,
            'image': image_path,
            'entryTime': int(time.time() * 1000)  # Timestamp in milliseconds
        }
        
        logger.info(f"📝 Recording entry: {license_plate} (Card: {card_id})")
        return self._make_request('POST', '', data)
    
    def find_by_card_id(self, card_id):
        """
        Find parking log by card ID
        
        Args:
            card_id: RFID card ID
            
        Returns:
            dict: Parking log data or None
        """
        logger.info(f"🔍 Finding parking log for card: {card_id}")
        response = self._make_request('GET', '', {'cardId': card_id})
        
        if response and response.get('success'):
            logs = response.get('data', {}).get('parkingLogs', [])
            if logs:
                logger.info(f"✅ Found parking log: {logs[0].get('licensePlate')}")
                return logs[0]
            else:
                logger.warning(f"⚠️ No parking log found for card: {card_id}")
        
        return None
    
    def delete_log(self, log_id):
        """
        Delete parking log (vehicle exit)
        
        Args:
            log_id: Parking log ID
            
        Returns:
            dict: Response data with exit info
        """
        logger.info(f"🗑️ Deleting parking log: {log_id}")
        return self._make_request('DELETE', log_id)
    
    def process_queued_requests(self):
        """Process any queued requests from offline mode"""
        if self.queue_manager:
            queue_size = self.queue_manager.get_queue_size()
            if queue_size > 0:
                logger.info(f"🔄 Processing {queue_size} queued requests...")
                self.queue_manager.process_queue(self._make_request)
            else:
                logger.debug("No queued requests to process")
    
    def health_check(self):
        """
        Check if backend API is reachable
        
        Returns:
            bool: True if API is reachable
        """
        try:
            response = requests.get(
                self.base_url.replace('/parking/logs', '/health'),
                timeout=3
            )
            return response.status_code == 200
        except:
            return False
