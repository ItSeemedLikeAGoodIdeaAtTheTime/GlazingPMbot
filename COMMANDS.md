# WORKING COMMANDS - Copy & Paste Ready

## ✓ ALL SYSTEMS OPERATIONAL

- Anthropic API: ✓ Working
- Google Sheets API: ✓ Working
- Vendor Database: ✓ 24 vendors ready
- Dashboard System: ✓ Ready
- 3 Projects: ✓ Ready to push to sheets

---

## Quick System Test

```bash
# Run all tests at once (Windows)
RUN_TESTS.bat

# Or test individually:
python test_connections.py          # Test both APIs
python test_vendor_system.py        # Test vendor system
python test_dashboard_system.py     # Test dashboard system
```

---

## Create Google Sheets (3 EASY STEPS)

### Step 1: Create New Google Sheets

**Go to:** https://docs.google.com/spreadsheets/

Create 4 new blank sheets:
1. "Company Dashboard"
2. "Vendor Database"
3. "P001 - Fire Rated Doors"
4. "P002 - Lead Glass"

### Step 2: Copy Each Sheet URL

The URL looks like:
```
https://docs.google.com/spreadsheets/d/ABC123.../edit
```

### Step 3: Run Commands (Replace URLs)

```bash
# A. Create Company Dashboard
python test_dashboard_system.py dashboard "PASTE_DASHBOARD_URL"

# B. Create Vendor Database (24 vendors)
python test_vendor_system.py "PASTE_VENDOR_URL"

# C. Create P001 Complete Project Sheet
python test_dashboard_system.py project P001 "PASTE_P001_URL"

# D. Create P002 Complete Project Sheet
python test_dashboard_system.py project P002 "PASTE_P002_URL"
```

**That's it!** Open your Google Sheets to see the results.

---

## What Each Command Creates

### Company Dashboard
- Summary metrics (total projects, total value)
- 3-month cash flow forecast
- Project status overview
- Ready for manual data entry or formulas

### Vendor Database
- **24 vendors** across 8 categories
- Contact names, phone, email fields
- Specialties and lead times
- Quality ratings
- Formatted with frozen headers

**Vendors include:**
- Vitrum, Hartung, Tacoma Glass (Glass)
- IML, Mayflower, CRL (Hardware)
- Kawneer, Oldcastle, Coast Aluminum (Metal)
- North Clad, ABF (Fabricators)
- And 12 more...

### Project Tracking Sheets
Each project gets **4 tabs:**

1. **PO Log** - Purchase order tracking
   - PO #, vendor, amount, dates
   - Delivery status
   - Billing status

2. **Submittal Log** - Submittal tracking
   - Item descriptions, spec sections
   - Submission and approval dates
   - Revision tracking
   - Billing triggers

3. **Installation Log** - Progress tracking
   - Location/area tracking
   - Scheduled vs actual dates
   - % completion
   - Billable amounts

4. **Invoice Tracker** - Vendor payments
   - Vendor invoices
   - Due dates, payment dates
   - Check numbers
   - Related PO numbers

---

## Alternative Commands (Same Results)

If you prefer the direct scripts:

```bash
# Vendor Database
python scripts/vendor_manager.py "SHEET_URL"

# Company Dashboard
python scripts/google_sheets_extended.py dashboard "SHEET_URL"

# Project Tracking
python scripts/google_sheets_extended.py project P001 "SHEET_URL"
python scripts/google_sheets_extended.py project P002 "SHEET_URL"
python scripts/google_sheets_extended.py project P003 "SHEET_URL"
```

---

## Current Project Status

| Project | Status | Can Create Sheets? |
|---------|--------|-------------------|
| P001 - Fire Rated Doors | ✓ Ready | YES |
| P002 - Lead Glass | ✓ Ready | YES |
| P003 - Dance Studio Mirrors | ✓ Ready | YES |

All 3 projects have:
- ✓ Contract documents processed
- ✓ Contract analysis completed
- ✓ Ready for sheet creation

---

