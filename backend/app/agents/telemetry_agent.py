import random
from datetime import datetime, timedelta
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.vehicle import VehicleTelemetry

class TelemetryAgent(BaseAgent):
    """Ingests and processes simulated vehicle telemetry data"""
    
    def __init__(self):
        super().__init__("TelemetryAgent")
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        vin = input_data.get("vin")
        if not vin:
            # Simulate data for a random vehicle if VIN not provided
            db = get_database()
            vehicles = await db.vehicles.find({}).limit(1).to_list(1)
            if vehicles:
                vin = vehicles[0]["vin"]
            else:
                vin = f"SIM_{random.randint(1000, 9999)}"
        
        # Generate simulated telemetry data
        telemetry_data = self._generate_telemetry(vin)
        
        # Store in database
        db = get_database()
        telemetry_doc = VehicleTelemetry(**telemetry_data)
        await db.vehicle_telemetry.insert_one(telemetry_doc.dict(by_alias=True))
        
        return {
            "status": "success",
            "telemetry": telemetry_data,
            "message": "Telemetry data ingested successfully"
        }
    
    def _generate_telemetry(self, vin: str) -> Dict[str, Any]:
        """Generate simulated vehicle telemetry data"""
        # Simulate realistic vehicle data with occasional anomalies
        base_temp = 85.0
        base_pressure = 45.0
        base_vibration = 2.5
        base_voltage = 12.6
        base_speed = random.uniform(0, 100)
        
        # Introduce occasional anomalies (10% chance)
        anomaly = random.random() < 0.1
        
        engine_temp = base_temp + random.uniform(-5, 10)
        if anomaly:
            engine_temp = random.uniform(95, 130)  # Overheating
        
        oil_pressure = base_pressure + random.uniform(-5, 5)
        if anomaly:
            oil_pressure = random.uniform(10, 25)  # Low pressure
        
        vibration = base_vibration + random.uniform(-0.5, 0.5)
        if anomaly:
            vibration = random.uniform(5.0, 10.0)  # High vibration
        
        voltage = base_voltage + random.uniform(-0.5, 0.5)
        if anomaly:
            voltage = random.uniform(10.0, 11.5)  # Low voltage
        
        # Calculate health score (0-100)
        health_score = 100.0
        if engine_temp > 100:
            health_score -= (engine_temp - 100) * 2
        if oil_pressure < 30:
            health_score -= (30 - oil_pressure) * 1.5
        if vibration > 4.0:
            health_score -= (vibration - 4.0) * 5
        if voltage < 12.0:
            health_score -= (12.0 - voltage) * 3
        
        health_score = max(0, min(100, health_score))
        
        # Error codes (OBD-II style)
        error_codes = []
        if engine_temp > 105:
            error_codes.append("P0217")  # Engine overheat
        if oil_pressure < 25:
            error_codes.append("P0521")  # Oil pressure low
        if vibration > 6.0:
            error_codes.append("P0300")  # Random misfire
        
        return {
            "vin": vin,
            "timestamp": datetime.utcnow(),
            "engine_temperature": round(engine_temp, 2),
            "oil_pressure": round(oil_pressure, 2),
            "vibration_level": round(vibration, 2),
            "battery_voltage": round(voltage, 2),
            "speed": round(base_speed, 2),
            "mileage": random.uniform(1000, 100000),
            "error_codes": error_codes,
            "health_score": round(health_score, 2),
            "anomaly_detected": anomaly,
            "prediction_risk": 0.0  # Will be calculated by Failure Prediction Agent
        }

