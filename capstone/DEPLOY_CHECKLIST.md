# Deployment Checklist ✅

Quick checklist before pushing to GitHub and deploying.

---

## Before Push

- [ ] **API Key Security**: Ensure `.env` files are in `.gitignore` (they are!)
- [ ] **Test Locally**: All 4 services running and working?
  - [ ] ADR-1 API (port 8000)
  - [ ] ADR-4 API (port 8001)
  - [ ] Workflow Backend (port 3001)
  - [ ] Workflow Frontend (port 5173)
- [ ] **Process Test Claim**: Can you process at least one claim end-to-end?

---

## Git Push

```bash
cd ~/gh/fde/capstone
git status                    # Check what's being committed
git add .                     # Add all deployment files
git commit -m "Add Render.com deployment config"
git push origin main          # Push to GitHub
```

---

## Render Setup

- [ ] **Account Created**: Signed up at render.com
- [ ] **Anthropic API Key Ready**: Have your key copied

---

## Deploy on Render

- [ ] **Blueprint Applied**: New → Blueprint → Connect repo → Apply
- [ ] **Services Created**: See 4 services in dashboard
- [ ] **API Keys Set**: Added `ANTHROPIC_API_KEY` to both Python services
- [ ] **Services Deployed**: All 4 services showing green checkmark

---

## Test Deployment

- [ ] **Frontend Loads**: Open `workflow-frontend` URL
- [ ] **Wait for Wake-Up**: First load takes 30-60 sec (free tier)
- [ ] **Process Test Claim**: Try `test-claims/t-CLM-2026-1000001.edi`
- [ ] **Check Routing**: Claim routes to correct queue
- [ ] **View Reasoning**: Can see ADR-4 reasoning trace

---

## Share Link

- [ ] **Copy URL**: From `workflow-frontend` service
- [ ] **Test in Incognito**: Works without your cookies?
- [ ] **Share with Coach**: Send link!

---

## Optional: Add Demo Data

Want to pre-load some processed claims for your coach?

1. Process 3-5 claims locally first
2. Take screenshots of each queue
3. Add to README or create a DEMO_GUIDE.md
4. Show expected results

---

## Troubleshooting Reference

If something breaks:
1. Check Render logs (Logs tab on each service)
2. Verify environment variables are set
3. See DEPLOYMENT.md "Common Issues" section
4. Still stuck? Check service URLs are correct in environment vars

---

**Time Estimate**: 
- Git push: 2 min
- Render setup: 10 min
- Deploy wait: 5-10 min
- Testing: 5 min
- **Total: ~25 minutes**

Good luck! 🚀
