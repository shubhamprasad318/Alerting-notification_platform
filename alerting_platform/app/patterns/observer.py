from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.alert import Alert

class AlertObserver(ABC):
    """Observer pattern for alert events"""
    
    @abstractmethod
    async def on_alert_created(self, alert: Alert) -> None:
        pass
    
    @abstractmethod
    async def on_alert_updated(self, alert: Alert) -> None:
        pass
    
    @abstractmethod
    async def on_alert_expired(self, alert: Alert) -> None:
        pass

class NotificationObserver(AlertObserver):
    """Observer that handles notifications when alerts change"""
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
    
    async def on_alert_created(self, alert: Alert) -> None:
        """Trigger initial notifications when alert is created"""
        await self.notification_service.process_new_alert(alert)
    
    async def on_alert_updated(self, alert: Alert) -> None:
        """Handle alert updates"""
        if alert.is_active:
            await self.notification_service.process_alert_update(alert)
    
    async def on_alert_expired(self, alert: Alert) -> None:
        """Clean up when alert expires"""
        await self.notification_service.process_alert_expiry(alert)

class AnalyticsObserver(AlertObserver):
    """Observer that tracks analytics for alerts"""
    
    def __init__(self, analytics_service):
        self.analytics_service = analytics_service
    
    async def on_alert_created(self, alert: Alert) -> None:
        await self.analytics_service.track_alert_created(alert)
    
    async def on_alert_updated(self, alert: Alert) -> None:
        await self.analytics_service.track_alert_updated(alert)
    
    async def on_alert_expired(self, alert: Alert) -> None:
        await self.analytics_service.track_alert_expired(alert)

class AlertSubject:
    """Subject class for observer pattern"""
    
    def __init__(self):
        self._observers: List[AlertObserver] = []
    
    def attach(self, observer: AlertObserver) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: AlertObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    
    async def notify_created(self, alert: Alert) -> None:
        for observer in self._observers:
            await observer.on_alert_created(alert)
    
    async def notify_updated(self, alert: Alert) -> None:
        for observer in self._observers:
            await observer.on_alert_updated(alert)
    
    async def notify_expired(self, alert: Alert) -> None:
        for observer in self._observers:
            await observer.on_alert_expired(alert)
