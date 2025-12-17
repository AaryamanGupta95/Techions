from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from app.models.vehicle import PyObjectId


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., unique=True, description="Username")
    email: EmailStr = Field(..., unique=True, description="Email")
    hashed_password: str = Field(..., description="Hashed password")
    role: str = Field(default="customer", description="customer, service_center, manufacturing, admin")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class AgentLog(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    agent_name: str = Field(..., description="Agent name")
    action: str = Field(..., description="Action performed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_data: dict = Field(default_factory=dict, description="Input data")
    output_data: dict = Field(default_factory=dict, description="Output data")
    execution_time_ms: float = Field(default=0.0, description="Execution time in milliseconds")
    status: str = Field(default="success", description="success, error, warning")
    error_message: Optional[str] = None
    
    # UEBA fields
    anomaly_score: float = Field(default=0.0, ge=0, le=1.0, description="Anomaly detection score")
    is_anomaly: bool = Field(default=False, description="Whether this action is anomalous")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class SecurityEvent(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    event_id: str = Field(..., unique=True, description="Unique event identifier")
    event_type: str = Field(..., description="Event type (unauthorized_access, anomaly, policy_violation)")
    severity: str = Field(..., description="low, medium, high, critical")
    agent_name: Optional[str] = None
    user_id: Optional[str] = None
    description: str = Field(..., description="Event description")
    details: dict = Field(default_factory=dict, description="Event details")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

