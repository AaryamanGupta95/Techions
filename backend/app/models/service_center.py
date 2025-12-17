from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.vehicle import PyObjectId


class ServiceCenter(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    center_id: str = Field(..., unique=True, description="Unique service center identifier")
    name: str = Field(..., description="Service center name")
    address: str = Field(..., description="Service center address")
    phone: str = Field(..., description="Contact phone")
    email: str = Field(..., description="Contact email")
    manufacturer: str = Field(default="Hero", description="Manufacturer (Hero/Mahindra)")
    capacity: int = Field(..., ge=1, description="Maximum concurrent service capacity")
    current_load: int = Field(default=0, ge=0, description="Current number of vehicles in service")
    operating_hours: dict = Field(default_factory=lambda: {
        "monday": {"open": "09:00", "close": "18:00"},
        "tuesday": {"open": "09:00", "close": "18:00"},
        "wednesday": {"open": "09:00", "close": "18:00"},
        "thursday": {"open": "09:00", "close": "18:00"},
        "friday": {"open": "09:00", "close": "18:00"},
        "saturday": {"open": "09:00", "close": "14:00"},
        "sunday": {"open": "closed", "close": "closed"},
    })
    status: str = Field(default="active", description="active, inactive")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class Technician(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    technician_id: str = Field(..., unique=True, description="Unique technician identifier")
    name: str = Field(..., description="Technician name")
    age: int = Field(..., ge=18, le=70, description="Technician age")
    contact_number: str = Field(..., description="Contact phone number")
    service_center_id: str = Field(..., description="Service center ID")
    specialization: list[str] = Field(default_factory=list, description="Specializations")
    current_assignments: int = Field(default=0, ge=0, description="Current number of assigned services")
    max_capacity: int = Field(default=3, ge=1, description="Maximum concurrent assignments")
    status: str = Field(default="available", description="available, busy, off_duty")
    vehicles_repaired_last_month: int = Field(default=0, ge=0, description="Number of vehicles repaired in last month")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

