from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from .vehicle import PyObjectId


class Customer(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    customer_id: str = Field(..., unique=True, description="Unique customer identifier")
    name: str = Field(..., description="Customer name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone number")
    address: str = Field(..., description="Customer address")
    vehicles: list[str] = Field(default_factory=list, description="List of VINs owned by customer")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class ServiceAppointment(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    appointment_id: str = Field(..., unique=True, description="Unique appointment identifier")
    customer_id: str = Field(..., description="Customer ID")
    vin: str = Field(..., description="Vehicle VIN")
    service_center_id: str = Field(..., description="Service center ID")
    technician_id: Optional[str] = Field(None, description="Assigned technician ID")
    scheduled_date: datetime = Field(..., description="Scheduled service date and time")
    service_type: str = Field(..., description="Type of service (predictive, emergency, regular)")
    status: str = Field(default="scheduled", description="scheduled, in_progress, completed, cancelled")
    description: str = Field(..., description="Service description")
    failure_risk: float = Field(default=0.0, ge=0, le=1.0, description="Predicted failure risk")
    priority: str = Field(default="medium", description="low, medium, high, critical")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class Feedback(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    feedback_id: str = Field(..., unique=True, description="Unique feedback identifier")
    appointment_id: str = Field(..., description="Service appointment ID")
    customer_id: str = Field(..., description="Customer ID")
    vin: str = Field(..., description="Vehicle VIN")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comments: str = Field(..., description="Customer comments")
    service_satisfaction: str = Field(..., description="Service satisfaction level")
    issues_resolved: bool = Field(..., description="Whether issues were resolved")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

