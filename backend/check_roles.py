from app.database import SessionLocal
from app.models import User, UserRole

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"{'Email':<30} | {'Role':<10} | {'Is Active':<10}")
    print("-" * 55)
    for user in users:
        print(f"{user.email:<30} | {user.role:<10} | {user.is_active:<10}")
finally:
    db.close()
