from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

# Association table for many-to-many relationship between users and teams
user_team_association = Table(
    'user_teams',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    teams = relationship("Team", secondary=user_team_association, back_populates="members")
    alert_preferences = relationship("UserAlertPreference", back_populates="user")
    notification_deliveries = relationship("NotificationDelivery", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship("User", secondary=user_team_association, back_populates="teams")
