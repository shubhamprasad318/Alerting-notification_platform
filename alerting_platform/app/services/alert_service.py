from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.alert import Alert, SeverityEnum, VisibilityTypeEnum
from ..models.user import User, Team
from ..models.notification import UserAlertPreference, UserAlertStateEnum
from ..patterns.observer import AlertSubject
from ..patterns.state import AlertStateContext

class AlertService:
    """Service for managing alerts with proper separation of concerns"""
    
    def __init__(self, db: Session, alert_subject: AlertSubject):
        self.db = db
        self.alert_subject = alert_subject
    
    async def create_alert(self, alert_data: Dict[str, Any], created_by: int) -> Alert:
        """Create a new alert and notify observers"""
        alert = Alert(
            title=alert_data["title"],
            message=alert_data["message"],
            severity=SeverityEnum(alert_data.get("severity", "info")),
            visibility_type=VisibilityTypeEnum(alert_data.get("visibility_type", "organization")),
            target_team_id=alert_data.get("target_team_id"),
            target_user_id=alert_data.get("target_user_id"),
            expiry_time=alert_data.get("expiry_time"),
            reminder_frequency_hours=alert_data.get("reminder_frequency_hours", 2),
            created_by=created_by
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # Create user preferences for all target users
        await self._create_user_preferences(alert)
        
        # Notify observers
        await self.alert_subject.notify_created(alert)
        
        return alert
    
    async def update_alert(self, alert_id: int, update_data: Dict[str, Any]) -> Optional[Alert]:
        """Update an existing alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        for key, value in update_data.items():
            if hasattr(alert, key):
                setattr(alert, key, value)
        
        alert.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alert)
        
        await self.alert_subject.notify_updated(alert)
        return alert
    
    async def archive_alert(self, alert_id: int) -> bool:
        """Archive an alert"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        alert.is_archived = True
        alert.is_active = False
        alert.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_alerts_by_admin(self, admin_id: int, filters: Dict[str, Any] = None) -> List[Alert]:
        """Get alerts created by admin with optional filters"""
        query = self.db.query(Alert).filter(Alert.created_by == admin_id)
        
        if filters:
            if "severity" in filters:
                query = query.filter(Alert.severity == filters["severity"])
            if "is_active" in filters:
                query = query.filter(Alert.is_active == filters["is_active"])
            if "visibility_type" in filters:
                query = query.filter(Alert.visibility_type == filters["visibility_type"])
        
        return query.order_by(Alert.created_at.desc()).all()
    
    def get_alerts_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get alerts visible to a specific user with their preference state"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Get alerts based on visibility
        alerts_query = self.db.query(Alert).filter(
            Alert.is_active == True,
            Alert.is_archived == False
        )
        
        # Filter by visibility rules
        visibility_filter = (
            (Alert.visibility_type == VisibilityTypeEnum.ORGANIZATION) |
            (Alert.visibility_type == VisibilityTypeEnum.USER, Alert.target_user_id == user_id) |
            (Alert.visibility_type == VisibilityTypeEnum.TEAM, Alert.target_team_id.in_([team.id for team in user.teams]))
        )
        
        alerts = alerts_query.filter(visibility_filter).all()
        
        # Enrich with user preferences
        result = []
        for alert in alerts:
            preference = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.alert_id == alert.id,
                UserAlertPreference.user_id == user_id
            ).first()
            
            result.append({
                "alert": alert,
                "state": preference.state.value if preference else "unread",
                "snoozed_until": preference.snoozed_until if preference else None,
                "read_at": preference.read_at if preference else None
            })
        
        return result
    
    async def _create_user_preferences(self, alert: Alert):
        """Create user alert preferences for all target users"""
        target_users = self._get_target_users(alert)
        
        for user in target_users:
            existing_preference = self.db.query(UserAlertPreference).filter(
                UserAlertPreference.alert_id == alert.id,
                UserAlertPreference.user_id == user.id
            ).first()
            
            if not existing_preference:
                preference = UserAlertPreference(
                    alert_id=alert.id,
                    user_id=user.id,
                    state=UserAlertStateEnum.UNREAD
                )
                self.db.add(preference)
        
        self.db.commit()
    
    def _get_target_users(self, alert: Alert) -> List[User]:
        """Get all users that should receive this alert based on visibility"""
        if alert.visibility_type == VisibilityTypeEnum.ORGANIZATION:
            return self.db.query(User).all()
        elif alert.visibility_type == VisibilityTypeEnum.TEAM and alert.target_team_id:
            team = self.db.query(Team).filter(Team.id == alert.target_team_id).first()
            return team.members if team else []
        elif alert.visibility_type == VisibilityTypeEnum.USER and alert.target_user_id:
            user = self.db.query(User).filter(User.id == alert.target_user_id).first()
            return [user] if user else []
        
        return []
