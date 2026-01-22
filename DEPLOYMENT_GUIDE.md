# VouchAI v1 - Deployment & Domain Setup Guide

## 🌐 Connecting vouchai.app to Your Project

Your domain: **vouchai.app** (managed in Cloudflare)

This guide will help you:
1. Deploy your backend (FastAPI)
2. Deploy your frontend (React from Lovable)
3. Configure Cloudflare DNS
4. Set up SSL/HTTPS

---

## 📋 Architecture Overview

```
vouchai.app (Frontend - React)
    ↓
api.vouchai.app (Backend - FastAPI)
    ↓
Google Gemini API + Tavily API
```

**OR** (Alternative setup):

```
vouchai.app (Frontend - React)
    ↓
vouchai.app/api (Backend - FastAPI on same domain)
```

---

## 🚀 Step 1: Deploy Backend (FastAPI)

Choose one of these platforms:

### Option A: Railway.app (Recommended - Easiest)

1. **Sign up:** https://railway.app
2. **Create New Project**
3. **Deploy from GitHub:**
   - Connect your GitHub repo
   - Select `vouchai` repository
   - Railway auto-detects Python/FastAPI

4. **Add Environment Variables:**
   ```
   GOOGLE_API_KEY=your_google_key_here
   TAVILY_API_KEY=your_tavily_key_here
   ```

5. **Configure Start Command:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

6. **Get Railway URL:** Something like `vouchai-production.up.railway.app`

7. **Add Custom Domain:**
   - In Railway: Settings → Domains
   - Add `api.vouchai.app`
   - Railway will give you a CNAME record

### Option B: Render.com

1. **Sign up:** https://render.com
2. **New Web Service**
3. **Connect GitHub repo**
4. **Configure:**
   - **Name:** vouchai-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt` (create requirements.txt first)
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables:** Add GOOGLE_API_KEY and TAVILY_API_KEY

6. **Custom Domain:** Add `api.vouchai.app` in dashboard

### Option C: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and Launch:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Set Secrets:**
   ```bash
   fly secrets set GOOGLE_API_KEY=your_key
   fly secrets set TAVILY_API_KEY=your_key
   ```

4. **Add Custom Domain:**
   ```bash
   fly certs add api.vouchai.app
   ```

### Creating requirements.txt (needed for most platforms)

```bash
cd /Users/raji/truth-engine
uv pip compile pyproject.toml -o requirements.txt
```

Or create manually:
```txt
fastapi>=0.128.0
uvicorn>=0.40.0
pydantic>=2.12.5
python-dotenv>=1.2.1
agno>=2.4.1
google-genai>=1.60.0
tavily-python>=0.7.19
```

---

## 🎨 Step 2: Deploy Frontend (Lovable → Vercel/Netlify)

### Option A: Lovable Built-in Deployment (Easiest)

1. Generate frontend in Lovable
2. In Lovable, click **"Publish"**
3. Lovable will give you a URL like `your-project.lovable.app`
4. Use this URL temporarily, or...

### Option B: Export from Lovable → Vercel

1. **Export from Lovable:**
   - Download your project code
   - You'll get a .zip file with your React app

2. **Push to GitHub:**
   ```bash
   # Create new repo for frontend
   # Extract zip and push to GitHub
   ```

3. **Deploy to Vercel:**
   - Go to https://vercel.com
   - "Import Project"
   - Select your frontend repo
   - **Environment Variable:** `VITE_API_URL=https://api.vouchai.app`
   - Deploy

4. **Add Custom Domain in Vercel:**
   - Project Settings → Domains
   - Add `vouchai.app`
   - Vercel gives you DNS records

### Option C: Netlify

1. Same as Vercel, but use https://netlify.com
2. Add `vouchai.app` in domain settings

---

## 🌍 Step 3: Configure Cloudflare DNS

### Scenario 1: Separate Subdomains (Recommended)

**Frontend:** `vouchai.app`
**Backend:** `api.vouchai.app`

**In Cloudflare DNS:**

1. **For Frontend (vouchai.app):**
   - Type: `A` or `CNAME`
   - Name: `@`
   - Value: Your Vercel/Netlify IP or CNAME
   - Proxy: ✅ Proxied (orange cloud)

2. **For Backend (api.vouchai.app):**
   - Type: `CNAME`
   - Name: `api`
   - Value: Your Railway/Render/Fly URL
   - Proxy: ✅ Proxied (orange cloud)

**Example:**
```
Type    Name    Content                              Proxy
A       @       76.76.21.21 (Vercel IP)             Proxied
CNAME   api     vouchai-production.up.railway.app   Proxied
```

### Scenario 2: Same Domain with Path

