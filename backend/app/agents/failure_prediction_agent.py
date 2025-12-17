from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import IsolationForest
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.vehicle import VehicleTelemetry

class FailurePredictionAgent(BaseAgent):
    """Predicts potential vehicle failures using ML models"""
    
    def __init__(self):
        super().__init__("FailurePredictionAgent")
        # Initialize Isolation Forest for anomaly detection
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_fitted = False
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        vin = input_data.get("vin")
        if not vin:
            return {"status": "error", "message": "VIN required"}
        
        db = get_database()
        
        # Get recent telemetry data for this vehicle
        recent_telemetry = await db.vehicle_telemetry.find(
            {"vin": vin}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        if not recent_telemetry:
            return {"status": "error", "message": "No telemetry data found"}
        
        # Get latest telemetry
        latest = recent_telemetry[0]
        
        # Calculate failure risk
        risk_score = self._calculate_risk_score(latest)
        
        # Update telemetry with prediction risk
        await db.vehicle_telemetry.update_one(
            {"_id": latest["_id"]},
            {"$set": {"prediction_risk": risk_score}}
        )
        
        # Determine if action is needed
        needs_action = risk_score > 0.6
        
        # Determine predicted failure window
        if risk_score > 0.7:
            failure_window = "3-5 days"
        elif risk_score > 0.5:
            failure_window = "7-14 days"
        elif risk_score > 0.3:
            failure_window = "30-60 days"
        else:
            failure_window = "No immediate risk detected"
        
        return {
            "status": "success",
            "vin": vin,
            "risk_score": risk_score,
            "health_score": latest.get("health_score", 100),
            "needs_action": needs_action,
            "recommendation": self._get_recommendation(risk_score, latest),
            "predicted_failure_window": failure_window
        }
    
    def _calculate_risk_score(self, telemetry: Dict[str, Any]) -> float:
        """Calculate failure risk score (0-1) based on telemetry data"""
        risk_factors = []
        
        # Health score is the primary indicator - inverse relationship
        health = telemetry.get("health_score", 100)
        if health is not None:
            # Convert health score (0-100) to risk score (0-1)
            # Lower health = higher risk
            health_risk = (100 - health) / 100.0
            # Weight health score heavily (40% of total risk)
            risk_factors.append(health_risk * 0.4)
        
        # Engine temperature risk
        temp = telemetry.get("engine_temperature", 85)
        if temp > 105:
            risk_factors.append(0.25)
        elif temp > 95:
            risk_factors.append(0.15)
        elif temp < 70:
            risk_factors.append(0.1)  # Too cold can also indicate issues
        
        # Oil pressure risk
        pressure = telemetry.get("oil_pressure", 45)
        if pressure < 25:
            risk_factors.append(0.3)
        elif pressure < 35:
            risk_factors.append(0.2)
        elif pressure > 60:
            risk_factors.append(0.1)  # Too high pressure
        
        # Vibration risk
        vibration = telemetry.get("vibration_level", 0.5)
        if vibration > 1.0:  # Adjusted threshold for realistic values
            risk_factors.append(0.2)
        elif vibration > 0.8:
            risk_factors.append(0.1)
        
        # Battery risk
        voltage = telemetry.get("battery_voltage", 12.6)
        if voltage < 11.5:
            risk_factors.append(0.25)
        elif voltage < 12.0:
            risk_factors.append(0.15)
        elif voltage > 14.5:
            risk_factors.append(0.1)  # Overcharging
        
        # Error codes risk
        error_codes = telemetry.get("error_codes", [])
        if isinstance(error_codes, list):
            risk_factors.append(min(0.3, len(error_codes) * 0.15))
        
        # Anomaly detection flag
        if telemetry.get("anomaly_detected", False):
            risk_factors.append(0.2)
        
        # Combine risk factors - use weighted sum with cap at 1.0
        # Ensure minimum risk if health is low
        total_risk = min(1.0, sum(risk_factors))
        
        # If health is very low (< 60), ensure minimum risk of 0.4
        if health is not None and health < 60:
            total_risk = max(0.4, total_risk)
        
        # If health is extremely low (< 40), ensure minimum risk of 0.7
        if health is not None and health < 40:
            total_risk = max(0.7, total_risk)
        
        return round(total_risk, 3)
    
    def _get_recommendation(self, risk_score: float, telemetry: Dict[str, Any]) -> str:
        """Get recommendation based on risk score"""
        if risk_score > 0.7:
            return "High risk detected. Immediate service recommended within 3-5 days."
        elif risk_score > 0.5:
            return "Moderate risk detected. Schedule service within 7-10 days."
        elif risk_score > 0.3:
            return "Low risk detected. Schedule preventive maintenance within 14-21 days."
        else:
            return "Vehicle is in good condition. Regular maintenance recommended."

