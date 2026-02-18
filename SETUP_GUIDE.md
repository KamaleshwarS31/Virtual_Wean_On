# 🚀 Complete Setup & Deployment Guide

## ✅ CURRENT STATUS

**Backend:** 100% Complete - All dependencies installed  
**Frontend:** 60% Complete - Core pages created  
**Database:** Initialized and ready

---

## 📋 STEP-BY-STEP SETUP

### 1. Backend Setup (5 minutes)

```powershell
cd backend

# Activate virtual environment
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python test_imports.py

# Initialize database (if not done)
python init_db.py

# Start backend server
uvicorn app.main:app --reload
```

**Backend URL:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

**Master Admin Credentials:**
- Email: `master@college.edu`
- Password: `change-this-password`

---

### 2. Frontend Setup (2 minutes)

```powershell
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

**Frontend URL:** http://localhost:3000

---

### 3. Environment Configuration

#### Backend `.env` File

Create `backend/.env` with:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=virtual-tryon

# JWT
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend
FRONTEND_URL=http://localhost:3000

# Limits
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=jpg,jpeg,png
MAX_TRYON_PER_USER=5

# Retention
UPLOADED_IMAGE_RETENTION_HOURS=2
GENERATED_IMAGE_RETENTION_HOURS=24

# Master Admin
MASTER_EMAIL=master@college.edu
MASTER_PASSWORD=change-this-password
```

#### Frontend `.env.local` File

Already created at `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Virtual Try-On
NEXT_PUBLIC_COLLEGE_NAME=College Cultural Fest
```

---

## 🧪 TESTING THE SYSTEM

### Test 1: Backend Health Check

1. Start backend: `uvicorn app.main:app --reload`
2. Visit: http://localhost:8000/health
3. Should see: `{"status": "healthy"}`

### Test 2: API Documentation

1. Visit: http://localhost:8000/docs
2. Explore all endpoints
3. Try `/api/auth/signup` endpoint

### Test 3: Frontend Pages

1. Start frontend: `npm run dev`
2. Visit: http://localhost:3000
3. Test navigation:
   - Landing page ✅
   - Signup page ✅
   - Login page ✅
   - Dashboard ✅
   - Upload page ✅

### Test 4: Full Authentication Flow

1. Go to http://localhost:3000/signup
2. Enter college email
3. Check email for OTP
4. Verify OTP
5. Login
6. See dashboard

---

## 📦 DEPENDENCIES INSTALLED

### Backend
- ✅ fastapi
- ✅ uvicorn
- ✅ python-jose (JWT)
- ✅ passlib + argon2-cffi (password hashing)
- ✅ sqlalchemy + psycopg2-binary (database)
- ✅ pydantic + email-validator
- ✅ opencv-python (image processing)
- ✅ mediapipe (pose detection)
- ✅ supabase (storage)
- ✅ requests, httpx
- ✅ All other requirements

### Frontend
- ✅ Next.js 15
- ✅ TypeScript
- ✅ Material UI
- ✅ Konva.js
- ✅ SCSS
- ✅ Axios

---

## 🎯 COMPLETED FEATURES

### Backend (100%)
- [x] Database models and migrations
- [x] Authentication (JWT + OTP)
- [x] Password hashing (Argon2)
- [x] Email service (SMTP)
- [x] File upload & validation
- [x] Try-on engine (MediaPipe)
- [x] Storage integration (Supabase)
- [x] Admin system
- [x] QR code generation
- [x] Approval workflow
- [x] Auto-deletion scheduler
- [x] API documentation

### Frontend (60%)
- [x] Landing page
- [x] Signup with OTP
- [x] Login page
- [x] Dashboard
- [x] Upload page
- [x] Design system
- [x] API client
- [x] Auth context
- [ ] Try-on canvas (Konva)
- [ ] Merch selection
- [ ] Session history
- [ ] Admin dashboard
- [ ] Master dashboard

---

## 🚧 REMAINING WORK

### High Priority
1. **Try-On Canvas Page** - Konva.js integration for merch overlay
2. **Merch Selection UI** - Gallery of available designs
3. **Download Functionality** - Save generated images

### Medium Priority
4. **Session History** - View past try-ons
5. **Admin Dashboard** - Approval queue and stats
6. **Master Dashboard** - Admin management

### Low Priority
7. **Disclaimer Modal** - Privacy notice
8. **CAPTCHA Component** - Bot protection
9. **Error Boundaries** - Better error handling
10. **Loading States** - Improved UX

---

## 🌐 DEPLOYMENT (Production)

### Backend → Render

1. Push code to GitHub
2. Create Render account
3. New Web Service → Connect repo
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

### Frontend → Vercel

1. Push code to GitHub
2. Create Vercel account
3. Import project
4. Root: `frontend`
5. Add environment variables
6. Deploy!

### Database → Supabase

1. Create Supabase account
2. New project
3. Copy connection string
4. Create storage bucket: `virtual-tryon`
5. Update backend `.env`

---

## 🔧 TROUBLESHOOTING

### Backend won't start

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Test imports
python test_imports.py

# Check .env file exists
ls .env
```

### Frontend build errors

```powershell
# Clear cache
rm -rf .next node_modules package-lock.json

# Reinstall
npm install

# Rebuild
npm run dev
```

### Database connection failed

- Check DATABASE_URL in `.env`
- Verify Supabase project is active
- Test connection manually

---

## 📞 QUICK COMMANDS

```powershell
# Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Test backend
cd backend
python test_imports.py

# Initialize DB
cd backend
python init_db.py
```

---

## 🎉 YOU'RE READY!

The system is **functional and ready to use**!

- Backend API is complete
- Frontend core pages are built
- Database is initialized
- Authentication works
- File upload works

**Next:** Build the try-on canvas page to complete the full workflow!

---

**Last Updated:** 2026-02-07  
**Status:** Backend 100% ✅ | Frontend 60% 🚧 | Ready for Testing! 🚀
