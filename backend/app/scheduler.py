"""
Background Scheduler for Auto-Deletion
Handles automatic deletion of expired images
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import TryOnSession, GeneratedImage
from .storage import storage_manager

scheduler = BackgroundScheduler()

def cleanup_expired_uploads():
    """Delete uploaded images that have expired (2 hours)"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        expired_sessions = db.query(TryOnSession).filter(
            TryOnSession.expires_at <= now
        ).all()
        
        deleted_count = 0
        for session in expired_sessions:
            # Delete from storage
            if session.uploaded_image_path:
                storage_manager.delete_file(session.uploaded_image_path)
            
            # Update database (keep metadata, remove path)
            session.uploaded_image_path = None
            session.uploaded_image_url = None
            deleted_count += 1
        
        db.commit()
        print(f"✅ Cleaned up {deleted_count} expired uploaded images")
        
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def cleanup_expired_generated():
    """Delete generated images that have expired (end of day)"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        expired_images = db.query(GeneratedImage).filter(
            GeneratedImage.expires_at <= now
        ).all()
        
        deleted_count = 0
        for image in expired_images:
            # Delete from storage
            if image.image_path:
                storage_manager.delete_file(image.image_path)
            
            # Update database (keep metadata, remove path)
            image.image_path = None
            image.image_url = None
            deleted_count += 1
        
        db.commit()
        print(f"✅ Cleaned up {deleted_count} expired generated images")
        
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler"""
    # Run cleanup every hour
    scheduler.add_job(cleanup_expired_uploads, 'interval', hours=1, id='cleanup_uploads')
    scheduler.add_job(cleanup_expired_generated, 'interval', hours=1, id='cleanup_generated')
    
    # Run cleanup at midnight daily
    scheduler.add_job(cleanup_expired_generated, 'cron', hour=0, minute=0, id='daily_cleanup')
    
    scheduler.start()
    print("✅ Scheduler started - Auto-deletion active")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
