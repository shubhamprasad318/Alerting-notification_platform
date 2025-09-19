from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.analytics_service import AnalyticsService
from ..schemas.analytics import SystemMetrics, AlertPerformance, UserEngagement
from ..models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_current_admin_user() -> User:
    """Mock function - replace with proper authentication"""
    return User(id=1, name="Admin", email="admin@example.com", role="admin")

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Get system-wide analytics metrics"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    metrics = analytics_service.get_system_metrics()
    return SystemMetrics(**metrics)

@router.get("/alerts/{alert_id}", response_model=AlertPerformance)
async def get_alert_performance(
    alert_id: int,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Get performance metrics for a specific alert"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    performance = analytics_service.get_alert_performance(alert_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertPerformance(**performance)

@router.get("/users/engagement", response_model=List[UserEngagement])
async def get_user_engagement(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user engagement metrics"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    engagement = analytics_service.get_user_engagement_metrics()
    return [UserEngagement(**item) for item in engagement]
