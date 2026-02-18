"""
Master Admin Routes
Manage admins, locations, and view global statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import os
import shutil
import tempfile

from ..database import get_db
from ..models import User, Admin, Location, ImageApproval, InteractionCount, UserRole, ApprovalStatus, GeneratedImage, TryOnSession, Merchandise
from ..storage import storage_manager
from ..auth import get_password_hash, verify_password, create_access_token
from .auth import get_current_user

router = APIRouter()

class MasterLoginRequest(BaseModel):
    email: str
    password: str

class CreateAdminRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class CreateLocationRequest(BaseModel):
    name: str
    description: Optional[str] = None

class ToggleAdminRequest(BaseModel):
    is_enabled: bool

# Dependency to ensure master role
async def get_current_master(current_user: User = Depends(get_current_user)) -> User:
    # Use .value to be safe with enum comparisons across different environments
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    if role_val != UserRole.MASTER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Master admin access required (current role: {role_val})"
        )
    return current_user

@router.post("/login")
async def master_login(request: MasterLoginRequest, db: Session = Depends(get_db)):
    """Master admin login"""
    
    user = db.query(User).filter(
        User.email == request.email,
        User.role == UserRole.MASTER
    ).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role.value
        }
    }

@router.post("/create-admin")
async def create_admin(
    request: CreateAdminRequest,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Create a new admin account"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(request.password)
    new_user = User(
        email=request.email,
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        is_verified=True,  # Admins are pre-verified
        is_active=True
    )
    db.add(new_user)
    db.flush()
    
    # Create admin profile
    new_admin = Admin(
        user_id=new_user.id,
        name=request.name,
        is_enabled=True
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return {
        "message": "Admin created successfully",
        "admin": {
            "id": new_admin.id,
            "name": new_admin.name,
            "email": new_user.email
        }
    }

@router.get("/admins")
async def get_all_admins(
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Get all admins with their statistics"""
    
    admins = db.query(Admin).join(User).all()
    
    result = []
    for admin in admins:
        # Get stats
        total_scans = db.query(InteractionCount).filter(
            InteractionCount.admin_id == admin.id
        ).count()
        
        unique_students = db.query(func.count(func.distinct(InteractionCount.student_email))).filter(
            InteractionCount.admin_id == admin.id
        ).scalar()
        
        approvals_count = db.query(ImageApproval).filter(
            ImageApproval.admin_id == admin.id
        ).count()
        
        result.append({
            "id": admin.id,
            "name": admin.name,
            "email": admin.user.email,
            "location": {
                "id": admin.location_id,
                "name": admin.location.name if admin.location else None
            } if admin.location_id else None,
            "is_enabled": admin.is_enabled,
            "stats": {
                "total_scans": total_scans,
                "unique_students": unique_students,
                "approvals_processed": approvals_count
            },
            "created_at": admin.created_at.isoformat()
        })
    
    return {
        "admins": result,
        "total_count": len(result)
    }

