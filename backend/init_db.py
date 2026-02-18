"""
Database Initialization Script
Creates tables and master admin account
"""

import sys
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, User, UserRole
from app.auth import get_password_hash
from app.config import settings

def init_database():
    """Initialize database with tables and master admin"""
    
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    db = SessionLocal()
    try:
        # Check if master admin exists
        master = db.query(User).filter(
            User.email == settings.MASTER_EMAIL,
            User.role == UserRole.MASTER
        ).first()
        
        if not master:
            print("👤 Creating master admin account...")
            master = User(
                email=settings.MASTER_EMAIL,
                hashed_password=get_password_hash(settings.MASTER_PASSWORD),
                role=UserRole.MASTER,
                is_verified=True,
                is_active=True
            )
            db.add(master)
            db.commit()
            print(f"✅ Master admin created: {settings.MASTER_EMAIL}")
        else:
            print(f"ℹ️  Master admin already exists: {settings.MASTER_EMAIL}")
        
        print("\n✅ Database initialization complete!")
        print(f"\nMaster Admin Credentials:")
        print(f"Email: {settings.MASTER_EMAIL}")
        print(f"Password: {settings.MASTER_PASSWORD}")
        print(f"\n⚠️  IMPORTANT: Change the master password after first login!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
