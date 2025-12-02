"""
Middleware functions
Equivalent to: utils/middleware.js
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError
from utils.logger import info, error
import time

# ==================== REQUEST LOGGER MIDDLEWARE ====================

async def log_requests(request: Request, call_next):
    """
    Log all incoming requests
    Equivalent to: requestLogger middleware in middleware.js
    """
    info('Method:', request.method)
    info('Path:', request.url.path)
    
    # Log body for POST/PUT/PATCH requests
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            info('Body:', body.decode())
        except:
            pass
    
    info('---')
    
    # Process request and measure time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add custom header with processing time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# ==================== ERROR HANDLERS ====================

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors (equivalent to ValidationError in Node.js)
    """
    error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"message": str(exc.errors())}}
    )

async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    """
    Handle MongoDB duplicate key errors (equivalent to E11000 in Node.js)
    """
    error(f"Duplicate key error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"message": "Duplicate entry - resource already exists"}}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    """
    error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"message": "Internal server error"}}
    )
