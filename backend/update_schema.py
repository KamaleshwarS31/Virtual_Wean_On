from app.database import engine
from sqlalchemy import text

def add_columns():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE try_on_sessions ADD COLUMN admin_id INTEGER REFERENCES admins(id);"))
            conn.commit()
            print("Added admin_id column successfully")
        except Exception as e:
            print(f"Did not add admin_id (might exist): {e}")
            
        try:
            conn.execute(text("ALTER TABLE try_on_sessions ADD COLUMN location_id INTEGER REFERENCES locations(id);"))
            conn.commit()
            print("Added location_id column successfully")
        except Exception as e:
            print(f"Did not add location_id (might exist): {e}")

if __name__ == "__main__":
    add_columns()
