# Glazing PM AI - Web Application Guide

## 🎉 What You Just Built

A complete web-based project management system with:

### Backend API (FastAPI)
- Document upload endpoints
- Project initialization
- SOV generation with scope/vendor breakdown
- Internal budget with cost codes
- Predictive billing schedule
- File download endpoints

### Frontend (HTML/JavaScript)
- 5 document upload boxes
- "Generate SOV" button
- Real-time status updates
- Download links for all generated files

### Generated Outputs
1. **Schedule of Values** (Client-facing)
   - Broken down by scopes
   - Sub-scopes with vendors
   - Metal vendor, Glass vendor, Hardware vendor, etc.
   - General Conditions

2. **Internal Budget** (Accounting)
   - Cost codes for all labor types
   - Material categories
   - Indirect costs
   - Totals per cost code (not month-by-month)

3. **Predictive Billing Schedule**
   - Month-by-month billing forecast
   - Milestones: Submittals → Materials → Storage → Installation → Retention
   - Based on vendor lead times
   - Billing triggers and dates

4. **Scope Analysis**
   - Identified scopes
   - Matched vendors
   - Requirements extraction
   - RFQ recommendations

---

## 🚀 Quick Start

### Step 1: Install FastAPI Dependencies

```bash
pip install -r api/requirements.txt
```

Or install individually:
```bash
pip install fastapi uvicorn python-multipart
```

### Step 2: Set API Key

```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"
```

### Step 3: Start the API Server

```bash
cd "C:\Users\clynn\OneDrive\Desktop\Glazing PM Ai"
python api/main.py
```

You should see:
```
======================================================================
  GLAZING PM AI - API SERVER
======================================================================

Starting server on http://localhost:8000
API docs available at http://localhost:8000/docs

Press CTRL+C to stop
======================================================================
```

### Step 4: Open the Web App

Open in your browser:
```
file:///C:/Users/clynn/OneDrive/Desktop/Glazing PM Ai/frontend/index.html
```

Or simply double-click `frontend/index.html`

---

## 📖 How to Use

### 1. Upload Documents

1. Enter project name (e.g., "City Hospital Emergency Dept")
2. Click each box to upload PDFs:
   - **Contract** - Main contract document
   - **Specifications** - Technical specifications
   - **Drawings** - Architectural/engineering drawings
   - **Schedule** - Project schedule
   - **Proposal** - Your original proposal (optional)
3. Click **"Upload & Initialize Project"**

Result: Project gets a number (P001, P002, etc.)

### 2. Generate SOV

1. After upload completes, click **"Generate Schedule of Values"**
2. Wait 1-2 minutes while AI analyzes documents
3. View results:
   - Identified scopes
   - Matched vendors
   - Download links

### 3. Download Files

Click any download button to get:
- **SOV (CSV)** - Import into Excel
- **SOV (JSON)** - Raw data
- **Internal Budget** - Cost code breakdown
- **Billing Schedule** - Month-by-month forecast
- **Scope Analysis** - Detailed scope report
- **Contract Analysis** - AI contract summary

---

## 📊 What Gets Generated

### Schedule of Values (Client-Facing)

**Structure:**
```
PROJECT TOTAL: $500,000

SCOPE 1: FIRE-RATED GLAZING ($50,000)
  Vendors: TGP Allegiant (Glass), IML (Hardware)

  01 - General Conditions
    - Product Data / Submittals          $6,000 (12%)

  02 - Materials
    - Fire-Rated Glass (TGP Allegiant)   $27,500 (55%)
    - Door Hardware (IML)                $5,000

  03 - Labor
    - Installation Labor                 $9,000 (18%)

  04 - Retention (5%)                    $2,500

SCOPE 2: STOREFRONT ($150,000)
  Vendors: Kawneer (Metal), Vitrum (Glass), IML (Hardware)

  [Same breakdown...]
```

### Internal Budget (Accounting)

**Cost Code Structure:**
```
Code        Description                   Qty    Unit Cost   Total

LABOR
L-GLZ-001   Glaziers - Foreman           40 hr   $85.00     $3,400
L-GLZ-002   Glaziers - Journeyman        80 hr   $65.00     $5,200
L-CLK-001   Caulkers - Foreman           20 hr   $80.00     $1,600

GLASS
M-FRG-002   Fire-Rated Glass (60-90min)  100 sf  $180.00    $18,000
M-IGU-001   IGU - Standard Clear         500 sf  $35.00     $17,500

METAL
M-MWN-001   Storefront Framing           200 lf  $65.00     $13,000

HARDWARE
H-LCH-003   Panic Devices                4 ea    $650.00    $2,600

SEALANTS
S-WTH-001   Perimeter Sealant            150 lf  $4.50      $675

INDIRECT
I-DRV-001   Drive Time                   40 hr   $55.00     $2,200
I-EQP-001   Equipment Rental - Lift      10 day  $450.00    $4,500
I-INS-001   Insurance                    1 ls    $1,500.00  $1,500

TOTAL: $70,175
```

### Predictive Billing Schedule

**Month-by-Month:**
```
Month          Milestone                  Amount      Cumulative

February 2025  Submittals Complete        $6,000      $6,000
April 2025     Materials Purchased        $27,500     $33,500
May 2025       Materials Stored           $5,000      $38,500
June 2025      Installation Complete      $9,000      $47,500
August 2025    Final Retention            $2,500      $50,000
```

