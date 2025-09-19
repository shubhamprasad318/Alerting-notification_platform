from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class SeverityEnum(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class VisibilityTypeEnum(str, Enum):
    ORGANIZATION = "organization"
    TEAM = "team"
    USER = "user"

class AlertCreate(BaseModel):
    title: str
    message: str
    severity: SeverityEnum = SeverityEnum.INFO
    visibility_type: VisibilityTypeEnum = VisibilityTypeEnum.ORGANIZATION
    target_team_id: Optional[int] = None
    target_user_id: Optional[int] = None
    expiry_time: Optional[datetime] = None
    reminder_frequency_hours: int = 2

class AlertUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    expiry_time: Optional[datetime] = None
    is_active: Optional[bool] = None

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    message: str
    severity: str
    visibility_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
