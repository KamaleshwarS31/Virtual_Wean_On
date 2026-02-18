# ⚡ Quick Start Guide

## 🎯 Get Running in 10 Minutes

### Step 1: Setup Supabase (3 minutes)

1. Go to [supabase.com](https://supabase.com) and sign up
2. Click "New Project"
3. Fill in:
   - Name: `virtual-tryon`
   - Database Password: (save this!)
   - Region: Choose closest to you
4. Wait for project to be created (~2 minutes)

5. **Get Database URL**:
   - Go to Settings → Database
   - Copy "Connection string" (URI format)
   - Replace `[YOUR-PASSWORD]` with your database password

6. **Get API Keys**:
   - Go to Settings → API
   - Copy "Project URL" and "anon public" key

7. **Create Storage Bucket**:
   - Go to Storage
   - Click "New bucket"
   - Name: `virtual-tryon`
   - Public: **OFF** (keep it private)
   - Click "Create bucket"

### Step 2: Setup Gmail SMTP (2 minutes)

1. Go to your Google Account settings
2. Security → 2-Step Verification → Enable it
3. Security → App passwords
4. Select "Mail" and "Other (Custom name)"
5. Name it "Virtual Try-On"
6. Copy the 16-character password

### Step 3: Backend Setup (3 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Now edit `backend/.env` with your credentials:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]
SUPABASE_BUCKET=virtual-tryon

SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=[YOUR-16-CHAR-APP-PASSWORD]
FROM_EMAIL=your-email@gmail.com

FRONTEND_URL=http://localhost:3000

MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=jpg,jpeg,png
MAX_TRYON_PER_USER=5

UPLOADED_IMAGE_RETENTION_HOURS=2
GENERATED_IMAGE_RETENTION_HOURS=24

MASTER_EMAIL=master@college.edu
MASTER_PASSWORD=ChangeThisPassword123!
```

```bash
# Initialize database
python init_db.py

# Start backend
uvicorn app.main:app --reload
```

✅ Backend running at http://localhost:8000
✅ API docs at http://localhost:8000/docs

### Step 4: Frontend Setup (2 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Virtual Try-On
NEXT_PUBLIC_COLLEGE_NAME=Your College Name
```

```bash
# Start frontend
npm run dev
```

✅ Frontend running at http://localhost:3000

## 🎉 You're Ready!

### Test the Backend

1. Open http://localhost:8000/docs
2. Try the endpoints:
   - POST `/api/auth/signup` - Create a student account
   - POST `/api/auth/verify-otp` - Verify with OTP
   - POST `/api/tryon/upload` - Upload a photo
   - POST `/api/tryon/generate/{session_id}` - Generate try-on

### View the Frontend

1. Open http://localhost:3000
2. See the beautiful landing page
3. Click "Get Started" (will show 404 - pages not built yet)

## 📝 Next Steps

### Add Merchandise Images

1. Create PNG images with transparency (1000x1200px)
2. Save to `backend/assets/merch/`:
   ```
   backend/assets/merch/fest_logo.png
   backend/assets/merch/college_tshirt.png
   ```

### Create Admin Account

Use the API docs at http://localhost:8000/docs:

1. Login as master:
   - POST `/api/master/login`
   - Email: `master@college.edu`
   - Password: `ChangeThisPassword123!`

2. Create location:
   - POST `/api/master/create-location`
   - Name: "Main Gate"

3. Create admin:
   - POST `/api/master/create-admin`
   - Name: "Admin Name"
   - Email: "admin@college.edu"
   - Password: "admin123"

### Test Try-On Engine

1. Use any photo with a person
2. Upload via API
3. Generate try-on with a merch design
4. See the realistic result!

## 🐛 Troubleshooting

### Backend won't start
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database connection error
- Check DATABASE_URL in .env
- Verify password is correct
- Check Supabase project is active

### Email not sending
- Verify Gmail App Password (not regular password)
- Check 2FA is enabled
- Try with a different Gmail account

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation

- **Main README**: `README.md`
- **Project Status**: `PROJECT_STATUS.md`
- **Summary**: `SUMMARY.md`
- **Backend README**: `backend/README.md`
- **API Docs**: http://localhost:8000/docs

## 🎯 What Works Right Now

✅ **Backend API** - Fully functional
✅ **Try-On Engine** - Ready to use
✅ **Database** - All tables created
✅ **Authentication** - JWT + OTP working
✅ **Email** - OTP sending works
✅ **Storage** - Supabase integration ready
✅ **Admin System** - QR codes, approvals working
✅ **Auto-Deletion** - Scheduler running

## 🚧 What's Being Built

🚧 **Frontend Pages** - In progress
🚧 **UI Components** - Design system ready
🚧 **Canvas Integration** - Konva.js installed

## 💡 Pro Tips

1. **Test with real photos**: Use photos with clear body poses
2. **Merch templates**: Make sure they have transparent backgrounds
3. **Email domain**: Update `validate_college_email()` in `backend/app/auth.py`
4. **Master password**: Change it after first login!
5. **Free tiers**: Monitor Supabase usage to stay within limits

## 🎊 You're All Set!

The backend is **production-ready**. You can:
- ✅ Create accounts
- ✅ Upload photos
- ✅ Generate realistic try-ons
- ✅ Manage approvals
- ✅ Track interactions

**Now build the frontend pages to connect to this powerful backend!**

---

Need help? Check the documentation files or test the API at http://localhost:8000/docs
