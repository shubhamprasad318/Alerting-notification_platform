from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models.alert import Alert, SeverityEnum
from ..models.notification import NotificationDelivery, UserAlertPreference, NotificationStatusEnum, UserAlertStateEnum
from ..models.user import User, Team

class AnalyticsService:
    """Service for analytics and metrics tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system-wide analytics"""
        
        # Total alerts created
        total_alerts = self.db.query(Alert).count()
        
        # Active alerts
        active_alerts = self.db.query(Alert).filter(
            Alert.is_active == True,
            Alert.is_archived == False
        ).count()
        
        # Alerts by severity
        severity_breakdown = self.db.query(
            Alert.severity,
            func.count(Alert.id)
        ).group_by(Alert.severity).all()
        
        # Total deliveries
        total_deliveries = self.db.query(NotificationDelivery).count()
        
        # Successful deliveries
        successful_deliveries = self.db.query(NotificationDelivery).filter(
            NotificationDelivery.status == NotificationStatusEnum.SENT
        ).count()
        
        # Read vs unread alerts
        read_alerts = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.state == UserAlertStateEnum.READ
        ).count()
        
        unread_alerts = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.state == UserAlertStateEnum.UNREAD
        ).count()
        
        snoozed_alerts = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.state == UserAlertStateEnum.SNOOZED
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_alerts = self.db.query(Alert).filter(
            Alert.created_at >= week_ago
        ).count()
        
        return {
            "total_alerts_created": total_alerts,
            "active_alerts": active_alerts,
            "alerts_delivered": total_deliveries,
            "alerts_read": read_alerts,
            "delivery_success_rate": (successful_deliveries / max(total_deliveries, 1)) * 100,
            "severity_breakdown": {
                str(severity): count for severity, count in severity_breakdown
            },
            "alert_states": {
                "read": read_alerts,
                "unread": unread_alerts,
                "snoozed": snoozed_alerts
            },
            "recent_activity": {
                "alerts_last_7_days": recent_alerts
            }
        }
    
    def get_alert_performance(self, alert_id: int) -> Dict[str, Any]:
        """Get performance metrics for a specific alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {}
        
        # Total target users
        total_preferences = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.alert_id == alert_id
        ).count()
        
        # State breakdown
        state_breakdown = self.db.query(
            UserAlertPreference.state,
            func.count(UserAlertPreference.id)
        ).filter(
            UserAlertPreference.alert_id == alert_id
        ).group_by(UserAlertPreference.state).all()
        
        # Delivery metrics
        deliveries = self.db.query(NotificationDelivery).filter(
            NotificationDelivery.alert_id == alert_id
        ).count()
        
        return {
            "alert_id": alert_id,
            "alert_title": alert.title,
            "total_target_users": total_preferences,
            "total_deliveries": deliveries,
            "state_breakdown": {
                str(state): count for state, count in state_breakdown
            },
            "engagement_rate": (
                sum(count for state, count in state_breakdown if state != UserAlertStateEnum.UNREAD) /
                max(total_preferences, 1)
            ) * 100
        }
    
    async def track_alert_created(self, alert: Alert):
        """Track when an alert is created (called by observer)"""
        # In a real implementation, this could log to analytics systems,
        # update counters in cache, send to monitoring systems, etc.
        pass
    
    async def track_alert_updated(self, alert: Alert):
        """Track when an alert is updated"""
        pass
    
    async def track_alert_expired(self, alert: Alert):
        """Track when an alert expires"""
        pass
    
    def get_user_engagement_metrics(self) -> List[Dict[str, Any]]:
        """Get user engagement metrics"""
        # Most active users (by alert interactions)
        user_engagement = self.db.query(
            UserAlertPreference.user_id,
            User.name,
            func.count(UserAlertPreference.id).label('total_alerts'),
            func.sum(
                func.case(
                    (UserAlertPreference.state == UserAlertStateEnum.READ, 1),
                    else_=0
                )
            ).label('read_count')
        ).join(User).group_by(
            UserAlertPreference.user_id, User.name
        ).order_by(func.count(UserAlertPreference.id).desc()).limit(10).all()
        
        return [
            {
                "user_id": user_id,
                "user_name": name,
                "total_alerts": total_alerts,
                "read_count": read_count or 0,
                "read_rate": ((read_count or 0) / max(total_alerts, 1)) * 100
            }
            for user_id, name, total_alerts, read_count in user_engagement
        ]
