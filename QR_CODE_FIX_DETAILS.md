# QR Code & Admin Interaction Fix

## ✅ Changes Made

1. **Updated Models**: Added `admin_id` and `location_id` to `TryOnSession` for precise tracking.
2. **QR Code**: Changed from "ID:Location" to a full Login URL: `http://localhost:3000/login?admin_id=X&location_id=Y` (can be scanned by any QR scanner).
3. **Tracking**:
   - Scanning the QR and logging in (or signing up via link) now records an interaction.
   - If user is already logged in, visiting the URL will record an interaction.
4. **Try On**: Uploading a photo now associates the session with the `admin_id` from the QR scan.
5. **Admin Portal**: Filtered pending approvals so admins ONLY see photos generated via their QR code.

## ⚠️ CRITICAL: Database Schema Update Required

Since we modified the `TryOnSession` table, you MUST update your database schema.
We created a script `backend/update_schema.py` to add the missing columns without losing data.

**Run this command in backend terminal:**
```bash
python update_schema.py
```
*(If this fails or hangs, you might need to recreate the database/tables if using dev environment, or use a migration tool like Alembic)*

## 🧪 Testing

1. **Admin Portal**:
   - Go to Dashboard -> Select Location.
   - Go to "QR Code" tab.
   - Scan the QR code (it should open Login page with params).
2. **Student**:
   - Login via the link.
   - Upload a photo.
3. **Admin Portal**:
   - Refresh Dashboard.
   - You should see the pending approval for that specific photo.
   - Interaction count should increase.

**Files Changed:**
- `backend/app/models.py`
- `backend/app/routes/admin.py`, `auth.py`, `tryon.py`
- `frontend/lib/api-client.ts`
- `frontend/app/login/page.tsx`
- `frontend/app/signup/page.tsx`
- `frontend/app/upload/page.tsx`
