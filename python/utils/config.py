"""
Configuration module - loads environment variables
Equivalent to: utils/config.js
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/parking')
PORT = int(os.getenv('PORT', 3001))
NODE_ENV = os.getenv('NODE_ENV', 'development')

# Validation
if not MONGODB_URI:
    raise ValueError("MONGODB_URI must be set in environment variables")

# Print config on import (for debugging)
if NODE_ENV == 'development':
    print(f"Config loaded: PORT={PORT}, ENV={NODE_ENV}")
