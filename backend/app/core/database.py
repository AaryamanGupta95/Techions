from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import PyMongoError
import asyncio
from app.core.config import settings


class MongoDB:
    client: AsyncIOMotorClient = None


db = MongoDB()


async def connect_to_mongo(retries: int = 3, timeout_ms: int = 5000):
    """Create database connection with retries and a server selection timeout.

    Returns the `Database` instance on success.
    """
    mongodb_url = settings.MONGODB_URL
    db_name = settings.MONGODB_DB_NAME

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            # Set a short server selection timeout so failures surface quickly
            db.client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=timeout_ms)
            # Test connection
            await db.client.admin.command("ping")
            print(f"Connected to MongoDB ({db_name}) on attempt {attempt}")
            return db.client[db_name]
        except (ConnectionFailure, ServerSelectionTimeoutError, PyMongoError) as e:
            last_err = e
            print(f"Attempt {attempt} - Failed to connect to MongoDB: {e}")
            # Close client before retrying
            try:
                if db.client:
                    db.client.close()
            except Exception:
                pass
            if attempt < retries:
                await asyncio.sleep(1 * attempt)

    # After retries, raise a clear error
    raise ConnectionFailure(
        f"Could not connect to MongoDB at '{mongodb_url}' after {retries} attempts. Last error: {last_err}"
    )


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        try:
            db.client.close()
            print("MongoDB connection closed")
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")


def get_database():
    """Get database instance.

    Raises a helpful error if the database client is not connected yet.
    """
    db_name = settings.MONGODB_DB_NAME
    if not db.client:
        raise RuntimeError(
            "MongoDB client is not initialized. Ensure the FastAPI app ran startup and `connect_to_mongo` succeeded."
        )
    return db.client[db_name]


async def init_database():
    """
    Initialize MongoDB database, collections and indexes.

    This runs automatically on FastAPI startup so that:
    - the `automotive_aftermarket` database exists
    - all required collections exist
    - important indexes are created (idempotent)
    """

    database = get_database()

    # Collections required by the application
    required_collections = [
        "users",
        "customers",
        "vehicles",
        "vehicle_telemetry",
        "service_centers",
        "technicians",
        "service_appointments",
        "feedbacks",
        "failure_patterns",
        "rcacapa_insights",
        "agent_logs",
        "security_events",
        "notifications",
        "chat_history",
    ]

    # Ensure collections exist (MongoDB creates DB/collections on first write)
    existing_collections = await database.list_collection_names()
    for name in required_collections:
        if name not in existing_collections:
            try:
                await database.create_collection(name)
                print(f"[DB] Created collection: {name}")
            except CollectionInvalid:
                # Collection was created in a race condition – safe to ignore
                pass

    # Create indexes (idempotent; MongoDB skips if already exist)
    await database.users.create_index("username", unique=True, name="idx_users_username_unique")
    await database.users.create_index("email", unique=True, name="idx_users_email_unique")

    await database.customers.create_index("customer_id", unique=True, name="idx_customers_id_unique")
    await database.customers.create_index("email", name="idx_customers_email")

    await database.vehicles.create_index("vin", unique=True, name="idx_vehicles_vin_unique")
    await database.vehicles.create_index("customer_id", name="idx_vehicles_customer_id")

    await database.vehicle_telemetry.create_index(
        [("vin", 1), ("timestamp", -1)], name="idx_telemetry_vin_timestamp"
    )

    await database.service_centers.create_index("center_id", unique=True, name="idx_centers_id_unique")

    await database.technicians.create_index(
        [("service_center_id", 1), ("technician_id", 1)], name="idx_tech_center_tech"
    )

    await database.service_appointments.create_index(
        [("customer_id", 1), ("scheduled_date", -1)], name="idx_appts_customer_date"
    )

    await database.agent_logs.create_index(
        [("agent_name", 1), ("timestamp", -1)], name="idx_agent_logs_agent_ts"
    )

    await database.security_events.create_index(
        [("event_type", 1), ("detected_at", -1)], name="idx_sec_events_type_ts"
    )

    print("[DB] Database initialization complete.")
