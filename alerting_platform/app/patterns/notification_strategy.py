from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.user import User
from ..models.alert import Alert

class NotificationStrategy(ABC):
    """Strategy pattern for different notification delivery methods"""
    
    @abstractmethod
    async def send_notification(self, user: User, alert: Alert) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        pass

class InAppNotificationStrategy(NotificationStrategy):
    """In-app notification strategy (MVP implementation)"""
    
    async def send_notification(self, user: User, alert: Alert) -> Dict[str, Any]:
        # For MVP, we just mark as "sent" - in real implementation, 
        # this could push to WebSocket connections, store in cache, etc.
        return {
            "status": "sent",
            "channel": "in_app",
            "user_id": user.id,
            "alert_id": alert.id,
            "message": f"Alert: {alert.title}"
        }
    
    def get_channel_name(self) -> str:
        return "in_app"

class EmailNotificationStrategy(NotificationStrategy):
    """Email notification strategy (future implementation)"""
    
    async def send_notification(self, user: User, alert: Alert) -> Dict[str, Any]:
        # Future implementation - integrate with email service
        return {
            "status": "not_implemented",
            "channel": "email",
            "user_id": user.id,
            "alert_id": alert.id
        }
    
    def get_channel_name(self) -> str:
        return "email"

class SMSNotificationStrategy(NotificationStrategy):
    """SMS notification strategy (future implementation)"""
    
    async def send_notification(self, user: User, alert: Alert) -> Dict[str, Any]:
        # Future implementation - integrate with SMS service
        return {
            "status": "not_implemented",
            "channel": "sms",
            "user_id": user.id,
            "alert_id": alert.id
        }
    
    def get_channel_name(self) -> str:
        return "sms"

class NotificationContext:
    """Context class for strategy pattern"""
    
    def __init__(self):
        self._strategies = {
            "in_app": InAppNotificationStrategy(),
            "email": EmailNotificationStrategy(),
            "sms": SMSNotificationStrategy()
        }
    
    def get_strategy(self, channel: str) -> NotificationStrategy:
        return self._strategies.get(channel, self._strategies["in_app"])
    
    def add_strategy(self, channel: str, strategy: NotificationStrategy):
        """Allows adding new notification strategies dynamically"""
        self._strategies[channel] = strategy
