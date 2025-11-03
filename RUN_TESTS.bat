@echo off
REM Quick test batch file for Windows
REM Run all system tests

echo ======================================================================
echo   GLAZING PM AI - SYSTEM TESTS
echo ======================================================================
echo.

REM Set API key
set ANTHROPIC_API_KEY=%anthropicAPIkey%

echo [1/4] Testing Anthropic API connection...
python test_connections.py
if errorlevel 1 (
    echo ERROR: API connection failed
    pause
    exit /b 1
)

echo.
echo [2/4] Testing Vendor Management System...
python test_vendor_system.py
if errorlevel 1 (
    echo ERROR: Vendor system test failed
    pause
    exit /b 1
)

echo.
echo [3/4] Testing Dashboard System...
python test_dashboard_system.py
if errorlevel 1 (
    echo ERROR: Dashboard system test failed
    pause
    exit /b 1
)

echo.
echo [4/4] Listing current projects...
echo.
type Logs\project_registry.csv
echo.

echo ======================================================================
echo   ALL TESTS PASSED - SYSTEM READY
echo ======================================================================
echo.
echo NEXT STEPS:
echo 1. Create a Google Sheet
echo 2. Run: python test_vendor_system.py "SHEET_URL"
echo 3. Run: python test_dashboard_system.py dashboard "SHEET_URL"
echo 4. Run: python test_dashboard_system.py project P001 "SHEET_URL"
echo.
echo ======================================================================
pause
