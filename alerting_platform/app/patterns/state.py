from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

class AlertState(ABC):
    """State pattern for alert user preferences"""
    
    @abstractmethod
    def mark_read(self, preference) -> 'AlertState':
        pass
    
    @abstractmethod
    def snooze(self, preference, until: Optional[datetime] = None) -> 'AlertState':
        pass
    
    @abstractmethod
    def should_remind(self, preference) -> bool:
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        pass

class UnreadState(AlertState):
    def mark_read(self, preference) -> AlertState:
        preference.read_at = datetime.utcnow()
        return ReadState()
    
    def snooze(self, preference, until: Optional[datetime] = None) -> AlertState:
        if until is None:
            # Snooze until end of day
            until = datetime.now().replace(hour=23, minute=59, second=59)
        preference.snoozed_until = until
        return SnoozedState()
    
    def should_remind(self, preference) -> bool:
        if preference.last_reminded_at is None:
            return True
        
        time_since_last_reminder = datetime.utcnow() - preference.last_reminded_at
        return time_since_last_reminder.total_seconds() >= preference.alert.reminder_frequency_hours * 3600
    
    def get_state_name(self) -> str:
        return "unread"

class ReadState(AlertState):
    def mark_read(self, preference) -> AlertState:
        # Already read, no state change
        return self
    
    def snooze(self, preference, until: Optional[datetime] = None) -> AlertState:
        if until is None:
            until = datetime.now().replace(hour=23, minute=59, second=59)
        preference.snoozed_until = until
        return SnoozedState()
    
    def should_remind(self, preference) -> bool:
        # Don't remind for read alerts
        return False
    
    def get_state_name(self) -> str:
        return "read"

class SnoozedState(AlertState):
    def mark_read(self, preference) -> AlertState:
        preference.read_at = datetime.utcnow()
        # Clear snooze when marked as read
        preference.snoozed_until = None
        return ReadState()
    
    def snooze(self, preference, until: Optional[datetime] = None) -> AlertState:
        # Already snoozed, update snooze time if provided
        if until:
            preference.snoozed_until = until
        return self
    
    def should_remind(self, preference) -> bool:
        if preference.snoozed_until is None:
            return True
        
        # Check if snooze period has expired
        if datetime.utcnow() > preference.snoozed_until:
            # Reset to unread state for next day
            preference.snoozed_until = None
            return True
        
        return False
    
    def get_state_name(self) -> str:
        return "snoozed"

class AlertStateContext:
    """Context for managing alert state transitions"""
    
    def __init__(self, initial_state: str = "unread"):
        self._states = {
            "unread": UnreadState(),
            "read": ReadState(),
            "snoozed": SnoozedState()
        }
        self._current_state = self._states[initial_state]
    
    def get_current_state(self) -> AlertState:
        return self._current_state
    
    def set_state(self, state_name: str):
        if state_name in self._states:
            self._current_state = self._states[state_name]
