# Cloudflare DNS Setup for VouchAI v1

## 🌐 Quick Setup for vouchai.app

Follow these steps in your Cloudflare dashboard.

---

## Step 1: Log into Cloudflare

1. Go to https://dash.cloudflare.com
2. Select your domain: **vouchai.app**
3. Click **DNS** in the left sidebar

---

## Step 2: Choose Your Architecture

### Option A: Separate Subdomains (Recommended)

**Best for:** Clean separation, easier debugging

- Frontend: `vouchai.app`
- Backend API: `api.vouchai.app`

### Option B: Same Domain

**Best for:** Simpler setup, single domain

- Frontend: `vouchai.app`
- Backend: `vouchai.app/api` (requires proxy rules)

**We recommend Option A** - continue below for that setup.

---

## Step 3: Deploy Your Services First

Before configuring DNS, deploy:

1. **Backend** → Railway/Render/Fly
   - You'll get a URL like: `vouchai-production.up.railway.app`

2. **Frontend** → Vercel/Netlify/Lovable
   - You'll get a URL or IP address

---

## Step 4: Configure DNS Records in Cloudflare

### For Frontend (vouchai.app):

If using **Vercel**:
1. In Cloudflare DNS, click **Add record**
2. Fill in:
   ```
   Type: CNAME
   Name: @
   Target: cname.vercel-dns.com
   Proxy status: Proxied (orange cloud ☁️)
   TTL: Auto
   ```

If using **Netlify**:
1. In Cloudflare DNS, click **Add record**
2. Fill in:
   ```
   Type: A
   Name: @
   IPv4 address: 75.2.60.5 (Netlify load balancer)
   Proxy status: Proxied (orange cloud ☁️)
   TTL: Auto
   ```

### For WWW Redirect:

Add this record so `www.vouchai.app` redirects to `vouchai.app`:
```
Type: CNAME
Name: www
Target: vouchai.app
Proxy status: Proxied (orange cloud ☁️)
TTL: Auto
```

### For Backend API (api.vouchai.app):

If using **Railway**:
```
Type: CNAME
Name: api
Target: vouchai-production.up.railway.app
Proxy status: Proxied (orange cloud ☁️)
TTL: Auto
```

If using **Render**:
```
Type: CNAME
Name: api
Target: your-service.onrender.com
Proxy status: Proxied (orange cloud ☁️)
TTL: Auto
```

If using **Fly.io**:
```
Type: CNAME
Name: api
Target: your-app.fly.dev
Proxy status: Proxied (orange cloud ☁️)
TTL: Auto
```

---

## Step 5: SSL/TLS Configuration

1. In Cloudflare, go to **SSL/TLS** → **Overview**
2. Set encryption mode to: **Full (strict)**
3. This ensures end-to-end encryption

---

## Step 6: Wait for Propagation

DNS changes can take **5-10 minutes** to propagate.

Check status:
```bash
# Check if DNS is working
dig vouchai.app
dig api.vouchai.app

# Or visit:
nslookup vouchai.app
nslookup api.vouchai.app
```

---

## Step 7: Verify Deployment

### Test Backend:
```bash
curl https://api.vouchai.app/
# Should return: {"message": "VouchAI v1 - Research You Can Vouch For", ...}
```

### Test Frontend:
Open browser to: `https://vouchai.app`

### Test End-to-End:
1. Go to https://vouchai.app
2. Submit a research query
3. Verify it works!

---

## 🎯 Final DNS Configuration

Your DNS records should look like this:

| Type  | Name | Content/Target                    | Proxy  | Status |
|-------|------|-----------------------------------|--------|--------|
| CNAME | @    | cname.vercel-dns.com              | ☁️ Proxied | Active |
| CNAME | www  | vouchai.app                       | ☁️ Proxied | Active |
| CNAME | api  | vouchai-production.up.railway.app | ☁️ Proxied | Active |

---

## 🔧 Cloudflare Page Rules (Optional)

If you want to redirect HTTP to HTTPS:

1. Go to **Rules** → **Page Rules**
2. Create new rule:
   ```
   URL: http://*vouchai.app/*
   Setting: Always Use HTTPS
   ```

---

## 🚨 Troubleshooting

### "DNS_PROBE_FINISHED_NXDOMAIN"
- Wait 5-10 more minutes for DNS propagation
- Clear your browser cache
- Try in incognito mode

### "ERR_SSL_VERSION_OR_CIPHER_MISMATCH"
- Check SSL/TLS mode is "Full (strict)" in Cloudflare
- Verify hosting platform has SSL enabled
- Wait for SSL certificate provisioning (can take a few minutes)

### CORS Errors
- Check `main.py` has `https://vouchai.app` in allowed origins
- Redeploy backend after CORS changes
- Check browser console for exact error

### 404 Not Found
- Verify hosting platform deployment succeeded
- Check DNS records point to correct targets
- Test backend URL directly (without DNS)

---

## 📊 Cloudflare Analytics

After deployment, you can view:
- **Analytics** → See traffic to vouchai.app
- **Speed** → Performance metrics
- **Security** → Threats blocked

---

## ✅ Deployment Checklist

- [ ] Backend deployed (Railway/Render/Fly)
- [ ] Frontend deployed (Vercel/Netlify)
- [ ] DNS A/CNAME record for `@` → frontend
- [ ] DNS CNAME record for `www` → vouchai.app
- [ ] DNS CNAME record for `api` → backend
- [ ] All records set to "Proxied" (orange cloud)
- [ ] SSL/TLS set to "Full (strict)"
- [ ] Waited 5-10 minutes for DNS propagation
- [ ] Tested https://vouchai.app in browser
- [ ] Tested https://api.vouchai.app/
- [ ] Submitted test research query
- [ ] No CORS errors in browser console

---

## 🎉 You're Live!

Once all checks pass:

✅ https://vouchai.app → Your beautiful frontend
✅ https://api.vouchai.app → Your FastAPI backend
✅ SSL secured with Cloudflare
✅ Ready to share on LinkedIn!

---

## 📞 Need Help?

- Cloudflare Docs: https://developers.cloudflare.com/dns
- DNS Checker: https://dnschecker.org
- SSL Checker: https://www.sslshopper.com/ssl-checker.html

---

*VouchAI v1 - Research You Can Vouch For*
*Domain: vouchai.app*
