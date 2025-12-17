from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from app.agents.base_agent import BaseAgent
from app.core.database import get_database
from app.models.customer import ServiceAppointment
import uuid

class SmartSchedulingAgent(BaseAgent):
    """Smartly schedules service appointments based on availability"""
    
    def __init__(self):
        super().__init__("SmartSchedulingAgent")
    
    async def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "schedule")
        
        if action == "schedule":
            return await self._schedule_appointment(input_data)
        elif action == "reschedule":
            return await self._reschedule_appointment(input_data)
        elif action == "check_availability":
            return await self._check_availability(input_data)
        elif action == "cancel":
            return await self._cancel_appointment(input_data)
        else:
            return {"status": "error", "message": "Unknown action"}
    
    async def _schedule_appointment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a service appointment"""
        customer_id = input_data.get("customer_id")
        vin = input_data.get("vin")
        service_center_id = input_data.get("service_center_id")
        service_type = input_data.get("service_type", "predictive")
        priority = input_data.get("priority", "medium")
        risk_score = input_data.get("risk_score", 0.0)
        scheduled_date_str = input_data.get("scheduled_date")  # ISO format string from frontend
        
        # Determine priority based on risk
        if risk_score > 0.7:
            priority = "critical"
        elif risk_score > 0.5:
            priority = "high"
        
        # Find available service center and slot
        db = get_database()
        
        # Get service centers - use selected one if provided, otherwise find best
        # Always fetch from MongoDB for live data
        if service_center_id:
            # First try to find by center_id and status
            service_center = await db.service_centers.find_one({"center_id": service_center_id, "status": "active"})
            
            # If not found, try without status filter (might be inactive)
            if not service_center:
                service_center = await db.service_centers.find_one({"center_id": service_center_id})
                if service_center:
                    return {"status": "error", "message": f"Service center {service_center.get('name', service_center_id)} is currently inactive. Please select another center."}
            
            # If still not found, return error with available centers
            if not service_center:
                all_centers = await db.service_centers.find({"status": "active"}).to_list(100)
                available_ids = [c.get("center_id") for c in all_centers]
                return {
                    "status": "error", 
                    "message": f"Service center {service_center_id} not found. Available centers: {', '.join(available_ids) if available_ids else 'None'}"
                }
            
            # Check if center has available capacity
            capacity = service_center.get("capacity", 10)
            current_load = service_center.get("current_load", 0)
            available_slots = capacity - current_load
            
            if available_slots <= 0:
                return {
                    "status": "error", 
                    "message": f"Service center {service_center.get('name')} is at full capacity ({current_load}/{capacity}). Please select another center."
                }
            
            service_centers = [service_center]
        else:
            service_centers = await db.service_centers.find({"status": "active"}).to_list(100)
        
        if not service_centers:
            return {"status": "error", "message": "No service centers available"}
        
        # Parse scheduled date if provided, otherwise find best slot
        if scheduled_date_str:
            try:
                # Handle ISO format with or without timezone; normalize to UTC
                if 'T' in scheduled_date_str:
                    scheduled_date = datetime.fromisoformat(scheduled_date_str.replace('Z', '+00:00'))
                    if scheduled_date.tzinfo is None:
                        scheduled_date = scheduled_date.replace(tzinfo=timezone.utc)
                    else:
                        scheduled_date = scheduled_date.astimezone(timezone.utc)
                else:
                    # If only date provided, use default time (10:00 AM UTC)
                    scheduled_date = datetime.fromisoformat(scheduled_date_str)
                    scheduled_date = scheduled_date.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                
                # Ensure date is in the future (compare in UTC)
                now_utc = datetime.now(timezone.utc)
                if scheduled_date < now_utc:
                    return {"status": "error", "message": "Scheduled date must be in the future"}
                
                center_id = service_centers[0]["center_id"]
                # Get predicted issue to match with technician specialization
                predicted_issue = input_data.get("predicted_issue", "")
                issue_category = self._extract_issue_category(predicted_issue)
                
                # Find available technician matching specialization
                technician_id = None
                if issue_category:
                    # First try to find technician with matching specialization
                    matching_technicians = await db.technicians.find({
                        "service_center_id": center_id,
                        "status": "available",
                        "specialization": {"$in": [issue_category]},
                        "$expr": {"$lt": ["$current_assignments", "$max_capacity"]}
                    }).to_list(100)
                    
                    if matching_technicians:
                        # Select technician with least current assignments
                        matching_technicians.sort(key=lambda x: x.get("current_assignments", 0))
                        technician_id = matching_technicians[0]["technician_id"]
                
                # If no matching specialist found, find any available technician
                if not technician_id:
                    technicians = await db.technicians.find({
                        "service_center_id": center_id,
                        "status": "available",
                        "$expr": {"$lt": ["$current_assignments", "$max_capacity"]}
                    }).sort("current_assignments", 1).limit(1).to_list(1)
                    
                    if technicians:
                        technician_id = technicians[0]["technician_id"]
                
                # Update technician assignments
                if technician_id:
                    await db.technicians.update_one(
                        {"technician_id": technician_id},
                        {"$inc": {"current_assignments": 1}}
                    )
                
                description = f"{service_type.capitalize()} service for vehicle"
            except Exception as e:
                return {"status": "error", "message": f"Invalid date format: {str(e)}"}
        else:
            # Find best available slot if no date provided
            appointment_details = await self._find_best_slot(
                service_centers, priority, service_type, input_data.get("predicted_issue", "")
            )
            if not appointment_details:
                return {"status": "error", "message": "No available slots"}
            scheduled_date = appointment_details["scheduled_date"]
            technician_id = appointment_details.get("technician_id")
            center_id = appointment_details["center_id"]
            description = appointment_details.get("description", "Predictive maintenance service")
        
        # Create appointment
        appointment_id = f"APT_{uuid.uuid4().hex[:8].upper()}"
        appointment = ServiceAppointment(
            appointment_id=appointment_id,
            customer_id=customer_id,
            vin=vin,
            service_center_id=center_id,
            technician_id=technician_id,
            scheduled_date=scheduled_date,
            service_type=service_type,
            status="scheduled",
            description=description,
            failure_risk=risk_score,
            priority=priority
        )
        
        await db.service_appointments.insert_one(appointment.dict(by_alias=True))
        
        # Update service center load
        await db.service_centers.update_one(
            {"center_id": center_id},
            {"$inc": {"current_load": 1}}
        )
        
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "scheduled_date": scheduled_date.isoformat(),
            "service_center_id": center_id,
            "priority": priority,
            "message": "Appointment scheduled successfully"
        }
    
    async def _find_best_slot(self, service_centers: List[Dict], priority: str, service_type: str, predicted_issue: str = "") -> Dict[str, Any]:
        """Find the best available appointment slot"""
        db = get_database()
        
        # For critical/high priority, try to schedule within 1-2 days
        # For medium/low, schedule within 1 week
        if priority in ["critical", "high"]:
            start_date = datetime.now(timezone.utc) + timedelta(days=1)
            end_date = datetime.now(timezone.utc) + timedelta(days=2)
        else:
            start_date = datetime.now(timezone.utc) + timedelta(days=1)
            end_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        # Get predicted issue to match with technician specialization
        predicted_issue = input_data.get("predicted_issue", "")
        issue_category = self._extract_issue_category(predicted_issue)
        
        # Find service center with available capacity
        for center in service_centers:
            if center.get("current_load", 0) < center.get("capacity", 10):
                technician_id = None
                
                # First try to find technician with matching specialization
                if issue_category:
                    matching_technicians = await db.technicians.find({
                        "service_center_id": center["center_id"],
                        "status": "available",
                        "specialization": {"$in": [issue_category]},
                        "$expr": {"$lt": ["$current_assignments", "$max_capacity"]}
                    }).to_list(100)
                    
                    if matching_technicians:
                        # Select technician with least current assignments
                        matching_technicians.sort(key=lambda x: x.get("current_assignments", 0))
                        technician_id = matching_technicians[0]["technician_id"]
                
                # If no matching specialist found, find any available technician
                if not technician_id:
                    technicians = await db.technicians.find({
                        "service_center_id": center["center_id"],
                        "status": "available",
                        "$expr": {"$lt": ["$current_assignments", "$max_capacity"]}
                    }).sort("current_assignments", 1).limit(1).to_list(1)
                    
                    if technicians:
                        technician_id = technicians[0]["technician_id"]
                
                # Update technician assignments
                if technician_id:
                    await db.technicians.update_one(
                        {"technician_id": technician_id},
                        {"$inc": {"current_assignments": 1}}
                    )
                
                # Generate appointment time (business hours: 9 AM - 6 PM)
                scheduled_date = start_date.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                
                return {
                    "center_id": center["center_id"],
                    "technician_id": technician_id,
                    "scheduled_date": scheduled_date,
                    "description": f"{service_type.capitalize()} service for vehicle"
                }
        
        return None
    
    async def _check_availability(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check service center availability - Fetches live data from MongoDB"""
        db = get_database()
        service_centers = await db.service_centers.find({"status": "active"}).to_list(100)
        
        availability = []
        for center in service_centers:
            capacity = center.get("capacity", 10)
            current_load = center.get("current_load", 0)
            available_slots = max(0, capacity - current_load)  # Ensure non-negative
            
            availability.append({
                "center_id": center.get("center_id"),
                "name": center.get("name", ""),
                "address": center.get("address", ""),
                "phone": center.get("phone", ""),
                "email": center.get("email", ""),
                "manufacturer": center.get("manufacturer", "Hero"),
                "available_slots": available_slots,
                "capacity": capacity,
                "current_load": current_load
            })
        
        # Sort by available slots (most available first)
        availability.sort(key=lambda x: x["available_slots"], reverse=True)
        
        return {
            "status": "success",
            "availability": availability
        }
    
    async def _reschedule_appointment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reschedule an existing appointment - cancels old and creates new"""
        appointment_id = input_data.get("appointment_id")
        if not appointment_id:
            return {"status": "error", "message": "Appointment ID required for rescheduling"}
        
        db = get_database()
        
        # Find the old appointment
        old_appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
        if not old_appointment:
            return {"status": "error", "message": "Appointment not found"}
        
        # Cancel the old appointment
        await db.service_appointments.update_one(
            {"appointment_id": appointment_id},
            {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
        )
        
        # Decrease service center load for old appointment
        old_center_id = old_appointment.get("service_center_id")
        if old_center_id:
            await db.service_centers.update_one(
                {"center_id": old_center_id},
                {"$inc": {"current_load": -1}}
            )
        
        # Decrease technician assignments for old appointment
        old_technician_id = old_appointment.get("technician_id")
        if old_technician_id:
            await db.technicians.update_one(
                {"technician_id": old_technician_id},
                {"$inc": {"current_assignments": -1}}
            )
        
        # Create new appointment with updated details
        # Use the same customer_id and vin from old appointment
        new_appointment_data = {
            "customer_id": old_appointment.get("customer_id"),
            "vin": old_appointment.get("vin"),
            "service_center_id": input_data.get("service_center_id", old_center_id),
            "service_type": input_data.get("service_type", old_appointment.get("service_type", "predictive")),
            "priority": input_data.get("priority", old_appointment.get("priority", "medium")),
            "risk_score": input_data.get("risk_score", old_appointment.get("failure_risk", 0.0)),
            "scheduled_date": input_data.get("scheduled_date")
        }
        
        # Schedule new appointment
        result = await self._schedule_appointment(new_appointment_data)
        
        if result.get("status") == "success":
            result["old_appointment_id"] = appointment_id
            result["message"] = "Appointment rescheduled successfully"
        
        return result
    
    async def _cancel_appointment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel an existing appointment"""
        appointment_id = input_data.get("appointment_id")
        if not appointment_id:
            return {"status": "error", "message": "Appointment ID required"}
        
        db = get_database()
        
        # Find the appointment
        appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
        if not appointment:
            return {"status": "error", "message": "Appointment not found"}
        
        # Check if appointment can be cancelled (only scheduled appointments)
        if appointment.get("status") not in ["scheduled"]:
            return {"status": "error", "message": f"Cannot cancel appointment with status: {appointment.get('status')}"}
        
        # Cancel the appointment
        await db.service_appointments.update_one(
            {"appointment_id": appointment_id},
            {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
        )
        
        # Decrease service center load
        center_id = appointment.get("service_center_id")
        if center_id:
            await db.service_centers.update_one(
                {"center_id": center_id},
                {"$inc": {"current_load": -1}}
            )
        
        # Decrease technician assignments
        technician_id = appointment.get("technician_id")
        if technician_id:
            await db.technicians.update_one(
                {"technician_id": technician_id},
                {"$inc": {"current_assignments": -1}}
            )
        
        return {
            "status": "success",
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id
        }
    
    def _extract_issue_category(self, predicted_issue: str) -> str:
        """Extract issue category from predicted issue text to match with technician specialization"""
        if not predicted_issue:
            return None
        
        issue_lower = predicted_issue.lower()
        
        # Map predicted issues to technician specializations
        category_mapping = {
            "engine": ["engine", "overheating", "temperature", "cooling", "turbo", "oil", "lubrication"],
            "electrical": ["electrical", "battery", "voltage", "charging", "wiring", "circuit"],
            "brakes": ["brake", "braking", "brake pad", "brake disc"],
            "suspension": ["suspension", "shock", "strut", "alignment"],
            "transmission": ["transmission", "gearbox", "clutch", "shifting"],
            "ac": ["ac", "air conditioning", "cooling system", "heating", "climate"],
            "tires": ["tire", "tyre", "wheel", "tread"],
            "steering": ["steering", "alignment", "wheel alignment"]
        }
        
        # Check which category matches
        for category, keywords in category_mapping.items():
            if any(keyword in issue_lower for keyword in keywords):
                return category.capitalize()
        
        return None

