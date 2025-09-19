import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the app directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database and all models
from app.database import engine, Base
from app.models.user import User, Team  # Import User and Team models
from app.models.alert import Alert, SeverityEnum, VisibilityTypeEnum  # Import Alert models
from app.models.notification import NotificationDelivery, UserAlertPreference, NotificationStatusEnum, UserAlertStateEnum  # Import Notification models

from datetime import datetime, timedelta

def create_tables():
    """Create all database tables"""
    print("🔄 Creating database tables...")
    
    # This will create all tables defined in the imported models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def create_seed_data():
    """Create initial test data"""
    
    # First, create all tables
    create_tables()
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🌱 Creating seed data...")
        
        # Check if data already exists
        existing_teams = db.query(Team).count()
        if existing_teams > 0:
            print("⚠️  Seed data already exists. Skipping...")
            return
        
        # Create teams
        engineering_team = Team(
            name="Engineering", 
            description="Software development team"
        )
        marketing_team = Team(
            name="Marketing", 
            description="Marketing and communications team"
        )
        
        db.add(engineering_team)
        db.add(marketing_team)
        db.flush()  # This gets the IDs without committing
        
        print(f"📂 Created teams: Engineering (ID: {engineering_team.id}), Marketing (ID: {marketing_team.id})")
        
        # Create users
        admin_user = User(
            name="Admin User",
            email="admin@example.com",
            role="admin"
        )
        
        eng_user1 = User(
            name="John Developer",
            email="john@example.com",
            role="user"
        )
        
        eng_user2 = User(
            name="Jane Engineer",
            email="jane@example.com",
            role="user"
        )
        
        marketing_user = User(
            name="Mike Marketer",
            email="mike@example.com",
            role="user"
        )
        
        db.add_all([admin_user, eng_user1, eng_user2, marketing_user])
        db.flush()  # Get user IDs
        
        print(f"👤 Created users: Admin (ID: {admin_user.id}), John (ID: {eng_user1.id}), Jane (ID: {eng_user2.id}), Mike (ID: {marketing_user.id})")
        
        # Add users to teams
        engineering_team.members.extend([eng_user1, eng_user2])
        marketing_team.members.append(marketing_user)
        
        # Commit team and user data
        db.commit()
        
        # Create sample alerts
        org_alert = Alert(
            title="System Maintenance Scheduled",
            message="The system will be down for maintenance on Saturday from 2-4 AM EST.",
            severity=SeverityEnum.WARNING,
            visibility_type=VisibilityTypeEnum.ORGANIZATION,
            expiry_time=datetime.now() + timedelta(days=7),
            created_by=admin_user.id
        )
        
        team_alert = Alert(
            title="Code Review Required",
            message="Please review the pending pull requests in the main repository.",
            severity=SeverityEnum.INFO,
            visibility_type=VisibilityTypeEnum.TEAM,
            target_team_id=engineering_team.id,
            expiry_time=datetime.now() + timedelta(days=3),
            created_by=admin_user.id
        )
        
        critical_alert = Alert(
            title="Production Issue Detected",
            message="High error rate detected in payment processing service.",
            severity=SeverityEnum.CRITICAL,
            visibility_type=VisibilityTypeEnum.TEAM,
            target_team_id=engineering_team.id,
            expiry_time=datetime.now() + timedelta(hours=24),
            created_by=admin_user.id
        )
        
        db.add_all([org_alert, team_alert, critical_alert])
        db.commit()
        
        print("🚨 Created sample alerts:")
        print(f"   - System Maintenance (ID: {org_alert.id})")
        print(f"   - Code Review Required (ID: {team_alert.id})")
        print(f"   - Production Issue (ID: {critical_alert.id})")
        
        print("\n✅ Seed data created successfully!")
        print(f"👤 Admin User ID: {admin_user.id} (email: {admin_user.email})")
        print(f"👥 Engineering Team ID: {engineering_team.id}")
        print(f"👥 Marketing Team ID: {marketing_team.id}")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
