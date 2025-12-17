from typing import Dict, Any
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.customer import Feedback
import uuid

class FeedbackAgent(BaseAgent):
    """Tracks service completion and customer feedback"""
    
    def __init__(self):
        super().__init__("FeedbackAgent")
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "collect_feedback")
        
        if action == "collect_feedback":
            return await self._collect_feedback(input_data)
        elif action == "get_feedback_summary":
            return await self._get_feedback_summary(input_data)
        else:
            return {"status": "error", "message": "Unknown action"}
    
    async def _collect_feedback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect customer feedback after service"""
        appointment_id = input_data.get("appointment_id")
        customer_id = input_data.get("customer_id")
        vin = input_data.get("vin")
        rating = input_data.get("rating", 5)
        comments = input_data.get("comments", "")
        service_satisfaction = input_data.get("service_satisfaction", "satisfied")
        issues_resolved = input_data.get("issues_resolved", True)
        
        db = get_database()
        
        # Create feedback record
        feedback_id = f"FB_{uuid.uuid4().hex[:8].upper()}"
        feedback = Feedback(
            feedback_id=feedback_id,
            appointment_id=appointment_id,
            customer_id=customer_id,
            vin=vin,
            rating=rating,
            comments=comments,
            service_satisfaction=service_satisfaction,
            issues_resolved=issues_resolved
        )
        
        await db.feedbacks.insert_one(feedback.dict(by_alias=True))
        
        # Update appointment status and loads ONLY if not already completed
        appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
        if appointment and appointment.get("status") != "completed":
            await db.service_appointments.update_one(
                {"appointment_id": appointment_id},
                {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
            )
            
            # Update service center load
            await db.service_centers.update_one(
                {"center_id": appointment["service_center_id"]},
                {"$inc": {"current_load": -1}}
            )
            
            # Update technician assignments
            if appointment.get("technician_id"):
                await db.technicians.update_one(
                    {"technician_id": appointment["technician_id"]},
                    {"$inc": {"current_assignments": -1}}
                )
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "Feedback collected successfully"
        }
    
    async def _get_feedback_summary(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get feedback summary for analysis"""
        db = get_database()
        vin = input_data.get("vin")
        service_center_id = input_data.get("service_center_id")
        
        query = {}
        if vin:
            query["vin"] = vin
        if service_center_id:
            # Get appointments for this service center
            appointments = await db.service_appointments.find(
                {"service_center_id": service_center_id}
            ).to_list(1000)
            appointment_ids = [apt["appointment_id"] for apt in appointments]
            query["appointment_id"] = {"$in": appointment_ids}
        
        feedbacks = await db.feedbacks.find(query).to_list(1000)
        
        if not feedbacks:
            return {"status": "success", "summary": {}, "count": 0}
        
        total_rating = sum(f.get("rating", 0) for f in feedbacks)
        avg_rating = total_rating / len(feedbacks)
        
        resolved_count = sum(1 for f in feedbacks if f.get("issues_resolved", False))
        resolution_rate = resolved_count / len(feedbacks) * 100
        
        satisfaction_counts = {}
        for f in feedbacks:
            sat = f.get("service_satisfaction", "unknown")
            satisfaction_counts[sat] = satisfaction_counts.get(sat, 0) + 1
        
        return {
            "status": "success",
            "summary": {
                "total_feedbacks": len(feedbacks),
                "average_rating": round(avg_rating, 2),
                "resolution_rate": round(resolution_rate, 2),
                "satisfaction_distribution": satisfaction_counts
            },
            "count": len(feedbacks)
        }

