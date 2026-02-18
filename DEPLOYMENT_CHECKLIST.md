# 📋 Deployment Checklist

## Pre-Deployment Setup

### ✅ Supabase Configuration
- [ ] Create Supabase account
- [ ] Create new project
- [ ] Note down database password
- [ ] Copy Project URL
- [ ] Copy anon/public API key
- [ ] Create storage bucket `virtual-tryon` (private)
- [ ] Whitelist deployment IPs (if needed)

### ✅ Gmail SMTP Setup
- [ ] Enable 2-Factor Authentication
- [ ] Generate App Password
- [ ] Test email sending locally
- [ ] Note down app password

### ✅ Merchandise Assets
- [ ] Create merch template images (PNG, transparent)
- [ ] Size: 1000x1200px recommended
- [ ] Save to `backend/assets/merch/`
- [ ] Test try-on locally with each design

### ✅ College Configuration
- [ ] Update college name in frontend env
- [ ] Update `validate_college_email()` in `backend/app/auth.py`
- [ ] Add allowed email domains

### ✅ Local Testing
- [ ] Backend runs without errors
- [ ] Database initialized successfully
- [ ] Master admin created
- [ ] Test student signup flow
- [ ] Test OTP email delivery
- [ ] Test photo upload
- [ ] Test try-on generation
- [ ] Test approval workflow
- [ ] Frontend builds successfully
- [ ] All API endpoints working

## Backend Deployment (Render)

### ✅ Render Setup
- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Select repository
- [ ] Set root directory to `backend` (if needed)

### ✅ Build Configuration
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment: Python 3.11
- [ ] Branch: main (or your branch)

### ✅ Environment Variables
Add all these in Render dashboard:

```
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_BUCKET=virtual-tryon
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
FROM_EMAIL=...
FRONTEND_URL=https://your-app.vercel.app
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=jpg,jpeg,png
MAX_TRYON_PER_USER=5
UPLOADED_IMAGE_RETENTION_HOURS=2
GENERATED_IMAGE_RETENTION_HOURS=24
MASTER_EMAIL=master@college.edu
MASTER_PASSWORD=...
```

### ✅ Deployment
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (~5-10 minutes)
- [ ] Check logs for errors
- [ ] Test health endpoint: `https://your-api.onrender.com/health`
- [ ] Test API docs: `https://your-api.onrender.com/docs`

### ✅ Post-Deployment
- [ ] Verify database tables created
- [ ] Verify master admin exists
- [ ] Test signup endpoint
- [ ] Test OTP email delivery
- [ ] Test file upload
- [ ] Test try-on generation

## Frontend Deployment (Vercel)

### ✅ Vercel Setup
- [ ] Create Vercel account
- [ ] Connect GitHub repository
- [ ] Import project
- [ ] Select `frontend` directory

