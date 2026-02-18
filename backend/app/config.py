from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET: str = "virtual-tryon"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png"
    
    # Try-On Limits
    MAX_TRYON_PER_USER: int = 5
    
    # Image Retention
    UPLOADED_IMAGE_RETENTION_HOURS: int = 2
    GENERATED_IMAGE_RETENTION_HOURS: int = 24
    
    # Master Admin
    MASTER_EMAIL: str
    MASTER_PASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
