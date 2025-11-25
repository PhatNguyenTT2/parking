"""
Central configuration for Parking System Raspberry Pi
"""
import os
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# Backend API
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3001/api/parking/logs')
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# Camera Settings
CAMERA_RESOLUTION = (1920, 1080)
CAMERA_WARMUP_TIME = 2  # seconds
OCR_CONFIDENCE_THRESHOLD = 0.6

# RFID Settings
RFID_READ_TIMEOUT = 5  # seconds
RFID_MAX_RETRIES = 3

# GPIO Settings
GATE_OPEN_DURATION = 5  # seconds
LED_BLINK_INTERVAL = 0.5  # seconds
BUZZER_BEEP_DURATION = 0.2  # seconds

# Offline Mode
ENABLE_OFFLINE_QUEUE = True
QUEUE_MAX_SIZE = 100
QUEUE_FILE_PATH = PROJECT_ROOT / 'data' / 'offline_queue.json'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = PROJECT_ROOT / 'logs'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Image Storage
IMAGE_STORAGE_PATH = PROJECT_ROOT / 'images'
IMAGE_RETENTION_DAYS = 30  # Delete images older than 30 days

# Lane Configuration
LANE_TYPE = os.getenv('LANE_TYPE', 'entry')  # 'entry' or 'exit'
LANE_ID = os.getenv('LANE_ID', 'lane_1')

# Create necessary directories
for directory in [LOG_FILE_PATH, IMAGE_STORAGE_PATH, QUEUE_FILE_PATH.parent]:
    directory.mkdir(parents=True, exist_ok=True)