## Example: Complete P001 Setup

```bash
# 1. Create Google Sheet (in browser)
# Name: "P001 - Fire Rated Doors - City Hospital"
# Copy URL

# 2. Create all tracking sheets
python test_dashboard_system.py project P001 "YOUR_SHEET_URL"

# Result: Sheet with 4 tabs ready to use!
```

---

## Vendor Database Categories

**Glass Manufacturers (6)**
- Vitrum (Roshain) - Premium, Canada
- Hartung (Ali) - USA, affordable
- Tacoma Glass (Carrie) - Fast turnaround
- General Glass (Kaylee)
- GlassPro (Jim Tarman) - Luxury glass
- Allegiant/TGP (Alaina Fox) - Fire-rated

**Door Hardware (4)**
- IML/Intermountain Lock (Mike Fender)
- Mayflower (Anatoly)
- FHC - Frameless Hardware
- CRL - CR Laurence

**Metal & Aluminum (5)**
- Coast Aluminum (Melissa) - Raw stock
- Kawneer (Skyler) - Curtain walls
- Oldcastle - Storefront
- North Clad (TJ) - Metal panels
- ABF (Brent Hammer) - Metal fabrication

**Paint & Finishing (2)**
- New Finishes (TJ) - High-end custom
- Accurate Industries (Elizabeth)

**Accessories & Supplies (4)**
- Colorado Steel & Sash (Jeremiah) - GE sealants
- Atlas Supply (Evan Moran) - Dow Corning
- Hilti - Anchors
- Tacoma Screw - Hardware

**Specialty Systems (2)**
- AD Systems - Hospital doors
- Nanawall - Folding doors

**Regional Fabricators (2)**
- Garibaldi Glass
- Glass Fab

---

## Troubleshooting

### "Can't find credentials.json"
```bash
ls credentials.json
# If missing, download from Google Cloud Console
```

### "Invalid sheet URL"
- Must be full URL starting with https://docs.google.com/spreadsheets/
- Include the /edit part
- No quotes needed in commands (quotes are for spaces in paths)

### "Permission denied"
- Make sure the Google Sheet is shared with the service account email
- Email found in credentials.json under "client_email"

### Unicode/Emoji Errors
- These are **cosmetic only** - code still works!
- Use the new test scripts (test_vendor_system.py, test_dashboard_system.py)
- They avoid emojis and work perfectly on Windows

---

## Next Steps After Creating Sheets

1. **Open Google Sheets** - View your created tabs
2. **Share sheets** - Give team members access
3. **Start tracking** - Fill in PO numbers, submittals, etc.
4. **Add formulas** - Link dashboard to project sheets
5. **Customize** - Add columns, adjust formatting

---

## Files Created for You

```
New test files (Windows-compatible):
├── test_connections.py          ✓ Test both APIs
├── test_vendor_system.py        ✓ Test vendor database
├── test_dashboard_system.py     ✓ Test dashboard system
├── RUN_TESTS.bat                ✓ Run all tests at once
├── COMMANDS.md                  ✓ This file
└── QUICK_START_GUIDE.md         ✓ Detailed guide

Existing system files:
├── scripts/vendor_manager.py          ✓ 24 vendors
├── scripts/google_sheets_extended.py  ✓ Dashboard & tracking
├── scripts/google_sheets_push_v2.py   ✓ SOV integration
└── main.py, pm.py                     ✓ Main orchestrators
```

---

## Summary: What You Have

**Working Systems:**
- ✓ Anthropic AI (contract processing)
- ✓ Google Sheets integration
- ✓ Vendor management (24 vendors)
- ✓ Company dashboard
- ✓ Project tracking (4 sheets per project)
- ✓ 3 processed projects ready to deploy

**Ready to Create:**
- Company dashboard (1 command)
- Vendor database (1 command)
- Full project tracking for P001, P002, P003 (1 command each)

**Time to Deploy:**
- About 2 minutes total to create all sheets
- Just need to create Google Sheets and run commands

🎉 **You're ready to go!**
