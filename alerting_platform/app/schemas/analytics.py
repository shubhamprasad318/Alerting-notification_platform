from pydantic import BaseModel
from typing import Dict, Any, List

class SystemMetrics(BaseModel):
    total_alerts_created: int
    active_alerts: int
    alerts_delivered: int
    alerts_read: int
    delivery_success_rate: float
    severity_breakdown: Dict[str, int]
    alert_states: Dict[str, int]
    recent_activity: Dict[str, int]

class AlertPerformance(BaseModel):
    alert_id: int
    alert_title: str
    total_target_users: int
    total_deliveries: int
    state_breakdown: Dict[str, int]
    engagement_rate: float

class UserEngagement(BaseModel):
    user_id: int
    user_name: str
    total_alerts: int
    read_count: int
    read_rate: float
