from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from ..models.alert import Alert
from ..models.user import User
from ..models.notification import NotificationDelivery, UserAlertPreference, NotificationStatusEnum, UserAlertStateEnum
from ..patterns.notification_strategy import NotificationContext
from ..patterns.state import AlertStateContext

class NotificationService:
    """Service for handling notification delivery and user interactions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_context = NotificationContext()
        self.state_contexts = {}
    
    async def process_new_alert(self, alert: Alert):
        """Process notifications for a newly created alert"""
        target_users = self._get_alert_target_users(alert)
        
        for user in target_users:
            await self._send_notification(user, alert)
    
    async def process_alert_update(self, alert: Alert):
        """Handle alert updates - may trigger new notifications"""
        # For updated alerts, we might want to send notifications again
        # depending on the update type
        target_users = self._get_alert_target_users(alert)
        
        for user in target_users:
            preference = self._get_user_preference(user.id, alert.id)
            if preference and preference.state != UserAlertStateEnum.READ:
                await self._send_notification(user, alert)
    
    async def process_alert_expiry(self, alert: Alert):
        """Clean up expired alerts"""
        # Mark all preferences as expired or clean up
        preferences = self.db.query(UserAlertPreference).filter(
            UserAlertPreference.alert_id == alert.id
        ).all()
        
        for preference in preferences:
            # Could add an "expired" state or just leave as-is
            pass
    
    async def mark_alert_read(self, user_id: int, alert_id: int) -> bool:
        """Mark an alert as read for a user using state pattern"""
        preference = self._get_user_preference(user_id, alert_id)
        if not preference:
            return False
        
        state_context = self._get_state_context(preference.state.value)
        new_state = state_context.get_current_state().mark_read(preference)
        
        preference.state = UserAlertStateEnum(new_state.get_state_name())
        preference.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def snooze_alert(self, user_id: int, alert_id: int, until: datetime = None) -> bool:
        """Snooze an alert for a user using state pattern"""
        preference = self._get_user_preference(user_id, alert_id)
        if not preference:
            return False
        
        state_context = self._get_state_context(preference.state.value)
        new_state = state_context.get_current_state().snooze(preference, until)
        
        preference.state = UserAlertStateEnum(new_state.get_state_name())
        preference.updated_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def process_reminders(self):
        """Process all pending reminders - called by scheduler"""
        # Get all active alerts with pending reminders
        active_preferences = self.db.query(UserAlertPreference).join(Alert).filter(
            Alert.is_active == True,
            Alert.is_archived == False,
            UserAlertPreference.state != UserAlertStateEnum.READ
        ).all()
        
        for preference in active_preferences:
            state_context = self._get_state_context(preference.state.value)
            
            if state_context.get_current_state().should_remind(preference):
                user = self.db.query(User).filter(User.id == preference.user_id).first()
                alert = self.db.query(Alert).filter(Alert.id == preference.alert_id).first()
                
                if user and alert:
                    await self._send_notification(user, alert)
                    preference.last_reminded_at = datetime.utcnow()
        
        self.db.commit()
    
    async def _send_notification(self, user: User, alert: Alert) -> Dict[str, Any]:
        """Send notification using strategy pattern"""
        strategy = self.notification_context.get_strategy(alert.delivery_type.value)
        
        try:
            result = await strategy.send_notification(user, alert)
            
            # Log delivery
            delivery = NotificationDelivery(
                alert_id=alert.id,
                user_id=user.id,
                delivery_type=strategy.get_channel_name(),
                status=NotificationStatusEnum.SENT if result.get("status") == "sent" else NotificationStatusEnum.FAILED
            )
            
            self.db.add(delivery)
            self.db.commit()
            
            return result
            
        except Exception as e:
            # Log failed delivery
            delivery = NotificationDelivery(
                alert_id=alert.id,
                user_id=user.id,
                delivery_type=strategy.get_channel_name(),
                status=NotificationStatusEnum.FAILED,
                error_message=str(e)
            )
            
            self.db.add(delivery)
            self.db.commit()
            
            return {"status": "failed", "error": str(e)}
    
    def _get_alert_target_users(self, alert: Alert) -> List[User]:
        """Get target users for an alert based on visibility settings"""
        if alert.visibility_type.value == "organization":
            return self.db.query(User).all()
        elif alert.visibility_type.value == "team" and alert.target_team_id:
            from ..models.user import Team
            team = self.db.query(Team).filter(Team.id == alert.target_team_id).first()
            return team.members if team else []
        elif alert.visibility_type.value == "user" and alert.target_user_id:
            user = self.db.query(User).filter(User.id == alert.target_user_id).first()
            return [user] if user else []
        
        return []
    
    def _get_user_preference(self, user_id: int, alert_id: int) -> UserAlertPreference:
        """Get user preference for an alert"""
        return self.db.query(UserAlertPreference).filter(
            UserAlertPreference.user_id == user_id,
            UserAlertPreference.alert_id == alert_id
        ).first()
    
    def _get_state_context(self, state_name: str) -> AlertStateContext:
        """Get or create state context for managing state transitions"""
        if state_name not in self.state_contexts:
            self.state_contexts[state_name] = AlertStateContext(state_name)
        return self.state_contexts[state_name]