@router.post("/toggle-admin/{admin_id}")
async def toggle_admin(
    admin_id: int,
    request: ToggleAdminRequest,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Enable or disable an admin account"""
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    admin.is_enabled = request.is_enabled
    db.commit()
    
    return {
        "message": f"Admin {'enabled' if request.is_enabled else 'disabled'}",
        "admin_id": admin.id,
        "is_enabled": admin.is_enabled
    }

@router.post("/create-location")
async def create_location(
    request: CreateLocationRequest,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Create a new location"""
    
    # Check if location name already exists
    existing = db.query(Location).filter(Location.name == request.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location name already exists"
        )
    
    new_location = Location(
        name=request.name,
        description=request.description,
        is_active=True
    )
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return {
        "message": "Location created successfully",
        "location": {
            "id": new_location.id,
            "name": new_location.name,
            "description": new_location.description
        }
    }

@router.get("/locations")
async def get_all_locations(
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Get all locations with statistics"""
    
    locations = db.query(Location).all()
    
    result = []
    for location in locations:
        # Get stats
        total_scans = db.query(InteractionCount).filter(
            InteractionCount.location_id == location.id
        ).count()
        
        unique_students = db.query(func.count(func.distinct(InteractionCount.student_email))).filter(
            InteractionCount.location_id == location.id
        ).scalar()
        
        admin_count = db.query(Admin).filter(
            Admin.location_id == location.id
        ).count()
        
        result.append({
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "is_active": location.is_active,
            "stats": {
                "total_scans": total_scans,
                "unique_students": unique_students,
                "admin_count": admin_count
            },
            "created_at": location.created_at.isoformat()
        })
    
    return {
        "locations": result,
        "total_count": len(result)
    }

@router.get("/global-stats")
async def get_global_stats(
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Get global system statistics"""
    
    # Total users
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    verified_students = db.query(User).filter(
        User.role == UserRole.STUDENT,
        User.is_verified == True
    ).count()
    
    # Total admins
    total_admins = db.query(Admin).count()
    active_admins = db.query(Admin).filter(Admin.is_enabled == True).count()
    
    # Total locations
    total_locations = db.query(Location).count()
    active_locations = db.query(Location).filter(Location.is_active == True).count()
    
    # Total interactions
    total_scans = db.query(InteractionCount).count()
    unique_students_scanned = db.query(func.count(func.distinct(InteractionCount.student_email))).scalar()
    
    # Approvals
    total_approvals = db.query(ImageApproval).count()
    pending_approvals = db.query(ImageApproval).filter(
        ImageApproval.status == ApprovalStatus.PENDING
    ).count()
    approved_count = db.query(ImageApproval).filter(
        ImageApproval.status == ApprovalStatus.APPROVED
    ).count()
    rejected_count = db.query(ImageApproval).filter(
        ImageApproval.status == ApprovalStatus.REJECTED
    ).count()
    
    return {
        "students": {
            "total": total_students,
            "verified": verified_students
        },
        "admins": {
            "total": total_admins,
            "active": active_admins
        },
        "locations": {
            "total": total_locations,
            "active": active_locations
        },
        "interactions": {
            "total_scans": total_scans,
            "unique_students": unique_students_scanned
        },
        "approvals": {
            "total": total_approvals,
            "pending": pending_approvals,
            "approved": approved_count,
            "rejected": rejected_count
        }
    }

@router.post("/override-approval/{approval_id}")
async def override_approval(
    approval_id: int,
    approved: bool,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Master can override any approval decision"""
    
    approval = db.query(ImageApproval).filter(ImageApproval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
    approval.reviewed_at = func.now()
    approval.notes = f"Overridden by Master Admin"
    
    db.commit()
    
    return {
        "message": "Approval overridden",
        "approval_id": approval.id,
        "status": approval.status.value
    }

@router.get("/approvals")
async def get_all_approvals(
    limit: int = 50,
    offset: int = 0,
    status: Optional[ApprovalStatus] = None,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Get all approvals (pending, approved, rejected)"""
    
    # Join chain: ImageApproval -> GeneratedImage -> TryOnSession -> User
    query = db.query(ImageApproval).join(GeneratedImage).join(TryOnSession).join(User)
    
    if status:
        query = query.filter(ImageApproval.status == status)
        
    # Order by most recent first
    query = query.order_by(ImageApproval.created_at.desc())
    
    total = query.count()
    approvals = query.offset(offset).limit(limit).all()
    
    result = []
    for approval in approvals:
        image_url = None
        if approval.image and approval.image.image_path:
            image_url = storage_manager.get_signed_url(approval.image.image_path, expires_in=3600)
        
        user_email = "Unknown"
        if approval.image and approval.image.session and approval.image.session.user:
            user_email = approval.image.session.user.email

        result.append({
            "id": approval.id,
            "image_url": image_url,
            "user_email": user_email,
            "status": approval.status.value,
            "created_at": approval.created_at.isoformat(),
            "reviewed_at": approval.reviewed_at.isoformat() if approval.reviewed_at else None,
            "admin_id": approval.admin_id,
            "notes": approval.notes
        })
        
    return {
        "approvals": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }

# Merchandise Management
@router.post("/merch")
async def create_merch(
    name: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Add new merchandise with image"""
    
    # Save file
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload
        upload_result = storage_manager.upload_file(temp_path, folder="merch")
        
        # Create record
        merch = Merchandise(
            name=name,
            category=category,
            image_path=upload_result['path'],
            is_active=True
        )
        db.add(merch)
        db.commit()
        db.refresh(merch)
        
        return {
            "message": "Merchandise added",
            "merch": {
                "id": merch.id,
                "name": merch.name,
                "category": merch.category,
                "image_url": storage_manager.get_signed_url(merch.image_path)
            }
        }
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@router.get("/merch")
async def list_merch(
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """List all merchandise"""
    merch_list = db.query(Merchandise).all()
    
    result = []
    for m in merch_list:
        result.append({
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "image_url": storage_manager.get_signed_url(m.image_path, expires_in=3600),
            "is_active": m.is_active
        })
    return {"merch": result}

@router.delete("/merch/{merch_id}")
async def delete_merch(
    merch_id: int,
    current_master: User = Depends(get_current_master),
    db: Session = Depends(get_db)
):
    """Delete merchandise"""
    merch = db.query(Merchandise).filter(Merchandise.id == merch_id).first()
    if not merch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Merchandise not found"
        )
    
    db.delete(merch)
    db.commit()
    return {"message": "Merchandise deleted"}
