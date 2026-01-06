from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.utils.logger_config import get_logger
import os

# Import all models to ensure they're registered with Base
from app.models import models

# Create logger
logger = get_logger()

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

# Create FastAPI app
app = FastAPI(
    title="Mahendra Hardware Inventory API",
    description="Inventory management system for hardware shop",
    version="1.0.0"
)

# Configure CORS for Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./inventory.db')}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Mahendra Hardware Inventory API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

# Import and include routers
from app.routers import categories, qualities, sizes, items, suppliers, sales, purchases, invoices, settings

app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(qualities.router, prefix="/api/qualities", tags=["qualities"])
app.include_router(sizes.router, prefix="/api/sizes", tags=["sizes"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["suppliers"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["purchases"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# TODO: Add remaining routers
# from app.routers import reports, audit
# app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
# app.include_router(audit.router, prefix="/api/audit-logs", tags=["audit"])


