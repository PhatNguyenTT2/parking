"""
Server entry point
Equivalent to: index.js
"""
import uvicorn
from utils.config import PORT, NODE_ENV
from utils.logger import info

if __name__ == "__main__":
    info(f"Starting server on port {PORT}")
    
    # Run server with uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=PORT,
        reload=(NODE_ENV == "development"),  # Auto-reload in dev mode
        log_level="info"
    )
