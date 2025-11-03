# Check if ready to deploy to Google Cloud Run

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Google Cloud Run - Deployment Check" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ready = $true

# Check 1: gcloud installed
Write-Host "[1/5] Checking gcloud CLI..." -ForegroundColor Yellow
try {
    $version = gcloud version 2>$null | Select-Object -First 1
    Write-Host "  ✓ gcloud installed: $version" -ForegroundColor Green
} catch {
    Write-Host "  ✗ gcloud CLI not found" -ForegroundColor Red
    Write-Host "     Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    $ready = $false
}

# Check 2: Authenticated
Write-Host "`n[2/5] Checking authentication..." -ForegroundColor Yellow
try {
    $account = gcloud config get-value account 2>$null
    if ($account) {
        Write-Host "  ✓ Authenticated as: $account" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Not authenticated" -ForegroundColor Red
        Write-Host "     Run: gcloud auth login" -ForegroundColor Yellow
        $ready = $false
    }
} catch {
    Write-Host "  ✗ Cannot check authentication" -ForegroundColor Red
    $ready = $false
}

# Check 3: Project set
Write-Host "`n[3/5] Checking project..." -ForegroundColor Yellow
try {
    $project = gcloud config get-value project 2>$null
    if ($project) {
        Write-Host "  ✓ Project: $project" -ForegroundColor Green
    } else {
        Write-Host "  ✗ No project set" -ForegroundColor Red
        Write-Host "     Run: gcloud config set project YOUR-PROJECT-ID" -ForegroundColor Yellow
        $ready = $false
    }
} catch {
    Write-Host "  ✗ Cannot check project" -ForegroundColor Red
    $ready = $false
}

# Check 4: API key available
Write-Host "`n[4/5] Checking Anthropic API key..." -ForegroundColor Yellow
if ($env:anthropicAPIkey) {
    $keyPreview = $env:anthropicAPIkey.Substring(0, 10) + "..." + $env:anthropicAPIkey.Substring($env:anthropicAPIkey.Length - 4)
    Write-Host "  ✓ API key found: $keyPreview" -ForegroundColor Green
} elseif ($env:ANTHROPIC_API_KEY) {
    $keyPreview = $env:ANTHROPIC_API_KEY.Substring(0, 10) + "..." + $env:ANTHROPIC_API_KEY.Substring($env:ANTHROPIC_API_KEY.Length - 4)
    Write-Host "  ✓ API key found: $keyPreview" -ForegroundColor Green
} else {
    Write-Host "  ✗ Anthropic API key not found in environment" -ForegroundColor Red
    Write-Host "     You'll need to provide it during deployment" -ForegroundColor Yellow
}

# Check 5: Docker files exist
Write-Host "`n[5/5] Checking deployment files..." -ForegroundColor Yellow
if (Test-Path "api/Dockerfile") {
    Write-Host "  ✓ Dockerfile exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Dockerfile missing" -ForegroundColor Red
    $ready = $false
}

if (Test-Path "api/main.py") {
    Write-Host "  ✓ API code exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ API code missing" -ForegroundColor Red
    $ready = $false
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
if ($ready) {
    Write-Host "  ✓ READY TO DEPLOY!" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Enable APIs:" -ForegroundColor Yellow
    Write-Host "     gcloud services enable run.googleapis.com" -ForegroundColor Gray
    Write-Host "     gcloud services enable containerregistry.googleapis.com" -ForegroundColor Gray
    Write-Host "     gcloud services enable cloudbuild.googleapis.com" -ForegroundColor Gray
    Write-Host "`n  2. Deploy:" -ForegroundColor Yellow
    Write-Host "     .\deploy-cloud-run.bat" -ForegroundColor Gray
    Write-Host "     OR follow DEPLOY_NOW.md step-by-step" -ForegroundColor Gray
} else {
    Write-Host "  ✗ NOT READY - Fix issues above" -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Cyan
}

Write-Host ""
