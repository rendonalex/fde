# Deploy via GitHub Codespaces (100% Free)

**No credit card required. Runs for free using GitHub's 60 hours/month.**

---

## Step 1: Create a Codespace

1. Go to https://github.com/rendonalex/fde
2. Click the green **"Code"** button
3. Click **"Codespaces"** tab
4. Click **"Create codespace on main"**
5. Wait ~2 minutes for environment to build

---

## Step 2: Set Your API Key

In the Codespace terminal:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

---

## Step 3: Start All Services

```bash
cd capstone
./start-demo.sh
```

Wait ~30 seconds for all services to start. You'll see:
- ✅ ADR-1 running on port 8000
- ✅ ADR-4 running on port 8001
- ✅ Backend running on port 3001
- ✅ Frontend running on port 5173

---

## Step 4: Make Port Public

1. Look at the **"PORTS"** tab (bottom panel in Codespaces)
2. Find port **5173** (Frontend)
3. Right-click → **"Port Visibility"** → **"Public"**
4. Copy the **Forwarded Address** URL (e.g., `https://xyz-5173.app.github.dev`)

---

## Step 5: Share Link

**Send that URL to your coach!**

Example: `https://xyz-5173.app.github.dev`

---

## ⚠️ Important Notes

- **Keep Codespace running** during demo (link only works while active)
- **Free tier**: 60 hours/month (plenty for demos)
- **Stop Codespace** after demo to save hours
- First load takes ~30 seconds (services waking up)

---

## Stopping Services

In terminal: Press **Ctrl+C**

To stop Codespace: Codespaces menu → "Stop Current Codespace"

---

## Troubleshooting

**Port 5173 not listed?**
- Wait 30 seconds for frontend to start
- Check terminal for errors

**Services not starting?**
- Make sure you exported `ANTHROPIC_API_KEY`
- Run: `echo $ANTHROPIC_API_KEY` (should show your key)

**Link not working?**
- Verify port 5173 is **Public** (not Private)
- Try opening in incognito mode

---

## Cost: $0

GitHub Codespaces free tier:
- 60 hours/month (core hours)
- 15 GB storage
- Perfect for demos!

**After demo:** Stop the Codespace to preserve hours for future demos.
