@echo off
REM Deploy Glazing PM API to Google Cloud Run

echo ======================================================================
echo   DEPLOY TO GOOGLE CLOUD RUN
echo ======================================================================
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Google Cloud SDK not found
    echo.
    echo Please install it from:
    echo https://cloud.google.com/sdk/docs/install
    echo.
    pause
    exit /b 1
)

echo [1/6] Checking gcloud authentication...
gcloud auth list

echo.
echo [2/6] Setting project...
gcloud config get-value project

echo.
set /p PROJECT_ID="Enter your Google Cloud Project ID (or press Enter to use current): "
if not "%PROJECT_ID%"=="" (
    gcloud config set project %PROJECT_ID%
)

echo.
echo [3/6] Building Docker image...
cd api
gcloud builds submit --tag gcr.io/%PROJECT_ID%/glazing-pm-api

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [4/6] Deploying to Cloud Run...
gcloud run deploy glazing-pm-api ^
    --image gcr.io/%PROJECT_ID%/glazing-pm-api ^
    --region us-central1 ^
    --platform managed ^
    --allow-unauthenticated ^
    --memory 512Mi ^
    --cpu 1 ^
    --timeout 300 ^
    --max-instances 10

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Deployment failed
    pause
    exit /b 1
)

echo.
echo [5/6] Setting environment variables...
set /p API_KEY="Enter your ANTHROPIC_API_KEY: "
gcloud run services update glazing-pm-api ^
    --region us-central1 ^
    --update-env-vars ANTHROPIC_API_KEY=%API_KEY%

echo.
echo [6/6] Getting service URL...
gcloud run services describe glazing-pm-api ^
    --region us-central1 ^
    --format "value(status.url)"

echo.
echo ======================================================================
echo   DEPLOYMENT COMPLETE!
echo ======================================================================
echo.
echo Copy the URL above and update frontend/config.js:
echo   API_URL_PRODUCTION: 'YOUR_CLOUD_RUN_URL'
echo.
echo Then commit and push:
echo   git add frontend/config.js
echo   git commit -m "Update production API URL"
echo   git push origin dev
echo.
pause
