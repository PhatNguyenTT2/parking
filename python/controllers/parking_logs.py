"""
Parking Logs API Routes
Equivalent to: controller/parkingLogs.js
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from models.parking_log import ParkingLogCreate, ParkingLogExit
from utils.database import get_database
from utils.logger import info, error
from bson import ObjectId

# Create router with prefix
router = APIRouter(prefix="/api/parking/logs", tags=["Parking Logs"])

# ==================== GET ALL LOGS ====================

@router.get("")
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

@router.get("/current")
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

@router.get("/{log_id}")
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

@router.post("", status_code=status.HTTP_201_CREATED)
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

@router.put("/exit")
async def process_exit(exit_data: ParkingLogExit):
    """
    Validate vehicle exit (DO NOT update database - only validate)
    
    Args:
        exit_data: ParkingLogExit model
        
    Returns:
        dict: {success: bool, data: vehicle_log} - for confirmation
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
        
        # DO NOT UPDATE DATABASE - Just return vehicle data for confirmation
        # Convert ObjectId to string
        log["id"] = str(log.pop("_id"))
        
        # Add exit image to response (not saved to DB yet)
        log["exitImage"] = exit_data.exitImage
        
        info(f"Validated exit for card {exit_data.cardId} - waiting for confirmation")
        
        return {
            "success": True,
            "data": log,
            "message": "Exit validation successful - please confirm to delete log"
        }
    except HTTPException:
        raise
    except Exception as e:
        error("Error validating exit:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DELETE LOG ====================

@router.delete("/{log_id}")
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
