"""
Logging utility module
Equivalent to: utils/logger.js
"""
import logging
import sys
from datetime import datetime

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def info(*args):
    """Log info message"""
    message = ' '.join(map(str, args))
    logger.info(message)

def error(*args):
    """Log error message"""
    message = ' '.join(map(str, args))
    logger.error(message)

def warn(*args):
    """Log warning message"""
    message = ' '.join(map(str, args))
    logger.warning(message)

def debug(*args):
    """Log debug message"""
    message = ' '.join(map(str, args))
    logger.debug(message)
