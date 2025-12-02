"""
Pydantic models for Parking Log
Equivalent to: model/parkingLog.js (Mongoose schema)
"""
from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

class PyObjectId(str):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

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
