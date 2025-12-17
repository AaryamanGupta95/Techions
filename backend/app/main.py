from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from app.core.database import connect_to_mongo, close_mongo_connection, init_database
from app.core.config import settings
from app.api import routes, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup: try to connect and initialize database (collections + indexes).
    # If DB is unavailable, log and continue so the API (and CORS middleware)
    # still start and can return informative errors to the frontend.
    try:
        await connect_to_mongo()
        try:
            await init_database()
        except Exception as e:
            print(f"Warning: database initialization failed: {e}")
    except Exception as e:
        print(f"Warning: could not connect to MongoDB during startup: {e}")

    yield

    # Shutdown - close connection if present
    try:
        await close_mongo_connection()
    except Exception as e:
        print(f"Warning: error while closing MongoDB connection: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS middleware - Allow all origins in development
# Note: Cannot use "*" with allow_credentials=True, so we specify origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(routes.router, prefix="/api/v1", tags=["API"])


@app.get("/")
async def root():
    return {
        "message": "Connected Intelligence Hub API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
