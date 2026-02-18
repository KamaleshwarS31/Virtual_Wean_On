from app.database import engine
from app.models import Base

# Create missing tables
Base.metadata.create_all(bind=engine)
print("Created merchandise table successfully")
