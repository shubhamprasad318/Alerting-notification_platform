from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import sessionmaker
from ..database import SessionLocal
from ..services.notification_service import NotificationService
import asyncio

def setup_scheduler(scheduler: AsyncIOScheduler):
    """Setup recurring jobs for reminder processing"""
    
    async def process_reminders():
        """Job function to process reminders every 2 hours"""
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            await notification_service.process_reminders()
        finally:
            db.close()
    
    # Schedule reminder processing every 2 hours
    scheduler.add_job(
        process_reminders,
        'interval',
        hours=2,
        id='reminder_processor',
        replace_existing=True
    )
