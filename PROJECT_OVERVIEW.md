# Glazing PM AI System

## Project Goal
Automate commercial glazing project management from contract receipt to final retention billing, prioritizing speed, customer service, and profitability.

## Tech Stack
- **Automation Platform**: Make.com (workflow orchestration)
- **AI**: Claude API (Anthropic) - document processing, analysis, constructibility checks
- **Spreadsheets**: Google Sheets (tracking, budgets, SOV)
- **Email**: Gmail (external communication)
- **Internal Comms**: Slack
- **PDF Processing**: Adobe Acrobat

## Inputs

### Contract Documents (PDFs)
- Contract/Proposal
- Specifications (e.g., spec section 088000 for glazing)
- Drawings
- Construction Schedules

### Vendor Documents (PDFs)
- Vendor Catalogs
- Vendor Quotes
- Vendor Order Confirmations
- Vendor Invoices
- Vendor Shop Drawings

### Internal Documents
- Internal Shop Drawings (produced externally, managed internally)

## Outputs

### Primary Deliverables
- **Schedule of Values (SOV)** - CSV for client billing
- **Purchase Orders (POs)** - To vendors for materials/services
- **Internal Budget** - One-time cost code breakdown at project start

### Billing Categories (within SOV)
Each spec section (e.g., 088000 glazing) divided into:
1. General Conditions/Submittals/Project Management (overhead)
2. Materials (purchased)
3. Installation Labor
4. Stored Materials (materials received but not installed)
5. Final Retention (typically 5% of total, billed at project completion)

## Key Workflows

### 1. Contract Processing
PDF contract docs → Extract requirements → Generate:
- Schedule of Values (SOV) with billing line items
- Internal Budget with cost codes

### 2. Procurement & Submittals
Specs + Vendor Catalogs → Product Data → Submit to Architect → Approval → Generate POs

### 3. Shop Drawing Management
- **Critical Goal**: Limit to ONE REVISION per shop drawing set
- Track: Internal shop drawings → Submit to Architect → Revisions → Approval
- Track: Vendor shop drawings → Review → Approval
- Monitor revision counts to prevent project delays

### 4. Progress Tracking
Track project phases for billing triggers:
1. **Submittals/General Conditions** - Product data submitted & approved
2. **Materials Purchased** - PO issued
3. **Stored Materials** - Materials received on site
4. **Installation** - Materials installed
5. **Final Retention** - Project complete (5% holdback)

### 5. Email Management
- Gmail for external vendor/client communication
- Slack for internal team communication
- AI-assisted email responses

### 6. Invoice & Cash Flow Awareness
- External stakeholders track: SOV billing vs. vendor invoices
- Goal: Positive monthly cash flow (billing > expenses)
- **Note**: Accounting department tracks cash flow; PM tracks project progress

## Success Metrics (Priority Order)

1. **Speed & Efficiency** - Reduce project timeline, minimize delays
2. **Customer Service** - Speed IS service; responsiveness to clients/architects
3. **Profitability** - Positive monthly cash flow + total net income
4. **Reportability** - Clear visibility into project status and financials

## AI Model Context Strategy

Build specialized Claude API prompts for specific tasks:

### Constructibility Checks (Shop Drawings)
- **Caulk Joint Sizing** - Validate joint dimensions per specs
- **Material Compatibility** - Check glass/metal/hardware compatibility
- **Code Compliance** - Verify building code requirements
- **Installation Feasibility** - Flag potential field installation issues

### Document Processing
- **Spec Extraction** - Pull requirements from spec sections
- **Drawing Analysis** - Extract dimensions, materials, schedules
- **Vendor Quote Comparison** - Compare quotes against specs

### Communication
- **Email Classification** - Categorize incoming emails
- **Response Generation** - Draft responses to common inquiries
- **RFI Management** - Track Requests for Information

## Project Phases (Billable Milestones)

```
Contract Received
    ↓
Generate SOV + Internal Budget
    ↓
Product Data Submittal → Architect Approval
    ↓ (Bill: General Conditions/Submittals)
Purchase Order Issued
    ↓ (Bill: Materials Purchased)
Materials Received/Stored
    ↓ (Bill: Stored Materials)
Installation Complete
    ↓ (Bill: Installation Labor)
Project Complete
    ↓ (Bill: Final Retention 5%)
```

## Flexibility Points

### SOV Division Decisions
- How to split spec sections into line items
- Percentage allocated to General Conditions vs. Materials vs. Labor
- Timing: Bill overhead upfront (5% total) or monthly ($2k/month)?

### Internal Budget Decisions
- Cost code structure
- Allocation across phases
- Contingency reserves

## Key Challenges to Solve

1. **Shop Drawing Revision Control** - Minimize architect/vendor revision cycles
2. **PO Speed** - Fast vendor ordering to reduce schedule delays
3. **Billing Optimization** - Maximize legitimate early billing opportunities
4. **Email Volume** - Automate routine communications
5. **Multi-vendor Coordination** - Track quotes, confirmations, deliveries across vendors
