"""
Script to initialize demo data for the Connected Intelligence Hub
Run this script after starting MongoDB to populate initial data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from app.core.security import get_password_hash

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "automotive_aftermarket"

async def init_demo_data():
    """Initialize demo data"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("Initializing demo data...")
    
    # Create demo users
    users = [
        {
            "username": "customer",
            "email": "customer@demo.com",
            "hashed_password": get_password_hash("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "username": "service_center",
            "email": "service@demo.com",
            "hashed_password": get_password_hash("password123"),
            "role": "service_center",
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "username": "manufacturing",
            "email": "manufacturing@demo.com",
            "hashed_password": get_password_hash("password123"),
            "role": "manufacturing",
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "username": "admin",
            "email": "admin@demo.com",
            "hashed_password": get_password_hash("password123"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    for user in users:
        existing = await db.users.find_one({"username": user["username"]})
        if not existing:
            await db.users.insert_one(user)
            print(f"[OK] Created user: {user['username']}")
        else:
            print(f"[SKIP] User already exists: {user['username']}")
    
    # Create demo customer
    customer = {
        "customer_id": "CUST_001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State",
        "vehicles": ["VIN001", "VIN002"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    existing_customer = await db.customers.find_one({"customer_id": customer["customer_id"]})
    if not existing_customer:
        await db.customers.insert_one(customer)
        print(f"[OK] Created customer: {customer['customer_id']}")
    else:
        print(f"[SKIP] Customer already exists: {customer['customer_id']}")
    
    # Create demo vehicles
    vehicles = [
        {
            "vin": "VIN001",
            "vehicle_name": "My Hero Bike",
            "plate_number": "MH-12-AB-1234",
            "model": "Hero Splendor",
            "manufacturer": "Hero",
            "year": 2023,
            "customer_id": "CUST_001",
            "registration_date": datetime.utcnow(),
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "vin": "VIN002",
            "vehicle_name": "Family Car",
            "plate_number": "MH-12-CD-5678",
            "model": "Mahindra XUV300",
            "manufacturer": "Mahindra",
            "year": 2022,
            "customer_id": "CUST_001",
            "registration_date": datetime.utcnow(),
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]
    
    for vehicle in vehicles:
        existing_vehicle = await db.vehicles.find_one({"vin": vehicle["vin"]})
        if not existing_vehicle:
            await db.vehicles.insert_one(vehicle)
            print(f"[OK] Created vehicle: {vehicle['vehicle_name']} ({vehicle['plate_number']})")
        else:
            # Update existing vehicle with new fields if missing
            update_data = {}
            if "vehicle_name" not in existing_vehicle:
                update_data["vehicle_name"] = vehicle["vehicle_name"]
            if "plate_number" not in existing_vehicle:
                update_data["plate_number"] = vehicle["plate_number"]
            if update_data:
                await db.vehicles.update_one({"vin": vehicle["vin"]}, {"$set": update_data})
                print(f"[OK] Updated vehicle: {vehicle['vin']} with name and plate")
            else:
                print(f"[SKIP] Vehicle already exists: {vehicle['vin']}")
    
    # Create sample telemetry data for vehicles with CONSISTENT health scores
    import random
    import hashlib
    
    for vehicle in vehicles:
        # Use VIN hash to generate consistent but unique health for each vehicle
        vin_hash = int(hashlib.md5(vehicle["vin"].encode()).hexdigest()[:8], 16)
        random.seed(vin_hash)  # Seed random with VIN hash for consistency
        
        # Determine base health based on vehicle (first vehicle has lower health for demo)
        if vehicle["vin"] == "VIN001" or "001" in vehicle["vin"]:
            base_health = 48.0  # Lower health for first vehicle
        elif vehicle["vin"] == "VIN002" or "002" in vehicle["vin"]:
            base_health = 72.0  # Medium health for second vehicle
        else:
            base_health = 82.0  # Good health for others
        
        existing_telemetry = await db.vehicle_telemetry.find_one({"vin": vehicle["vin"]})
        if not existing_telemetry:
            # Generate 30 data points (one per hour for last 30 hours) with CONSISTENT health
            telemetry_data = []
            base_time = datetime.utcnow()
            
            for i in range(30):
                timestamp = base_time - timedelta(hours=30-i)
                
                # Small realistic variation in health (not random each time)
                # Health should slightly degrade over time for demo
                time_factor = i * 0.1  # Slight degradation over 30 hours
                health_variation = random.uniform(-2, 2)  # Small variation
                health_score = max(30, min(100, base_health - time_factor + health_variation))
                
                # Generate telemetry that correlates with health (consistent)
                if health_score < 50:
                    engine_temp = round(95 + random.uniform(-2, 8), 1)
                    oil_pressure = round(28 + random.uniform(-3, 5), 1)
                    battery_voltage = round(11.9 + random.uniform(-0.1, 0.3), 2)
                    vibration_level = round(0.85 + random.uniform(-0.1, 0.2), 2)
                    error_codes = ["P0300", "P0171"] if random.random() < 0.5 else []
                    anomaly_detected = True
                    prediction_risk = round(0.65 + random.uniform(-0.1, 0.15), 3)
                elif health_score < 70:
                    engine_temp = round(88 + random.uniform(-3, 5), 1)
                    oil_pressure = round(32 + random.uniform(-3, 5), 1)
                    battery_voltage = round(12.2 + random.uniform(-0.2, 0.3), 2)
                    vibration_level = round(0.65 + random.uniform(-0.1, 0.15), 2)
                    error_codes = []
                    anomaly_detected = random.random() < 0.3
                    prediction_risk = round(0.35 + random.uniform(-0.1, 0.15), 3)
                else:
                    engine_temp = round(85 + random.uniform(-3, 5), 1)
                    oil_pressure = round(38 + random.uniform(-3, 5), 1)
                    battery_voltage = round(12.6 + random.uniform(-0.2, 0.3), 2)
                    vibration_level = round(0.55 + random.uniform(-0.1, 0.1), 2)
                    error_codes = []
                    anomaly_detected = False
                    prediction_risk = round(0.15 + random.uniform(-0.05, 0.1), 3)
                
                telemetry_data.append({
                    "vin": vehicle["vin"],
                    "timestamp": timestamp,
                    "engine_temperature": engine_temp,
                    "oil_pressure": oil_pressure,
                    "vibration_level": vibration_level,
                    "battery_voltage": battery_voltage,
                    "speed": round(random.uniform(0, 80), 1),
                    "mileage": 15000 + i * 10,
                    "error_codes": error_codes,
                    "health_score": round(health_score, 1),
                    "anomaly_detected": anomaly_detected,
                    "prediction_risk": prediction_risk,
                    "created_at": timestamp
                })
            
            if telemetry_data:
                await db.vehicle_telemetry.insert_many(telemetry_data)
                latest_health = telemetry_data[-1]["health_score"]
                print(f"[OK] Created {len(telemetry_data)} telemetry records for {vehicle['vehicle_name']} (Health: {latest_health:.1f}%)")
        else:
            # Update existing telemetry to have consistent health if needed
            latest = await db.vehicle_telemetry.find_one(
                {"vin": vehicle["vin"]},
                sort=[("timestamp", -1)]
            )
            if latest:
                print(f"[SKIP] Telemetry already exists for {vehicle['vehicle_name']} (Latest Health: {latest.get('health_score', 'N/A')}%)")
    
    # Create demo service centers (more for testing with available slots)
    service_centers = [
        {
            "center_id": "SC_001",
            "name": "Hero Service Center Downtown",
            "manufacturer": "Hero",
            "address": "456 Service Ave, City, State",
            "phone": "+1234567891",
            "email": "service@hero.com",
            "capacity": 20,
            "current_load": 5,  # 15 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_002",
            "name": "Mahindra Service Center West",
            "manufacturer": "Mahindra",
            "address": "789 West Street, City, State",
            "phone": "+1234567892",
            "email": "service@mahindra.com",
            "capacity": 25,
            "current_load": 8,  # 17 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_003",
            "name": "Hero Service Center East",
            "manufacturer": "Hero",
            "address": "321 East Avenue, City, State",
            "phone": "+1234567893",
            "email": "service.east@hero.com",
            "capacity": 15,
            "current_load": 2,  # 13 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_004",
            "name": "Mahindra Service Center North",
            "manufacturer": "Mahindra",
            "address": "123 North Boulevard, City, State",
            "phone": "+1234567894",
            "email": "service.north@mahindra.com",
            "capacity": 18,
            "current_load": 3,  # 15 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_005",
            "name": "Hero Service Center South",
            "address": "567 South Road, City, State",
            "phone": "+1234567895",
            "email": "service.south@hero.com",
            "capacity": 12,
            "current_load": 0,  # 12 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_006",
            "name": "Mahindra Service Center Central",
            "address": "890 Central Plaza, City, State",
            "phone": "+1234567896",
            "email": "service.central@mahindra.com",
            "capacity": 30,
            "current_load": 10,  # 20 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_007",
            "name": "Hero Express Service Center",
            "address": "111 Express Highway, City, State",
            "phone": "+1234567897",
            "email": "express@hero.com",
            "capacity": 22,
            "current_load": 4,  # 18 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_008",
            "name": "Mahindra Premium Service",
            "address": "222 Premium Lane, City, State",
            "phone": "+1234567898",
            "email": "premium@mahindra.com",
            "capacity": 16,
            "current_load": 1,  # 15 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_009",
            "name": "Hero Quick Service Point",
            "address": "333 Quick Street, City, State",
            "phone": "+1234567899",
            "email": "quick@hero.com",
            "capacity": 14,
            "current_load": 0,  # 14 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_010",
            "name": "Mahindra City Center",
            "address": "444 City Square, City, State",
            "phone": "+1234567900",
            "email": "city@mahindra.com",
            "capacity": 28,
            "current_load": 6,  # 22 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_011",
            "name": "Hero Metro Service Hub",
            "address": "555 Metro Avenue, City, State",
            "phone": "+1234567901",
            "email": "metro@hero.com",
            "capacity": 24,
            "current_load": 5,  # 19 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        },
        {
            "center_id": "SC_012",
            "name": "Mahindra Suburban Service",
            "address": "666 Suburban Road, City, State",
            "phone": "+1234567902",
            "email": "suburban@mahindra.com",
            "capacity": 20,
            "current_load": 2,  # 18 slots available
            "status": "active",
            "created_at": datetime.utcnow()
        }
    ]
    
    for service_center in service_centers:
        existing_sc = await db.service_centers.find_one({"center_id": service_center["center_id"]})
        if not existing_sc:
            await db.service_centers.insert_one(service_center)
            available = service_center['capacity'] - service_center['current_load']
            print(f"[OK] Created service center: {service_center['name']} ({service_center['center_id']}) - {available} slots available")
        else:
            # ALWAYS update capacity and load to ensure correct availability
            # Force update to match the new demo data
            update_data = {
                "capacity": service_center["capacity"],
                "current_load": service_center["current_load"],
                "name": service_center["name"],
                "address": service_center["address"],
                "phone": service_center["phone"],
                "email": service_center["email"],
                "status": "active"
            }
            await db.service_centers.update_one(
                {"center_id": service_center["center_id"]},
                {"$set": update_data}
            )
            available = service_center.get("capacity", 0) - service_center.get("current_load", 0)
            print(f"[OK] Updated service center: {service_center['name']} ({service_center['center_id']}) - {available} slots available")
    
    # Create demo technicians (more for the additional service centers)
    technicians = [
        # SC_001 technicians (5 load, need 5+ more capacity)
        {
            "technician_id": "TECH_001",
            "name": "Mike Johnson",
            "service_center_id": "SC_001",
            "specialization": ["Engine", "Electrical"],
            "current_assignments": 2,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_002",
            "name": "Sarah Williams",
            "service_center_id": "SC_001",
            "specialization": ["Brakes", "Suspension"],
            "current_assignments": 2,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_003",
            "name": "Raj Kumar",
            "service_center_id": "SC_001",
            "specialization": ["Engine", "Transmission"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_002 technicians (8 load, need 8+ more capacity)
        {
            "technician_id": "TECH_004",
            "name": "Priya Sharma",
            "service_center_id": "SC_002",
            "specialization": ["Electrical", "AC"],
            "current_assignments": 3,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_005",
            "name": "Amit Patel",
            "service_center_id": "SC_002",
            "specialization": ["Brakes", "Tires"],
            "current_assignments": 3,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_006",
            "name": "Lisa Chen",
            "service_center_id": "SC_002",
            "specialization": ["Engine", "Oil"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_003 technicians (2 load, need 2+ more capacity)
        {
            "technician_id": "TECH_007",
            "name": "David Brown",
            "service_center_id": "SC_003",
            "specialization": ["Electrical", "AC"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_008",
            "name": "Anjali Singh",
            "service_center_id": "SC_003",
            "specialization": ["Transmission", "Clutch"],
            "current_assignments": 1,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_004 technicians (3 load, need 3+ more capacity)
        {
            "technician_id": "TECH_009",
            "name": "James Wilson",
            "service_center_id": "SC_004",
            "specialization": ["Engine", "Cooling"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_010",
            "name": "Sneha Reddy",
            "service_center_id": "SC_004",
            "specialization": ["Electrical", "Battery"],
            "current_assignments": 1,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_005 technicians (0 load, fully available)
        {
            "technician_id": "TECH_011",
            "name": "Robert Taylor",
            "service_center_id": "SC_005",
            "specialization": ["Engine", "Turbo"],
            "current_assignments": 0,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_012",
            "name": "Meera Nair",
            "service_center_id": "SC_005",
            "specialization": ["Suspension", "Steering"],
            "current_assignments": 0,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_013",
            "name": "Kevin Martinez",
            "service_center_id": "SC_005",
            "specialization": ["AC", "Heating"],
            "current_assignments": 0,
            "max_capacity": 3,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_006 technicians (10 load, need 10+ more capacity)
        {
            "technician_id": "TECH_014",
            "name": "Alex Thompson",
            "service_center_id": "SC_006",
            "specialization": ["Engine", "Transmission"],
            "current_assignments": 4,
            "max_capacity": 7,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_015",
            "name": "Priyanka Desai",
            "service_center_id": "SC_006",
            "specialization": ["Electrical", "Battery"],
            "current_assignments": 3,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_016",
            "name": "Carlos Rodriguez",
            "service_center_id": "SC_006",
            "specialization": ["Brakes", "Tires"],
            "current_assignments": 3,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_007 technicians (4 load)
        {
            "technician_id": "TECH_017",
            "name": "Emily Watson",
            "service_center_id": "SC_007",
            "specialization": ["Engine", "Oil"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_018",
            "name": "Vikram Joshi",
            "service_center_id": "SC_007",
            "specialization": ["AC", "Cooling"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_008 technicians (1 load)
        {
            "technician_id": "TECH_019",
            "name": "Sophie Anderson",
            "service_center_id": "SC_008",
            "specialization": ["Electrical", "Battery"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_020",
            "name": "Arjun Mehta",
            "service_center_id": "SC_008",
            "specialization": ["Engine", "Transmission"],
            "current_assignments": 0,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_009 technicians (0 load)
        {
            "technician_id": "TECH_021",
            "name": "Michael Chang",
            "service_center_id": "SC_009",
            "specialization": ["Brakes", "Suspension"],
            "current_assignments": 0,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_022",
            "name": "Riya Kapoor",
            "service_center_id": "SC_009",
            "specialization": ["AC", "Heating"],
            "current_assignments": 0,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_023",
            "name": "Daniel Kim",
            "service_center_id": "SC_009",
            "specialization": ["Electrical", "Battery"],
            "current_assignments": 0,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_010 technicians (6 load)
        {
            "technician_id": "TECH_024",
            "name": "Nisha Patel",
            "service_center_id": "SC_010",
            "specialization": ["Engine", "Turbo"],
            "current_assignments": 2,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_025",
            "name": "John Smith",
            "service_center_id": "SC_010",
            "specialization": ["Transmission", "Clutch"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_026",
            "name": "Ananya Rao",
            "service_center_id": "SC_010",
            "specialization": ["Brakes", "Tires"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_011 technicians (5 load)
        {
            "technician_id": "TECH_027",
            "name": "Tom Wilson",
            "service_center_id": "SC_011",
            "specialization": ["Engine", "Oil"],
            "current_assignments": 2,
            "max_capacity": 6,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_028",
            "name": "Kavya Nair",
            "service_center_id": "SC_011",
            "specialization": ["Electrical", "AC"],
            "current_assignments": 2,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_029",
            "name": "Ryan O'Connor",
            "service_center_id": "SC_011",
            "specialization": ["Suspension", "Steering"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        # SC_012 technicians (2 load)
        {
            "technician_id": "TECH_030",
            "name": "Isha Gupta",
            "service_center_id": "SC_012",
            "specialization": ["Engine", "Cooling"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_031",
            "name": "Lucas Silva",
            "service_center_id": "SC_012",
            "specialization": ["Battery", "Electrical"],
            "current_assignments": 1,
            "max_capacity": 5,
            "status": "available",
            "created_at": datetime.utcnow()
        },
        {
            "technician_id": "TECH_032",
            "name": "Aisha Khan",
            "service_center_id": "SC_012",
            "specialization": ["AC", "Heating"],
            "current_assignments": 0,
            "max_capacity": 4,
            "status": "available",
            "created_at": datetime.utcnow()
        }
    ]
    
    for technician in technicians:
        existing_tech = await db.technicians.find_one({"technician_id": technician["technician_id"]})
        if not existing_tech:
            await db.technicians.insert_one(technician)
            print(f"[OK] Created technician: {technician['name']} ({technician['technician_id']})")
        else:
            print(f"[SKIP] Technician already exists: {technician['technician_id']}")

    # ------------------------------------------------------------------
    # DEMO DATA FOR MANUFACTURING (FAILURE PATTERNS & RCA/CAPA INSIGHTS)
    # ------------------------------------------------------------------
    print("\n[STEP] Creating demo manufacturing failure patterns...")

    failure_patterns = [
        {
            "pattern_id": "PAT_HERO_ENGINE_OVERHEAT",
            "failure_type": "Engine Overheating",
            "component": "Engine Cooling System",
            "manufacturer": "Hero",
            "model": "Hero Splendor",
            "error_codes": ["P0217"],
            "occurrence_count": 8,
            "first_seen": datetime.utcnow() - timedelta(days=60),
            "last_seen": datetime.utcnow() - timedelta(days=2),
            "severity": "critical",
            "created_at": datetime.utcnow() - timedelta(days=60),
            "updated_at": datetime.utcnow()
        },
        {
            "pattern_id": "PAT_HERO_BRAKE_WEAR",
            "failure_type": "Brake Pad Wear",
            "component": "Braking System",
            "manufacturer": "Hero",
            "model": "Hero Splendor",
            "error_codes": ["P0521"],
            "occurrence_count": 5,
            "first_seen": datetime.utcnow() - timedelta(days=45),
            "last_seen": datetime.utcnow() - timedelta(days=5),
            "severity": "high",
            "created_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow()
        },
        {
            "pattern_id": "PAT_MAHINDRA_BATTERY",
            "failure_type": "Battery Drain",
            "component": "Electrical System",
            "manufacturer": "Mahindra",
            "model": "Mahindra XUV300",
            "error_codes": ["P0300"],
            "occurrence_count": 7,
            "first_seen": datetime.utcnow() - timedelta(days=50),
            "last_seen": datetime.utcnow() - timedelta(days=1),
            "severity": "high",
            "created_at": datetime.utcnow() - timedelta(days=50),
            "updated_at": datetime.utcnow()
        },
        {
            "pattern_id": "PAT_MAHINDRA_OIL_PRESSURE",
            "failure_type": "Low Oil Pressure",
            "component": "Engine Oil System",
            "manufacturer": "Mahindra",
            "model": "Mahindra XUV300",
            "error_codes": ["P0521"],
            "occurrence_count": 4,
            "first_seen": datetime.utcnow() - timedelta(days=40),
            "last_seen": datetime.utcnow() - timedelta(days=3),
            "severity": "medium",
            "created_at": datetime.utcnow() - timedelta(days=40),
            "updated_at": datetime.utcnow()
        },
    ]

    for pattern in failure_patterns:
        existing_pattern = await db.failure_patterns.find_one({"pattern_id": pattern["pattern_id"]})
        if not existing_pattern:
            await db.failure_patterns.insert_one(pattern)
            print(f"[OK] Created failure pattern: {pattern['pattern_id']} ({pattern['manufacturer']})")
        else:
            print(f"[SKIP] Failure pattern already exists: {pattern['pattern_id']}")

    # ------------------------------------------------------------------
    # DEMO DATA FOR ADMIN / UEBA (AGENT LOGS & SECURITY EVENTS)
    # ------------------------------------------------------------------
    print("\n[STEP] Creating demo agent logs and security events for admin panel...")

    # Simple, recent timestamps so they appear in last 24h window
    now = datetime.utcnow()

    agent_logs = [
        {
            "agent_name": "Master Agent",
            "action": "orchestrate_workflow",
            "timestamp": now - timedelta(minutes=10),
            "input_data": {"workflow": "monitor_and_predict"},
            "output_data": {"status": "success"},
            "execution_time_ms": 220.5,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.1,
            "is_anomaly": False,
        },
        {
            "agent_name": "Telemetry Agent",
            "action": "ingest_telemetry",
            "timestamp": now - timedelta(minutes=8),
            "input_data": {"vin": "VIN001"},
            "output_data": {"records_ingested": 50},
            "execution_time_ms": 150.2,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.15,
            "is_anomaly": False,
        },
        {
            "agent_name": "Failure Prediction Agent",
            "action": "predict_failure",
            "timestamp": now - timedelta(minutes=6),
            "input_data": {"vin": "VIN002"},
            "output_data": {"risk_score": 0.72},
            "execution_time_ms": 310.8,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.82,  # Slightly anomalous
            "is_anomaly": True,
        },
        {
            "agent_name": "Customer Engagement Agent",
            "action": "send_alert",
            "timestamp": now - timedelta(minutes=5),
            "input_data": {"customer_id": "CUST_001"},
            "output_data": {"notifications_sent": 1},
            "execution_time_ms": 180.0,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.2,
            "is_anomaly": False,
        },
        {
            "agent_name": "Smart Scheduling Agent",
            "action": "schedule",
            "timestamp": now - timedelta(minutes=4),
            "input_data": {"vin": "VIN001", "service_center_id": "SC_001"},
            "output_data": {"status": "success"},
            "execution_time_ms": 260.3,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.25,
            "is_anomaly": False,
        },
        {
            "agent_name": "UEBA Security Agent",
            "action": "analyze_logs",
            "timestamp": now - timedelta(minutes=2),
            "input_data": {},
            "output_data": {"anomaly_count": 1},
            "execution_time_ms": 420.7,
            "status": "success",
            "error_message": None,
            "anomaly_score": 0.9,
            "is_anomaly": True,
        },
    ]

    for log in agent_logs:
        await db.agent_logs.insert_one(log)

    # A couple of security events so the admin UEBA panel looks live
    security_events = [
        {
            "event_id": "SEC_DEMO_001",
            "event_type": "anomaly",
            "severity": "high",
            "agent_name": "Failure Prediction Agent",
            "user_id": None,
            "description": "Unusually high failure risk detected for Mahindra XUV300 vehicles.",
            "details": {
                "affected_vins": ["VIN002"],
                "risk_score": 0.82,
                "threshold": 0.7,
            },
            "detected_at": now - timedelta(minutes=3),
            "resolved": False,
            "resolved_at": None,
        },
        {
            "event_id": "SEC_DEMO_002",
            "event_type": "policy_violation",
            "severity": "medium",
            "agent_name": "Customer Engagement Agent",
            "user_id": "admin",
            "description": "Multiple alerts sent to the same customer within a short time window.",
            "details": {
                "customer_id": "CUST_001",
                "alerts_sent": 3,
                "time_window_minutes": 15,
            },
            "detected_at": now - timedelta(minutes=7),
            "resolved": True,
            "resolved_at": now - timedelta(minutes=1),
        },
    ]

    for event in security_events:
        existing_event = await db.security_events.find_one({"event_id": event["event_id"]})
        if not existing_event:
            await db.security_events.insert_one(event)
            print(f"[OK] Created security event: {event['event_id']}")
        else:
            print(f"[SKIP] Security event already exists: {event['event_id']}")

    # ------------------------------------------------------------------
    # DEMO DATA FOR SERVICE CENTER REVIEWS (COMPLETED APPOINTMENTS + FEEDBACK)
    # ------------------------------------------------------------------
    print("\n[STEP] Creating demo appointments and reviews for service centers...")
    
    # Create some completed appointments with reviews
    demo_appointments = [
        {
            "appointment_id": "APT_DEMO_001",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_001",
            "technician_id": "TECH_001",
            "scheduled_date": now - timedelta(days=5),
            "status": "completed",
            "service_type": "General Maintenance",
            "description": "Engine oil change and filter replacement",
            "predicted_issue": "Engine oil degradation",
            "created_at": now - timedelta(days=7),
            "updated_at": now - timedelta(days=5),
        },
        {
            "appointment_id": "APT_DEMO_002",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_002",
            "technician_id": "TECH_004",
            "scheduled_date": now - timedelta(days=10),
            "status": "completed",
            "service_type": "Electrical Repair",
            "description": "Battery replacement and charging system check",
            "predicted_issue": "Battery drain",
            "created_at": now - timedelta(days=12),
            "updated_at": now - timedelta(days=10),
        },
        {
            "appointment_id": "APT_DEMO_003",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_001",
            "technician_id": "TECH_002",
            "scheduled_date": now - timedelta(days=15),
            "status": "completed",
            "service_type": "Brake Service",
            "description": "Brake pad replacement and brake fluid flush",
            "predicted_issue": "Brake pad wear",
            "created_at": now - timedelta(days=17),
            "updated_at": now - timedelta(days=15),
        },
        {
            "appointment_id": "APT_DEMO_004",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_010",
            "technician_id": "TECH_028",
            "scheduled_date": now - timedelta(days=3),
            "status": "completed",
            "service_type": "AC Service",
            "description": "AC system cleaning and refrigerant recharge",
            "predicted_issue": "AC cooling system",
            "created_at": now - timedelta(days=5),
            "updated_at": now - timedelta(days=3),
        },
        {
            "appointment_id": "APT_DEMO_005",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_003",
            "technician_id": "TECH_007",
            "scheduled_date": now - timedelta(days=20),
            "status": "completed",
            "service_type": "Engine Repair",
            "description": "Cooling system flush and thermostat replacement",
            "predicted_issue": "Engine overheating",
            "created_at": now - timedelta(days=22),
            "updated_at": now - timedelta(days=20),
        },
        {
            "appointment_id": "APT_DEMO_006",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_002",
            "technician_id": "TECH_005",
            "scheduled_date": now - timedelta(days=7),
            "status": "completed",
            "service_type": "General Maintenance",
            "description": "Tire rotation and alignment check",
            "predicted_issue": "Tire wear",
            "created_at": now - timedelta(days=9),
            "updated_at": now - timedelta(days=7),
        },
        {
            "appointment_id": "APT_DEMO_007",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_010",
            "technician_id": "TECH_029",
            "scheduled_date": now - timedelta(days=12),
            "status": "completed",
            "service_type": "Electrical Repair",
            "description": "Alternator replacement and wiring check",
            "predicted_issue": "Electrical system",
            "created_at": now - timedelta(days=14),
            "updated_at": now - timedelta(days=12),
        },
        {
            "appointment_id": "APT_DEMO_008",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_001",
            "technician_id": "TECH_003",
            "scheduled_date": now - timedelta(days=18),
            "status": "completed",
            "service_type": "Transmission Service",
            "description": "Transmission fluid change and filter replacement",
            "predicted_issue": "Transmission maintenance",
            "created_at": now - timedelta(days=20),
            "updated_at": now - timedelta(days=18),
        },
        {
            "appointment_id": "APT_DEMO_009",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_010",
            "technician_id": "TECH_028",
            "scheduled_date": now - timedelta(days=25),
            "status": "completed",
            "service_type": "General Maintenance",
            "description": "Complete vehicle inspection and tune-up",
            "predicted_issue": "General maintenance",
            "created_at": now - timedelta(days=27),
            "updated_at": now - timedelta(days=25),
        },
        {
            "appointment_id": "APT_DEMO_010",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_010",
            "technician_id": "TECH_029",
            "scheduled_date": now - timedelta(days=30),
            "status": "completed",
            "service_type": "Engine Service",
            "description": "Engine diagnostics and performance optimization",
            "predicted_issue": "Engine performance",
            "created_at": now - timedelta(days=32),
            "updated_at": now - timedelta(days=30),
        },
    ]
    
    for apt in demo_appointments:
        existing_apt = await db.service_appointments.find_one({"appointment_id": apt["appointment_id"]})
        if not existing_apt:
            await db.service_appointments.insert_one(apt)
            print(f"[OK] Created appointment: {apt['appointment_id']}")
        else:
            print(f"[SKIP] Appointment already exists: {apt['appointment_id']}")
    
    # Create demo feedback/reviews for completed appointments
    demo_feedback = [
        {
            "feedback_id": "FB_DEMO_001",
            "appointment_id": "APT_DEMO_001",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_001",
            "rating": 5,
            "comments": "Excellent service! The technician was very professional and explained everything clearly. My bike is running smoothly now.",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=5),
        },
        {
            "feedback_id": "FB_DEMO_002",
            "appointment_id": "APT_DEMO_002",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_002",
            "rating": 4,
            "comments": "Good service overall. Battery replacement was done quickly. Could improve on communication about wait times.",
            "service_satisfaction": "satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=10),
        },
        {
            "feedback_id": "FB_DEMO_003",
            "appointment_id": "APT_DEMO_003",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_001",
            "rating": 5,
            "comments": "Outstanding work! Brakes feel brand new. The team was knowledgeable and courteous. Highly recommend!",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=15),
        },
        {
            "feedback_id": "FB_DEMO_004",
            "appointment_id": "APT_DEMO_004",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_010",
            "rating": 5,
            "comments": "AC is working perfectly now! Fast service and reasonable pricing. Will definitely come back.",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=3),
        },
        {
            "feedback_id": "FB_DEMO_005",
            "appointment_id": "APT_DEMO_005",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_003",
            "rating": 4,
            "comments": "Good service. Engine cooling issue resolved. Technician was helpful and explained the problem well.",
            "service_satisfaction": "satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=20),
        },
        {
            "feedback_id": "FB_DEMO_006",
            "appointment_id": "APT_DEMO_006",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_002",
            "rating": 5,
            "comments": "Perfect alignment job! Vehicle handles much better now. Professional service and clean facility.",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=7),
        },
        {
            "feedback_id": "FB_DEMO_007",
            "appointment_id": "APT_DEMO_007",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_010",
            "rating": 5,
            "comments": "Excellent electrical repair service! Alternator replacement was done efficiently. Very satisfied with the work.",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=12),
        },
        {
            "feedback_id": "FB_DEMO_008",
            "appointment_id": "APT_DEMO_008",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_001",
            "rating": 4,
            "comments": "Transmission service completed on time. Good quality work. Staff was friendly and professional.",
            "service_satisfaction": "satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=18),
        },
        # Additional reviews for SC_010 (Mahindra City Center) to show variety
        {
            "feedback_id": "FB_DEMO_009",
            "appointment_id": "APT_DEMO_009",
            "customer_id": "CUST_001",
            "vin": "VIN002",
            "service_center_id": "SC_010",
            "rating": 5,
            "comments": "Best service center in the city! Quick turnaround time and excellent customer service. Highly recommended!",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=25),
        },
        {
            "feedback_id": "FB_DEMO_010",
            "appointment_id": "APT_DEMO_010",
            "customer_id": "CUST_001",
            "vin": "VIN001",
            "service_center_id": "SC_010",
            "rating": 5,
            "comments": "Professional team and quality service. My vehicle is running like new. Will definitely return for future services.",
            "service_satisfaction": "very_satisfied",
            "issues_resolved": True,
            "created_at": now - timedelta(days=30),
        },
    ]
    
    for feedback in demo_feedback:
        existing_fb = await db.feedbacks.find_one({"feedback_id": feedback["feedback_id"]})
        if not existing_fb:
            await db.feedbacks.insert_one(feedback)
            print(f"[OK] Created feedback: {feedback['feedback_id']} (Rating: {feedback['rating']}/5)")
        else:
            print(f"[SKIP] Feedback already exists: {feedback['feedback_id']}")

    print("\n[SUCCESS] Demo data initialization complete!")
    print("\nYou can now login with:")
    print("  - customer / password123")
    print("  - service_center / password123")
    print("  - manufacturing / password123")
    print("  - admin / password123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(init_demo_data())

