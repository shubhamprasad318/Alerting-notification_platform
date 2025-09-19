from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
import asyncio

from .database import create_tables, get_db
from .routers import admin, user, analytics
from .services.notification_service import NotificationService
from .core.scheduler import setup_scheduler

# Scheduler instance
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    create_tables()
    setup_scheduler(scheduler)
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(
    title="Alerting & Notification Platform",
    description="A comprehensive alerting system with admin controls and user management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {
        "message": "Alerting & Notification Platform API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
