# Deployment Guide - Render.com

Step-by-step instructions to deploy your AI Claims Processing Workflow to Render.com.

---

## ✅ Prerequisites

1. GitHub account
2. Render.com account (free) - [Sign up here](https://render.com)
3. Anthropic API key - [Get one here](https://console.anthropic.com/)

---

## 📦 Step 1: Push to GitHub

```bash
cd ~/gh/fde/capstone

# Add all files
git add .

# Commit
git commit -m "Add deployment configuration for Render.com"

# Push to GitHub
git push origin main
```

---

## 🚀 Step 2: Deploy to Render

### Option A: One-Click Blueprint (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New" → "Blueprint"**
3. **Connect your GitHub repo**: `rendonalex/fde`
4. **Select `main` branch**
5. **Render auto-detects `render.yaml`** and shows 4 services:
   - `adr1-intake-agent` (Python)
   - `adr4-triage-agent` (Python)
   - `workflow-backend` (Node.js)
   - `workflow-frontend` (Static Site)
6. **Click "Apply"**

### Option B: Manual Service Creation

If blueprint doesn't work, create each service manually:

#### Service 1: ADR-1 Intake Agent
- **Type**: Web Service
- **Name**: `adr1-intake-agent`
- **Runtime**: Python 3
- **Build Command**: `pip install -r adr1-intake-agent/requirements.txt`
- **Start Command**: `cd adr1-intake-agent && uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `ANTHROPIC_API_KEY` = (your key)
  - `PYTHON_VERSION` = `3.9.18`

#### Service 2: ADR-4 Triage Agent
- **Type**: Web Service
- **Name**: `adr4-triage-agent`
- **Runtime**: Python 3
- **Build Command**: `pip install -r adr4-triage-agent/requirements.txt`
- **Start Command**: `cd adr4-triage-agent && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `ANTHROPIC_API_KEY` = (your key)
  - `PYTHON_VERSION` = `3.9.18`

#### Service 3: Workflow Backend
- **Type**: Web Service
- **Name**: `workflow-backend`
- **Runtime**: Node
- **Build Command**: `cd workflow-ui/backend && npm install`
- **Start Command**: `cd workflow-ui/backend && node server.js`
- **Environment Variables**:
  - `ADR1_URL` = `https://adr1-intake-agent.onrender.com` (use your service URL)
  - `ADR4_URL` = `https://adr4-triage-agent.onrender.com` (use your service URL)

#### Service 4: Workflow Frontend
- **Type**: Static Site
- **Name**: `workflow-frontend`
- **Build Command**: `cd workflow-ui/frontend && npm install && npm run build`
- **Publish Directory**: `workflow-ui/frontend/dist`
- **Environment Variables**:
  - `VITE_API_URL` = `https://workflow-backend.onrender.com` (use your backend URL)

---

## 🔑 Step 3: Add API Key

For each Python service (ADR-1, ADR-4):

1. Go to service dashboard
2. Click **"Environment"** tab
3. Add variable:
   - **Key**: `ANTHROPIC_API_KEY`
   - **Value**: `sk-ant-api03-...` (your API key)
4. Click **"Save Changes"**
5. Service auto-redeploys

---

## ⏳ Step 4: Wait for Deployment

- Each service takes ~3-5 minutes to build
- Watch build logs in Render dashboard
- ✅ Green checkmark = deployed successfully
- ❌ Red X = check logs for errors

---

## 🌐 Step 5: Get Your Link

Once `workflow-frontend` deploys:

1. Click on the service
2. Copy the URL (e.g., `https://workflow-frontend-abc123.onrender.com`)
3. **Share this link with your coach!**

---

## 🧪 Step 6: Test Deployment

1. Open your deployed URL
2. Wait ~30-60 seconds (free tier services sleep when inactive)
3. Try processing a claim:
   - Select `test-claims/t-CLM-2026-1000001.edi`
   - Click "Process Selected Claims"
   - Claim should route to Fast Path

---

## ⚠️ Common Issues

### Issue 1: "Service Unavailable" on first request
**Cause**: Free tier services sleep after 15 min inactivity  
**Fix**: Wait 30-60 seconds, refresh page

### Issue 2: ADR-1 or ADR-4 returns 500 error
**Cause**: Missing API key  
**Fix**: Check Environment tab, ensure `ANTHROPIC_API_KEY` is set

### Issue 3: Frontend can't connect to backend
**Cause**: `VITE_API_URL` not set or wrong URL  
**Fix**: Update `VITE_API_URL` in frontend environment to correct backend URL

### Issue 4: Build fails with Python version error
**Cause**: Render using wrong Python version  
**Fix**: Add `PYTHON_VERSION=3.9.18` environment variable

### Issue 5: "Module not found" errors
**Cause**: Build command not running from correct directory  
**Fix**: Ensure build commands start with `cd <service-dir>`

---

## 🔄 Updating Deployment

After making code changes locally:

```bash
git add .
git commit -m "Update feature X"
git push origin main
```

Render auto-detects the push and redeploys all services automatically (takes ~5 min).

---

## 💰 Cost

**Free Tier**: 750 hours/month shared across all services  
**Usage**: ~4 services × 24h/day = 96 hours/day  
**Free for**: ~7-8 days/month of continuous uptime  
**After that**: Services shut down or upgrade to paid ($7/month per service)

**For a demo/coaching session**: Free tier is perfect!

---

## 📊 Monitoring

View logs in real-time:
1. Go to service dashboard
2. Click **"Logs"** tab
3. See requests, errors, API calls

---

## 🗑️ Cleanup (After Demo)

To avoid hitting free tier limits:

1. Go to Render dashboard
2. Click each service → **Settings** → **Delete Service**
3. Or **Suspend** instead of deleting (can resume later)

---

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- Check build logs for specific error messages
- Common fix: Ensure all file paths in commands are correct

---

**🎉 Once deployed, share your link!**

Example: `https://fde-claims-workflow.onrender.com`
