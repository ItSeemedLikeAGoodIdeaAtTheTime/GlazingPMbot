# Deployment Guide - Glazing PM AI

## 🌐 Live Website Architecture

### Frontend (GitHub Pages) ✓ Ready
**URL:** https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/

**Status:** Auto-deploys from `main` branch
**What's hosted:** Web interface (HTML/CSS/JS)
**Cost:** Free

### Backend (Choose One)

The API backend needs to be hosted separately. Here are your options:

---

## 🚀 Backend Deployment Options

### Option 1: Railway (Recommended - Easiest)

**Pros:**
- ✓ Free tier (500 hours/month)
- ✓ Auto-deploy from GitHub
- ✓ Simplest setup (5 minutes)
- ✓ Automatic HTTPS

**Setup Steps:**

1. **Go to Railway:** https://railway.app
2. **Sign in with GitHub**
3. **New Project → Deploy from GitHub**
4. **Select:** `GlazingPMbot` repository
5. **Root Directory:** `/api`
6. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Add Environment Variable:**
   ```
   ANTHROPIC_API_KEY = your-key-here
   ```
8. **Deploy!**
9. **Copy the Railway URL** (e.g., `https://glazingpmbot.railway.app`)
10. **Update `frontend/config.js`:**
    ```javascript
    API_URL_PRODUCTION: 'https://glazingpmbot.railway.app'
    ```

**Cost:** Free tier = 500 hours/month (~20 days)

---

### Option 2: Render

**Pros:**
- ✓ Free tier (forever)
- ✓ Auto-deploy from GitHub
- ✓ Good for APIs

**Cons:**
- ✗ Spins down after 15 min inactivity (slow cold starts)

**Setup Steps:**

1. **Go to Render:** https://render.com
2. **Sign in with GitHub**
3. **New → Web Service**
4. **Connect:** `GlazingPMbot` repository
5. **Settings:**
   - **Root Directory:** `api`
   - **Build Command:** `pip install -r requirements.txt && pip install -r ../requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables:**
   ```
   ANTHROPIC_API_KEY = your-key-here
   PYTHON_VERSION = 3.12
   ```
7. **Create Web Service**
8. **Copy the Render URL**
9. **Update `frontend/config.js`**

**Cost:** Free forever, but spins down when idle

---

### Option 3: Google Cloud Run (Your Google Account)

**Pros:**
- ✓ Free tier (2M requests/month)
- ✓ You already have Google credentials
- ✓ Scales to zero (pay only for usage)
- ✓ Fast cold starts

**Cons:**
- ✗ Requires Docker setup
- ✗ More complex initial setup

**Setup Steps:**

1. **Install Google Cloud CLI:** https://cloud.google.com/sdk/docs/install

2. **Create Dockerfile in `/api`:**
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   COPY ../requirements.txt ./requirements-parent.txt
   RUN pip install -r requirements.txt && pip install -r requirements-parent.txt
   COPY . .
   CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy:**
   ```bash
   gcloud run deploy glazing-pm-api \
     --source ./api \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ANTHROPIC_API_KEY=your-key-here
   ```

4. **Copy the Cloud Run URL**
5. **Update `frontend/config.js`**

**Cost:** Free tier = 2M requests/month

---

### Option 4: Fly.io

**Pros:**
- ✓ Good free tier (3 small VMs)
- ✓ Fast global deployment
- ✓ Free SSL

**Cons:**
- ✗ Requires Docker
- ✗ CLI tool needed

**Setup Steps:**

1. **Install Fly CLI:** https://fly.io/docs/hands-on/install-flyctl/

2. **In the `/api` folder:**
   ```bash
   fly launch
   # Follow prompts, say NO to Postgres/Redis
   ```

3. **Set secrets:**
   ```bash
   fly secrets set ANTHROPIC_API_KEY=your-key-here
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

5. **Copy the Fly.io URL**
6. **Update `frontend/config.js`**

