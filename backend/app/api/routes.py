from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from app.api.dependencies import get_current_user, require_role
from app.agents.master_agent import MasterAgent
from app.core.database import get_database
from app.models.vehicle import Vehicle, VehicleTelemetry
from app.models.customer import Customer, ServiceAppointment, Feedback
from app.models.service_center import ServiceCenter, Technician
from app.models.manufacturing import RCACAPAInsight
from app.models.security import User, SecurityEvent

router = APIRouter()
master_agent = MasterAgent()

# Helper function to convert ObjectId and datetime to JSON-serializable formats
def convert_objectid(obj):
    """Recursively convert ObjectId to string and datetime to ISO format for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# Health check
@router.get("/health")
async def health_check():
    """Health check - also reports MongoDB connectivity when available."""
    status = {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    try:
        # Try to check DB connectivity if available
        db = get_database()
        try:
            # lightweight ping
            await db.command("ping")
            status["mongodb"] = "connected"
        except Exception:
            status["mongodb"] = "unavailable"
    except Exception:
        status["mongodb"] = "not_initialized"

    return status

# Master Agent endpoint
@router.post("/workflow/execute")
async def execute_workflow(
    workflow_data: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Execute master agent workflow"""
    try:
        result = await master_agent.execute(workflow_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Telemetry endpoints
@router.post("/telemetry/ingest")
async def ingest_telemetry(
    telemetry_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Ingest vehicle telemetry data"""
    result = await master_agent.telemetry_agent.execute(telemetry_data)
    return result

@router.get("/telemetry/{vin}")
async def get_telemetry(
    vin: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get telemetry data for a vehicle - Customers can only access their own vehicles"""
    db = get_database()
    
    # Role-based access: Customers can only view their own vehicles' telemetry
    user_role = current_user.get("role")
    if user_role == "customer":
        # Verify vehicle belongs to customer
        vehicle = await db.vehicles.find_one({"vin": vin})
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if customer_id == "customer":
            customer_id = "CUST_001"
        if vehicle.get("customer_id") != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view telemetry for your own vehicles"
            )
    
    telemetry = await db.vehicle_telemetry.find(
        {"vin": vin}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"vin": vin, "telemetry": telemetry}

# Failure prediction endpoints
@router.post("/predictions/predict")
async def predict_failure(
    prediction_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Predict vehicle failure"""
    result = await master_agent.failure_prediction_agent.execute(prediction_data)
    return result

# Customer engagement endpoints
@router.post("/engagement/send-alert")
async def send_alert(
    alert_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send alert to customer"""
    result = await master_agent.customer_engagement_agent.execute({
        "action": "send_alert",
        **alert_data
    })
    return result

@router.post("/engagement/chat")
async def chat(
    chat_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Handle customer chat"""
    result = await master_agent.customer_engagement_agent.execute({
        "action": "get_chat_response",
        **chat_data
    })
    return result

# Scheduling endpoints
@router.post("/scheduling/schedule")
async def schedule_appointment(
    appointment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Schedule service appointment with smart technician assignment based on specialization"""
    vin = appointment_data.get("vin")
    predicted_issue = None
    
    # Get predicted issue for smart technician assignment
    if vin:
        try:
            db = get_database()
            # Try to get prediction from failure prediction agent
            prediction_result = await master_agent.failure_prediction_agent.execute({"vin": vin})
            if prediction_result.get("status") == "success":
                predicted_issue = prediction_result.get("recommendation", "")
            else:
                # Fallback to telemetry
                recent_telemetry = await db.vehicle_telemetry.find(
                    {"vin": vin}
                ).sort("timestamp", -1).limit(1).to_list(1)
                if recent_telemetry:
                    latest = recent_telemetry[0]
                    health = latest.get("health_score", 100.0)
                    if health < 50:
                        predicted_issue = "Critical health issues detected - immediate attention required"
                    elif health < 70:
                        predicted_issue = "Elevated risk indicators - preventive maintenance recommended"
                    else:
                        predicted_issue = "General maintenance service"
        except Exception as e:
            print(f"Error getting prediction for scheduling: {str(e)}")
            predicted_issue = "General maintenance service"
    
    # Add predicted_issue to appointment data for smart assignment
    if predicted_issue:
        appointment_data["predicted_issue"] = predicted_issue
    
    result = await master_agent.smart_scheduling_agent.execute({
        "action": "schedule",
        **appointment_data
    })
    return result

@router.post("/scheduling/reschedule")
async def reschedule_appointment(
    appointment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Reschedule an existing appointment"""
    result = await master_agent.smart_scheduling_agent.execute({
        "action": "reschedule",
        **appointment_data
    })
    return result

@router.post("/scheduling/cancel")
async def cancel_appointment(
    appointment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an existing appointment"""
    # Role-based access: Customers can only cancel their own appointments
    if current_user.get("role") == "customer":
        db = get_database()
        appointment_id = appointment_data.get("appointment_id")
        if appointment_id:
            appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
            if appointment:
                customer_id = current_user.get("customer_id") or current_user.get("username")
                if appointment.get("customer_id") != customer_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied: You can only cancel your own appointments"
                    )
    
    result = await master_agent.smart_scheduling_agent.execute({
        "action": "cancel",
        **appointment_data
    })
    return result

@router.get("/scheduling/availability")
async def check_availability(
    current_user: dict = Depends(get_current_user)
):
    """Check service center availability"""
    result = await master_agent.smart_scheduling_agent.execute({
        "action": "check_availability"
    })
    return result

@router.get("/scheduling/appointments/{customer_id}")
async def get_appointments(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get customer appointments - Customers can only see their own appointments"""
    # Map username "customer" to customer_id "CUST_001"
    if customer_id == "customer":
        customer_id = "CUST_001"
    
    # Role-based access: Customers can only see their own appointments
    if current_user.get("role") == "customer":
        user_customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if user_customer_id == "customer":
            user_customer_id = "CUST_001"
        if customer_id != user_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own appointments"
            )
    
    db = get_database()
    # Only return active appointments (not cancelled) - rescheduled appointments are cancelled
    appointments = await db.service_appointments.find(
        {"customer_id": customer_id, "status": {"$ne": "cancelled"}}
    ).sort("scheduled_date", -1).to_list(100)
    
    # Convert ObjectId to string for JSON serialization
    appointments = [convert_objectid(apt) for apt in appointments]
    
    return {"customer_id": customer_id, "appointments": appointments}

# Service Center endpoints
@router.get("/service-centers")
async def get_service_centers(
    current_user: dict = Depends(get_current_user)
):
    """Get all service centers - for service center selection"""
    db = get_database()
    centers = await db.service_centers.find({"status": "active"}).to_list(100)
    centers = [convert_objectid(c) for c in centers]
    return {"status": "success", "service_centers": centers}

@router.get("/service-centers/{center_id}/appointments")
async def get_service_center_appointments(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get appointments for a specific service center"""
    # Role-based access: Service center users can only see their own center's appointments
    if current_user.get("role") == "service_center":
        # Service center users should have a service_center_id associated
        user_center_id = current_user.get("service_center_id")
        if user_center_id and center_id != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own service center's appointments"
            )
    
    db = get_database()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Get ALL appointments (not just future) - for bookings page
    appointments = await db.service_appointments.find({
        "service_center_id": center_id,
        "status": {"$ne": "cancelled"}
    }).sort("scheduled_date", -1).to_list(100)
    
    # Get vehicle and prediction data for each appointment
    appointments_with_details = []
    for apt in appointments:
        apt_dict = convert_objectid(apt)
        vin = apt.get("vin")
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin})
        if vehicle:
            apt_dict["vehicle_name"] = vehicle.get("vehicle_name") or vehicle.get("model")
            apt_dict["plate_number"] = vehicle.get("plate_number")
        
        # Get technician name if technician_id is assigned
        technician_id = apt.get("technician_id")
        if technician_id:
            technician = await db.technicians.find_one({"technician_id": technician_id})
            if technician:
                apt_dict["technician_name"] = technician.get("name", technician_id)
            else:
                apt_dict["technician_name"] = technician_id
        else:
            apt_dict["technician_name"] = None
        
        # Get prediction/telemetry for pre-diagnosis
        try:
            prediction_result = await master_agent.failure_prediction_agent.execute({"vin": vin})
            if prediction_result.get("status") == "success":
                apt_dict["predicted_issue"] = prediction_result.get("recommendation", "General maintenance required")
                apt_dict["health_score"] = prediction_result.get("health_score", 100.0)
            else:
                # Fallback to telemetry
                recent_telemetry = await db.vehicle_telemetry.find(
                    {"vin": vin}
                ).sort("timestamp", -1).limit(1).to_list(1)
                if recent_telemetry:
                    latest = recent_telemetry[0]
                    health = latest.get("health_score", 100.0)
                    apt_dict["health_score"] = health
                    if health < 50:
                        apt_dict["predicted_issue"] = "Critical health issues detected - immediate attention required"
                    elif health < 70:
                        apt_dict["predicted_issue"] = "Elevated risk indicators - preventive maintenance recommended"
                    else:
                        apt_dict["predicted_issue"] = "General maintenance service"
        except Exception as e:
            apt_dict["predicted_issue"] = "General maintenance service"
            apt_dict["health_score"] = 100.0
        
        appointments_with_details.append(apt_dict)
    
    return {"status": "success", "appointments": appointments_with_details}

@router.get("/service-centers/{center_id}/pre-diagnosed-cases")
async def get_pre_diagnosed_cases(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get pre-diagnosed service cases (upcoming appointments with predicted issues)"""
    # Role-based access
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and center_id != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    db = get_database()
    now = datetime.utcnow()
    # Get upcoming appointments (scheduled, not yet started)
    upcoming_appointments = await db.service_appointments.find({
        "service_center_id": center_id,
        "status": "scheduled",
        "scheduled_date": {"$gte": now}
    }).sort("scheduled_date", 1).to_list(50)
    
    # Get vehicle and prediction data for each appointment
    pre_diagnosed_cases = []
    for apt in upcoming_appointments:
        apt_dict = convert_objectid(apt)
        vin = apt.get("vin")
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin})
        if vehicle:
            apt_dict["vehicle_name"] = vehicle.get("vehicle_name") or vehicle.get("model")
            apt_dict["plate_number"] = vehicle.get("plate_number")
        
        # Get technician name if assigned
        technician_id = apt.get("technician_id")
        if technician_id:
            technician = await db.technicians.find_one({"technician_id": technician_id})
            if technician:
                apt_dict["technician_name"] = technician.get("name", technician_id)
                apt_dict["technician_specialization"] = technician.get("specialization", [])
            else:
                apt_dict["technician_name"] = technician_id
        else:
            apt_dict["technician_name"] = None
        
        # Get prediction/telemetry for pre-diagnosis
        try:
            prediction_result = await master_agent.failure_prediction_agent.execute({"vin": vin})
            if prediction_result.get("status") == "success":
                apt_dict["predicted_issue"] = prediction_result.get("recommendation", "General maintenance required")
                apt_dict["health_score"] = prediction_result.get("health_score", 100.0)
                apt_dict["risk_score"] = prediction_result.get("risk_score", 0.0)
            else:
                # Fallback to telemetry
                recent_telemetry = await db.vehicle_telemetry.find(
                    {"vin": vin}
                ).sort("timestamp", -1).limit(1).to_list(1)
                if recent_telemetry:
                    latest = recent_telemetry[0]
                    health = latest.get("health_score", 100.0)
                    apt_dict["health_score"] = health
                    apt_dict["risk_score"] = latest.get("prediction_risk", (100 - health) / 100.0)
                    if health < 50:
                        apt_dict["predicted_issue"] = "Critical health issues detected - immediate attention required"
                    elif health < 70:
                        apt_dict["predicted_issue"] = "Elevated risk indicators - preventive maintenance recommended"
                    else:
                        apt_dict["predicted_issue"] = "General maintenance service"
        except Exception as e:
            apt_dict["predicted_issue"] = "General maintenance service"
            apt_dict["health_score"] = 100.0
            apt_dict["risk_score"] = 0.0
        
        # Determine recommended tools/parts based on predicted issue
        apt_dict["recommended_tools"] = _get_recommended_tools(apt_dict.get("predicted_issue", ""))
        apt_dict["recommended_parts"] = _get_recommended_parts(apt_dict.get("predicted_issue", ""))
        
        pre_diagnosed_cases.append(apt_dict)
    
    return {"status": "success", "pre_diagnosed_cases": pre_diagnosed_cases}

def _get_recommended_tools(predicted_issue: str) -> list:
    """Get recommended tools based on predicted issue"""
    if not predicted_issue:
        return ["Standard diagnostic tools", "OBD scanner"]
    
    issue_lower = predicted_issue.lower()
    tools = []
    
    if any(keyword in issue_lower for keyword in ["engine", "temperature", "overheating", "cooling"]):
        tools.extend(["Thermometer", "Cooling system pressure tester", "OBD scanner"])
    if any(keyword in issue_lower for keyword in ["electrical", "battery", "voltage"]):
        tools.extend(["Multimeter", "Battery tester", "Electrical diagnostic tools"])
    if any(keyword in issue_lower for keyword in ["brake", "braking"]):
        tools.extend(["Brake fluid tester", "Brake pad gauge", "Lift/jack"])
    if any(keyword in issue_lower for keyword in ["suspension", "alignment"]):
        tools.extend(["Alignment machine", "Suspension tester", "Lift/jack"])
    if any(keyword in issue_lower for keyword in ["transmission", "gearbox"]):
        tools.extend(["Transmission fluid tester", "OBD scanner", "Lift/jack"])
    if any(keyword in issue_lower for keyword in ["ac", "air conditioning", "cooling"]):
        tools.extend(["AC pressure gauge", "Refrigerant leak detector", "Thermometer"])
    
    if not tools:
        tools = ["Standard diagnostic tools", "OBD scanner"]
    
    return tools[:5]  # Limit to 5 tools

def _get_recommended_parts(predicted_issue: str) -> list:
    """Get recommended parts based on predicted issue"""
    if not predicted_issue:
        return ["Standard maintenance parts"]
    
    issue_lower = predicted_issue.lower()
    parts = []
    
    if any(keyword in issue_lower for keyword in ["engine", "temperature", "overheating"]):
        parts.extend(["Coolant", "Thermostat", "Radiator cap"])
    if any(keyword in issue_lower for keyword in ["electrical", "battery"]):
        parts.extend(["Battery", "Alternator", "Fuses"])
    if any(keyword in issue_lower for keyword in ["brake", "braking"]):
        parts.extend(["Brake pads", "Brake fluid", "Brake rotors"])
    if any(keyword in issue_lower for keyword in ["suspension"]):
        parts.extend(["Shock absorbers", "Struts", "Suspension bushings"])
    if any(keyword in issue_lower for keyword in ["transmission"]):
        parts.extend(["Transmission fluid", "Transmission filter"])
    if any(keyword in issue_lower for keyword in ["ac", "air conditioning"]):
        parts.extend(["Refrigerant", "AC filter", "AC compressor"])
    if any(keyword in issue_lower for keyword in ["oil", "lubrication"]):
        parts.extend(["Engine oil", "Oil filter", "Oil pan gasket"])
    
    if not parts:
        parts = ["Standard maintenance parts"]
    
    return parts[:5]  # Limit to 5 parts

@router.get("/service-centers/{center_id}/ongoing-bookings")
async def get_ongoing_bookings(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get ongoing bookings (in_progress and completed) for a service center"""
    # Role-based access
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and center_id != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    db = get_database()
    
    # Get in_progress and completed appointments
    appointments = await db.service_appointments.find({
        "service_center_id": center_id,
        "status": {"$in": ["in_progress", "completed"]}
    }).sort("scheduled_date", -1).to_list(100)
    
    # Get vehicle info for each appointment
    appointments_with_details = []
    for apt in appointments:
        apt_dict = convert_objectid(apt)
        vin = apt.get("vin")
        
        # Get vehicle info
        vehicle = await db.vehicles.find_one({"vin": vin})
        if vehicle:
            apt_dict["vehicle_name"] = vehicle.get("vehicle_name") or vehicle.get("model")
            apt_dict["plate_number"] = vehicle.get("plate_number")
        
        # Get customer info
        customer_id = apt.get("customer_id")
        if customer_id:
            customer = await db.customers.find_one({"customer_id": customer_id})
            if customer:
                apt_dict["customer_name"] = customer.get("name")
        
        # Get technician name if technician_id is assigned
        technician_id = apt.get("technician_id")
        if technician_id:
            technician = await db.technicians.find_one({"technician_id": technician_id})
            if technician:
                apt_dict["technician_name"] = technician.get("name", technician_id)
            else:
                apt_dict["technician_name"] = technician_id
        else:
            apt_dict["technician_name"] = None
        
        appointments_with_details.append(apt_dict)
    
    return {"status": "success", "appointments": appointments_with_details}

@router.get("/service-centers/{center_id}/technicians")
async def get_service_center_technicians(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get technicians for a specific service center with detailed stats"""
    # Role-based access: Service center users can only see their own center's technicians
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and center_id != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own service center's technicians"
            )
    
    db = get_database()
    
    # Get technicians
    technicians = await db.technicians.find({"service_center_id": center_id}).to_list(100)
    
    # Calculate vehicles repaired last month for each technician
    one_month_ago = datetime.utcnow() - timedelta(days=30)
    
    technicians_with_stats = []
    for tech in technicians:
        tech_dict = convert_objectid(tech)
        technician_id = tech.get("technician_id")
        
        # Count completed appointments in last month
        completed_count = await db.service_appointments.count_documents({
            "technician_id": technician_id,
            "status": "completed",
            "updated_at": {"$gte": one_month_ago}
        })
        
        tech_dict["vehicles_repaired_last_month"] = completed_count
        
        technicians_with_stats.append(tech_dict)
    
    return {"status": "success", "technicians": technicians_with_stats}

@router.get("/service-centers/{center_id}/workload")
async def get_service_center_workload(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workload statistics for a service center including workload distribution"""
    # Role-based access
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and center_id != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    db = get_database()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    # Count scheduled today
    scheduled_today = await db.service_appointments.count_documents({
        "service_center_id": center_id,
        "status": "scheduled",
        "scheduled_date": {"$gte": today, "$lt": tomorrow}
    })
    
    # Count in progress - use actual appointment status
    in_progress = await db.service_appointments.count_documents({
        "service_center_id": center_id,
        "status": "in_progress"
    })
    
    # Count completed today
    completed_today = await db.service_appointments.count_documents({
        "service_center_id": center_id,
        "status": "completed",
        "updated_at": {"$gte": today, "$lt": tomorrow}
    })
    
    # Count available technicians - only count those with NO current assignments (not working)
    all_technicians = await db.technicians.find({"service_center_id": center_id}).to_list(100)
    available_technicians = sum(1 for tech in all_technicians 
                              if tech.get("status") == "available" 
                              and tech.get("current_assignments", 0) == 0)
    
    # Get workload distribution (technician assignments)
    workload_distribution = []
    for tech in all_technicians:
        tech_dict = convert_objectid(tech)
        workload_distribution.append({
            "technician_id": tech.get("technician_id"),
            "technician_name": tech.get("name"),
            "current_assignments": tech.get("current_assignments", 0),
            "max_capacity": tech.get("max_capacity", 3),
            "status": tech.get("status", "available"),
            "utilization_percent": round((tech.get("current_assignments", 0) / tech.get("max_capacity", 3)) * 100, 1) if tech.get("max_capacity", 3) > 0 else 0
        })
    
    return {
        "status": "success",
        "workload": {
            "scheduled_today": scheduled_today,
            "in_progress": in_progress,
            "completed_today": completed_today,
            "available_technicians": available_technicians,
            "workload_distribution": workload_distribution
        }
    }

@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    status_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update appointment status (in_progress, completed)"""
    new_status = status_data.get("status")
    if new_status not in ["in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'in_progress' or 'completed'"
        )
    
    db = get_database()
    appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Role-based access: Service center users can only update their own center's appointments
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and appointment.get("service_center_id") != user_center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only update your own service center's appointments"
            )
    
    # Update status
    update_data = {"status": new_status, "updated_at": datetime.utcnow()}
    
    # If marking as completed, decrease technician assignments and service center load
    if new_status == "completed" and appointment.get("status") != "completed":
        technician_id = appointment.get("technician_id")
        if technician_id:
            await db.technicians.update_one(
                {"technician_id": technician_id},
                {"$inc": {"current_assignments": -1}}
            )
        
        center_id = appointment.get("service_center_id")
        if center_id:
            await db.service_centers.update_one(
                {"center_id": center_id},
                {"$inc": {"current_load": -1}}
            )
        
        # When service completes, refresh vehicle health to a healthy baseline (96%)
        vin = appointment.get("vin")
        if vin:
            try:
                # Insert a new healthy telemetry record
                await db.vehicle_telemetry.insert_one({
                    "vin": vin,
                    "health_score": 96.0,
                    "prediction_risk": 0.04,
                    "timestamp": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "source": "service_completion",
                    "appointment_id": appointment_id
                })

                # Deactivate any active maintenance alerts for this vehicle & customer
                customer_id = appointment.get("customer_id")
                if customer_id:
                    if customer_id == "customer":
                        customer_id = "CUST_001"

                    result = await db.notifications.update_many(
                        {
                            "customer_id": customer_id,
                            "vin": vin,
                            "type": "maintenance_alert",
                            "status": "active"
                        },
                        {
                            "$set": {
                                "status": "inactive",
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    print(f"[SERVICE COMPLETION] Deactivated {result.modified_count} maintenance alerts for {vin}")
            except Exception as telemetry_error:
                print(f"[SERVICE COMPLETION] Failed to insert recovery telemetry / deactivate alerts for {vin}: {telemetry_error}")

        # Create completion notification for customer
        customer_id = appointment.get("customer_id")
        vin = appointment.get("vin")
        if customer_id and vin:
            # Map username "customer" to customer_id "CUST_001"
            if customer_id == "customer":
                customer_id = "CUST_001"
            
            # Get service center name
            service_center_name = center_id
            if center_id:
                center = await db.service_centers.find_one({"center_id": center_id})
                if center:
                    service_center_name = center.get("name", center_id)
            
            # Get vehicle info
            vehicle = await db.vehicles.find_one({"vin": vin})
            vehicle_name = vehicle.get("vehicle_name") if vehicle else vin
            
            # Get technician name if assigned
            technician_name = None
            if technician_id:
                technician = await db.technicians.find_one({"technician_id": technician_id})
                if technician:
                    technician_name = technician.get("name", technician_id)
            
            # Create completion notification
            completion_message = f"✅ Service Completed: Your vehicle {vehicle_name} (VIN: {vin}) has been successfully serviced at {service_center_name}."
            if technician_name:
                completion_message += f" Technician: {technician_name}."
            if appointment.get("description"):
                completion_message += f" Service details: {appointment.get('description')}."
            
            notification = {
                "notification_id": f"COMPLETION_{appointment_id}_{datetime.utcnow().timestamp()}",
                "customer_id": customer_id,
                "vin": vin,
                "type": "service_completed",
                "message": completion_message,
                "appointment_id": appointment_id,
                "service_center_id": center_id,
                "service_center_name": service_center_name,
                "technician_name": technician_name,
                "status": "active",
                "created_at": datetime.utcnow(),
                "read": False
            }
            await db.notifications.insert_one(notification)
    
    # If marking as in_progress, ensure technician assignment and update service center load
    if new_status == "in_progress" and appointment.get("status") == "scheduled":
        center_id = appointment.get("service_center_id")
        
        # Auto-assign technician if not already assigned (with specialization matching)
        if not appointment.get("technician_id"):
            # Get predicted issue for smart assignment
            vin = appointment.get("vin")
            predicted_issue = None
            if vin:
                try:
                    prediction_result = await master_agent.failure_prediction_agent.execute({"vin": vin})
                    if prediction_result.get("status") == "success":
                        predicted_issue = prediction_result.get("recommendation", "")
                except Exception:
                    pass
            
            # Extract issue category for matching
            issue_category = None
            if predicted_issue:
                issue_lower = predicted_issue.lower()
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
                for category, keywords in category_mapping.items():
                    if any(keyword in issue_lower for keyword in keywords):
                        issue_category = category.capitalize()
                        break
            
            technician_id = None
            # First try to find technician with matching specialization
            if issue_category:
                matching_technicians = await db.technicians.find({
                    "service_center_id": center_id,
                    "status": "available",
                    "specialization": {"$in": [issue_category]},
                    "$expr": {"$lt": ["$current_assignments", "$max_capacity"]}
                }).sort("current_assignments", 1).limit(1).to_list(1)
                
                if matching_technicians:
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
            
            if technician_id:
                update_data["technician_id"] = technician_id
                await db.technicians.update_one(
                    {"technician_id": technician_id},
                    {"$inc": {"current_assignments": 1}}
                )
        else:
            # If technician already assigned, increment their assignments
            technician_id = appointment.get("technician_id")
            await db.technicians.update_one(
                {"technician_id": technician_id},
                {"$inc": {"current_assignments": 1}}
            )
        
        # Update service center load when starting service
        if center_id:
            await db.service_centers.update_one(
                {"center_id": center_id},
                {"$inc": {"current_load": 1}}
            )
    
    await db.service_appointments.update_one(
        {"appointment_id": appointment_id},
        {"$set": update_data}
    )
    
    # Convert and return updated appointment
    updated_appointment = await db.service_appointments.find_one({"appointment_id": appointment_id})
    updated_appointment = convert_objectid(updated_appointment) if updated_appointment else None
    
    return {
        "status": "success", 
        "message": f"Appointment status updated to {new_status}",
        "appointment": updated_appointment
    }

# Feedback endpoints
@router.post("/feedback/submit")
async def submit_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Submit service feedback"""
    result = await master_agent.feedback_agent.execute({
        "action": "collect_feedback",
        **feedback_data
    })
    return result

@router.get("/feedback/summary")
async def get_feedback_summary(
    vin: Optional[str] = None,
    service_center_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get feedback summary"""
    result = await master_agent.feedback_agent.execute({
        "action": "get_feedback_summary",
        "vin": vin,
        "service_center_id": service_center_id
    })
    return result

@router.get("/service-centers/{center_id}/feedback")
async def get_service_center_feedback(
    center_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed feedback and rating for a specific service center"""
    db = get_database()
    
    # Role-based access:
    # - service_center users can only see their own feedback
    # - manufacturing and admin can see all
    if current_user.get("role") == "service_center":
        user_center_id = current_user.get("service_center_id")
        if user_center_id and user_center_id != center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view feedback for your own service center"
            )
    
    # Get appointments for this service center
    appointments = await db.service_appointments.find(
        {"service_center_id": center_id}
    ).to_list(1000)
    appointment_ids = [apt.get("appointment_id") for apt in appointments]
    
    if not appointment_ids:
        return {"status": "success", "feedback": [], "average_rating": 0, "total_feedbacks": 0}
    
    # Get feedbacks linked to those appointments
    feedbacks = await db.feedbacks.find(
        {"appointment_id": {"$in": appointment_ids}}
    ).sort("created_at", -1).to_list(200)
    
    if not feedbacks:
        return {"status": "success", "feedback": [], "average_rating": 0, "total_feedbacks": 0}
    
    total_rating = sum(f.get("rating", 0) for f in feedbacks)
    avg_rating = total_rating / len(feedbacks)
    
    return {
        "status": "success",
        "feedback": convert_objectid(feedbacks),
        "average_rating": round(avg_rating, 2),
        "total_feedbacks": len(feedbacks)
    }

# Manufacturing insights endpoints
@router.post("/manufacturing/generate-insights")
async def generate_insights(
    manufacturer: Optional[str] = None,
    current_user: dict = Depends(require_role("manufacturing"))
):
    """Generate manufacturing insights (optionally filtered by manufacturer)"""
    result = await master_agent.manufacturing_insights_agent.execute({
        "action": "generate_insights",
        "manufacturer": manufacturer
    })
    return result

@router.get("/manufacturing/insights")
async def get_insights(
    manufacturer: Optional[str] = None,
    current_user: dict = Depends(require_role("manufacturing"))
):
    """Get manufacturing insights (optionally filtered by manufacturer)"""
    db = get_database()
    query = {}
    if manufacturer:
        query["manufacturer"] = manufacturer
    insights = await db.rcacapa_insights.find(query).sort("created_at", -1).to_list(100)
    return {"insights": insights}

@router.get("/manufacturing/patterns")
async def get_patterns(
    manufacturer: Optional[str] = None,
    current_user: dict = Depends(require_role("manufacturing"))
):
    """Get failure patterns"""
    result = await master_agent.manufacturing_insights_agent.execute({
        "action": "get_patterns",
        "manufacturer": manufacturer
    })
    return result

# Security/UEBA endpoints
@router.post("/security/analyze")
async def analyze_security(
    current_user: dict = Depends(require_role("admin"))
):
    """Analyze agent logs for security anomalies"""
    result = await master_agent.ueba_security_agent.execute({
        "action": "analyze_logs"
    })
    return result

@router.get("/security/events")
async def get_security_events(
    current_user: dict = Depends(require_role("admin"))
):
    """Get security events"""
    db = get_database()
    events = await db.security_events.find({}).sort("detected_at", -1).limit(100).to_list(100)
    return {"events": events}

@router.get("/security/agent/{agent_name}")
async def check_agent_security(
    agent_name: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Check specific agent security"""
    result = await master_agent.ueba_security_agent.execute({
        "action": "check_specific_agent",
        "agent_name": agent_name
    })
    return result

# Vehicle endpoints
@router.post("/vehicles")
async def create_vehicle(
    vehicle_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create vehicle - Automatically sets customer_id from current user"""
    db = get_database()
    
    # Set customer_id from current user if not provided
    if "customer_id" not in vehicle_data:
        raw_customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001" for consistency
        if raw_customer_id == "customer":
            vehicle_data["customer_id"] = "CUST_001"
        else:
            vehicle_data["customer_id"] = raw_customer_id
    
    vehicle = Vehicle(**vehicle_data)
    await db.vehicles.insert_one(vehicle.dict(by_alias=True))
    return {"status": "success", "vehicle": vehicle.dict()}

@router.get("/vehicles/customer/{customer_id}")
async def get_customer_vehicles(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all vehicles for a customer - Customers can only see their own vehicles"""
    # Map username "customer" to customer_id "CUST_001"
    if customer_id == "customer":
        customer_id = "CUST_001"
    
    # Role-based access: Customers can only see their own vehicles
    if current_user.get("role") == "customer":
        user_customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if user_customer_id == "customer":
            user_customer_id = "CUST_001"
        if customer_id != user_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own vehicles"
            )
    
    db = get_database()
    vehicles_cursor = db.vehicles.find({"customer_id": customer_id})
    vehicles = await vehicles_cursor.to_list(100)
    
    # Convert ObjectId to string for JSON serialization
    vehicles = [convert_objectid(v) for v in vehicles]
    
    # Debug logging
    print(f"[DEBUG] get_customer_vehicles: customer_id={customer_id}, found {len(vehicles)} vehicles")
    if vehicles:
        print(f"[DEBUG] Vehicle VINs: {[v.get('vin') for v in vehicles[:5]]}")
    
    return {"customer_id": customer_id, "vehicles": vehicles}

@router.get("/vehicles/{vin}")
async def get_vehicle(
    vin: str,
    current_user: dict = Depends(get_current_user)
):
    """Get vehicle by VIN - Customers can only see their own vehicles"""
    db = get_database()
    vehicle = await db.vehicles.find_one({"vin": vin})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Role-based access: Customers can only see their own vehicles
    if current_user.get("role") == "customer":
        customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if customer_id == "customer":
            customer_id = "CUST_001"
        if vehicle.get("customer_id") != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own vehicles"
            )
    
    # Convert ObjectId to string for JSON serialization
    return convert_objectid(vehicle)

# Customer endpoints
@router.post("/customers")
async def create_customer(
    customer_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create customer"""
    db = get_database()
    customer = Customer(**customer_data)
    await db.customers.insert_one(customer.dict(by_alias=True))
    return {"status": "success", "customer": customer.dict()}

@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get customer"""
    db = get_database()
    customer = await db.customers.find_one({"customer_id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# AI Notification System - Proactive Maintenance Alerts
@router.post("/notifications/check-and-create")
async def check_and_create_alerts(
    request_data: Optional[dict] = None,
    current_user: dict = Depends(get_current_user)
):
    """AI-controlled notification system - automatically detects failures and creates alerts"""
    # Get customer_id from request body or current user
    customer_id = None
    if request_data and isinstance(request_data, dict):
        customer_id = request_data.get("customer_id")
    if not customer_id:
        customer_id = current_user.get("customer_id") or current_user.get("username")
    
    # Map username "customer" to customer_id "CUST_001"
    if customer_id == "customer":
        customer_id = "CUST_001"
    
    db = get_database()
    
    # Role-based access: Customers can only check their own alerts
    if current_user.get("role") == "customer":
        user_customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if user_customer_id == "customer":
            user_customer_id = "CUST_001"
        if customer_id != user_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only check your own alerts"
            )
    
    # Get all vehicles for customer
    vehicles = await db.vehicles.find({"customer_id": customer_id}).to_list(100)
    
    # Get existing scheduled appointments
    appointments = await db.service_appointments.find({
        "customer_id": customer_id,
        "status": {"$in": ["scheduled", "in_progress"]}
    }).to_list(100)
    scheduled_vins = {apt["vin"] for apt in appointments}
    
    # FIRST: Clean up ALL existing alerts that don't meet strict criteria
    # This ensures old alerts are removed immediately
    all_existing_alerts = await db.notifications.find({
        "customer_id": customer_id,
        "status": "active",
        "type": "maintenance_alert"
    }).to_list(1000)
    
    for old_alert in all_existing_alerts:
        old_vin = old_alert.get("vin")
        if not old_vin:
            continue
        
        # Skip if vehicle has scheduled appointment
        if old_vin in scheduled_vins:
            continue
        
        # Re-check if alert is still valid by running prediction
        try:
            old_prediction = await master_agent.failure_prediction_agent.execute({"vin": old_vin})
            old_health = old_prediction.get("health_score", 100.0)
            old_risk = old_prediction.get("risk_score", 0.0)
            
            # Check if alert still meets criteria (health < 70)
            still_valid = old_health < 70
            
            # If health >= 70, deactivate alert
            if old_health >= 70:
                still_valid = False
                # Deactivate immediately
                await db.notifications.update_one(
                    {"notification_id": old_alert.get("notification_id")},
                    {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
                )
                continue  # Skip to next alert
            
            if not still_valid:
                # Deactivate alert immediately
                await db.notifications.update_one(
                    {"notification_id": old_alert.get("notification_id")},
                    {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
                )
        except Exception as e:
            # If we can't check, deactivate the alert to be safe
            await db.notifications.update_one(
                {"notification_id": old_alert.get("notification_id")},
                {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
            )
    
    alerts_created = []
    
    for vehicle in vehicles:
        vin = vehicle.get("vin")
        if not vin:
            continue
        
        # Skip if vehicle already has scheduled appointment
        if vin in scheduled_vins:
            continue
        
        # Run AI failure prediction with fallback to direct telemetry check
        try:
            db = get_database()
            health_score = 100.0
            risk_score = 0.0
            
            # Try to get health score from failure prediction agent
            try:
                prediction_result = await master_agent.failure_prediction_agent.execute({"vin": vin})
                if prediction_result.get("status") == "success":
                    risk_score = prediction_result.get("risk_score", 0.0)
                    health_score = prediction_result.get("health_score", 100.0)
                else:
                    # Agent returned error, try direct telemetry lookup
                    raise Exception("Prediction agent returned error")
            except Exception as agent_error:
                # Fallback: Check telemetry directly if agent fails
                print(f"Prediction agent failed for {vin}, checking telemetry directly: {str(agent_error)}")
                recent_telemetry = await db.vehicle_telemetry.find(
                    {"vin": vin}
                ).sort("timestamp", -1).limit(1).to_list(1)
                
                if recent_telemetry and len(recent_telemetry) > 0:
                    latest_telemetry = recent_telemetry[0]
                    health_score = latest_telemetry.get("health_score", 100.0)
                    risk_score = latest_telemetry.get("prediction_risk", 0.0)
                    
                    # If no risk score, calculate from health
                    if risk_score == 0.0:
                        risk_score = (100 - health_score) / 100.0
                    
                    print(f"Found telemetry for {vin}: health={health_score}, risk={risk_score}")
                else:
                    # No telemetry data - try to generate some using telemetry agent
                    print(f"No telemetry data found for vehicle {vin}. Attempting to generate initial telemetry...")
                    try:
                        # Try to generate telemetry for this vehicle
                        telemetry_result = await master_agent.telemetry_agent.execute({"vin": vin})
                        if telemetry_result.get("status") == "success":
                            # Now try to get the health score again
                            recent_telemetry = await db.vehicle_telemetry.find(
                                {"vin": vin}
                            ).sort("timestamp", -1).limit(1).to_list(1)
                            if recent_telemetry and len(recent_telemetry) > 0:
                                latest_telemetry = recent_telemetry[0]
                                health_score = latest_telemetry.get("health_score", 100.0)
                                risk_score = latest_telemetry.get("prediction_risk", 0.0)
                                if risk_score == 0.0:
                                    risk_score = (100 - health_score) / 100.0
                                print(f"Generated telemetry for {vin}: health={health_score}, risk={risk_score}")
                            else:
                                print(f"Warning: Could not retrieve generated telemetry for {vin}")
                                continue
                        else:
                            print(f"Warning: Could not generate telemetry for {vin}: {telemetry_result.get('message', 'Unknown error')}")
                            continue
                    except Exception as telemetry_error:
                        print(f"Error generating telemetry for {vin}: {str(telemetry_error)}")
                        continue  # Skip this vehicle if we can't generate telemetry
            
            # Debug logging - detailed information
            needs_alert = health_score < 70
            print(f"[ALERT CHECK] Vehicle {vin}: health={health_score:.2f}%, risk={risk_score:.3f}, needs_alert={needs_alert}, threshold=70%")
            
            # Create alert for vehicles with health < 70
            # Show alerts for vehicles that need attention (health < 70)
            
            # Check if alert already exists for this vehicle
            existing_alert = await db.notifications.find_one({
                "vin": vin,
                "customer_id": customer_id,
                "status": "active",
                "type": "maintenance_alert"
            })
            
            if needs_alert:
                print(f"[ALERT CREATION] Vehicle {vin} needs alert (health={health_score:.2f}% < 70%)")
                # Create or keep alert
                if not existing_alert:
                    print(f"[ALERT CREATION] Creating new alert for vehicle {vin}")
                    # Create new alert with specific repair booking confirmation message
                    vehicle_name = vehicle.get("vehicle_name") or vehicle.get("model", "your vehicle")
                    plate_number = vehicle.get("plate_number", "")
                    
                    # Build vehicle identifier
                    vehicle_identifier = vehicle_name
                    if plate_number:
                        vehicle_identifier += f" ({plate_number})"
                    
                    # Create specific messages for repair booking confirmation based on health score
                    if health_score < 50 or risk_score > 0.65:
                        alert_message = f"⚠️ URGENT: Your vehicle {vehicle_identifier} has critical health issues (Health: {health_score:.1f}%). Please confirm your schedule booking for repair immediately to prevent further damage."
                    elif health_score < 60 or risk_score > 0.55:
                        alert_message = f"⚠️ IMPORTANT: Your vehicle {vehicle_identifier} requires immediate attention (Health: {health_score:.1f}%). Please confirm your schedule booking for repair within 7 days to avoid potential breakdowns."
                    else:
                        alert_message = f"⚠️ NOTIFICATION: Your vehicle {vehicle_identifier} needs preventive repair service (Health: {health_score:.1f}%). Please confirm your schedule booking for repair within 14 days to maintain optimal performance."
                    
                    alert = {
                        "notification_id": f"ALERT_{vin}_{datetime.utcnow().timestamp()}",
                        "customer_id": customer_id,
                        "vin": vin,
                        "type": "maintenance_alert",
                        "message": alert_message,
                        "risk_level": "high" if (health_score < 50 or risk_score > 0.65) else "medium" if (health_score < 60 or risk_score > 0.55) else "low",
                        "health_score": health_score,
                        "risk_score": risk_score,
                        "status": "active",
                        "created_at": datetime.utcnow(),
                        "action_required": True,
                        "notification_type": "repair_booking_confirmation"
                    }
                    
                    await db.notifications.insert_one(alert)
                    alerts_created.append(alert)
                    print(f"[ALERT CREATION] Successfully created alert for vehicle {vin} with health {health_score:.2f}%")
                else:
                    print(f"[ALERT CHECK] Alert already exists for vehicle {vin}, keeping existing alert")
                # else: Alert already exists and still valid - keep it
            else:
                # Vehicle no longer needs alert - remove/deactivate existing alert
                if existing_alert:
                    print(f"[ALERT DEACTIVATION] Vehicle {vin} health improved to {health_score:.2f}% (>= 70%), deactivating alert")
                    await db.notifications.update_one(
                        {"notification_id": existing_alert.get("notification_id")},
                        {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
                    )
                else:
                    print(f"[ALERT CHECK] Vehicle {vin} health is {health_score:.2f}% (>= 70%), no alert needed")
        except Exception as e:
            print(f"Error checking vehicle {vin}: {str(e)}")
            continue
    
    print(f"[ALERT SUMMARY] Created {len(alerts_created)} new alerts for customer {customer_id}")
    return {
        "status": "success",
        "alerts_created": len(alerts_created),
        "alerts": alerts_created,
        "total_vehicles_checked": len(vehicles)
    }

@router.get("/notifications/customer/{customer_id}")
async def get_customer_notifications(
    customer_id: str,
    notification_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get all active notifications/alerts for a customer
    
    Args:
        customer_id: Customer ID
        notification_type: Optional filter by type ('maintenance_alert', 'service_completed', or None for all)
    """
    # Map username "customer" to customer_id "CUST_001"
    if customer_id == "customer":
        customer_id = "CUST_001"
    
    # Role-based access: Customers can only see their own notifications
    if current_user.get("role") == "customer":
        user_customer_id = current_user.get("customer_id") or current_user.get("username")
        # Map username "customer" to customer_id "CUST_001"
        if user_customer_id == "customer":
            user_customer_id = "CUST_001"
        if customer_id != user_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own notifications"
            )
    
    db = get_database()
    
    # Build query based on notification type
    query = {
        "customer_id": customer_id,
        "status": "active"
    }
    if notification_type:
        query["type"] = notification_type
    
    # Get active notifications
    all_notifications = await db.notifications.find(query).sort("created_at", -1).to_list(100)
    
    # For maintenance_alert type, filter to only include those that still meet criteria (health < 70)
    valid_notifications = []
    for notif in all_notifications:
        if notif.get("type") == "maintenance_alert":
            health_score = notif.get("health_score", 100)
            
            # Check if alert still meets criteria (health < 70)
            still_valid = health_score < 70
            
            if still_valid:
                valid_notifications.append(notif)
            else:
                # Deactivate alert that no longer meets criteria
                await db.notifications.update_one(
                    {"notification_id": notif.get("notification_id")},
                    {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
                )
        else:
            # For other notification types (like service_completed), include them
            valid_notifications.append(notif)
    
    # Convert ObjectId to string for JSON serialization
    valid_notifications = [convert_objectid(notif) for notif in valid_notifications]
    
    # If filtering by type, return appropriate key
    if notification_type == "maintenance_alert":
        return {"alerts": valid_notifications}
    elif notification_type == "service_completed":
        return {"completions": valid_notifications}
    else:
        # Return all notifications separated by type
        alerts = [n for n in valid_notifications if n.get("type") == "maintenance_alert"]
        completions = [n for n in valid_notifications if n.get("type") == "service_completed"]
        return {"alerts": alerts, "completions": completions}

