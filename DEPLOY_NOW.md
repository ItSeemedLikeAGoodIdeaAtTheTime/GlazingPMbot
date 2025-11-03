# 🚀 Deploy to Google Cloud Run - Step by Step

You're authenticated! ✓ Now let's deploy.

---

## Step 1: Verify Setup (1 minute)

Open a **new PowerShell or Command Prompt** window and run:

```powershell
# Check gcloud is working
gcloud version

# Check your current project
gcloud config get-value project

# List your projects (if you have multiple)
gcloud projects list
```

**If you need to set a different project:**
```powershell
gcloud config set project YOUR-PROJECT-ID
```

---

## Step 2: Enable APIs (1 minute)

```powershell
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com
```

You should see messages like:
```
Operation "operations/..." finished successfully.
```

---

## Step 3: Deploy to Cloud Run (5-10 minutes)

### Option A: Use the Deployment Script (Easiest)

```powershell
cd "C:\Users\clynn\OneDrive\Desktop\Glazing PM Ai"
.\deploy-cloud-run.bat
```

The script will:
1. Build your Docker image
2. Deploy to Cloud Run
3. Ask for your API key
4. Give you the URL

### Option B: Manual Deployment (If script doesn't work)

```powershell
cd "C:\Users\clynn\OneDrive\Desktop\Glazing PM Ai"

# Build and submit to Cloud Build
cd api
gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/glazing-pm-api
cd ..

# Deploy to Cloud Run
gcloud run deploy glazing-pm-api `
  --image gcr.io/YOUR-PROJECT-ID/glazing-pm-api `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10
```

**When prompted:**
- Allow unauthenticated invocations: **Y** (yes)

---

## Step 4: Set Environment Variables (1 minute)

```powershell
# Set your Anthropic API key (replace with your actual key)
gcloud run services update glazing-pm-api `
  --region us-central1 `
  --update-env-vars ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Find your API key:**
- It's in your environment variables as `anthropicAPIkey`
- Or get it from: https://console.anthropic.com/

---

## Step 5: Get Your Cloud Run URL (30 seconds)

```powershell
# Get the service URL
gcloud run services describe glazing-pm-api `
  --region us-central1 `
  --format "value(status.url)"
```

**Copy the URL!** It will look like:
```
https://glazing-pm-api-abc123xyz-uc.a.run.app
```

---

## Step 6: Test Your Deployment (1 minute)

```powershell
# Test health endpoint (replace URL with yours)
curl https://YOUR-CLOUD-RUN-URL/health
```

Should return:
```json
{
  "status": "healthy",
  "anthropic_api": "configured",
  "timestamp": "..."
}
```

**Or visit in browser:**
```
https://YOUR-CLOUD-RUN-URL/docs
```

You should see the API documentation!

---

## Step 7: Update Frontend Config (2 minutes)

Edit `frontend/config.js` and update line:

```javascript
API_URL_PRODUCTION: 'https://your-cloud-run-url-here.run.app',
```

Replace with your actual Cloud Run URL.

Then commit:

```powershell
cd "C:\Users\clynn\OneDrive\Desktop\Glazing PM Ai"
git add frontend/config.js
git commit -m "Add Cloud Run API URL"
git push origin dev
```

---

## Step 8: Enable GitHub Pages (2 minutes)

1. Go to: https://github.com/ItSeemedLikeAGoodIdeaAtTheTime/GlazingPMbot
2. Click **Settings** → **Pages**
3. **Source:** Deploy from a branch
4. **Branch:** `main`
5. **Folder:** `/ (root)`
6. Click **Save**

Wait 2-5 minutes, then visit:
```
https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/
```

---

## Step 9: Merge to Production (When Ready)

```powershell
git checkout main
git merge dev
git push origin main
```

GitHub Pages will auto-update!

---

## 🎉 You're Live!

**Frontend:**
```
https://itseemedlikeagoodideaatthetime.github.io/GlazingPMbot/
```

**Backend:**
```
https://YOUR-CLOUD-RUN-URL.run.app
```

**API Docs:**
```
https://YOUR-CLOUD-RUN-URL.run.app/docs
```

---

## 📊 Monitor Your Deployment

**View in Cloud Console:**
```
https://console.cloud.google.com/run
```

**View Logs:**
```powershell
gcloud run services logs read glazing-pm-api --region us-central1
```

**View Metrics:**
Go to Cloud Console → Cloud Run → glazing-pm-api → Metrics

---

## 🔧 Troubleshooting

### Build fails with "permission denied"
```powershell
gcloud auth application-default login
```

### Deployment fails
Check logs:
```powershell
gcloud run services logs read glazing-pm-api --region us-central1 --limit 50
```

### API returns 500 errors
Check environment variables are set:
```powershell
gcloud run services describe glazing-pm-api --region us-central1
```

### Frontend can't connect to backend
- Check CORS settings in `api/main.py`
- Verify URL in `frontend/config.js`
- Check browser console (F12) for errors

---

## 💰 Estimated Costs

**With your expected usage:**
- 0-50 projects/month: **FREE** ✓
- 100 projects/month: ~$2-3
- 500 projects/month: ~$10-15

Free tier includes:
- 2M requests/month
- 360,000 GB-seconds compute

Most small businesses stay FREE!

---

## 🎯 Quick Commands Reference

```powershell
# Deploy/Update
gcloud run deploy glazing-pm-api --source ./api --region us-central1 --allow-unauthenticated

# Set env vars
gcloud run services update glazing-pm-api --region us-central1 --update-env-vars KEY=VALUE

# Get URL
gcloud run services describe glazing-pm-api --region us-central1 --format "value(status.url)"

# View logs
gcloud run services logs read glazing-pm-api --region us-central1

# Delete (if needed)
gcloud run services delete glazing-pm-api --region us-central1
```

---

## ✅ Deployment Checklist

- [x] gcloud authenticated ✓
- [ ] APIs enabled (run, containerregistry, cloudbuild)
- [ ] Service deployed
- [ ] ANTHROPIC_API_KEY set
- [ ] Cloud Run URL copied
- [ ] Frontend config updated
- [ ] Changes committed to git
- [ ] GitHub Pages enabled
- [ ] Full workflow tested

---

**Start with Step 2 (Enable APIs) in a new PowerShell window!**

If you run into any issues, let me know which step failed and I'll help debug.
