"""
Queue Manager for offline mode
Stores failed API requests and retries them when connection is restored
"""
import json
import time
from pathlib import Path
from config.settings import QUEUE_FILE_PATH, QUEUE_MAX_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)

class QueueManager:
    """Manages offline request queue"""
    
    def __init__(self):
        self.queue_file = QUEUE_FILE_PATH
        self.max_size = QUEUE_MAX_SIZE
        self.queue = self._load_queue()
    
    def _load_queue(self):
        """Load queue from file"""
        try:
            if self.queue_file.exists():
                with open(self.queue_file, 'r') as f:
                    queue = json.load(f)
                    logger.info(f"📥 Loaded {len(queue)} requests from queue")
                    return queue
        except Exception as e:
            logger.error(f"❌ Failed to load queue: {e}")
        
        return []
    
    def _save_queue(self):
        """Save queue to file"""
        try:
            with open(self.queue_file, 'w') as f:
                json.dump(self.queue, f, indent=2)
            logger.debug(f"💾 Queue saved ({len(self.queue)} items)")
        except Exception as e:
            logger.error(f"❌ Failed to save queue: {e}")
    
    def add_request(self, method, endpoint, data=None, files=None):
        """
        Add failed request to queue
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            files: Files to upload (paths only, not file objects)
        """
        if len(self.queue) >= self.max_size:
            logger.warning(f"⚠️ Queue is full ({self.max_size} items), removing oldest")
            self.queue.pop(0)
        
        request = {
            'method': method,
            'endpoint': endpoint,
            'data': data,
            'files': files,
            'timestamp': int(time.time()),
            'retry_count': 0
        }
        
        self.queue.append(request)
        self._save_queue()
        
        logger.info(f"➕ Request queued: {method} {endpoint}")
    
    def process_queue(self, request_handler):
        """
        Process all queued requests
        
        Args:
            request_handler: Function to handle requests (e.g., api_service._make_request)
        """
        if not self.queue:
            logger.debug("Queue is empty, nothing to process")
            return
        
        logger.info(f"🔄 Processing {len(self.queue)} queued requests...")
        
        processed = []
        failed = []
        
        for request in self.queue:
            try:
                method = request['method']
                endpoint = request['endpoint']
                data = request['data']
                files = request['files']
                
                logger.info(f"🔄 Retrying: {method} {endpoint}")
                
                # Try to process request
                result = request_handler(method, endpoint, data, files)
                
                if result:
                    logger.info(f"✅ Queued request processed successfully")
                    processed.append(request)
                else:
                    request['retry_count'] += 1
                    if request['retry_count'] < 5:
                        failed.append(request)
                        logger.warning(f"⚠️ Request failed, will retry later (attempt {request['retry_count']})")
                    else:
                        logger.error(f"❌ Request failed after 5 retries, dropping")
                        processed.append(request)  # Remove from queue
                
            except Exception as e:
                logger.error(f"❌ Error processing queued request: {e}")
                failed.append(request)
        
        # Update queue with only failed requests
        self.queue = failed
        self._save_queue()
        
        logger.info(f"✅ Queue processing complete: {len(processed)} processed, {len(failed)} remaining")
    
    def clear_queue(self):
        """Clear all queued requests"""
        self.queue = []
        self._save_queue()
        logger.info("🗑️ Queue cleared")
    
    def get_queue_size(self):
        """Get current queue size"""
        return len(self.queue)
