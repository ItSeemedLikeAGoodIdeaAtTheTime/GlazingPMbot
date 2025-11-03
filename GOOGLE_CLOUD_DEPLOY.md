# Google Cloud Run Deployment Guide

## 🚀 Deploy Your Backend to Google Cloud Run

You already have Google credentials from the Sheets integration, so this will be straightforward!

---

## ⚡ Quick Deploy (10 minutes)

### Prerequisites

1. **Google Cloud Project** - You should already have one
2. **Google Cloud SDK** - Install if needed
3. **Billing enabled** - Free tier is generous (2M requests/month)

---

## 📦 Step-by-Step Deployment

### Step 1: Install Google Cloud SDK (if not installed)

**Download:** https://cloud.google.com/sdk/docs/install-sdk

**Windows:**
```bash
# Download and run: GoogleCloudSDKInstaller.exe
```

**After install, run:**
```bash
gcloud init
```

This will:
- Log you in to your Google account
- Select your project
- Set default region

### Step 2: Verify Your Setup

```bash
# Check you're logged in
gcloud auth list

# Check your project
gcloud config get-value project

# If you need to set a different project:
gcloud config set project YOUR-PROJECT-ID
```

### Step 3: Enable Required APIs

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com
```

### Step 4: Deploy! (Easy Mode)

**Option A: Use the Batch Script (Windows)**

```bash
# Just run this!
deploy-cloud-run.bat
```

The script will:
1. Check if gcloud is installed
2. Build your Docker image
3. Deploy to Cloud Run
4. Set your API key
5. Give you the URL

**Option B: Manual Commands**

```bash
# Navigate to project root
cd "C:\Users\clynn\OneDrive\Desktop\Glazing PM Ai"

# Build and deploy
gcloud run deploy glazing-pm-api \
  --source ./api \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### Step 5: Set Environment Variables

```bash
# Set your Anthropic API key
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --update-env-vars ANTHROPIC_API_KEY=your-key-here
```

### Step 6: Get Your URL

```bash
gcloud run services describe glazing-pm-api \
  --region us-central1 \
  --format "value(status.url)"
```

Copy this URL! It will look like:
```
https://glazing-pm-api-abc123-uc.a.run.app
```

### Step 7: Update Frontend Config

Edit `frontend/config.js`:

```javascript
const CONFIG = {
    API_URL_PRODUCTION: 'https://glazing-pm-api-abc123-uc.a.run.app',  // Your Cloud Run URL
    // ...
};
```

### Step 8: Commit and Deploy

```bash
git add frontend/config.js
git commit -m "Add Google Cloud Run API URL"
git push origin dev

# When ready for production:
git checkout main
git merge dev
git push origin main
```

---

## 🔐 Upload Google Credentials (For Sheets)

Your `credentials.json` file is NOT in git (for security). You need to add it to Cloud Run:

### Option 1: As Environment Variable (Recommended)

```bash
# Get the base64 encoded credentials
certutil -encode credentials.json credentials-base64.txt

# Copy the content (without BEGIN/END lines)
# Then set as environment variable:
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --update-env-vars GOOGLE_SHEETS_CREDENTIALS_BASE64="paste-base64-here"
```

Then update your Python code to decode it:

```python
import os
import base64
import json

# In scripts that use Google Sheets
creds_base64 = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_BASE64")
if creds_base64:
    creds_json = base64.b64decode(creds_base64)
    # Write to temp file or use directly
```

### Option 2: As Secret (More Secure)

```bash
# Create secret
gcloud secrets create google-sheets-creds \
  --data-file=credentials.json

# Grant access to Cloud Run
gcloud secrets add-iam-policy-binding google-sheets-creds \
  --member="serviceAccount:YOUR-PROJECT-NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update Cloud Run to mount secret
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --update-secrets GOOGLE_SHEETS_CREDENTIALS=google-sheets-creds:latest
```

---

## 🧪 Test Your Deployment

### 1. Test Health Endpoint

```bash
curl https://your-cloud-run-url.run.app/health
```

Should return:
```json
{
  "status": "healthy",
  "anthropic_api": "configured",
  "timestamp": "..."
}
```

