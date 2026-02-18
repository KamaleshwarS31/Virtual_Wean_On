"""
Try-On Routes
Upload, generate, and download virtual try-on images
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import os
import tempfile
import shutil

from ..database import get_db
from ..models import User, TryOnSession, GeneratedImage, ImageApproval, ApprovalStatus, Merchandise
from ..tryon_engine import TryOnEngine
from ..storage import storage_manager
from ..config import settings
from .auth import get_current_user

router = APIRouter()
tryon_engine = TryOnEngine()

# File validation
ALLOWED_EXTENSIONS = settings.ALLOWED_EXTENSIONS.split(',')
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

def validate_file(file: UploadFile):
    """Validate uploaded file"""
    # Check extension
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read first chunk to estimate)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    return True

@router.get("/merch")
async def list_available_merch(db: Session = Depends(get_db)):
    """List available merchandise"""
    merch_list = db.query(Merchandise).filter(Merchandise.is_active == True).all()
    
    result = []
    for m in merch_list:
        result.append({
            "id": str(m.id),
            "name": m.name,
            "image_url": storage_manager.get_signed_url(m.image_path, expires_in=3600),
            "category": m.category
        })
    return {"merch": result}

@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    admin_id: Optional[int] = Form(None),
    location_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user photo for try-on"""
    
    # Validate file
    validate_file(file)
    
    # Check try-on limit
    session_count = db.query(TryOnSession).filter(
        TryOnSession.user_id == current_user.id
    ).count()
    
    if session_count >= settings.MAX_TRYON_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum {settings.MAX_TRYON_PER_USER} try-ons allowed per user"
        )
    
    # Save file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to Supabase
        upload_result = storage_manager.upload_file(temp_path, folder="uploads")
        
        # Create session
        session = TryOnSession(
            user_id=current_user.id,
            uploaded_image_path=upload_result['path'],
            merch_type="",  # Will be set during generation
            merch_design="",
            expires_at=datetime.utcnow() + timedelta(hours=settings.UPLOADED_IMAGE_RETENTION_HOURS),
            admin_id=admin_id,
            location_id=location_id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "session_id": session.id,
            "message": "Photo uploaded successfully",
            "expires_at": session.expires_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

@router.post("/generate/{session_id}")
async def generate_tryon(
    session_id: int,
    merch_type: str = Form(...),
    merch_design: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate virtual try-on image"""
    
    # Get session
    session = db.query(TryOnSession).filter(
        TryOnSession.id == session_id,
        TryOnSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if not session.uploaded_image_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session image has expired"
        )
    
    # Update session with merch info
    session.merch_type = merch_type
    session.merch_design = merch_design
    
    # Download images to temp files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Get uploaded image
        uploaded_url = storage_manager.get_signed_url(session.uploaded_image_path)
        uploaded_temp = os.path.join(temp_dir, "uploaded.jpg")
        
        # Download or copy uploaded image
        if uploaded_url.startswith("/"):
            # Local file handling
            local_path = uploaded_url.lstrip("/")
            # Handle potential leading slash if lstrip behaves differently or if url is absolute path?
            # get_signed_url returns f"/storage/{file_path}"
            if local_path.startswith("/"): local_path = local_path[1:]
            
            if not os.path.exists(local_path):
                 raise HTTPException(status_code=404, detail=f"Source image file missing: {local_path}")
            shutil.copy(local_path, uploaded_temp)
        else:
            # Remote URL handling
            import requests
            response = requests.get(uploaded_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to retrieve source image")
            with open(uploaded_temp, 'wb') as f:
                f.write(response.content)
        
        # Get merch template
        merch_path = ""
        merch_record = None
        
        # Check if it's a DB ID
        if merch_design.isdigit():
            merch_record = db.query(Merchandise).filter(Merchandise.id == int(merch_design)).first()
            
        if merch_record:
            # Download from storage
            merch_url = storage_manager.get_signed_url(merch_record.image_path)
            temp_merch = os.path.join(temp_dir, f"merch_{merch_record.id}.png")
            
            if merch_url.startswith("/"):
                # Local file handling
                local_merch_path = merch_url.lstrip("/")
                if local_merch_path.startswith("/"): local_merch_path = local_merch_path[1:]
                
                if not os.path.exists(local_merch_path):
                     raise HTTPException(status_code=404, detail=f"Merchandise image file missing: {local_merch_path}")
                shutil.copy(local_merch_path, temp_merch)
                merch_path = temp_merch
            else:
                import requests
                resp = requests.get(merch_url)
                if resp.status_code == 200:
                    with open(temp_merch, 'wb') as f:
                        f.write(resp.content)
                    merch_path = temp_merch
                else:
                     raise HTTPException(status_code=400, detail="Failed to download merch image")
        else:
            # Fallback to local assets
            merch_path = os.path.join("assets", "merch", f"{merch_design}.png")
            if not os.path.exists(merch_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Merch design not found"
                )
        
        # Generate try-on
        result_image, processing_time = tryon_engine.apply_tryon(uploaded_temp, merch_path)
        
        # Save result
        result_temp = os.path.join(temp_dir, "result.jpg")
        import cv2
        cv2.imwrite(result_temp, result_image)
        
        # Upload result to storage
        upload_result = storage_manager.upload_file(result_temp, folder="generated")
        
        # Calculate end of day for expiration
        now = datetime.utcnow()
        end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
        if now.hour >= 23:
            end_of_day += timedelta(days=1)
        
        # Create generated image record
        generated = GeneratedImage(
            session_id=session.id,
            image_path=upload_result['path'],
            processing_time_ms=processing_time,
            expires_at=end_of_day
        )
        db.add(generated)
        db.flush()  # Generate ID for approval record
        
        # Create approval record
        approval = ImageApproval(
            image_id=generated.id,
            status=ApprovalStatus.PENDING
        )
        db.add(approval)
        
        db.commit()
        db.refresh(generated)
        
        # Get preview URL
        preview_url = storage_manager.get_signed_url(generated.image_path, expires_in=3600)
        
        return {
            "image_id": generated.id,
            "preview_url": preview_url,
            "processing_time_ms": processing_time,
            "status": "pending_approval",
            "message": "Try-on generated! Waiting for admin approval."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )
    finally:
        # Cleanup temp files
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

@router.get("/my-sessions")
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's try-on sessions"""
    
    sessions = db.query(TryOnSession).filter(
        TryOnSession.user_id == current_user.id
    ).order_by(TryOnSession.created_at.desc()).all()
    
    result = []
    for session in sessions:
        session_data = {
            "id": session.id,
            "merch_type": session.merch_type,
            "merch_design": session.merch_design,
            "created_at": session.created_at.isoformat(),
            "uploaded_image_url": storage_manager.get_signed_url(session.uploaded_image_path, expires_in=3600) if session.uploaded_image_path else None,
            "images": []
        }
        
        for image in session.generated_images:
            approval = image.approval
            image_data = {
                "id": image.id,
                "status": approval.status.value if approval else "unknown",
                "created_at": image.created_at.isoformat(),
                "can_download": approval and approval.status == ApprovalStatus.APPROVED
            }
            
            # Add preview URL if image still exists
            if image.image_path:
                image_data["preview_url"] = storage_manager.get_signed_url(image.image_path, expires_in=1800)
            
            session_data["images"].append(image_data)
        
        result.append(session_data)
    
    return {
        "sessions": result,
        "total_sessions": len(sessions),
        "remaining_tryons": settings.MAX_TRYON_PER_USER - len(sessions)
    }

@router.get("/download/{image_id}")
async def download_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download approved try-on image"""
    
    # Get image with approval
    image = db.query(GeneratedImage).join(TryOnSession).filter(
        GeneratedImage.id == image_id,
        TryOnSession.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Check approval status
    if not image.approval or image.approval.status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Image not approved for download"
        )
    
    if not image.image_path:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Image has expired and been deleted"
        )
    
    # Generate download URL (valid for 1 hour)
    download_url = storage_manager.get_signed_url(image.image_path, expires_in=3600)
    
    return {
        "download_url": download_url,
        "expires_in": 3600,
        "message": "Download link valid for 1 hour"
    }
