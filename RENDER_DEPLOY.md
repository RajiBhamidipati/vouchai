# Deploy VouchAI Backend to Render.com (Free)

## Why Render?
- 100% free tier (no credit card needed)
- Simpler than Railway
- Auto-deploys from GitHub
- Works great with Python/FastAPI

---

## Step-by-Step Deployment

### Step 1: Sign Up on Render

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest)

### Step 2: Create New Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Connect your **vouchai** GitHub repository
   - If you don't see it, click "Configure account" and give Render access

### Step 3: Configure Your Service

Fill in these settings:

**Basic Settings:**
- **Name:** `vouchai-api`
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** (not "Starter")

### Step 4: Add Environment Variables

Scroll down to **"Environment Variables"** section:

Click **"Add Environment Variable"** and add:

1. **Key:** `GOOGLE_API_KEY`
   **Value:** `your_actual_google_api_key`

2. **Key:** `TAVILY_API_KEY`
   **Value:** `your_actual_tavily_api_key`

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will start building (takes 2-3 minutes)
3. Wait for "Live" status

### Step 6: Get Your Backend URL

Once deployed, you'll see your URL at the top:
- Example: `https://vouchai-api.onrender.com`
- Copy this URL - you'll need it for Cloudflare DNS

---

## Step 7: Test Your Backend

Open this URL in your browser:
```
https://vouchai-api.onrender.com/
```

You should see:
```json
{
  "message": "VouchAI v1 - Research You Can Vouch For",
  "status": "running",
  "version": "1.0.0",
  "domain": "vouchai.app"
}
```

Also test:
```
https://vouchai-api.onrender.com/stats
```

---

## Important: Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (more than enough)
- ⚠️ Sleeps after 15 min of inactivity (first request takes 30-60 seconds to wake up)
- ✅ Unlimited deploys
- ✅ Auto-deploys on git push

**For production/demo:** This is perfect! First request might be slow, but then it's fast.

---

## Next Steps After Backend Deployment

Once your backend is live on Render:

### 1. Configure Cloudflare DNS
Add this CNAME record:
```
Type: CNAME
Name: api
Target: vouchai-api.onrender.com
Proxy: Proxied (orange cloud)
```

### 2. Update Lovable Frontend
In your Lovable project, update the API URL to:
```
https://api.vouchai.app
```

---

## Auto-Deploy on Git Push

Render automatically redeploys when you push to GitHub! Just:
```bash
git add .
git commit -m "Update backend"
git push
```

Render detects the push and redeploys automatically.

---

**Ready? Go to https://render.com and follow the steps above!**
