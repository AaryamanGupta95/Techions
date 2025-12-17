"""
Quick script to check if service centers exist in MongoDB
Run this to verify service centers are properly initialized
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_service_centers():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['automotive_aftermarket']  # Use correct database name
    
    print("Checking service centers in MongoDB...")
    print("=" * 60)
    
    centers = await db.service_centers.find({}).to_list(100)
    
    if len(centers) == 0:
        print("❌ No service centers found!")
        print("\nPlease run: python scripts/init_demo_data.py")
    else:
        print(f"✅ Found {len(centers)} service center(s):\n")
        for center in centers:
            capacity = center.get('capacity', 0)
            load = center.get('current_load', 0)
            available = capacity - load
            status = center.get('status', 'unknown')
            
            print(f"  {center.get('center_id')}: {center.get('name')}")
            print(f"    Status: {status}")
            print(f"    Capacity: {capacity}, Current Load: {load}, Available: {available}")
            print(f"    Address: {center.get('address', 'N/A')}")
            print()
        
        # Check if any have available slots
        available_centers = [c for c in centers if (c.get('capacity', 0) - c.get('current_load', 0)) > 0]
        if len(available_centers) == 0:
            print("⚠️  Warning: All service centers are at full capacity!")
        else:
            print(f"✅ {len(available_centers)} service center(s) have available slots")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_service_centers())