---

## 🔧 API Endpoints

Browse interactive API docs: **http://localhost:8000/docs**

### Key Endpoints:

**Upload Documents**
```
POST /api/upload
FormData: project_name, contract, specifications, drawings, schedule, proposal
```

**Initialize Project**
```
POST /api/project/initialize
Body: { "project_name": "Project Name" }
Response: { "project_number": "P001", ... }
```

**Generate SOV**
```
POST /api/project/generate-sov
Body: {
  "project_number": "P001",
  "include_budget": true,
  "include_billing_schedule": true
}
```

**Download Files**
```
GET /api/download/{file_type}/{project_number}
file_type: sov_csv, sov_json, budget, billing, scope, analysis
```

**List Projects**
```
GET /api/projects
```

**Get Cost Codes**
```
GET /api/cost-codes
```

---

## 📁 File Structure

```
Glazing PM Ai/
├── api/
│   ├── main.py                    # FastAPI server
│   ├── budget_generator.py        # Cost code budget generator
│   ├── billing_scheduler.py       # Predictive billing schedule
│   └── requirements.txt           # Python dependencies
│
├── frontend/
│   └── index.html                 # Web interface
│
├── cost_codes.json                # Cost code structure (82 codes)
│
├── Vendor_Data/
│   ├── scope_matrix.md            # 10 scope types
│   └── vendor_capability_matrix.csv  # 24 vendors
│
├── Output/
│   ├── Budgets/                   # Internal budgets
│   ├── Billing_Schedules/         # Month-by-month forecasts
│   ├── Draft_SOV/                 # SOVs
│   ├── Scope_Analysis/            # Scope reports
│   └── Reports/                   # Contract analyses
│
└── Projects/                      # Project folders
```

---

## 🎯 Cost Code Categories (17 Categories, 82 Codes)

### Labor
- **Glaziers** (Foreman, Journeyman, Apprentice)
- **Caulkers** (Foreman, Journeyman, Apprentice)
- **Shop Labor** (Foreman, Journeyman, Apprentice)
- **Door Glaziers** (Foreman, Journeyman, Apprentice)

### Glass
- **Monolithic** (Annealed, Tempered, Laminated)
- **IGUs** (Standard, Low-E, High-Performance)
- **Fire-Rated** (20-45min, 60-90min, 120min)
- **Specialty** (Lead Glass, Bullet-Resistant, Mirrors, Decorative)

### Metal
- **Doors** (Aluminum Frames, Hollow Metal, All-Glass)
- **Windows** (Storefront, Curtain Wall, Metal Panels)

### Hardware
- **Hinges** (Standard, Heavy-Duty, Pivots)
- **Latching** (Locksets, Panic Devices, Exit Devices)
- **Operators** (Automatic Swing, Automatic Sliding)
- **Accessories** (Closers, Thresholds, Weatherstripping, Push/Pull)

### Sealants
- **Structural** (2-Part Silicone, VHB Tape)
- **Weather** (Silicone, Polyurethane, Joint Sealant)
- **Beauty** (Interior Beauty Sealant)

### Accessories
- **Shims** (Plastic, Metal)
- **Setting Blocks** (Neoprene, EPDM)

### Indirect Costs
- Drive Time
- Parking
- Shipping
- Crating
- Consumable Tools
- Equipment Rental (Lift, Crane, Other)
- Insurance

---

## 🔄 Typical Workflow

1. **Day 1** - Upload contract documents
2. **Day 1** - Generate SOV, budget, billing schedule
3. **Day 1** - Review AI-generated scope analysis
4. **Day 1** - Download SOV and send to client
5. **Day 1** - Download budget and send to accounting
6. **Ongoing** - Update billing schedule as project progresses

---

## 🚧 Next Enhancements

### Phase 2 (RFQ Generation)
- Auto-generate RFQ emails
- Extract relevant drawing pages
- Send to 2 vendors per category

### Phase 3 (Quote Comparison)
- Import vendor quotes
- Compare pricing/lead times
- Recommend best vendors
- Generate PO recommendations

### Phase 4 (Progress Tracking)
- Update actual vs predicted billing
- Track submittal status
- Monitor installation progress
- Real-time cash flow dashboard

---

## 💡 Tips

1. **API must be running** for frontend to work
2. **Upload at least one file** to initialize project
3. **Wait 1-2 minutes** for AI analysis to complete
4. **Download CSV files** to open in Excel
5. **Check Output folders** for all generated files

---

## 🐛 Troubleshooting

### "API connection failed"
- Make sure API server is running: `python api/main.py`
- Check that it's on port 8000
- Check firewall settings

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="$anthropicAPIkey"
```

### "No module named 'fastapi'"
```bash
pip install fastapi uvicorn python-multipart
```

### "File not found" errors
- Make sure you're running from project root directory
- Check that all folders exist (Input, Output, Projects, Logs)

---

## ✅ Summary

You now have:
- ✓ Web interface for document upload
- ✓ API backend with 10+ endpoints
- ✓ SOV generation with scope/vendor breakdown
- ✓ Internal budget with 82 cost codes
- ✓ Predictive billing schedule
- ✓ 10 scope types mapped to 24 vendors
- ✓ Automatic vendor matching
- ✓ Downloadable Excel-ready files

**Ready to process projects! 🚀**
