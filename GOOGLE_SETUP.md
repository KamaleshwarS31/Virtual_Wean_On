# 🔧 How to Set Up Google Sign-In (Optional)

## ✅ Current Status:
- Google Sign-In button is **hidden** until you configure it
- Email/Password signup works perfectly **without** Google
- CAPTCHA verification is active

---

## 📝 Quick Setup (5 Minutes):

### Step 1: Create Google OAuth Client

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Click "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth 2.0 Client ID"
5. If prompted, configure OAuth consent screen first:
   - User Type: **External**
   - App name: **VIT Virtual Try-On**
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through all steps

### Step 2: Configure OAuth Client

1. Application type: **Web application**
2. Name: **VIT Try-On Web Client**
3. Authorized JavaScript origins:
   - Add: `http://localhost:3000`
   - Add: `http://localhost:3001`
4. Authorized redirect URIs: (leave empty for now)
5. Click "Create"
6. **Copy the Client ID** (looks like: `123456789-abc123.apps.googleusercontent.com`)

### Step 3: Update Frontend Config

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=YOUR_ACTUAL_CLIENT_ID_HERE.apps.googleusercontent.com
```

Replace `YOUR_ACTUAL_CLIENT_ID_HERE` with the Client ID you copied.

### Step 4: Restart Frontend

```bash
# Stop the server (Ctrl+C in the terminal)
npm run dev
```

### Step 5: Test It!

1. Go to http://localhost:3000/signup
2. You should now see the "Sign in with Google" button
3. Click it and sign in with your VIT Google account
4. Done! ✅

---

## ⚠️ Important Notes:

### Email Requirement:
- You **MUST** use a VIT email (@vitstudent.ac.in or @vit.ac.in)
- Personal Gmail accounts won't work
- The backend validates the email domain

### Without Google Setup:
- The Google button is **automatically hidden**
- Email/password signup works perfectly
- CAPTCHA is still required
- No errors or issues

### Testing Accounts:
- Use your actual VIT Google account
- Or use email/password signup (no Google needed)

---

## 🧪 Testing:

### With Google Configured:
1. Visit signup page
2. See Google button
3. Click and sign in
4. Instant access! ✅

### Without Google (Current State):
1. Visit signup page
2. No Google button (hidden)
3. Use email/password form
4. Check CAPTCHA
5. Sign up! ✅

---

## 🔒 Security:

### What's Validated:
- ✅ VIT email domain (@vitstudent.ac.in, @vit.ac.in)
- ✅ Google OAuth token
- ✅ CAPTCHA verification (for email/password)
- ✅ Password strength (min 8 chars)

### What's Protected:
- Only VIT emails can sign up
- Google handles authentication securely
- No password storage for Google users
- JWT tokens for session management

---

## 📊 Current Features:

### Working Now (Without Google):
- ✅ Email/password signup
- ✅ CAPTCHA verification
- ✅ Instant account creation
- ✅ Login with email/password
- ✅ VIT email validation
- ✅ Dashboard access

### With Google (After Setup):
- ✅ All above features
- ✅ **PLUS** One-click Google Sign-In
- ✅ No password needed
- ✅ Faster signup/login

---

## 🎯 Recommendation:

**For Testing:** Use email/password (no Google setup needed)
**For Production:** Set up Google Sign-In for better UX

---

## 🆘 Troubleshooting:

### "OAuth client was not found" Error:
- This means Google Client ID is not configured
- The button is now **hidden** to prevent this error
- Use email/password signup instead

### Google Button Not Showing:
- Check `.env.local` has correct Client ID
- Make sure it's not the placeholder value
- Restart the frontend server

### VIT Email Required:
- Both signup methods require VIT email
- @vitstudent.ac.in or @vit.ac.in only
- Other domains are rejected

---

**Status:** Google Sign-In is **optional** and **hidden** until configured ✅
**Current Mode:** Email/Password + CAPTCHA (fully functional) 🎉
