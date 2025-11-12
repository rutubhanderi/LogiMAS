from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .api.routers import admin, ai_router, auth, delivery, order, inventory, analytics,shipment,warehouse,vehicle
from .config import settings
import logging

# Import models to register them with Base
from .models import (
    Customer,
    Warehouse,
    Vehicle,
    Order,
    Shipment,
    Inventory,
    VehicleTelemetry,
    FuelPrice,
    PackagingType,
    Document,
    AgentAuditLog,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    try:
        logger.info("Attempting to create database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Could not create database tables at startup: {e}")
        logger.warning("Tables will be created on first database access")

    yield

    logger.info("Application shutting down")

app = FastAPI(
    title="LogiMAS API",
    version="1.0.0",
    description="Logistics Management System API with JWT Authentication",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin - User Management"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(delivery.router, prefix="/api/v1/delivery", tags=["Delivery"])
app.include_router(ai_router.router, prefix="/ai", tags=["AI"])
app.include_router(order.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(shipment.router, prefix="/api/v1/shipments", tags=["Shipments"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(warehouse.router, prefix="/api/v1/warehouses", tags=["Warehouses"])
app.include_router(vehicle.router, prefix="/api/v1/vehicles", tags=["Vehicles"])

@app.get("/api/health", tags=["Health Check"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}

@app.get("/api/health/db", tags=["Health Check"])
def database_health_check():
    """Database health check endpoint"""
    from sqlalchemy import text
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "message": "Database connection successful",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "message": "Database connection failed",
            "database": "disconnected",
            "error": str(e),
        }