**Cost:** 3 small VMs free

---

### Option 5: Local + ngrok (Testing Only)

**Pros:**
- ✓ No deployment needed
- ✓ Instant setup
- ✓ Good for testing

**Cons:**
- ✗ Your computer must be running
- ✗ Not permanent
- ✗ URL changes each restart (unless paid plan)

**Setup Steps:**

1. **Install ngrok:** https://ngrok.com/download

2. **Start your local API:**
   ```bash
   START_WEB_APP.bat
   ```

3. **In another terminal:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the ngrok URL** (e.g., `https://abc123.ngrok.io`)

5. **Update `frontend/config.js`:**
   ```javascript
   API_URL_PRODUCTION: 'https://abc123.ngrok.io'
   ```

**Cost:** Free tier available

---

## 📝 After Deploying Backend

### Update Frontend Configuration

Edit `frontend/config.js`:

```javascript
const CONFIG = {
    API_URL_PRODUCTION: 'https://YOUR-BACKEND-URL-HERE',  // ← Update this!
    // ...
};
```

### Commit and Push

```bash
git add frontend/config.js
git commit -m "Update production API URL"
git push origin dev
```

### Merge to Main

When ready for production:
```bash
git checkout main
git merge dev
git push origin main
```

GitHub Pages will auto-deploy the updated frontend.

---

## 🧪 Testing Your Live Site

### 1. Check Frontend
Visit: `https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/`

Open browser console (F12), should see:
```
Running in PRODUCTION mode
API URL: https://your-backend-url
```

### 2. Check Backend
Visit: `https://your-backend-url/health`

Should return:
```json
{
  "status": "healthy",
  "anthropic_api": "configured",
  "timestamp": "..."
}
```

### 3. Test Upload
Upload a small PDF and verify it works end-to-end.

---

## 🔐 Security Considerations

### Environment Variables (Backend)
Never commit these to git:
- `ANTHROPIC_API_KEY` - Set in hosting platform
- Google credentials - Upload separately to hosting platform

### CORS (Backend)
For production, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://itseemedlikeagoodideaatthetime.github.io",
        "http://localhost:8000"  # For local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Recommended Setup

**For Quick Testing:**
- Frontend: GitHub Pages ✓
- Backend: Railway or ngrok

**For Production:**
- Frontend: GitHub Pages ✓
- Backend: Railway (if <500hr/mo) or Google Cloud Run (unlimited requests)

**Best Overall:**
- Frontend: GitHub Pages ✓
- Backend: **Railway** (easiest) or **Google Cloud Run** (most scalable)

---

## 🆘 Troubleshooting

### Frontend shows but API calls fail
- Check browser console (F12) for CORS errors
- Verify API URL in `config.js`
- Check backend is running: visit `https://your-api-url/health`

### Backend deployment fails
- Check logs in hosting platform
- Verify all dependencies in `requirements.txt`
- Check environment variables are set

### "API key not configured" error
- Add `ANTHROPIC_API_KEY` environment variable to backend host

---

## 📈 Next Steps

1. **Enable GitHub Pages** (see below)
2. **Deploy backend** to Railway/Render/etc
3. **Update `config.js`** with backend URL
4. **Test live site**
5. **Merge to main** when ready

---

## 🔧 Enable GitHub Pages

### Via GitHub Website:

1. Go to: https://github.com/ItSeemedLikeAGoodIdeaAtTheTime/GlazingPMbot
2. Click **Settings**
3. Click **Pages** (left sidebar)
4. **Source:** Deploy from a branch
5. **Branch:** main
6. **Folder:** / (root)
7. Click **Save**
8. Wait 2-5 minutes
9. Visit: `https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/`

### Via Git:

```bash
# Already set up! Just push to main:
git checkout main
git merge dev
git push origin main
```

---

**Your frontend will be live at:**
```
https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/
```

**Next: Choose and deploy your backend!**
