from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from ..database import Base

class NotificationStatusEnum(enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"

class UserAlertStateEnum(enum.Enum):
    UNREAD = "unread"
    READ = "read"
    SNOOZED = "snoozed"

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    delivery_type = Column(String)
    status = Column(Enum(NotificationStatusEnum))
    delivered_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    alert = relationship("Alert", back_populates="deliveries")
    user = relationship("User", back_populates="notification_deliveries")

class UserAlertPreference(Base):
    __tablename__ = "user_alert_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    state = Column(Enum(UserAlertStateEnum), default=UserAlertStateEnum.UNREAD)
    snoozed_until = Column(DateTime, nullable=True)
    last_reminded_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alert_preferences")
    alert = relationship("Alert", back_populates="user_preferences")