### 2. Test API Docs

Visit: `https://your-cloud-run-url.run.app/docs`

You should see the interactive API documentation.

### 3. Test Full Flow

1. Go to your GitHub Pages site (once enabled)
2. Upload a test PDF
3. Generate SOV
4. Verify it works end-to-end

---

## 💰 Cost Estimate

**Google Cloud Run Pricing:**
- **Free Tier:** 2M requests/month, 360,000 GB-seconds compute
- **After Free Tier:** ~$0.00002 per request

**Typical usage for your app:**
- Small business: **FREE** (well within limits)
- 100 projects/month: ~$2-5/month
- 1000 projects/month: ~$20-40/month

**Your configuration:**
- Memory: 512MB
- CPU: 1
- Timeout: 5 minutes
- Max instances: 10

**Estimated costs:**
- 0-50 projects/month: **$0** (free tier)
- 100 projects/month: **$2-3**
- 500 projects/month: **$10-15**

---

## 🔧 Configuration Options

### Increase Resources (If Needed)

```bash
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --memory 1Gi \
  --cpu 2
```

### Set Minimum Instances (Avoid Cold Starts)

```bash
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --min-instances 1
```

Note: Keeping 1 minimum instance running costs ~$10/month but eliminates cold starts.

### Increase Timeout (For Large Documents)

```bash
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --timeout 600  # 10 minutes
```

---

## 📊 Monitoring

### View Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=glazing-pm-api" --limit 50
```

Or visit: https://console.cloud.google.com/run

### View Metrics

Go to Cloud Console → Cloud Run → glazing-pm-api → Metrics

You'll see:
- Request count
- Latency
- Error rate
- CPU/Memory usage

---

## 🔄 Update Deployment

When you make changes:

```bash
# Pull latest from git
git pull origin dev

# Redeploy (uses same command as initial deploy)
gcloud run deploy glazing-pm-api \
  --source ./api \
  --region us-central1 \
  --allow-unauthenticated
```

Or use Cloud Build for CI/CD:

```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## 🐛 Troubleshooting

### "gcloud not found"
Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### "Permission denied"
```bash
gcloud auth login
gcloud auth application-default login
```

### "Billing not enabled"
Go to: https://console.cloud.google.com/billing
Enable billing (free tier is generous!)

### "Service deployment failed"
Check logs:
```bash
gcloud run services logs read glazing-pm-api --region us-central1
```

### "Cold starts are slow"
Set minimum instances:
```bash
gcloud run services update glazing-pm-api \
  --region us-central1 \
  --min-instances 1
```

### "CORS errors"
Check that `frontend/config.js` has correct URL and that CORS is configured in `api/main.py`.

---

## 🎯 Next Steps After Deployment

1. **Copy Cloud Run URL**
2. **Update `frontend/config.js`**
3. **Commit and push to dev**
4. **Test with GitHub Pages**
5. **Merge to main when ready**

---

## 📝 Quick Commands Reference

```bash
# Deploy
gcloud run deploy glazing-pm-api --source ./api --region us-central1 --allow-unauthenticated

# Update env vars
gcloud run services update glazing-pm-api --region us-central1 --update-env-vars KEY=VALUE

# Get URL
gcloud run services describe glazing-pm-api --region us-central1 --format "value(status.url)"

# View logs
gcloud run services logs read glazing-pm-api --region us-central1

# Delete service
gcloud run services delete glazing-pm-api --region us-central1
```

---

## ✅ Deployment Checklist

- [ ] Google Cloud SDK installed
- [ ] Authenticated with gcloud
- [ ] Project selected
- [ ] APIs enabled (Cloud Run, Container Registry, Cloud Build)
- [ ] Service deployed
- [ ] ANTHROPIC_API_KEY set
- [ ] Google credentials uploaded (for Sheets features)
- [ ] Cloud Run URL copied
- [ ] Frontend config updated
- [ ] Changes committed to git
- [ ] GitHub Pages enabled
- [ ] Full workflow tested

---

**You're ready to deploy! Run `deploy-cloud-run.bat` to get started!** 🚀
