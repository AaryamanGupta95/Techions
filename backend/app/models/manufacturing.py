from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.vehicle import PyObjectId


class FailurePattern(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    pattern_id: str = Field(..., unique=True, description="Unique pattern identifier")
    failure_type: str = Field(..., description="Type of failure")
    component: str = Field(..., description="Component name")
    manufacturer: str = Field(..., description="Manufacturer (Hero/Mahindra)")
    model: str = Field(..., description="Vehicle model")
    error_codes: List[str] = Field(default_factory=list, description="Associated error codes")
    occurrence_count: int = Field(default=1, ge=0, description="Number of occurrences")
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    severity: str = Field(..., description="low, medium, high, critical")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class RCACAPAAction(BaseModel):
    action_type: str = Field(..., description="preventive, corrective, improvement")
    description: str = Field(..., description="Action description")
    priority: str = Field(..., description="low, medium, high")
    responsible_team: str = Field(..., description="Team responsible")
    due_date: Optional[datetime] = None
    status: str = Field(default="pending", description="pending, in_progress, completed")


class RCACAPAInsight(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    insight_id: str = Field(..., unique=True, description="Unique insight identifier")
    failure_pattern_id: str = Field(..., description="Associated failure pattern ID")
    manufacturer: str = Field(default="Unknown", description="Manufacturer (Hero/Mahindra)")
    title: str = Field(..., description="Insight title")
    
    # RCA (Root Cause Analysis)
    root_causes: List[str] = Field(default_factory=list, description="Identified root causes")
    contributing_factors: List[str] = Field(default_factory=list, description="Contributing factors")
    analysis_summary: str = Field(..., description="Analysis summary")
    
    # CAPA (Corrective and Preventive Actions)
    corrective_actions: List[RCACAPAAction] = Field(default_factory=list)
    preventive_actions: List[RCACAPAAction] = Field(default_factory=list)
    
    # Metadata
    affected_vehicles_count: int = Field(default=0, ge=0)
    estimated_impact: str = Field(..., description="Impact assessment")
    recommendation_priority: str = Field(..., description="low, medium, high, critical")
    manufacturing_team_notified: bool = Field(default=False)
    status: str = Field(default="new", description="new, reviewed, actioned, resolved")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

