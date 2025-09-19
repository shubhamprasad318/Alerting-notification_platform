from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..services.alert_service import AlertService
from ..services.notification_service import NotificationService
from ..services.analytics_service import AnalyticsService
from ..patterns.observer import AlertSubject, NotificationObserver, AnalyticsObserver
from ..schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from ..models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    """Dependency to create AlertService with observers"""
    alert_subject = AlertSubject()
    
    # Attach observers
    notification_service = NotificationService(db)
    analytics_service = AnalyticsService(db)
    
    alert_subject.attach(NotificationObserver(notification_service))
    alert_subject.attach(AnalyticsObserver(analytics_service))
    
    return AlertService(db, alert_subject)

def get_current_admin_user() -> User:
    """Mock function to get current admin user - replace with proper authentication"""
    # In real implementation, extract from JWT token or session
    return User(id=1, name="Admin", email="admin@example.com", role="admin")

@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new alert"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        alert = await alert_service.create_alert(
            alert_data.dict(),
            current_user.id
        )
        return AlertResponse.from_orm(alert)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    update_data: AlertUpdate,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Update an existing alert"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    alert = await alert_service.update_alert(alert_id, update_data.dict(exclude_unset=True))
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse.from_orm(alert)

@router.delete("/alerts/{alert_id}")
async def archive_alert(
    alert_id: int,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Archive an alert"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = await alert_service.archive_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert archived successfully"}

@router.get("/alerts", response_model=List[AlertResponse])
async def get_admin_alerts(
    severity: Optional[str] = None,
    is_active: Optional[bool] = None,
    visibility_type: Optional[str] = None,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_admin_user)
):
    """Get alerts created by the admin with optional filters"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    filters = {}
    if severity:
        filters["severity"] = severity
    if is_active is not None:
        filters["is_active"] = is_active
    if visibility_type:
        filters["visibility_type"] = visibility_type
    
    alerts = alert_service.get_alerts_by_admin(current_user.id, filters)
    return [AlertResponse.from_orm(alert) for alert in alerts]

@router.post("/alerts/trigger-reminders")
async def trigger_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Manually trigger reminder processing (for testing/demo purposes)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    notification_service = NotificationService(db)
    await notification_service.process_reminders()
    
    return {"message": "Reminders processed"}
