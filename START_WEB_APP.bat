@echo off
REM Start Glazing PM AI Web Application

echo ======================================================================
echo   GLAZING PM AI - Web Application Startup
echo ======================================================================
echo.

REM Set API key
set ANTHROPIC_API_KEY=%anthropicAPIkey%

echo [1/2] Setting up environment...
echo   - API Key: Set
echo.

echo [2/2] Starting API server...
echo   - URL: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo.

echo ======================================================================
echo   SERVER STARTING - DO NOT CLOSE THIS WINDOW
echo ======================================================================
echo.
echo To use the web app:
echo 1. Keep this window open
echo 2. Open frontend\index.html in your browser
echo 3. Upload documents and generate SOVs
echo.
echo Press CTRL+C to stop the server
echo ======================================================================
echo.

cd /d "%~dp0"
python api\main.py

pause
