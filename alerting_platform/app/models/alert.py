from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class SeverityEnum(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class DeliveryTypeEnum(enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"

class VisibilityTypeEnum(enum.Enum):
    ORGANIZATION = "organization"
    TEAM = "team"
    USER = "user"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    message = Column(Text)
    severity = Column(Enum(SeverityEnum), default=SeverityEnum.INFO)
    delivery_type = Column(Enum(DeliveryTypeEnum), default=DeliveryTypeEnum.IN_APP)
    visibility_type = Column(Enum(VisibilityTypeEnum), default=VisibilityTypeEnum.ORGANIZATION)
    
    # Targeting
    target_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Scheduling
    start_time = Column(DateTime, default=datetime.utcnow)
    expiry_time = Column(DateTime)
    reminder_frequency_hours = Column(Integer, default=2)
    
    # Management
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    target_team = relationship("Team", foreign_keys=[target_team_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    user_preferences = relationship("UserAlertPreference", back_populates="alert")
    deliveries = relationship("NotificationDelivery", back_populates="alert")
