"""
Admin Routes
Admin login, QR generation, approval management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
import qrcode
import io
import base64

from ..database import get_db
from ..models import User, Admin, Location, ImageApproval, GeneratedImage, TryOnSession, ApprovalStatus, InteractionCount, UserRole
from ..auth import verify_password, create_access_token
from ..email_service import email_service
from ..storage import storage_manager
from .auth import get_current_user

router = APIRouter()

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class SelectLocationRequest(BaseModel):
    location_id: int

class ApprovalActionRequest(BaseModel):
    notes: Optional[str] = None

# Dependency to ensure admin role
async def get_current_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Admin:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin profile not found"
        )
    
    if not admin.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled"
        )
    
    return admin

@router.post("/login")
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login"""
    
    user = db.query(User).filter(
        User.email == request.email,
        User.role == UserRole.ADMIN
    ).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    admin = db.query(Admin).filter(Admin.user_id == user.id).first()
    if not admin or not admin.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": user.email,
            "location_id": admin.location_id
        }
    }

@router.get("/locations")
async def get_locations(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all active locations"""
    
    locations = db.query(Location).filter(Location.is_active == True).all()
    
    return {
        "locations": [
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description
            }
            for loc in locations
        ]
    }

@router.post("/select-location")
async def select_location(
    request: SelectLocationRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Select location and generate QR code"""
    
    # Verify location exists
    location = db.query(Location).filter(
        Location.id == request.location_id,
        Location.is_active == True
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Update admin location
    current_admin.location_id = request.location_id
    
    # Generate QR code data (URL for redirection)
    # In production, this should come from environment variable
    frontend_url = "http://localhost:3000"
    qr_data = f"{frontend_url}/login?admin_id={current_admin.id}&location_id={request.location_id}"
    current_admin.qr_code_data = qr_data
    
    db.commit()
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "message": "Location selected",
        "location": {
            "id": location.id,
            "name": location.name
        },
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "qr_data": qr_data
    }

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get pending approval queue for admin's location"""
    
    if not current_admin.location_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a location first"
        )
    
    # Get pending approvals from students who scanned this admin's QR
    pending = db.query(ImageApproval, GeneratedImage, TryOnSession, User).join(
        GeneratedImage, ImageApproval.image_id == GeneratedImage.id
    ).join(
        TryOnSession, GeneratedImage.session_id == TryOnSession.id
    ).join(
        User, TryOnSession.user_id == User.id
    ).filter(
        ImageApproval.status == ApprovalStatus.PENDING,
        TryOnSession.admin_id == current_admin.id
    ).order_by(ImageApproval.created_at.asc()).all()
    
    result = []
    for approval, image, session, user in pending:
        if image.image_path:
            preview_url = storage_manager.get_signed_url(image.image_path, expires_in=1800)
            
            result.append({
                "approval_id": approval.id,
                "image_id": image.id,
                "student_email": user.email,
                "merch_type": session.merch_type,
                "merch_design": session.merch_design,
                "preview_url": preview_url,
                "created_at": approval.created_at.isoformat()
            })
    
    return {
        "pending_approvals": result,
        "count": len(result)
    }

@router.post("/approve/{approval_id}")
async def approve_image(
    approval_id: int,
    request: ApprovalActionRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a try-on image"""
    
    approval = db.query(ImageApproval).filter(ImageApproval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval already processed"
        )
    
    # Update approval
    approval.status = ApprovalStatus.APPROVED
    approval.admin_id = current_admin.id
    approval.reviewed_at = func.now()
    approval.notes = request.notes
    
    db.commit()
    
    # Get student email for notification
    image = db.query(GeneratedImage).join(TryOnSession).join(User).filter(
        GeneratedImage.id == approval.image_id
    ).first()
    
    if image and image.session.user:
        email_service.send_approval_notification(image.session.user.email, approved=True)
    
    return {
        "message": "Image approved",
        "approval_id": approval.id
    }

@router.post("/reject/{approval_id}")
async def reject_image(
    approval_id: int,
    request: ApprovalActionRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a try-on image"""
    
    approval = db.query(ImageApproval).filter(ImageApproval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found"
        )
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval already processed"
        )
    
    # Update approval
    approval.status = ApprovalStatus.REJECTED
    approval.admin_id = current_admin.id
    approval.reviewed_at = func.now()
    approval.notes = request.notes
    
    db.commit()
    
    # Get student email for notification
    image = db.query(GeneratedImage).join(TryOnSession).join(User).filter(
        GeneratedImage.id == approval.image_id
    ).first()
    
    if image and image.session.user:
        email_service.send_approval_notification(image.session.user.email, approved=False)
    
    return {
        "message": "Image rejected",
        "approval_id": approval.id
    }

@router.get("/stats")
async def get_admin_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
    
    # Total interactions (QR scans)
    total_scans = db.query(InteractionCount).filter(
        InteractionCount.admin_id == current_admin.id
    ).count()
    
    # Unique students
    unique_students = db.query(func.count(func.distinct(InteractionCount.student_email))).filter(
        InteractionCount.admin_id == current_admin.id
    ).scalar()
    
    # Approvals processed
    approvals_processed = db.query(ImageApproval).filter(
        ImageApproval.admin_id == current_admin.id
    ).count()
    
    # Pending approvals
    pending_count = db.query(ImageApproval).filter(
        ImageApproval.status == ApprovalStatus.PENDING
    ).count()
    
    return {
        "total_scans": total_scans,
        "unique_students": unique_students,
        "approvals_processed": approvals_processed,
        "pending_approvals": pending_count,
        "location": {
            "id": current_admin.location_id,
            "name": current_admin.location.name if current_admin.location else None
        }
    }

@router.get("/qr-code")
async def get_qr_code(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin's QR code"""
    
    if not current_admin.location_id or not current_admin.qr_code_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location not selected"
        )
        
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(current_admin.qr_code_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "qr_code": f"data:image/png;base64,{qr_base64}",
        "qr_data": current_admin.qr_code_data
    }