**Frontend:** `vouchai.app`
**Backend:** `vouchai.app/api`

Use Cloudflare Page Rules or Workers to route `/api/*` to backend.

---

## 🔐 Step 4: SSL/HTTPS Setup

### If Using Cloudflare Proxy (Orange Cloud):

**SSL is automatic!** Cloudflare handles it.

1. **In Cloudflare:**
   - SSL/TLS → Overview
   - Set to: **"Full (strict)"**

2. **Verify HTTPS:**
   - `https://vouchai.app` → Frontend
   - `https://api.vouchai.app` → Backend

### If NOT Using Cloudflare Proxy:

Your hosting platform (Railway/Vercel) provides SSL automatically.

---

## ⚙️ Step 5: Update Frontend API URL

After backend is deployed, update frontend to use production API.

### In Lovable (before deploying):

Update the API base URL in your code:
```javascript
// Change from:
const API_URL = "http://localhost:8000"

// To:
const API_URL = "https://api.vouchai.app"
```

Or use environment variables:
```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
```

Then set `VITE_API_URL=https://api.vouchai.app` in Vercel/Netlify.

---

## ✅ Step 6: Test Your Deployment

### Backend Test:
```bash
curl https://api.vouchai.app/
# Should return: {"message": "VouchAI v1 - Research You Can Vouch For", ...}

curl https://api.vouchai.app/stats
# Should return stats
```

### Frontend Test:
1. Visit `https://vouchai.app`
2. Should see your beautiful frontend
3. Submit a research query
4. Verify it calls `api.vouchai.app`

---

## 🚨 Troubleshooting

### CORS Errors?

Update your `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vouchai.app",
        "https://www.vouchai.app",
        "http://localhost:5173"  # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL Certificate Errors?

- Wait 5-10 minutes for DNS propagation
- Check Cloudflare SSL mode is "Full (strict)"
- Verify hosting platform has SSL enabled

### 404 Not Found?

- Check DNS records are correct
- Verify hosting platform deployment succeeded
- Check Cloudflare proxy status (orange cloud)

### API Timeout?

- Check backend logs on Railway/Render
- Verify API keys are set in environment
- Test backend URL directly

---

## 📊 Recommended DNS Setup

**Complete Cloudflare DNS Configuration:**

```
Type    Name    Content                              TTL    Proxy
A       @       76.76.21.21 (or Vercel CNAME)       Auto   Proxied
CNAME   www     vouchai.app                          Auto   Proxied
CNAME   api     your-backend.railway.app             Auto   Proxied
TXT     @       "v=spf1 include:_spf.mx.cloudflare.net ~all" (for email)
```

---

## 🎯 Quick Start Checklist

- [ ] Deploy backend to Railway/Render/Fly
- [ ] Get backend URL (e.g., `api.vouchai.app`)
- [ ] Add environment variables (API keys) to hosting platform
- [ ] Test backend: `curl https://api.vouchai.app/`
- [ ] Deploy frontend to Vercel/Netlify/Lovable
- [ ] Update frontend API_URL to production backend
- [ ] Configure Cloudflare DNS:
  - [ ] Add A/CNAME record for `@` → frontend
  - [ ] Add CNAME record for `api` → backend
- [ ] Enable Cloudflare proxy (orange cloud)
- [ ] Set Cloudflare SSL to "Full (strict)"
- [ ] Wait 5-10 minutes for DNS propagation
- [ ] Test `https://vouchai.app` in browser
- [ ] Test research query end-to-end
- [ ] Check `https://vouchai.app/stats`

---

## 💰 Cost Estimate

**Free Tier (Perfect for MVP):**
- Railway: Free $5 credit/month (enough for API)
- Vercel: Free tier (perfect for frontend)
- Cloudflare: Free (DNS + SSL)
- **Total: $0/month** (within free limits)

**Paid (When You Scale):**
- Railway: ~$5-20/month
- Vercel Pro: $20/month
- Cloudflare: Free (or $20/month for Pro features)

---

## 🔄 Deployment Workflow

### For Future Updates:

1. **Backend Changes:**
   ```bash
   git add .
   git commit -m "Update backend"
   git push
   # Railway/Render auto-deploys
   ```

2. **Frontend Changes:**
   - Update in Lovable
   - Re-export and push to GitHub
   - Vercel auto-deploys

---

## 🎉 You're Live!

After deployment:

1. Visit **https://vouchai.app**
2. Your 4-agent research platform is live!
3. Share it on LinkedIn with [LINKEDIN_POST.md](LINKEDIN_POST.md)

---

**Need Help?**

- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Cloudflare docs: https://developers.cloudflare.com

---

*VouchAI v1 - Research You Can Vouch For*
*Live at: vouchai.app*
