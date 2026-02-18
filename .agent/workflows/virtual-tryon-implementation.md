---
description: Virtual Merchandise Try-On Implementation Plan
---

# Virtual Merchandise Try-On Website - Implementation Plan

## Phase 1: Project Setup & Architecture (Day 1-2)

### 1.1 Initialize Next.js Frontend
```bash
npx create-next-app@latest frontend --no-tailwind --typescript --app --no-src-dir
cd frontend
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install konva react-konva
npm install sass
npm install qrcode
npm install axios
```

### 1.2 Initialize FastAPI Backend
```bash
mkdir backend
cd backend
python -m venv venv
# Windows activation
venv\Scripts\activate
pip install fastapi uvicorn python-multipart pillow opencv-python mediapipe sqlalchemy psycopg2-binary python-jose passlib bcrypt pydantic-settings
pip freeze > requirements.txt
```

### 1.3 Setup Database (Supabase)
- Create Supabase project (free tier)
- Setup PostgreSQL database
- Configure storage buckets (private)
- Get connection credentials

## Phase 2: Backend Development (Day 3-5)

### 2.1 Database Schema
Create tables:
- users (students)
- admins
- locations
- try_on_sessions
- generated_images
- approval_queue
- interaction_counts

### 2.2 Core Backend Features
- Authentication (JWT)
- Email verification system
- Role-based access control
- Image upload & validation
- MediaPipe integration for pose detection
- Virtual try-on processing engine
- Admin approval workflow
- QR code generation
- Auto-deletion scheduler

### 2.3 API Endpoints
**Student Routes:**
- POST /api/auth/signup
- POST /api/auth/verify-otp
- POST /api/auth/login
- POST /api/tryon/upload
- POST /api/tryon/generate
- GET /api/tryon/my-sessions
- GET /api/tryon/download/{id}

**Admin Routes:**
- POST /api/admin/login
- POST /api/admin/select-location
- GET /api/admin/qr-code
- GET /api/admin/pending-approvals
- POST /api/admin/approve/{id}
- POST /api/admin/reject/{id}
- GET /api/admin/stats

**Master Routes:**
- GET /api/master/all-admins
- GET /api/master/all-locations
- GET /api/master/all-stats
- POST /api/master/toggle-admin/{id}
- POST /api/master/override-approval/{id}

## Phase 3: Computer Vision Try-On Engine (Day 6-8)

### 3.1 MediaPipe Integration
- Setup MediaPipe Pose for landmark detection
- Setup MediaPipe Selfie Segmentation
- Detect multiple people in group photos
- Extract body measurements (shoulder width, torso height)

### 3.2 Realistic Overlay Implementation
**Critical Features:**
1. **Pose-aware positioning**
   - Map merch to shoulder/neck landmarks
   - Calculate rotation angle from shoulders
   
2. **Automatic scaling**
   - Measure shoulder width in pixels
   - Scale merch proportionally per person
   
3. **Depth & occlusion**
   - Use segmentation to detect arms/hair
   - Layer merch behind foreground elements
   
4. **Fabric deformation**
   - Apply perspective transform at shoulders
   - Add slight curvature using mesh warping
   
5. **Lighting & shadows**
   - Analyze photo brightness
   - Add shadow under chin
   - Match merch lighting to photo
   
6. **Edge blending**
   - Feather merch edges (alpha gradient)
   - Soft composite with background

### 3.3 Performance Optimization
- Process images at optimal resolution (max 1920px width)
- Use efficient numpy operations
- Cache pose landmarks
- Parallel processing for group photos

## Phase 4: Frontend Development (Day 9-12)

### 4.1 Design System (SCSS)
Create `styles/design-system.scss`:
- Color palette (vibrant, modern)
- Typography (Google Fonts)
- Spacing system
- Component tokens
- Animation utilities
- Glassmorphism effects

### 4.2 Pages & Components
**Student Portal:**
- Landing page (QR scan entry)
- Signup/Login with email verification
- CAPTCHA component
- Disclaimer modal
- Photo upload interface
- Merch selection gallery
- Try-on preview canvas
- Download interface (post-approval)
- Session history

**Admin Portal:**
- Admin login
- Location selection
- QR code display
- Approval queue dashboard
- Image review interface
- Statistics dashboard

**Master Portal:**
- Master login
- Admin management
- Location management
- Global statistics
- Override controls

### 4.3 Canvas Implementation (Konva.js)
- Real-time try-on preview
- Zoom/pan controls
- Multi-person handling
- Export to image

## Phase 5: Integration & Security (Day 13-14)

### 5.1 Security Implementation
- EXIF stripping
- File type validation
- Size limits (5MB max)
- UUID filenames
- Signed URL generation (30min expiry)
- Rate limiting
- CORS configuration

### 5.2 Auto-Deletion System
- Cron job for uploaded images (2hr deletion)
- Cron job for generated images (end-of-day deletion)
- Metadata retention (counts only)

### 5.3 Email System
- OTP generation & sending
- Approval notifications
- Use free SMTP (Gmail SMTP with app password)

## Phase 6: Deployment (Day 15-16)

### 6.1 Backend Deployment (Render)
- Create `render.yaml`
- Setup environment variables
- Deploy FastAPI app
- Configure auto-sleep settings

### 6.2 Frontend Deployment (Vercel)
- Connect GitHub repo
- Configure environment variables
- Deploy Next.js app
- Setup redirects

### 6.3 Database & Storage (Supabase)
- Finalize schema
- Setup RLS policies
- Configure storage policies
- Setup backup (if available in free tier)

## Phase 7: Testing & Optimization (Day 17-18)

### 7.1 Testing
- Single person try-on
- Group photo try-on (2-5 people)
- Different merch sizes
- Mobile responsiveness
- Admin workflow
- Master controls
- Load testing (150-200 concurrent users)

### 7.2 Performance Optimization
- Image compression
- Lazy loading
- API response caching
- CDN usage (Vercel edge)

## Phase 8: Documentation & Handoff (Day 19-20)

### 8.1 Documentation
- Setup guide
- Admin user guide
- Master user guide
- API documentation
- Troubleshooting guide

### 8.2 Deployment Checklist
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Storage buckets configured
- [ ] Email SMTP configured
- [ ] Master account created
- [ ] Admin accounts created
- [ ] QR codes generated
- [ ] Auto-deletion cron active
- [ ] Disclaimer text finalized

## Timeline Summary
- **Week 1:** Setup + Backend Core
- **Week 2:** CV Engine + Frontend Core
- **Week 3:** Integration + Deployment + Testing

## Critical Success Factors
1. MediaPipe integration must work reliably
2. Try-on must look realistic (not just overlay)
3. Performance must be < 1 second for preview
4. All free tier limits must be respected
5. Auto-deletion must work flawlessly
6. Admin approval workflow must be smooth
