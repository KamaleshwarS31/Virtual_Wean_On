from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"
    MASTER = "master"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    try_on_sessions = relationship("TryOnSession", back_populates="user")
    
class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    is_enabled = Column(Boolean, default=True)
    qr_code_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    location = relationship("Location", back_populates="admins")
    approvals = relationship("ImageApproval", back_populates="admin")
    interactions = relationship("InteractionCount", back_populates="admin")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    admins = relationship("Admin", back_populates="location")
    interactions = relationship("InteractionCount", back_populates="location")

class TryOnSession(Base):
    __tablename__ = "try_on_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_image_path = Column(String, nullable=False)
    uploaded_image_url = Column(Text, nullable=True)
    merch_type = Column(String, nullable=False)  # tshirt, hoodie, etc.
    merch_design = Column(String, nullable=False)  # design identifier
    num_people_detected = Column(Integer, default=1)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True) # Booth tracking
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True) # Location tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Auto-delete time
    
    # Relationships
    user = relationship("User", back_populates="try_on_sessions")
    generated_images = relationship("GeneratedImage", back_populates="session")
    admin = relationship("Admin")
    location = relationship("Location")

class GeneratedImage(Base):
    __tablename__ = "generated_images"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("try_on_sessions.id"), nullable=False)
    image_path = Column(String, nullable=False)
    image_url = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # End of day deletion
    
    # Relationships
    session = relationship("TryOnSession", back_populates="generated_images")
    approval = relationship("ImageApproval", back_populates="image", uselist=False)

class ImageApproval(Base):
    __tablename__ = "image_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("generated_images.id"), unique=True, nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("GeneratedImage", back_populates="approval")
    admin = relationship("Admin", back_populates="approvals")

class InteractionCount(Base):
    __tablename__ = "interaction_counts"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    student_email = Column(String, nullable=False)  # Track unique students
    scanned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = relationship("Admin", back_populates="interactions")
    location = relationship("Location", back_populates="interactions")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)

class Merchandise(Base):
    __tablename__ = "merchandise"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # t-shirt, hoodie
    image_path = Column(String, nullable=False) # storage path
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
