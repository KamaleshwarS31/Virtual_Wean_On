"""
Supabase Storage Manager
Handles file uploads, signed URLs, and auto-deletion
Falls back to local storage if Supabase is not configured
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not installed - using local storage")
from PIL import Image
import io
from .config import settings

class StorageManager:
    def __init__(self):
        self.supabase = None
        self.bucket_name = None
        self.enabled = False
        
        if SUPABASE_AVAILABLE and hasattr(settings, 'SUPABASE_URL'):
            try:
                self.supabase: Client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                self.bucket_name = settings.SUPABASE_BUCKET
                self.enabled = True
                print("✅ Supabase storage enabled")
            except Exception as e:
                print(f"⚠️  Supabase init failed: {e} - using local storage")
                self.enabled = False
        else:
            print("⚠️  Supabase not configured - using local storage fallback")
    
    def strip_exif(self, image_path: str) -> bytes:
        """Remove EXIF data from image for privacy"""
        image = Image.open(image_path)
        
        # Remove EXIF data
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image_without_exif.save(img_byte_arr, format=image.format or 'JPEG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
    
    def upload_file(self, file_path: str, folder: str = "uploads") -> dict:
        """
        Upload file to Supabase storage or local storage
        Returns: {'path': str, 'url': str, 'local': bool}
        """
        # Generate unique filename
        file_ext = os.path.splitext(file_path)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        storage_path = f"{folder}/{unique_filename}"
        
        # Strip EXIF data
        file_bytes = self.strip_exif(file_path)
        
        # If Supabase is not enabled, use local storage
        if not self.enabled:
            # Create local storage directory
            local_storage_dir = os.path.join("storage", folder)
            os.makedirs(local_storage_dir, exist_ok=True)
            
            # Save file locally
            local_path = os.path.join(local_storage_dir, unique_filename)
            with open(local_path, 'wb') as f:
                f.write(file_bytes)
            
            print(f"📁 File saved locally: {local_path}")
            return {
                'path': storage_path,
                'url': f"/storage/{folder}/{unique_filename}",
                'local': True
            }
        
        # Upload to Supabase
        try:
            response = self.supabase.storage.from_(self.bucket_name).upload(
                storage_path,
                file_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            print(f"☁️  File uploaded to Supabase: {storage_path}")
            return {
                'path': storage_path,
                'url': None,  # Will use signed URLs for access
                'local': False
            }
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")
    
    def get_signed_url(self, file_path: str, expires_in: int = 1800) -> str:
        """
        Get signed URL for private file access
        expires_in: seconds (default 30 minutes)
        """
        if not self.enabled:
            # For local storage, return local path
            return f"/storage/{file_path}"
        
        try:
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path,
                expires_in
            )
            return response['signedURL']
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        if not self.enabled:
            # Delete from local storage
            try:
                local_path = os.path.join("storage", file_path)
                if os.path.exists(local_path):
                    os.remove(local_path)
                    print(f"🗑️  Deleted local file: {local_path}")
                return True
            except Exception as e:
                print(f"Delete failed: {str(e)}")
                return False
        
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            print(f"🗑️  Deleted from Supabase: {file_path}")
            return True
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False
    
    def delete_files_batch(self, file_paths: list) -> bool:
        """Delete multiple files"""
        if not self.enabled:
            # Delete from local storage
            try:
                for file_path in file_paths:
                    local_path = os.path.join("storage", file_path)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                print(f"🗑️  Deleted {len(file_paths)} local files")
                return True
            except Exception as e:
                print(f"Batch delete failed: {str(e)}")
                return False
        
        try:
            self.supabase.storage.from_(self.bucket_name).remove(file_paths)
            print(f"🗑️  Deleted {len(file_paths)} files from Supabase")
            return True
        except Exception as e:
            print(f"Batch delete failed: {str(e)}")
            return False

# Global instance
storage_manager = StorageManager()
