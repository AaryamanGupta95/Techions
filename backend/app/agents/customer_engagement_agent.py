from typing import Dict, Any
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.core.database import get_database

class CustomerEngagementAgent(BaseAgent):
    """Handles customer communication and engagement"""
    
    def __init__(self):
        super().__init__("CustomerEngagementAgent")
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "send_alert")
        vin = input_data.get("vin")
        customer_id = input_data.get("customer_id")
        risk_score = input_data.get("risk_score", 0.0)
        message_type = input_data.get("message_type", "prediction_alert")
        
        if action == "send_alert":
            return await self._send_alert(vin, customer_id, risk_score, message_type)
        elif action == "get_chat_response":
            return await self._handle_chat(input_data.get("message", ""), customer_id, vin)
        else:
            return {"status": "error", "message": "Unknown action"}
    
    async def _send_alert(self, vin: str, customer_id: str, risk_score: float, message_type: str) -> Dict[str, Any]:
        """Send alert to customer"""
        db = get_database()
        
        # Get customer info
        customer = await db.customers.find_one({"customer_id": customer_id})
        if not customer:
            return {"status": "error", "message": "Customer not found"}
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin})
        if not vehicle:
            return {"vehicle": None}
        
        # Generate alert message based on risk
        message = self._generate_alert_message(risk_score, vehicle, message_type)
        
        # Store notification
        notification = {
            "customer_id": customer_id,
            "vin": vin,
            "message": message,
            "message_type": message_type,
            "risk_score": risk_score,
            "timestamp": datetime.utcnow(),
            "read": False
        }
        await db.notifications.insert_one(notification)
        
        return {
            "status": "success",
            "customer_id": customer_id,
            "customer_name": customer.get("name"),
            "message": message,
            "message_type": message_type,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    def _generate_alert_message(self, risk_score: float, vehicle: Dict[str, Any], message_type: str) -> str:
        """Generate alert message based on risk score"""
        model = vehicle.get("model", "vehicle")
        
        if risk_score > 0.7:
            return f"🚨 URGENT: Your {model} requires immediate attention. High failure risk detected. Please schedule service immediately or call our emergency line."
        elif risk_score > 0.5:
            return f"⚠️ ALERT: Your {model} shows elevated risk indicators. We recommend scheduling service within 7 days to prevent potential breakdowns."
        elif risk_score > 0.3:
            return f"ℹ️ NOTICE: Your {model} has some risk indicators. We suggest scheduling a preventive maintenance check soon."
        else:
            return f"✅ Your {model} is operating normally. Continue regular maintenance as scheduled."
    
    async def _handle_chat(self, message: str, customer_id: str, vin: str) -> Dict[str, Any]:
        """Handle customer chat message with enhanced responses"""
        db = get_database()
        message_lower = message.lower().strip()
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin}) if vin else None
        vehicle_name = vehicle.get("vehicle_name") if vehicle else "your vehicle"
        vehicle_model = vehicle.get("model") if vehicle else "vehicle"
        
        # Get latest telemetry and prediction
        latest_telemetry = None
        if vin:
            latest_telemetry = await db.vehicle_telemetry.find_one(
                {"vin": vin},
                sort=[("timestamp", -1)]
            )
        
        # Get active alerts for this vehicle
        active_alerts = []
        if vin:
            alerts = await db.notifications.find({
                "vin": vin,
                "read": False
            }).sort("timestamp", -1).limit(5).to_list(5)
            active_alerts = alerts
        
        # Enhanced rule-based responses
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            greeting = "Hello! I'm your vehicle assistant. "
            if active_alerts:
                alert_msg = active_alerts[0].get("message", "")
                response = f"{greeting}I have an important alert for you: {alert_msg} Would you like to schedule a service appointment?"
            else:
                response = f"{greeting}I'm here to help with {vehicle_name}. How can I assist you today?"
        
        elif any(word in message_lower for word in ["status", "health", "condition", "how is my vehicle", "vehicle status"]):
            if latest_telemetry:
                health = latest_telemetry.get("health_score", 100)
                risk = latest_telemetry.get("prediction_risk", 0)
                
                response = f"Your {vehicle_model} ({vehicle_name}) has a health score of {health:.1f}/100. "
                
                if health < 50:
                    response += f"⚠️ This is concerning. Your vehicle shows high risk indicators ({risk*100:.0f}% failure risk). "
                    response += "I strongly recommend scheduling service immediately. Would you like me to help you book an appointment?"
                elif health < 70:
                    response += f"⚠️ There are some risk indicators present ({risk*100:.0f}% failure risk). "
                    response += "I recommend scheduling preventive maintenance within 7-10 days. Would you like to book a service?"
                elif health < 80:
                    response += "The vehicle is in fair condition. Regular maintenance is recommended soon."
                else:
                    response += "✅ Everything looks good! Your vehicle is operating normally."
            else:
                response = f"I don't have recent telemetry data for {vehicle_name}. Please check back later or contact support."
        
        elif any(word in message_lower for word in ["alert", "warning", "issue", "problem", "risk"]):
            if active_alerts:
                alert = active_alerts[0]
                response = f"⚠️ Alert: {alert.get('message', 'There is an issue with your vehicle.')} "
                response += "Would you like to schedule a service appointment to address this?"
            elif latest_telemetry:
                risk = latest_telemetry.get("prediction_risk", 0)
                health = latest_telemetry.get("health_score", 100)
                if risk > 0.5 or health < 70:
                    response = f"We detected potential issues with {vehicle_name}. "
                    response += f"Health score: {health:.1f}/100, Risk: {risk*100:.0f}%. "
                    response += "Would you like to schedule a service appointment?"
                else:
                    response = f"Good news! {vehicle_name} is currently operating normally. No immediate alerts."
            else:
                response = "I don't have recent data. Please check the dashboard for alerts or contact support."
        
        elif any(word in message_lower for word in ["service", "appointment", "schedule", "book", "maintenance", "repair"]):
            if any(word in message_lower for word in ["yes", "sure", "okay", "ok", "please", "book"]):
                response = "Great! I can help you schedule a service appointment. "
                response += "Please click the 'Confirm Service Booking' button in the alerts section above, "
                response += "or I can guide you through the process. Which service center would you prefer?"
            else:
                response = "I can help you schedule a service appointment for your vehicle. "
                if active_alerts:
                    response += "I see you have active alerts. Would you like to book a service now? "
                response += "You can click 'Confirm Service Booking' in the alerts section, or tell me if you'd like to proceed."
        
        elif any(word in message_lower for word in ["yes", "sure", "okay", "ok", "confirm", "proceed"]):
            if any(word in message_lower for word in ["service", "appointment", "book"]):
                response = "Perfect! Please click the 'Confirm Service Booking' button in the alerts section above. "
                response += "You'll be able to select a service center and preferred time slot."
            else:
                response = "Great! How can I help you further? You can ask about your vehicle's health, schedule service, or get information about maintenance."
        
        elif any(word in message_lower for word in ["no", "not now", "later", "cancel"]):
            response = "No problem! Feel free to reach out whenever you're ready to schedule service or if you have any questions about your vehicle."
        
        elif any(word in message_lower for word in ["temperature", "engine temp", "overheating"]):
            if latest_telemetry:
                temp = latest_telemetry.get("engine_temperature", 85)
                response = f"Your engine temperature is currently {temp:.1f}°C. "
                if temp > 100:
                    response += "⚠️ This is higher than normal. Your engine may be overheating. I recommend scheduling service soon."
                elif temp > 95:
                    response += "This is slightly elevated. Monitor it closely."
                else:
                    response += "This is within normal operating range."
            else:
                response = "I don't have current temperature data. Please check back later."
        
        elif any(word in message_lower for word in ["oil", "oil pressure", "pressure"]):
            if latest_telemetry:
                pressure = latest_telemetry.get("oil_pressure", 45)
                response = f"Your oil pressure is currently {pressure:.1f} PSI. "
                if pressure < 25:
                    response += "⚠️ This is critically low! Please schedule service immediately."
                elif pressure < 35:
                    response += "This is below optimal. I recommend checking your oil level and scheduling service."
                else:
                    response += "This is within normal range."
            else:
                response = "I don't have current oil pressure data. Please check back later."
        
        elif any(word in message_lower for word in ["battery", "voltage", "electrical"]):
            if latest_telemetry:
                voltage = latest_telemetry.get("battery_voltage", 12.6)
                response = f"Your battery voltage is currently {voltage:.2f}V. "
                if voltage < 11.5:
                    response += "⚠️ This is low. Your battery may need charging or replacement. Schedule service soon."
                elif voltage < 12.0:
                    response += "This is slightly low. Monitor it and consider checking your battery."
                else:
                    response += "This is within normal range."
            else:
                response = "I don't have current battery data. Please check back later."
        
        elif any(word in message_lower for word in ["what", "help", "information", "info"]):
            response = f"I can help you with information about {vehicle_name}. You can ask me about: "
            response += "• Vehicle health status and risk indicators\n"
            response += "• Engine temperature, oil pressure, battery voltage\n"
            response += "• Scheduling service appointments\n"
            response += "• Understanding alerts and warnings\n"
            response += "Just ask me anything about your vehicle!"
        
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
            response = "You're welcome! I'm here whenever you need help with your vehicle. Is there anything else I can assist you with?"
        
        else:
            # Default response with helpful suggestions
            response = f"I understand you're asking about {vehicle_name}. "
            response += "I can help you with vehicle health status, scheduling service, or answering questions about maintenance. "
            response += "Could you please rephrase your question or ask about: health status, service booking, or vehicle alerts?"
        
        # Store chat history
        chat_entry = {
            "customer_id": customer_id,
            "vin": vin,
            "user_message": message,
            "bot_response": response,
            "timestamp": datetime.utcnow()
        }
        await db.chat_history.insert_one(chat_entry)
        
        return {
            "status": "success",
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }

