from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..services.alert_service import AlertService
from ..services.notification_service import NotificationService
from ..patterns.observer import AlertSubject, NotificationObserver
from ..models.user import User

router = APIRouter(prefix="/user", tags=["user"])

def get_current_user() -> User:
    """Mock function - replace with proper authentication"""
    return User(id=1, name="Test User", email="user@example.com", role="user")

def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    alert_subject = AlertSubject()
    notification_service = NotificationService(db)
    alert_subject.attach(NotificationObserver(notification_service))
    return AlertService(db, alert_subject)

@router.get("/alerts")
async def get_user_alerts(
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_user)
):
    """Get alerts for the current user"""
    alerts = alert_service.get_alerts_for_user(current_user.id)
    return alerts

@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an alert as read"""
    notification_service = NotificationService(db)
    success = await notification_service.mark_alert_read(current_user.id, alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert marked as read"}

@router.post("/alerts/{alert_id}/snooze")
async def snooze_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Snooze an alert until end of day"""
    notification_service = NotificationService(db)
    success = await notification_service.snooze_alert(current_user.id, alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert snoozed until end of day"}
