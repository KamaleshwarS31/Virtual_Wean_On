"""
Authentication Routes
Student signup, login, OTP verification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models import User, OTPVerification, UserRole, InteractionCount
from ..auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    decode_access_token,
    generate_otp,
    validate_college_email
)
from ..email_service import email_service

router = APIRouter()
security = HTTPBearer()

# Pydantic Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    admin_qr_data: Optional[str] = None  # QR code data from admin

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    admin_id: Optional[int] = None
    location_id: Optional[int] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ... (get_current_user implementation remains same)

# ... (signup implementation) ...

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Student login"""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Track interaction if admin/location provided
    if request.admin_id and request.location_id:
        try:
            interaction = InteractionCount(
                admin_id=request.admin_id,
                location_id=request.location_id,
                student_email=user.email
            )
            db.add(interaction)
            db.commit()
        except Exception as e:
            # Don't block login if tracking fails
            print(f"Interaction tracking error: {e}")
            pass
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user

@router.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Student signup - immediate verification (no OTP)"""
    
    # Validate college email
    if not validate_college_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use a valid VIT college email address (@vitstudent.ac.in or @vit.ac.in)"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create verified user immediately (no OTP needed)
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        role=UserRole.STUDENT,
        is_verified=True,  # Auto-verified
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Track interaction if QR data provided
    if request.admin_qr_data:
        try:
            parts = request.admin_qr_data.split(":")
            if len(parts) == 2:
                admin_id, location_id = int(parts[0]), int(parts[1])
                interaction = InteractionCount(
                    admin_id=admin_id,
                    location_id=location_id,
                    student_email=request.email
                )
                db.add(interaction)
                db.commit()
        except:
            pass
    
    # Generate access token immediately
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role.value})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role.value
        }
    )

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and activate user account"""
    
    # Find valid OTP
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.email == request.email,
        OTPVerification.otp_code == request.otp,
        OTPVerification.is_used == False,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Mark OTP as used
    otp_record.is_used = True
    
    # Activate user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    db.commit()
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )



@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_verified": current_user.is_verified
    }

class GoogleAuthRequest(BaseModel):
    id_token: str
    email: str
    admin_id: Optional[int] = None
    location_id: Optional[int] = None

class InteractionRequest(BaseModel):
    admin_id: int
    location_id: int

@router.post("/interaction")
async def record_interaction(
    request: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record interaction for logged-in user"""
    try:
        interaction = InteractionCount(
            admin_id=request.admin_id,
            location_id=request.location_id,
            student_email=current_user.email
        )
        db.add(interaction)
        db.commit()
    except:
        pass
    return {"status": "recorded"}

@router.post("/google-auth", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Google OAuth authentication"""
    
    # Validate VIT email
    if not validate_college_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use a valid VIT college email address"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Create new user with Google auth
        user = User(
            email=request.email,
            hashed_password="",  # No password for Google auth
            role=UserRole.STUDENT,
            is_verified=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Track interaction if admin/location provided
    if request.admin_id and request.location_id:
        try:
            interaction = InteractionCount(
                admin_id=request.admin_id,
                location_id=request.location_id,
                student_email=user.email
            )
            db.add(interaction)
            db.commit()
        except:
            pass
            
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )

