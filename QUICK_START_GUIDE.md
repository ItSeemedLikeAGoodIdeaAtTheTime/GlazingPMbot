# Glazing PM AI - Quick Start Guide

## Connection Status: ALL SYSTEMS OPERATIONAL ✓

- **Anthropic API:** ✓ Working (Claude Sonnet 4)
- **Google Sheets API:** ✓ Working (authenticated)
- **Vendor Database:** ✓ Ready (24 vendors)
- **Dashboard System:** ✓ Ready

---

## Quick Test Commands

### Test Both API Connections
```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"
python test_connections.py
```

### Test Just Anthropic API
```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"
python test_api_detailed.py
```

---

## Current Projects Status

| Project | Name | Documents | SOV | Tracking Sheets |
|---------|------|-----------|-----|-----------------|
| P001 | Fire Rated Doors - City Hospital | ✓ | ✓ | Ready to create |
| P002 | Lead Glass - Medical Center X-Ray | ✓ | ✗ | Ready to create |
| P003 | Dance Studio Mirrors - Arts Academy | ✓ | ✓ | Ready to create |

---

## Vendor Management System

**Status:** Fully implemented ✓

**Features:**
- 24 vendors across 8 categories
- Contact information and specialties
- Lead times and quality ratings
- Auto-formatted Google Sheets

**Categories:**
- Glass Manufacturers (6 vendors)
- Door Hardware (4 vendors)
- Metal & Aluminum (5 vendors)
- Paint & Finishing (2 vendors)
- Accessories & Supplies (4 vendors)
- Specialty Systems (2 vendors)
- Regional Fabricators (2 vendors)

**Top Vendors:**
- **Vitrum** (Roshain) - Premium glass, Canada - "Gold Standard"
- **Tacoma Glass** (Carrie) - Fast 2-3 day turnaround
- **IML** (Mike Fender) - Door hardware
- **Kawneer** (Skyler) - Curtain wall systems

### Create Vendor Database
```bash
# Create a new Google Sheet, then:
python scripts/vendor_manager.py "YOUR_SHEET_URL_HERE"
```

---

## Google Sheets Dashboard System

**Status:** Fully implemented ✓

**Available Features:**

### 1. Company Dashboard
Creates a master cash flow dashboard with:
- Total active projects summary
- Contract value totals
- 3-month cash flow forecast
- Project status overview

```bash
# Create in a new or existing sheet:
python scripts/google_sheets_extended.py dashboard "YOUR_SHEET_URL"
```

### 2. Project Tracking Sheets
For each project, creates 4 tracking tabs:
- **PO Log** - Purchase orders, delivery tracking, billing status
- **Submittal Log** - Submittal tracking, approvals, revisions
- **Installation Log** - Progress tracking, completion percentages
- **Invoice Tracker** - Vendor invoices, payment tracking

```bash
# For P001:
python scripts/google_sheets_extended.py project P001 "YOUR_SHEET_URL"

# For P002:
python scripts/google_sheets_extended.py project P002 "YOUR_SHEET_URL"

# For P003:
python scripts/google_sheets_extended.py project P003 "YOUR_SHEET_URL"
```

### 3. Push SOV to Sheets
```bash
# Set API key first
export ANTHROPIC_API_KEY="$anthropicAPIkey"

# Push existing SOV
python pm.py sheets P001 -u "YOUR_SHEET_URL"
python pm.py sheets P003 -u "YOUR_SHEET_URL"

# Generate missing SOV for P002 and push
python pm.py sov P002
python pm.py sheets P002 -u "YOUR_SHEET_URL"
```

---

## Complete Workflow Examples

### Example 1: Set Up Complete Tracking for P001

```bash
# Step 1: Set API key
export ANTHROPIC_API_KEY="$anthropicAPIkey"

# Step 2: Create a new Google Sheet (manually in browser)
# Name it: "P001 - Fire Rated Doors - City Hospital"
# Copy the URL

# Step 3: Push SOV to the sheet
python pm.py sheets P001 -u "PASTE_YOUR_SHEET_URL_HERE"

# Step 4: Add project tracking tabs
python scripts/google_sheets_extended.py project P001 "SAME_SHEET_URL"

# Result: You now have a complete project management sheet with:
# - SOV tab (billing schedule)
# - PO Log tab
# - Submittal Log tab
# - Installation Log tab
# - Invoice Tracker tab
```

### Example 2: Create Master Vendor Database

```bash
# Step 1: Create a new Google Sheet
# Name it: "Vendor Database - Master List"

# Step 2: Run vendor manager
python scripts/vendor_manager.py "YOUR_SHEET_URL"

# Result: Sheet populated with 24 vendors, formatted and ready
```

### Example 3: Create Company Dashboard

```bash
# Step 1: Create a new Google Sheet
# Name it: "Company Dashboard - Cash Flow"

# Step 2: Create dashboard
python scripts/google_sheets_extended.py dashboard "YOUR_SHEET_URL"

# Step 3: Manually add project data or link to project sheets

# Result: Executive dashboard showing all projects and cash flow
```

### Example 4: Process a Brand New Project

```bash
# Step 1: Create folder in Input/
mkdir "Input/New Project Name"

# Step 2: Add PDF files to that folder
# (contract, specs, drawings, etc.)

# Step 3: Set API key
export ANTHROPIC_API_KEY="$anthropicAPIkey"

# Step 4: Run full workflow
python main.py process

# Step 5: Review outputs
ls Output/Reports/        # Contract analysis
ls Output/Draft_SOV/      # Generated SOV
ls Output/Draft_Emails/   # Draft emails

# Step 6: Push to Google Sheets
# Create a new sheet, then:
python pm.py sheets P004 -u "YOUR_SHEET_URL"
python scripts/google_sheets_extended.py project P004 "SAME_URL"
```

---

## Testing the Full Stack

### Quick Test: Generate Missing P002 SOV
```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"
python pm.py sov P002
```

### Create a Complete Demo Sheet

**Option 1: All-in-One Project Sheet (P001)**
```bash
# Create ONE Google Sheet, copy URL, then run:
export ANTHROPIC_API_KEY="$anthropicAPIkey"

SHEET_URL="YOUR_URL_HERE"

python pm.py sheets P001 -u "$SHEET_URL"
python scripts/google_sheets_extended.py project P001 "$SHEET_URL"

# Now you have 1 sheet with 5 tabs: SOV + 4 tracking sheets
```

**Option 2: Separate Sheets for Each Function**
```bash
# Sheet 1: Company Dashboard
python scripts/google_sheets_extended.py dashboard "DASHBOARD_SHEET_URL"

# Sheet 2: Vendor Database
python scripts/vendor_manager.py "VENDOR_SHEET_URL"

# Sheet 3-5: Individual Project Sheets
python pm.py sheets P001 -u "P001_SHEET_URL"
python scripts/google_sheets_extended.py project P001 "P001_SHEET_URL"
# Repeat for P002, P003
```

---

## What's in the Codebase

### Core Python Scripts
```
scripts/
├── contract_processor.py      # Claude AI contract analysis
├── sov_generator.py           # Schedule of Values generation
├── email_generator.py         # Draft emails (not yet implemented)
├── file_mover.py              # Project file organization
├── logger.py                  # CSV activity logging
├── vendor_manager.py          # ✓ Vendor database manager
├── google_sheets_push_v2.py   # SOV → Google Sheets
└── google_sheets_extended.py  # ✓ Dashboard & tracking sheets
```

### Main Entry Points
- `main.py` - Simple workflow (process → analyze → SOV → emails)
- `pm.py` - Advanced CLI (granular control of each step)
- `test_connections.py` - Test both API connections

### Vendor Database Details
**scripts/vendor_manager.py** contains:
- 24 fully detailed vendors
- Categories: Glass, Hardware, Metal, Paint, Accessories, Specialty
- Contact names, locations, specialties, lead times, ratings
- Auto-formatted Google Sheets output with frozen headers

### Dashboard System Details
**scripts/google_sheets_extended.py** contains:
- `create_company_dashboard()` - Master cash flow view
- `create_project_tracking_sheets()` - 4 tabs per project:
  - PO Log (purchase orders)
  - Submittal Log (submittals & approvals)
  - Installation Log (progress tracking)
  - Invoice Tracker (vendor payments)

---

## Next Steps to Make Everything Look Good

### 1. Generate Missing Content
```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"

# Generate P002 SOV
python pm.py sov P002

# Generate emails for all projects
python scripts/email_generator.py P001
python scripts/email_generator.py P002
python scripts/email_generator.py P003
```

### 2. Create Demo Google Sheets

Create 4 separate Google Sheets and run these commands:

**A. Company Dashboard Sheet**
```bash
python scripts/google_sheets_extended.py dashboard "DASH_URL"
```

**B. Vendor Database Sheet**
```bash
python scripts/vendor_manager.py "VENDOR_URL"
```

**C. P001 Complete Project Sheet**
```bash
python pm.py sheets P001 -u "P001_URL"
python scripts/google_sheets_extended.py project P001 "P001_URL"
```

**D. P002 Complete Project Sheet**
```bash
python pm.py sov P002  # Generate SOV first
python pm.py sheets P002 -u "P002_URL"
python scripts/google_sheets_extended.py project P002 "P002_URL"
```

### 3. View Your Data

All generated files are in:
```
Output/
├── Reports/              # Contract analyses (JSON + Markdown)
├── Draft_SOV/           # Schedule of Values (JSON + CSV)
└── Draft_Emails/        # Email drafts (TXT)

Logs/
├── project_registry.csv # All projects
└── agent_activity.csv   # All AI actions
```

---

## Troubleshooting

### API Key Issues
```bash
# Check if key is set
env | grep -i anthropic

# Set it (if needed)
export ANTHROPIC_API_KEY="$anthropicAPIkey"

# Test it
python test_connections.py
```

### Google Sheets Issues
```bash
# Verify credentials exist
ls -la credentials.json

# Test authentication
python -c "
from google.oauth2.service_account import Credentials
import gspread
creds = Credentials.from_service_account_file('credentials.json')
gc = gspread.authorize(creds)
print('Authentication successful!')
"
```

### Sheet URL Format
Must be the full URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```

---

## Summary

**Working Features:**
- ✓ Anthropic API integration (Claude AI)
- ✓ Google Sheets API integration
- ✓ Contract processing (3 projects done)
- ✓ SOV generation (2/3 done, 1 missing)
- ✓ Vendor management (24 vendors ready)
- ✓ Company dashboard creation
- ✓ Project tracking sheets (4 per project)
- ✓ SOV push to Google Sheets

**Ready to Test:**
- Create vendor database sheet
- Create company dashboard
- Push existing SOVs to sheets
- Create tracking sheets for all projects
- Generate missing P002 SOV

**Next Enhancements:**
- Email generation completion
- Automatic dashboard aggregation
- Vendor quote comparison
- RFI management
- Shop drawing tracking
