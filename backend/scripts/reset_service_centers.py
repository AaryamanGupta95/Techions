"""
Reset Service Centers Script
This script will DELETE all existing service centers and recreate them with available slots.
Use this if service centers have incorrect capacity/load data.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def reset_service_centers():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['automotive_aftermarket']  # Use correct database name
    
    print("Resetting service centers...")
    print("=" * 60)
    
    # Delete all existing service centers
    result = await db.service_centers.delete_many({})
    print(f"[OK] Deleted {result.deleted_count} existing service centers")
    
    # Create new service centers with available slots
    service_centers = [
        {
            "center_id": "SC_001",
            "name": "Hero Service Center Downtown",
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
    
    # Insert all service centers
    await db.service_centers.insert_many(service_centers)
    
    print(f"\n[SUCCESS] Created {len(service_centers)} service centers with available slots:\n")
    for sc in service_centers:
        available = sc['capacity'] - sc['current_load']
        print(f"  {sc['center_id']}: {sc['name']} - {available} slots available (Capacity: {sc['capacity']}, Load: {sc['current_load']})")
    
    print("\n[SUCCESS] Service centers reset complete!")
    print("You can now test the booking system with multiple available centers.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reset_service_centers())

