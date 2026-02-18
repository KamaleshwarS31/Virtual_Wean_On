"""
Test script to verify backend setup
"""
import sys

print("Testing imports...")

try:
    print("1. Testing pydantic...")
    from pydantic import BaseModel, EmailStr
    print("   ✅ Pydantic OK")
except Exception as e:
    print(f"   ❌ Pydantic failed: {e}")
    sys.exit(1)

try:
    print("2. Testing pydantic-settings...")
    from pydantic_settings import BaseSettings
    print("   ✅ Pydantic-settings OK")
except Exception as e:
    print(f"   ❌ Pydantic-settings failed: {e}")
    sys.exit(1)

try:
    print("3. Testing python-jose...")
    from jose import jwt
    print("   ✅ Python-jose OK")
except Exception as e:
    print(f"   ❌ Python-jose failed: {e}")
    sys.exit(1)

try:
    print("4. Testing passlib...")
    from passlib.context import CryptContext
    print("   ✅ Passlib OK")
except Exception as e:
    print(f"   ❌ Passlib failed: {e}")
    sys.exit(1)

try:
    print("5. Testing sqlalchemy...")
    from sqlalchemy import create_engine
    print("   ✅ SQLAlchemy OK")
except Exception as e:
    print(f"   ❌ SQLAlchemy failed: {e}")
    sys.exit(1)

try:
    print("6. Testing fastapi...")
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
except Exception as e:
    print(f"   ❌ FastAPI failed: {e}")
    sys.exit(1)

try:
    print("7. Testing app.config...")
    from app.config import settings
    print("   ✅ App config OK")
except Exception as e:
    print(f"   ❌ App config failed: {e}")
    sys.exit(1)

try:
    print("8. Testing app.models...")
    from app.models import Base, User
    print("   ✅ App models OK")
except Exception as e:
    print(f"   ❌ App models failed: {e}")
    sys.exit(1)

try:
    print("9. Testing app.main...")
    from app.main import app
    print("   ✅ App main OK")
except Exception as e:
    print(f"   ❌ App main failed: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! Backend is ready to run.")
print("\nStart the server with:")
print("  uvicorn app.main:app --reload")
