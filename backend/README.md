# Virtual Try-On Backend

FastAPI backend for the Virtual Merchandise Try-On system.

## Features

- ✅ Student authentication with OTP verification
- ✅ Admin and Master admin roles
- ✅ Computer vision-based virtual try-on using MediaPipe
- ✅ Image upload and storage (Supabase)
- ✅ Approval workflow
- ✅ QR code generation for admins
- ✅ Automatic image deletion (privacy)
- ✅ Location-based interaction tracking

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required configurations:
- **DATABASE_URL**: PostgreSQL connection string (Supabase/Render)
- **SUPABASE_URL** & **SUPABASE_KEY**: From Supabase project settings
- **SMTP credentials**: Gmail app password for OTP emails
- **SECRET_KEY**: Generate with `openssl rand -hex 32`
- **MASTER_EMAIL** & **MASTER_PASSWORD**: Initial master admin credentials

### 4. Initialize Database

```bash
python init_db.py
```

This will:
- Create all database tables
- Create the master admin account
- Display master credentials

### 5. Add Merchandise Templates

Place merchandise template images in `assets/merch/` directory:
- Format: PNG with transparency
- Naming: `{design_name}.png` (e.g., `fest_logo.png`)
- Size: Recommended 1000x1200px for best results

### 6. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /signup` - Student signup (sends OTP)
- `POST /verify-otp` - Verify OTP and activate account
- `POST /login` - Student login
- `GET /me` - Get current user info

### Try-On (`/api/tryon`)
- `POST /upload` - Upload photo
- `POST /generate/{session_id}` - Generate virtual try-on
- `GET /my-sessions` - Get user's sessions
- `GET /download/{image_id}` - Download approved image

### Admin (`/api/admin`)
- `POST /login` - Admin login
- `GET /locations` - Get available locations
- `POST /select-location` - Select location & get QR code
- `GET /pending-approvals` - Get approval queue
- `POST /approve/{approval_id}` - Approve image
- `POST /reject/{approval_id}` - Reject image
- `GET /stats` - Get admin statistics

### Master (`/api/master`)
- `POST /login` - Master login
- `POST /create-admin` - Create new admin
- `POST /create-location` - Create new location
- `GET /admins` - Get all admins
- `GET /locations` - Get all locations
- `POST /toggle-admin/{admin_id}` - Enable/disable admin
- `GET /global-stats` - Get system statistics
- `POST /override-approval/{approval_id}` - Override approval

## Deployment (Render)

### 1. Create `render.yaml`

```yaml
services:
  - type: web
    name: virtual-tryon-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### 2. Set Environment Variables

In Render dashboard, add all variables from `.env`

### 3. Deploy

Connect your GitHub repo and deploy!

## Auto-Deletion Schedule

- **Uploaded images**: Deleted after 2 hours
- **Generated images**: Deleted at end of day
- **Metadata**: Retained for statistics

## Security Features

- ✅ EXIF data stripping
- ✅ File type validation
- ✅ Size limits (5MB)
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Signed URLs (30min expiry)
- ✅ College email validation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Storage**: Supabase Storage
- **Computer Vision**: MediaPipe
- **Image Processing**: OpenCV, Pillow
- **Authentication**: JWT (python-jose)
- **Email**: SMTP (Gmail)
- **Scheduler**: APScheduler

## Development Tips

1. **Testing MediaPipe**: Ensure you have a webcam or test images
2. **Email Testing**: Use Gmail app passwords, not regular password
3. **Database**: Use Supabase free tier for PostgreSQL
4. **Storage**: Configure Supabase storage bucket as private
5. **QR Codes**: Test with a QR scanner app

## Troubleshooting

### MediaPipe Installation Issues
```bash
pip install mediapipe --no-cache-dir
```

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure IP is whitelisted (Supabase)

### Email Not Sending
- Enable "Less secure app access" or use App Password
- Check SMTP credentials
- Verify firewall allows port 587

## License

MIT License - College Fest Project
