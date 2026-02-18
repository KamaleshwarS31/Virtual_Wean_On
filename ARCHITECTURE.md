# System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          VIRTUAL TRY-ON SYSTEM                          │
│                         (Zero-Cost Architecture)                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                              │
│                         (Next.js 15 - Vercel Free)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Student    │  │    Admin     │  │    Master    │                 │
│  │   Portal     │  │   Portal     │  │   Portal     │                 │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤                 │
│  │ • Landing    │  │ • Login      │  │ • Login      │                 │
│  │ • Signup/OTP │  │ • QR Gen     │  │ • Admin Mgmt │                 │
│  │ • Upload     │  │ • Approvals  │  │ • Location   │                 │
│  │ • Try-On     │  │ • Stats      │  │ • Stats      │                 │
│  │ • Download   │  │              │  │ • Override   │                 │
│  └──────────────┘  └──────────────┘  └──────────────┘                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │              Shared Components & Design System                  │    │
│  │  • Glassmorphism UI  • Animations  • Konva Canvas              │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ HTTPS / REST API
                             │ JWT Authentication
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                            BACKEND LAYER                                 │
│                       (FastAPI - Render Free)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        API ROUTES                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │  │   Auth   │  │  Try-On  │  │  Admin   │  │  Master  │       │   │
│  │  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │       │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     CORE SERVICES                                │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │   │
│  │  │  Try-On Engine │  │  Auth Service  │  │ Email Service  │   │   │
│  │  │  (MediaPipe)   │  │  (JWT + OTP)   │  │  (Gmail SMTP)  │   │   │
│  │  ├────────────────┤  ├────────────────┤  ├────────────────┤   │   │
│  │  │ • Pose Detect  │  │ • Password     │  │ • OTP Emails   │   │   │
│  │  │ • Segmentation │  │ • JWT Tokens   │  │ • Approval     │   │   │
│  │  │ • Auto-Scale   │  │ • OTP Gen      │  │   Notifs       │   │   │
│  │  │ • Lighting     │  │ • Validation   │  │                │   │   │
│  │  │ • Shadows      │  │                │  │                │   │   │
│  │  │ • Blending     │  │                │  │                │   │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘   │   │
│  │                                                                  │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │   │
│  │  │Storage Manager │  │   Scheduler    │  │   QR Service   │   │   │
│  │  │  (Supabase)    │  │ (APScheduler)  │  │                │   │   │
│  │  ├────────────────┤  ├────────────────┤  ├────────────────┤   │   │
│  │  │ • Upload       │  │ • Auto-Delete  │  │ • Generate QR  │   │   │
│  │  │ • EXIF Strip   │  │ • 2hr Uploads  │  │ • Track Scans  │   │   │
│  │  │ • Signed URLs  │  │ • EOD Generated│  │                │   │   │
│  │  └────────────────┘  └────────────────┘  └────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└────────────────┬──────────────────────────┬──────────────────────────────┘
                 │                          │
                 │                          │
┌────────────────▼──────────┐  ┌───────────▼──────────────────────────────┐
│      DATABASE LAYER        │  │        STORAGE LAYER                     │
│  (PostgreSQL - Supabase)   │  │    (Supabase Storage)                   │
├────────────────────────────┤  ├──────────────────────────────────────────┤
│                            │  │                                          │
│  ┌──────────────────────┐ │  │  ┌────────────────────────────────────┐ │
│  │  Tables:             │ │  │  │  Buckets:                          │ │
│  │  • users             │ │  │  │  • virtual-tryon (private)         │ │
│  │  • admins            │ │  │  │                                    │ │
│  │  • locations         │ │  │  │  Folders:                          │ │
│  │  • try_on_sessions   │ │  │  │  • uploads/   (2hr retention)     │ │
│  │  • generated_images  │ │  │  │  • generated/ (EOD retention)     │ │
│  │  • image_approvals   │ │  │  │                                    │ │
│  │  • interaction_counts│ │  │  │  Features:                         │ │
│  │  • otp_verifications │ │  │  │  • EXIF stripping                  │ │
│  │  └──────────────────┘ │  │  │  • Signed URLs (30min)             │ │
│  │                        │  │  │  • Auto-deletion                   │ │
│  │  Features:             │  │  └────────────────────────────────────┘ │
│  │  • SQLAlchemy ORM      │  │                                          │
│  │  • Relationships       │  │                                          │
│  │  • Migrations          │  │                                          │
│  └────────────────────────┘  └──────────────────────────────────────────┘
│                            │
└────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  Gmail SMTP      │  │  MediaPipe       │  │  OpenCV          │     │
│  │  (Free)          │  │  (Open Source)   │  │  (Open Source)   │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • OTP Emails     │  │ • Pose Detection │  │ • Image Process  │     │
│  │ • Notifications  │  │ • Segmentation   │  │ • Transformations│     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STUDENT WORKFLOW:                                                       │
│  1. Scan QR Code → Landing Page                                         │
│  2. Signup → OTP Email → Verify → Login                                 │
│  3. Upload Photo → Supabase Storage                                     │
│  4. Select Merch → Generate Try-On                                      │
│     └─> MediaPipe: Detect Pose → Scale Merch → Apply Effects           │
│  5. Wait for Admin Approval                                             │
│  6. Download Approved Image (Signed URL)                                │
│                                                                          │
│  ADMIN WORKFLOW:                                                         │
│  1. Login → Select Location → Generate QR Code                          │
│  2. View Pending Approvals                                              │
│  3. Approve/Reject Images → Email Notification to Student               │
│  4. View Statistics (Scans, Students, Approvals)                        │
│                                                                          │
│  MASTER WORKFLOW:                                                        │
│  1. Login → Dashboard                                                    │
│  2. Create Admins & Locations                                            │
│  3. View Global Statistics                                               │
│  4. Enable/Disable Admins                                                │
│  5. Override Approvals                                                   │
│                                                                          │
│  AUTO-DELETION:                                                          │
│  • Hourly: Delete uploaded images > 2 hours old                         │
│  • Daily (Midnight): Delete generated images from previous day          │
│  • Metadata retained for statistics                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Authentication:  JWT Tokens + OTP Verification                       │
│  2. Authorization:   Role-Based Access Control (Student/Admin/Master)   │
│  3. File Security:   EXIF Stripping + Type Validation + Size Limits     │
│  4. Storage:         Private Buckets + Signed URLs (30min expiry)       │
│  5. Privacy:         Auto-Deletion (2hr uploads, EOD generated)          │
│  6. Email:           College Domain Validation                           │
│  7. API:             CORS + Rate Limiting                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Production Environment (All Free Tiers):                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Frontend: Vercel                                                 │  │
│  │  • Next.js deployment                                             │  │
│  │  • Edge network (CDN)                                             │  │
│  │  • Automatic HTTPS                                                │  │
│  │  • Environment variables                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Backend: Render                                                  │  │
│  │  • FastAPI deployment                                             │  │
│  │  • Auto-deploy from Git                                           │  │
│  │  • Environment variables                                          │  │
│  │  • Health checks                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Database & Storage: Supabase                                     │  │
│  │  • PostgreSQL (500MB)                                             │  │
│  │  • Storage (1GB)                                                  │  │
│  │  • Realtime (optional)                                            │  │
│  │  • Auto-backups                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

COST BREAKDOWN: $0.00 / month (100% Free)
ESTIMATED CAPACITY: 150-200 concurrent users
RUNTIME: 1 month (as per requirements)
```
