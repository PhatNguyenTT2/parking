"""
FastAPI Application
Equivalent to: app.js
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pymongo.errors import DuplicateKeyError
from contextlib import asynccontextmanager
import os

from utils.config import NODE_ENV
from utils.logger import info
from utils.database import connect_db, close_db
from utils.middleware import (
    log_requests,
    validation_exception_handler,
    duplicate_key_exception_handler,
    general_exception_handler
)
from controllers.parking_logs import router as parking_logs_router

# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown
    """
    # Startup
    await connect_db()
    info(f"Application started in {NODE_ENV} mode")
    yield
    # Shutdown
    await close_db()
    info("Application shutdown")

# ==================== CREATE FASTAPI APP ====================

app = FastAPI(
    title="Parking Management API",
    description="API for managing parking lot entries and exits",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# ==================== CORS CONFIGURATION ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REQUEST LOGGER MIDDLEWARE ====================

@app.middleware("http")
async def log_middleware(request, call_next):
    """Apply request logging to all requests"""
    return await log_requests(request, call_next)

# ==================== EXCEPTION HANDLERS ====================

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DuplicateKeyError, duplicate_key_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ==================== API ROUTES ====================

# Include parking logs router
app.include_router(parking_logs_router)

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "environment": NODE_ENV,
        "service": "Parking Management API"
    }

# ==================== STATIC FILES ====================

# Serve frontend build (dist/)
dist_path = os.path.join(os.path.dirname(__file__), "..", "dist")
if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")
    info("Serving frontend from dist/")
else:
    info("Frontend build not found at dist/, skipping static files")

# Serve public files (images)
public_path = os.path.join(os.path.dirname(__file__), "..", "public")
if os.path.exists(public_path):
    app.mount("/public", StaticFiles(directory=public_path), name="public")
    info("Serving public files from public/")
else:
    info("Public directory not found, skipping static files")
