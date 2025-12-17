"""
Quick script to fix customer_id for the "customer" user
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_customer_id():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['automotive_aftermarket']
    
    # Update user to have customer_id
    result = await db.users.update_one(
        {"username": "customer"},
        {"$set": {"customer_id": "CUST_001"}}
    )
    
    if result.modified_count > 0:
        print("[OK] Updated user 'customer' with customer_id='CUST_001'")
    else:
        print("[SKIP] User 'customer' already has customer_id or doesn't exist")
    
    # Verify
    user = await db.users.find_one({"username": "customer"})
    if user:
        print(f"[OK] User customer_id: {user.get('customer_id', 'NOT SET')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_customer_id())

