from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler
    ) -> core_schema.CoreSchema:
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
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid ObjectId")
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class Vehicle(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    vin: str = Field(..., description="Vehicle Identification Number")
    vehicle_name: str = Field(..., description="Vehicle name/nickname given by customer")
    plate_number: str = Field(..., description="Vehicle license plate number")
    model: str = Field(..., description="Vehicle model")
    manufacturer: str = Field(..., description="Manufacturer (Hero/Mahindra)")
    year: int = Field(..., description="Manufacturing year")
    customer_id: str = Field(..., description="Customer ID")
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active", description="active, inactive, service_required")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class VehicleTelemetry(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    vin: str = Field(..., description="Vehicle Identification Number")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Sensor data
    engine_temperature: float = Field(..., ge=0, le=150, description="Engine temperature in Celsius")
    oil_pressure: float = Field(..., ge=0, description="Oil pressure in PSI")
    vibration_level: float = Field(..., ge=0, description="Vibration level")
    battery_voltage: float = Field(..., ge=0, description="Battery voltage")
    speed: float = Field(..., ge=0, description="Vehicle speed in km/h")
    mileage: float = Field(..., ge=0, description="Total mileage in km")
    
    # Error codes
    error_codes: list[str] = Field(default_factory=list, description="Diagnostic error codes")
    
    # Calculated fields
    health_score: float = Field(default=100.0, ge=0, le=100, description="Overall vehicle health score")
    anomaly_detected: bool = Field(default=False, description="Whether anomaly was detected")
    prediction_risk: float = Field(default=0.0, ge=0, le=1.0, description="Failure prediction risk score")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

