# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Automate commercial glazing project management workflows from contract receipt through final retention billing. The system processes PDF construction documents, generates schedules of values, manages purchase orders, and tracks project progress through billable milestones.

## Technology Stack

- **Make.com** - Workflow orchestration and automation
- **Claude API** - Document processing, analysis, and constructibility checks
- **Google Sheets** - Tracking spreadsheets, budgets, and SOV management
- **Gmail** - External communication (vendors, clients, architects)
- **Slack** - Internal team communication
- **Adobe Acrobat** - PDF processing and annotation

## System Architecture

### Input Processing Flow
1. Contract documents (PDFs) arrive via email/upload
2. Make.com triggers Claude API for document extraction
3. Extracted data populates Google Sheets templates
4. Approval workflows route through Slack
5. Outputs generated (SOV, POs, budgets)

### Key Workflows
- **Contract → SOV/Budget**: Extract specs, generate billing line items
- **Specs → Product Data → Submittals → PO**: Procurement pipeline
- **Shop Drawings**: Track revisions (target: 1 revision max), manage approvals
- **Progress Tracking**: Monitor phases (submittals → purchase → stored → installed → retention)
- **Email Management**: Classify, route, and draft responses via Claude

## Directory Structure

- `Make_Workflows/` - Make.com scenario exports and workflow documentation
- `Claude_Prompts/` - Specialized system prompts for Claude API calls
  - Document processing (contracts, specs, drawings, quotes)
  - Constructibility checks (caulk joints, material compatibility, code compliance)
  - Financial tools (SOV generation, budget building, invoice matching)
  - Communication (email classification, response generation, RFI handling)
  - Shop drawing management (reviews, revision tracking)
  - Procurement (PO generation, vendor comparison)
- `Templates/` - Google Sheets templates and CSV formats
- `Tracking_Sheets/` - Reference sheets for active project tracking
- `Contract Docs/` - Incoming contract documents (PDFs)

## Project Management Philosophy

**Priority Order:**
1. **Speed & Efficiency** - Minimize project timeline
2. **Customer Service** - Responsiveness = service quality
3. **Profitability** - Positive cash flow and net income
4. **Reportability** - Clear visibility for stakeholders

**Critical Success Factor:** Limit shop drawing revisions to ONE per set. Multiple revisions kill schedule momentum.

## Billable Milestone Phases

Projects progress through these billing triggers:

1. **General Conditions/Submittals** (10-15% of section value)
   - Bill as: Upfront or monthly rate
   - Trigger: Project start, submittal preparation

2. **Materials Purchased** (50-60% of section value)
   - Bill as: Progressive (PO issued → stored → installed)
   - Trigger: Purchase order released

3. **Stored Materials** (subset of materials value)
   - Bill as: Percentage when materials arrive on site
   - Trigger: Material delivery confirmation

4. **Installation Labor** (25-35% of section value)
   - Bill as: Progressive by zone/floor/phase
   - Trigger: Installation completion in area

5. **Final Retention** (5% of total contract)
   - Bill as: Lump sum
   - Trigger: Project substantial completion

## Claude API Prompt Usage

When working with prompts in `Claude_Prompts/`:

1. Each `.md` file contains a specialized system prompt for a specific task
2. Make.com HTTP modules call Claude API with:
   - System message: Prompt file contents
   - User message: Dynamic data (PDF text, drawing details, etc.)
3. Expected response format is documented in each prompt file
4. Prompts are designed for JSON structured output when applicable

### Key Prompt Categories
- **Constructibility**: Technical reviews (caulk joints, material specs, code compliance)
- **Financial**: SOV generation, budget creation, invoice processing
- **Communication**: Email triage, response drafting, RFI management
- **Procurement**: PO generation, vendor quote comparison

## Schedule of Values (SOV) Structure

Each spec section (e.g., 088000 Glazing) breaks into:
- General Conditions line items (submittals, engineering, PM)
- Material line items (glass, metal, hardware, sealants)
- Labor line items (installation by phase/zone)
- Retention line item (5% holdback)

**Billing Strategy:** Maximize legitimate early billing opportunities while maintaining professional accuracy. Front-load general conditions, bill for stored materials, progressive labor billing.

## Common Development Tasks

### Adding a New Claude Prompt
1. Create `.md` file in `Claude_Prompts/` following template structure
2. Define purpose, input format, output format, and system prompt
3. Include example usage
4. Test prompt via Claude API before deploying to Make.com

### Creating a Make.com Workflow
1. Design workflow in Make.com interface
2. Export scenario blueprint (JSON)
3. Save to `Make_Workflows/` with descriptive name
4. Document trigger conditions and data mappings
5. Link to relevant Claude prompts used in HTTP modules

### Updating Google Sheets Templates
1. Templates in `Templates/` define expected data structure
2. Make.com modules reference specific sheet/range locations
3. Update both template file and Make.com mappings when changing structure

## Domain-Specific Knowledge

### Glazing Spec Sections (CSI MasterFormat)
- **079200** - Joint Sealants
- **080000** - Openings (Division 8)
- **081100** - Metal Doors and Frames
- **084000** - Entrances, Storefronts, and Curtain Walls
- **088000** - Glazing (primary spec section for glass installation)
- **088300** - Mirrors

### Typical Material Categories
- Curtain wall systems (stick-built or unitized)
- Storefront framing (aluminum)
- Entrance doors and frames
- Glass types (clear, tinted, low-e, laminated, tempered, insulated)
- Structural silicone
- Wet-seal gaskets and setting blocks
- Perimeter sealants
- Hardware (panic devices, closers, pivots, hinges, locks)

### Shop Drawing Review Focus
- **Caulk joint sizing** - Typically 1/2" to 3/4", depth-to-width ratio 1:2
- **Material compatibility** - Glass type matches frame capacity, hardware matches door weight
- **Code compliance** - Safety glazing, fire ratings, wind loads, thermal performance
- **Installation feasibility** - Access, sequencing, shoring requirements

## Cash Flow Awareness

- PM tracks project progress and billing opportunities
- Accounting department tracks: SOV billing vs. vendor invoices
- Goal: Monthly billing > monthly expenses
- SOV and Internal Budget are separate documents with different purposes:
  - **SOV** - Client-facing, optimized for billing timing
  - **Internal Budget** - Cost codes for internal tracking, created once at project start

## Communication Protocols

- **External (Gmail)**: Vendors, clients, architects, general contractors
- **Internal (Slack)**: Team coordination, approval requests, status updates
- **Document Delivery**: Shop drawings, submittals, RFIs via email with PDF attachments

## Notes for Future Development

- Future migration from Google Sheets to Smartsheet (not immediate priority)
- Adobe Acrobat is current PDF processor; potential future migration to Bluebeam
- Shop drawings produced by external sources (not generated by this system)
- System does not directly track cash flow (accounting function); focuses on project progress tracking
- Vendor catalogs are key input for product selection and PO generation