### ✅ Build Configuration
- [ ] Framework: Next.js
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm run build` (auto-detected)
- [ ] Output Directory: `.next` (auto-detected)
- [ ] Install Command: `npm install` (auto-detected)

### ✅ Environment Variables
Add in Vercel dashboard:

```
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
NEXT_PUBLIC_APP_NAME=Virtual Try-On
NEXT_PUBLIC_COLLEGE_NAME=Your College Name
```

### ✅ Deployment
- [ ] Click "Deploy"
- [ ] Wait for deployment (~2-3 minutes)
- [ ] Check deployment logs
- [ ] Visit deployed URL
- [ ] Test landing page loads

### ✅ Post-Deployment
- [ ] Update `FRONTEND_URL` in backend env vars
- [ ] Redeploy backend with new frontend URL
- [ ] Test CORS (API calls from frontend)
- [ ] Test authentication flow
- [ ] Test all user workflows

## Database Initialization

### ✅ Master Admin
- [ ] Login to backend API docs
- [ ] Verify master admin credentials work
- [ ] Change master password (recommended)

### ✅ Create Locations
Using Master API:
- [ ] Create location: "Main Gate"
- [ ] Create location: "Auditorium"
- [ ] Create location: "Cafeteria"
- [ ] (Add more as needed)

### ✅ Create Admin Accounts
For each location/admin:
- [ ] Create admin account via Master API
- [ ] Note down credentials
- [ ] Share credentials securely with admins
- [ ] Test admin login

## Admin Setup

### ✅ For Each Admin
- [ ] Login to admin portal
- [ ] Select location
- [ ] Generate QR code
- [ ] Download/Print QR code
- [ ] Test QR code scanning
- [ ] Verify interaction tracking

## Testing in Production

### ✅ Student Flow
- [ ] Scan QR code
- [ ] Signup with college email
- [ ] Receive OTP email
- [ ] Verify OTP
- [ ] Login
- [ ] Upload photo
- [ ] Select merchandise
- [ ] Generate try-on
- [ ] Verify realistic result
- [ ] Wait for approval
- [ ] Download approved image

### ✅ Admin Flow
- [ ] Login as admin
- [ ] Select location
- [ ] View QR code
- [ ] Check pending approvals
- [ ] Approve an image
- [ ] Reject an image
- [ ] Verify email notifications sent
- [ ] View statistics
- [ ] Verify interaction counts

### ✅ Master Flow
- [ ] Login as master
- [ ] View all admins
- [ ] View all locations
- [ ] View global statistics
- [ ] Toggle admin status
- [ ] Override an approval
- [ ] Verify changes reflected

## Performance Testing

### ✅ Load Testing
- [ ] Test with 10 concurrent users
- [ ] Test with 50 concurrent users
- [ ] Test with 100 concurrent users
- [ ] Monitor response times
- [ ] Check for errors in logs
- [ ] Verify auto-deletion works

### ✅ Image Processing
- [ ] Test single person photos
- [ ] Test group photos (2-5 people)
- [ ] Test different photo sizes
- [ ] Test different lighting conditions
- [ ] Verify processing time < 1 second
- [ ] Check result quality

## Security Checks

### ✅ Authentication
- [ ] Verify JWT tokens expire correctly
- [ ] Test invalid token handling
- [ ] Test OTP expiration (10 minutes)
- [ ] Verify college email validation
- [ ] Test password strength requirements

### ✅ Authorization
- [ ] Student cannot access admin routes
- [ ] Admin cannot access master routes
- [ ] Verify role-based access control
- [ ] Test unauthorized access attempts

### ✅ File Security
- [ ] Verify file type validation
- [ ] Verify file size limits
- [ ] Test EXIF stripping
- [ ] Verify signed URL expiration
- [ ] Test malicious file upload

### ✅ Privacy
- [ ] Verify uploaded images deleted after 2 hours
- [ ] Verify generated images deleted EOD
- [ ] Check metadata retention
- [ ] Verify no permanent storage

## Monitoring Setup

### ✅ Render Monitoring
- [ ] Enable email alerts for downtime
- [ ] Monitor CPU/Memory usage
- [ ] Check logs regularly
- [ ] Set up health check pings

### ✅ Supabase Monitoring
- [ ] Monitor database size
- [ ] Monitor storage usage
- [ ] Check API request count
- [ ] Verify within free tier limits

### ✅ Error Tracking
- [ ] Check backend logs daily
- [ ] Monitor email delivery rate
- [ ] Track failed try-on generations
- [ ] Monitor approval queue length

## Documentation

### ✅ User Guides
- [ ] Create student user guide
- [ ] Create admin user guide
- [ ] Create QR code placement guide
- [ ] Create troubleshooting guide

### ✅ Admin Training
- [ ] Train admins on approval process
- [ ] Explain quality standards
- [ ] Show how to use QR codes
- [ ] Demonstrate statistics dashboard

### ✅ Support
- [ ] Set up support email/contact
- [ ] Create FAQ document
- [ ] Prepare common issue solutions
- [ ] Set up feedback collection

## Launch Preparation

### ✅ Marketing Materials
- [ ] Create announcement posters
- [ ] Prepare social media posts
- [ ] Print QR codes for locations
- [ ] Create demo video (optional)

### ✅ Soft Launch
- [ ] Test with 10-20 students
- [ ] Gather feedback
- [ ] Fix any issues
- [ ] Optimize based on feedback

### ✅ Full Launch
- [ ] Announce to all students
- [ ] Place QR codes at locations
- [ ] Monitor system closely
- [ ] Be ready for support requests

## Post-Launch

### ✅ Daily Tasks
- [ ] Check system health
- [ ] Monitor approval queue
- [ ] Review statistics
- [ ] Check for errors in logs
- [ ] Respond to support requests

### ✅ Weekly Tasks
- [ ] Review usage statistics
- [ ] Check free tier limits
- [ ] Backup important data
- [ ] Update documentation if needed

### ✅ End of Event
- [ ] Export final statistics
- [ ] Backup all data
- [ ] Thank admins and users
- [ ] Archive project
- [ ] Delete all user data (privacy)

## Emergency Contacts

```
Backend Issues:
- Render Dashboard: https://dashboard.render.com
- Render Support: support@render.com

Frontend Issues:
- Vercel Dashboard: https://vercel.com/dashboard
- Vercel Support: support@vercel.com

Database Issues:
- Supabase Dashboard: https://app.supabase.com
- Supabase Support: support@supabase.io

Email Issues:
- Gmail Support: https://support.google.com/mail
```

## Success Metrics

### ✅ Track These
- [ ] Total students signed up
- [ ] Total try-ons generated
- [ ] Total approvals/rejections
- [ ] Average processing time
- [ ] QR scans per location
- [ ] Unique students per admin
- [ ] System uptime percentage
- [ ] User satisfaction (feedback)

## Backup Plan

### ✅ If System Goes Down
1. Check Render/Vercel status pages
2. Check Supabase status
3. Review error logs
4. Restart services if needed
5. Contact support if issue persists
6. Communicate with users about downtime

### ✅ If Free Tier Limits Exceeded
1. Monitor usage closely
2. Optimize queries if needed
3. Consider upgrading (if budget allows)
4. Limit new signups temporarily
5. Clean up old data aggressively

---

## Final Checklist Before Launch

- [ ] All environment variables set correctly
- [ ] Database initialized with master admin
- [ ] Admin accounts created
- [ ] Locations created
- [ ] QR codes generated and printed
- [ ] Merchandise templates uploaded
- [ ] All workflows tested end-to-end
- [ ] Email delivery confirmed
- [ ] Auto-deletion verified
- [ ] Performance acceptable
- [ ] Security measures in place
- [ ] Documentation complete
- [ ] Support system ready
- [ ] Monitoring enabled
- [ ] Backup plan prepared

## 🎉 Ready to Launch!

Once all items are checked, you're ready to go live!

**Good luck with your college cultural fest! 🚀**
