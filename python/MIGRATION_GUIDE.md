# HƯỚNG DẪN MIGRATION BACKEND: NODE.JS → PYTHON

**Dự án:** Hệ Thống Quản Lý Bãi Giữ Xe Máy  
**Ngày tạo:** December 2, 2025  
**Thời gian ước tính:** 2-4 giờ

---

## 📋 MỤC LỤC

1. [Tổng Quan Migration](#tổng-quan-migration)
2. [Chuẩn Bị](#chuẩn-bị)
3. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
4. [Các Bước Migration](#các-bước-migration)
5. [Testing & Validation](#testing--validation)
6. [Deployment](#deployment)
7. [Rollback Plan](#rollback-plan)

---

## 🎯 TỔNG QUAN MIGRATION

### Stack Hiện Tại (Node.js)
- **Runtime:** Node.js
- **Framework:** Express.js v5.1.0
- **Database:** MongoDB + Mongoose v8.11.0
- **Dependencies:** cors, dotenv, express, mongoose

### Stack Mới (Python)
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Database:** MongoDB + Motor (async driver)
- **Dependencies:** fastapi, uvicorn, motor, pydantic, python-dotenv

### Lý Do Migration
- ✅ Type safety với Pydantic
- ✅ Auto API documentation (Swagger/ReDoc)
- ✅ Performance tốt hơn (async/await native)
- ✅ Code sạch hơn, dễ maintain
- ✅ Validation tự động
- ✅ Sẵn sàng tích hợp AI/ML

---

## 🛠️ CHUẨN BỊ

### 1. Requirements
- ✅ Python 3.11+ đã cài đặt
- ✅ pip đã cài đặt
- ✅ MongoDB đang chạy
- ✅ Backend Node.js hiện tại đang hoạt động

### 2. Kiểm Tra Python
```powershell
# Kiểm tra Python version
python --version
# Output: Python 3.11.x hoặc cao hơn

# Kiểm tra pip
pip --version
```

### 3. Backup Database
```powershell
# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/parking" --out="backup/$(Get-Date -Format 'yyyy-MM-dd')"
```

### 4. Document Current API
```powershell
# Test tất cả endpoints hiện tại
# Lưu lại response format để so sánh sau này
```

**Current Endpoints:**
- `GET /api/parking/logs` - Lấy tất cả logs
- `GET /api/parking/logs/current` - Lấy xe đang trong bãi
- `GET /api/parking/logs/:id` - Lấy log theo ID
- `POST /api/parking/logs` - Tạo entry mới (xe vào)
- `PUT /api/parking/logs/exit` - Xử lý xe ra
- `DELETE /api/parking/logs/:id` - Xóa log

---

## 📂 CẤU TRÚC THƯ MỤC

### Cấu Trúc Mới (Python)
```
python/
├── main.py                    # Server entry point
├── app.py                     # FastAPI app setup
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (copy từ root)
│
├── controllers/
│   ├── __init__.py
│   └── parking_logs.py        # API routes & handlers
│
├── models/
│   ├── __init__.py
│   └── parking_log.py         # Pydantic models
│
├── utils/
│   ├── __init__.py
│   ├── config.py              # Configuration
│   ├── logger.py              # Logging
│   ├── middleware.py          # Middlewares
│   └── database.py            # MongoDB connection
│
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_parking_logs.py
│
└── docs/
    └── API.md                 # API documentation
```

---

## 🚀 CÁC BƯỚC MIGRATION

### BƯỚC 1: Setup Python Environment

```powershell
# Di chuyển vào thư mục python
cd e:\UIT\parking\python

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Verify activation (prompt sẽ có (venv))
# (venv) PS E:\UIT\parking\python>
```

---

### BƯỚC 2: Tạo `requirements.txt`

**File:** `python/requirements.txt`

```txt
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0

# Database
motor==3.6.0
pymongo==4.10.1

# Data Validation
pydantic==2.10.0
pydantic-settings==2.6.1

# Environment
python-dotenv==1.0.1

# Development
pytest==8.3.4
httpx==0.28.1
```

**Install:**
```powershell
pip install -r requirements.txt
```

---

### BƯỚC 3: Tạo Configuration

**File:** `python/utils/__init__.py`
```python
# Empty file to make utils a package
```

**File:** `python/utils/config.py`

```python
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
```

---

### BƯỚC 4: Tạo Logger

**File:** `python/utils/logger.py`

```python
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
```

---

### BƯỚC 5: Tạo Database Connection

**File:** `python/utils/database.py`

```python
"""
Database connection module
Handles MongoDB connection using Motor (async driver)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import MONGODB_URI
from utils.logger import info, error

# Global database client
client = None
db = None

async def connect_db():
    """Connect to MongoDB"""
    global client, db
    
    try:
        info('connecting to', MONGODB_URI)
        client = AsyncIOMotorClient(MONGODB_URI)
        
        # Get database from URI or use default
        db = client.get_default_database()
        
        # Test connection
        await client.admin.command('ping')
        info('connected to MongoDB')
        
    except Exception as e:
        error('error connecting to MongoDB:', str(e))
        raise

async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        info('MongoDB connection closed')

def get_database():
    """Get database instance"""
    return db

def get_collection(name: str):
    """Get collection by name"""
    return db[name]
```

---

### BƯỚC 6: Tạo Models

**File:** `python/models/__init__.py`
```python
# Empty file to make models a package
```

**File:** `python/models/parking_log.py`

```python
"""
Pydantic models for Parking Log
Equivalent to: model/parkingLog.js (Mongoose schema)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# ==================== REQUEST MODELS ====================

class ParkingLogCreate(BaseModel):
    """Model for creating new parking entry"""
    cardId: str = Field(..., min_length=1, description="Card ID (required)")
    licensePlate: str = Field(..., min_length=1, description="License plate (required)")
    entryImage: Optional[str] = Field(None, description="Entry image URL (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cardId": "CARD001",
                "licensePlate": "59A1-2345",
                "entryImage": "http://example.com/entry.jpg"
            }
        }

class ParkingLogExit(BaseModel):
    """Model for processing vehicle exit"""
    cardId: str = Field(..., min_length=1, description="Card ID (required)")
    exitLicensePlate: str = Field(..., min_length=1, description="License plate from exit recognition (required)")
    exitImage: Optional[str] = Field(None, description="Exit image URL (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cardId": "CARD001",
                "exitLicensePlate": "59A1-2345",
                "exitImage": "http://example.com/exit.jpg"
            }
        }

# ==================== RESPONSE MODELS ====================

class ParkingLogResponse(BaseModel):
    """Model for parking log response"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    cardId: str
    licensePlate: str
    entryTime: datetime
    exitTime: Optional[datetime] = None
    entryImage: Optional[str] = None
    exitImage: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ==================== DATABASE SCHEMA ====================
"""
MongoDB Collection: parkinglogs

Schema:
{
    _id: ObjectId,
    cardId: String (required),
    licensePlate: String (required),
    entryTime: Date (default: now),
    exitTime: Date (optional, null = still in parking),
    entryImage: String (optional),
    exitImage: String (optional)
}

Indexes:
- cardId: For fast lookup by card
- exitTime: For querying current parking (where exitTime is null)
"""
```

---

### BƯỚC 7: Tạo Middleware

**File:** `python/utils/middleware.py`

```python
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
    Handle validation errors
    Equivalent to: ValidationError handling in errorHandler
    """
    error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"message": str(exc.errors())}}
    )

async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    """
    Handle MongoDB duplicate key errors
    Equivalent to: MongoServerError E11000 handling in errorHandler
    """
    error(f"Duplicate key error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"message": "Duplicate entry - resource already exists"}}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    Fallback error handler
    """
    error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"message": "Internal server error"}}
    )
```

---

### BƯỚC 8: Tạo Controllers/Routes

**File:** `python/controllers/__init__.py`
```python
# Empty file to make controllers a package
```

**File:** `python/controllers/parking_logs.py`

```python
"""
Parking Logs API Routes
Equivalent to: controller/parkingLogs.js
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from models.parking_log import ParkingLogCreate, ParkingLogExit, ParkingLogResponse
from utils.database import get_database
from utils.logger import info, error
from bson import ObjectId

# Create router with prefix
router = APIRouter(prefix="/api/parking/logs", tags=["Parking Logs"])

# ==================== GET ALL LOGS ====================

@router.get("", response_model=dict)
async def get_all_logs():
    """
    Get all parking logs
    
    Returns:
        dict: {success: bool, data: {parkingLogs: list}}
    """
    db = get_database()
    
    try:
        # Get all parking logs, sorted by entry time (newest first)
        logs = await db.parkinglogs.find().sort("entryTime", -1).to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log["id"] = str(log.pop("_id"))
        
        return {
            "success": True,
            "data": {"parkingLogs": logs}
        }
    except Exception as e:
        error("Error fetching logs:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== GET CURRENT PARKING ====================

@router.get("/current", response_model=dict)
async def get_current_parking():
    """
    Get vehicles currently in parking (exitTime is null)
    
    Returns:
        dict: {success: bool, data: {parkingLogs: list}}
    """
    db = get_database()
    
    try:
        # Query for logs with no exit time
        logs = await db.parkinglogs.find(
            {"exitTime": None}
        ).sort("entryTime", -1).to_list(length=None)
        
        # Convert ObjectId to string
        for log in logs:
            log["id"] = str(log.pop("_id"))
        
        return {
            "success": True,
            "data": {"parkingLogs": logs}
        }
    except Exception as e:
        error("Error fetching current parking:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== GET LOG BY ID ====================

@router.get("/{log_id}", response_model=dict)
async def get_log_by_id(log_id: str):
    """
    Get parking log by ID
    
    Args:
        log_id: MongoDB ObjectId as string
        
    Returns:
        dict: {success: bool, data: log_object}
    """
    db = get_database()
    
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(log_id):
            raise HTTPException(
                status_code=400, 
                detail="Invalid ID format"
            )
        
        # Find log by ID
        log = await db.parkinglogs.find_one({"_id": ObjectId(log_id)})
        
        if not log:
            raise HTTPException(
                status_code=404, 
                detail="Log not found"
            )
        
        # Convert ObjectId to string
        log["id"] = str(log.pop("_id"))
        
        return {
            "success": True,
            "data": log
        }
    except HTTPException:
        raise
    except Exception as e:
        error("Error fetching log:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CREATE NEW ENTRY ====================

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_log(log_data: ParkingLogCreate):
    """
    Create new parking entry (vehicle enters)
    
    Args:
        log_data: ParkingLogCreate model
        
    Returns:
        dict: {success: bool, data: created_log}
    """
    db = get_database()
    
    try:
        # Check if cardId already has active entry (no exit time)
        existing = await db.parkinglogs.find_one({
            "cardId": log_data.cardId,
            "exitTime": None
        })
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Card {log_data.cardId} already has an active entry"
            )
        
        # Create new log document
        new_log = {
            "cardId": log_data.cardId,
            "licensePlate": log_data.licensePlate.upper(),
            "entryTime": datetime.now(),
            "exitTime": None,
            "entryImage": log_data.entryImage,
            "exitImage": None
        }
        
        # Insert into database
        result = await db.parkinglogs.insert_one(new_log)
        
        # Fetch the created document
        created_log = await db.parkinglogs.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        created_log["id"] = str(created_log.pop("_id"))
        
        info(f"Created new parking log for card {log_data.cardId}")
        
        return {
            "success": True,
            "data": created_log
        }
    except HTTPException:
        raise
    except Exception as e:
        error("Error creating log:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROCESS EXIT ====================

@router.put("/exit", response_model=dict)
async def process_exit(exit_data: ParkingLogExit):
    """
    Process vehicle exit
    
    Args:
        exit_data: ParkingLogExit model
        
    Returns:
        dict: {success: bool, data: updated_log}
    """
    db = get_database()
    
    try:
        # Find active entry with matching cardId
        log = await db.parkinglogs.find_one({
            "cardId": exit_data.cardId,
            "exitTime": None
        })
        
        if not log:
            raise HTTPException(
                status_code=404,
                detail=f"No active entry found for card {exit_data.cardId}"
            )
        
        # Verify license plate matches
        if log["licensePlate"].upper() != exit_data.exitLicensePlate.upper():
            raise HTTPException(
                status_code=400,
                detail=f"License plate mismatch. Expected: {log['licensePlate']}, Got: {exit_data.exitLicensePlate}"
            )
        
        # Update with exit information
        exit_time = datetime.now()
        
        await db.parkinglogs.update_one(
            {"_id": log["_id"]},
            {
                "$set": {
                    "exitTime": exit_time,
                    "exitImage": exit_data.exitImage
                }
            }
        )
        
        # Fetch updated log
        updated_log = await db.parkinglogs.find_one({"_id": log["_id"]})
        updated_log["id"] = str(updated_log.pop("_id"))
        
        info(f"Processed exit for card {exit_data.cardId}")
        
        return {
            "success": True,
            "data": updated_log,
            "message": "Exit processed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        error("Error processing exit:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DELETE LOG ====================

@router.delete("/{log_id}", response_model=dict)
async def delete_log(log_id: str):
    """
    Delete parking log (for testing/admin purposes)
    
    Args:
        log_id: MongoDB ObjectId as string
        
    Returns:
        dict: {success: bool, message: str}
    """
    db = get_database()
    
    try:
        # Validate ObjectId format
        if not ObjectId.is_valid(log_id):
            raise HTTPException(
                status_code=400, 
                detail="Invalid ID format"
            )
        
        # Delete log
        result = await db.parkinglogs.delete_one({"_id": ObjectId(log_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, 
                detail="Log not found"
            )
        
        info(f"Deleted log {log_id}")
        
        return {
            "success": True,
            "message": f"Log {log_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        error("Error deleting log:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

---

### BƯỚC 9: Tạo Main App

**File:** `python/app.py`

```python
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
    Equivalent to: app.listen() and MongoDB connection in app.js
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
```

---

### BƯỚC 10: Tạo Server Entry Point

**File:** `python/main.py`

```python
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
```

---

### BƯỚC 11: Copy Environment Variables

```powershell
# Copy .env from root to python folder
Copy-Item ..\\.env .env
```

**Verify .env contains:**
```env
MONGODB_URI=mongodb://localhost:27017/parking
PORT=3001
NODE_ENV=development
```

---

### BƯỚC 12: Test Python Backend

```powershell
# Ensure virtual environment is activated
# (venv) PS E:\UIT\parking\python>

# Run server
python main.py
```

**Expected output:**
```
Config loaded: PORT=3001, ENV=development
connecting to mongodb://localhost:27017/parking
connected to MongoDB
Application started in development mode
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3001 (Press CTRL+C to quit)
```

---

## ✅ TESTING & VALIDATION

### 1. Test API Documentation

```powershell
# Open browser
Start-Process "http://localhost:3001/docs"         # Swagger UI
Start-Process "http://localhost:3001/redoc"        # ReDoc
```

### 2. Test Endpoints

**Test 1: Health Check**
```powershell
curl http://localhost:3001/health
# Expected: {"status":"ok","environment":"development","service":"Parking Management API"}
```

**Test 2: Get All Logs**
```powershell
curl http://localhost:3001/api/parking/logs
# Expected: {"success":true,"data":{"parkingLogs":[]}}
```

**Test 3: Create Entry**
```powershell
curl -X POST http://localhost:3001/api/parking/logs `
  -H "Content-Type: application/json" `
  -d '{\"cardId\":\"CARD001\",\"licensePlate\":\"59A1-2345\",\"entryImage\":\"http://example.com/entry.jpg\"}'
```

**Test 4: Get Current Parking**
```powershell
curl http://localhost:3001/api/parking/logs/current
# Should return the entry created in Test 3
```

**Test 5: Process Exit**
```powershell
curl -X PUT http://localhost:3001/api/parking/logs/exit `
  -H "Content-Type: application/json" `
  -d '{\"cardId\":\"CARD001\",\"exitLicensePlate\":\"59A1-2345\",\"exitImage\":\"http://example.com/exit.jpg\"}'
```

**Test 6: Verify Exit**
```powershell
curl http://localhost:3001/api/parking/logs/current
# Should return empty list (no vehicles in parking)
```

### 3. Test Frontend Integration

```powershell
# Stop Python server (Ctrl+C)
# Start Node.js server temporarily
cd ..
npm run dev

# Open frontend
Start-Process "http://localhost:3001"

# Test all features:
# - Add vehicle entry
# - View vehicle list
# - Process vehicle exit
# - Verify data updates
```

### 4. Test Error Handling

**Test Invalid ID:**
```powershell
curl http://localhost:3001/api/parking/logs/invalid-id
# Expected: 400 Bad Request - Invalid ID format
```

**Test Duplicate Entry:**
```powershell
# Create entry with CARD002
curl -X POST http://localhost:3001/api/parking/logs `
  -H "Content-Type: application/json" `
  -d '{\"cardId\":\"CARD002\",\"licensePlate\":\"59B1-6789\"}'

# Try to create again with same cardId
curl -X POST http://localhost:3001/api/parking/logs `
  -H "Content-Type: application/json" `
  -d '{\"cardId\":\"CARD002\",\"licensePlate\":\"59C1-1111\"}'
# Expected: 400 Bad Request - Card already has active entry
```

**Test License Plate Mismatch:**
```powershell
curl -X PUT http://localhost:3001/api/parking/logs/exit `
  -H "Content-Type: application/json" `
  -d '{\"cardId\":\"CARD002\",\"exitLicensePlate\":\"WRONG-PLATE\"}'
# Expected: 400 Bad Request - License plate mismatch
```

---

## 📊 VALIDATION CHECKLIST

- [ ] Python server starts without errors
- [ ] MongoDB connection successful
- [ ] All endpoints return correct response format
- [ ] API documentation accessible at `/docs`
- [ ] Frontend can connect to Python backend
- [ ] CRUD operations work correctly
- [ ] Error handling works as expected
- [ ] Static files (images) served correctly
- [ ] CORS works for frontend requests
- [ ] Logging output is clear and helpful

---

## 🚢 DEPLOYMENT

### Option 1: Replace Node.js Backend

```powershell
# 1. Stop Node.js server

# 2. Update package.json scripts (optional)
# Add Python start script:
# "start:python": "cd python && python main.py"

# 3. Update frontend .env to point to Python backend
# (No change needed if using same port 3001)

# 4. Start Python server
cd python
.\venv\Scripts\activate
python main.py
```

### Option 2: Run Both (Different Ports)

```powershell
# Node.js on port 3001
npm run dev

# Python on port 3002
cd python
$env:PORT=3002
python main.py
```

### Option 3: Production Deployment

```powershell
# 1. Install production WSGI server
pip install gunicorn

# 2. Create systemd service or use PM2
# 3. Use nginx as reverse proxy
# 4. Set NODE_ENV=production
```

---

## 🔄 ROLLBACK PLAN

### If Migration Fails:

**Step 1: Stop Python Server**
```powershell
# Press Ctrl+C in Python terminal
```

**Step 2: Restore Node.js Server**
```powershell
cd e:\UIT\parking
npm run dev
```

**Step 3: Restore Database (if needed)**
```powershell
# Restore from backup
mongorestore --uri="mongodb://localhost:27017/parking" backup/2025-12-02
```

**Step 4: Verify Node.js Working**
```powershell
curl http://localhost:3001/api/parking/logs
```

---

## 📝 NOTES & TIPS

### Performance Optimization
- Use connection pooling for MongoDB
- Enable caching for static files
- Use async/await consistently
- Add database indexes for frequently queried fields

### Security Best Practices
- Use environment variables for sensitive data
- Validate all user inputs (Pydantic does this automatically)
- Implement rate limiting
- Use HTTPS in production
- Restrict CORS origins in production

### Monitoring
- Add logging for all operations
- Monitor database queries
- Track API response times
- Set up error alerts

### Future Enhancements
- Add JWT authentication
- Implement WebSocket for real-time updates
- Add Redis caching
- Integrate ML models for license plate recognition
- Add unit tests with pytest

---

## 🎯 SUCCESS CRITERIA

Migration is successful when:
- ✅ All API endpoints work identically to Node.js version
- ✅ Frontend works without any changes
- ✅ Database operations are correct
- ✅ Error handling matches original behavior
- ✅ Response formats are identical
- ✅ Performance is equal or better
- ✅ Logging provides good debugging info
- ✅ Auto-generated API docs work

---

## 📞 TROUBLESHOOTING

### Issue: ModuleNotFoundError
**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: MongoDB Connection Failed
**Solution:**
```powershell
# Check MongoDB is running
mongosh

# Verify MONGODB_URI in .env
cat .env

# Test connection manually
python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017').server_info())"
```

### Issue: Port Already in Use
**Solution:**
```powershell
# Find process using port 3001
netstat -ano | findstr :3001

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
$env:PORT=3002
python main.py
```

### Issue: Import Errors
**Solution:**
```powershell
# Ensure __init__.py exists in all package directories
New-Item -ItemType File -Path "utils/__init__.py" -Force
New-Item -ItemType File -Path "models/__init__.py" -Force
New-Item -ItemType File -Path "controllers/__init__.py" -Force
```

---

## ✅ COMPLETION CHECKLIST

### Pre-Migration
- [ ] Python 3.11+ installed
- [ ] MongoDB running
- [ ] Node.js backend working
- [ ] Database backed up
- [ ] Current API endpoints documented

### Migration
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] All Python files created
- [ ] Configuration files set up
- [ ] Environment variables copied

### Testing
- [ ] Server starts successfully
- [ ] All endpoints tested
- [ ] Frontend integration verified
- [ ] Error handling validated
- [ ] Performance acceptable

### Deployment
- [ ] Production configuration ready
- [ ] Rollback plan prepared
- [ ] Monitoring set up
- [ ] Documentation updated

---

**GOOD LUCK WITH THE MIGRATION! 🚀**

**Estimated Time:** 2-4 hours  
**Difficulty:** Medium  
**Risk Level:** Low (easy rollback)
