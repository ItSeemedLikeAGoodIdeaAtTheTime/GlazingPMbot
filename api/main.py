#!/usr/bin/env python3
"""
Glazing PM AI - FastAPI Backend
Main API server for document processing and SOV generation
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from scripts.file_mover import FileMover
from scripts.contract_processor import ContractProcessor
from scripts.sov_generator import SOVGenerator
from scripts.scope_analyzer import ScopeAnalyzer
from scripts.budget_generator import BudgetGenerator
from scripts.template_processor import TemplateProcessor
from scripts.ai_estimator import AIEstimator
from scripts.submittal_generator import SubmittalGenerator, generate_submittal_log_excel
from scripts.document_reviewer import DocumentReviewer, review_document


# Initialize FastAPI app
app = FastAPI(
    title="Glazing PM AI API",
    description="Commercial glazing project management automation API",
    version="1.0.0"
)

# Enable CORS for frontend
# Allow all origins for now (GitHub Pages and local development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ProjectRequest(BaseModel):
    project_name: str
    selected_vendors: Optional[List[str]] = None
    pm_email: str
    assistant_email: Optional[str] = None


class ProjectResponse(BaseModel):
    success: bool
    project_number: str
    project_name: str
    message: str


class SOVRequest(BaseModel):
    project_number: str
    include_budget: bool = True
    include_billing_schedule: bool = True


class SOVResponse(BaseModel):
    success: bool
    project_number: str
    sov_file: str
    budget_file: Optional[str] = None
    billing_schedule_file: Optional[str] = None
    sov_excel_file: Optional[str] = None
    budget_excel_file: Optional[str] = None
    scopes: List[dict] = []
    message: str


# New models for separate Budget and SOV generation
class BudgetRequest(BaseModel):
    project_number: str
    revision: Optional[int] = None  # Auto-increment if not provided


class BudgetResponse(BaseModel):
    success: bool
    project_number: str
    revision: int
    json_file: Optional[str] = None
    excel_file: Optional[str] = None
    summary: Optional[dict] = None
    message: str


class SOVGenerateRequest(BaseModel):
    project_number: str
    billing_month: str  # e.g., "September"
    billing_year: int   # e.g., 2024


class SOVGenerateResponse(BaseModel):
    success: bool
    project_number: str
    billing_month: str
    billing_year: int
    application_number: Optional[int] = None
    json_file: Optional[str] = None
    excel_file: Optional[str] = None
    summary: Optional[dict] = None
    message: str


class PreviousBillingUpload(BaseModel):
    project_number: str
    billing_month: str
    billing_year: int
    file_url: str  # URL to the uploaded file in Supabase storage


# Root endpoint
@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Glazing PM AI API",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
async def health_check():
    """Detailed health check"""

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropicAPIkey")
    has_api_key = bool(api_key)

    # Check directories
    required_dirs = [
        Path("Input"),
        Path("Output"),
        Path("Projects"),
        Path("Logs"),
        Path("Vendor_Data")
    ]

    dirs_exist = all(d.exists() for d in required_dirs)

    return {
        "status": "healthy" if (has_api_key and dirs_exist) else "degraded",
        "anthropic_api": "configured" if has_api_key else "missing",
        "directories": "ok" if dirs_exist else "missing",
        "timestamp": datetime.now().isoformat()
    }


# Get vendors
@app.get("/api/vendors")
async def get_vendors():
    """Get all vendors from capability matrix"""

    try:
        import csv

        vendor_file = Path("Vendor_Data/vendor_capability_matrix.csv")
        if not vendor_file.exists():
            return []

        vendors = []
        with open(vendor_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract capabilities (columns with Yes/No values)
                capabilities = []
                capability_fields = [
                    "Aluminum Framing", "Glass Monolithic", "Glass IGU",
                    "Glass Fire-Rated", "Glass Specialty", "Door Hardware",
                    "All-Glass Hardware", "Sealants", "Anchors",
                    "Metal Panels", "Paint Finishing"
                ]

                for field in capability_fields:
                    if row.get(field, '').strip().lower() == 'yes':
                        capabilities.append(field)

                vendors.append({
                    "id": row['Vendor Name'].lower().replace(' ', '_'),
                    "name": row['Vendor Name'],
                    "contact": row.get('Primary Contact', ''),
                    "category": row.get('Category', ''),
                    "phone": row.get('Phone', ''),
                    "email": row.get('Email', ''),
                    "lead_time": row.get('Lead Time', ''),
                    "notes": row.get('Notes', ''),
                    "capabilities": capabilities,
                    "active": True  # Default all to active
                })

        return vendors

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Upload documents
@app.post("/api/upload")
async def upload_documents(
    project_name: str,
    contract: Optional[UploadFile] = File(None),
    specifications: Optional[UploadFile] = File(None),
    drawings: Optional[UploadFile] = File(None),
    schedule: Optional[UploadFile] = File(None),
    proposal: Optional[UploadFile] = File(None),
    sov_template: Optional[UploadFile] = File(None),
    budget_template: Optional[UploadFile] = File(None)
):
    """
    Upload project documents

    Creates project folder and saves uploaded files.
    Templates (sov_template, budget_template) are stored in a Templates subfolder.
    """

    try:
        # Create project folder in Input
        project_folder = Path("Input") / project_name
        project_folder.mkdir(parents=True, exist_ok=True)

        # Create templates subfolder
        templates_folder = project_folder / "Templates"
        templates_folder.mkdir(parents=True, exist_ok=True)

        # Save uploaded files
        uploaded_files = []

        # Regular documents
        for file, label in [
            (contract, "contract"),
            (specifications, "specifications"),
            (drawings, "drawings"),
            (schedule, "schedule"),
            (proposal, "proposal")
        ]:
            if file and file.filename:
                file_path = project_folder / file.filename

                # Read and save file
                content = await file.read()
                with open(file_path, 'wb') as f:
                    f.write(content)

                uploaded_files.append({
                    "type": label,
                    "filename": file.filename,
                    "size": len(content)
                })

        # Template files - save to Templates subfolder
        for file, label in [
            (sov_template, "sov_template"),
            (budget_template, "budget_template")
        ]:
            if file and file.filename:
                file_path = templates_folder / file.filename

                # Read and save file
                content = await file.read()
                with open(file_path, 'wb') as f:
                    f.write(content)

                uploaded_files.append({
                    "type": label,
                    "filename": file.filename,
                    "size": len(content),
                    "path": str(file_path)
                })

        return {
            "success": True,
            "project_name": project_name,
            "folder": str(project_folder),
            "templates_folder": str(templates_folder),
            "uploaded_files": uploaded_files,
            "message": f"Uploaded {len(uploaded_files)} documents"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialize project
@app.post("/api/project/initialize", response_model=ProjectResponse)
async def initialize_project(request: ProjectRequest, background_tasks: BackgroundTasks):
    """
    Initialize new project

    Moves files from Input to Projects folder and creates project number
    Stores selected vendor preferences for SOV generation
    """

    try:
        mover = FileMover()
        result = mover.initialize_project(request.project_name)

        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Initialization failed'))

        project_number = result['project_number']

        # Save project info (vendor preferences and PM emails)
        project_folder = Path(f"Projects/{project_number}-{request.project_name}")
        project_folder.mkdir(parents=True, exist_ok=True)

        project_info = {
            "project_number": project_number,
            "project_name": request.project_name,
            "pm_email": request.pm_email,
            "assistant_email": request.assistant_email,
            "selected_vendors": request.selected_vendors or [],
            "created_date": datetime.now().isoformat()
        }

        # Save to project_info.json
        project_info_file = project_folder / "project_info.json"
        with open(project_info_file, 'w', encoding='utf-8') as f:
            json.dump(project_info, f, indent=2)

        # Also save vendor_preferences.json for backwards compatibility
        if request.selected_vendors:
            vendor_prefs_file = project_folder / "vendor_preferences.json"
            with open(vendor_prefs_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "selected_vendors": request.selected_vendors,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)

        return ProjectResponse(
            success=True,
            project_number=project_number,
            project_name=request.project_name,
            message=f"Project {project_number} initialized with {len(request.selected_vendors or [])} vendors"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Generate SOV
@app.post("/api/project/generate-sov", response_model=SOVResponse)
async def generate_sov(request: SOVRequest):
    """
    Generate Schedule of Values with scope/vendor breakdown

    Also generates:
    - Internal budget with cost codes
    - Predictive billing schedule
    - Scope analysis with vendor matching
    """

    try:
        project_number = request.project_number

        # Step 1: Analyze contract (if not already done)
        analysis_file = Path(f"Output/Reports/{project_number}_contract_analysis.json")

        if not analysis_file.exists():
            # Run contract analysis
            project_folders = list(Path("Projects").glob(f"{project_number}-*"))
            if not project_folders:
                raise HTTPException(status_code=404, detail=f"Project {project_number} not found")

            processor = ContractProcessor()
            analysis_result = processor.analyze_contract_documents(project_folders[0], project_number)

            if not analysis_result['success']:
                raise HTTPException(status_code=500, detail="Contract analysis failed")

        # Load contract analysis
        with open(analysis_file, 'r', encoding='utf-8') as f:
            contract_analysis = json.load(f)

        # Load vendor preferences if available
        selected_vendors = None
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if project_folders:
            vendor_prefs_file = project_folders[0] / "vendor_preferences.json"
            if vendor_prefs_file.exists():
                with open(vendor_prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    selected_vendors = prefs.get('selected_vendors')

        # Step 2: Run scope analysis with vendor preferences
        analyzer = ScopeAnalyzer()
        scope_result = analyzer.analyze_project_scope(
            project_number,
            contract_analysis,
            selected_vendors=selected_vendors
        )

        if not scope_result['success']:
            raise HTTPException(status_code=500, detail="Scope analysis failed")

        # Step 3: Generate enhanced SOV with scope/vendor breakdown
        sov_gen = SOVGenerator()
        sov_result = sov_gen.generate_sov(project_number, contract_analysis)

        if not sov_result['success']:
            raise HTTPException(status_code=500, detail="SOV generation failed")

        # Step 4: Generate internal budget with cost codes (if requested)
        budget_file = None
        if request.include_budget:
            budget_gen = BudgetGenerator()
            budget_result = budget_gen.generate_budget(
                project_number,
                contract_analysis,
                scope_result.get('scope_analysis', scope_result)
            )
            if budget_result['success']:
                budget_file = budget_result['csv_file']

        # Step 5: Generate predictive billing schedule (if requested)
        # TODO: Implement billing schedule generator
        billing_file = None

        # Step 6: Fill Excel templates if they exist
        sov_excel_file = None
        budget_excel_file = None

        if project_folders:
            templates_folder = project_folders[0] / "06-Templates"

            if templates_folder.exists():
                # Collect all project data for template filling
                project_data = {
                    "project_number": project_number,
                    "contract_analysis": contract_analysis,
                    "scope_analysis": scope_result.get('scope_analysis', scope_result)
                }

                # Load generated SOV data
                sov_json_file = Path(f"Output/Draft_SOV/{project_number}_SOV.json")
                if sov_json_file.exists():
                    with open(sov_json_file, 'r', encoding='utf-8') as f:
                        project_data["sov"] = json.load(f)

                # Load generated budget data
                budget_json_file = Path(f"Output/Budgets/{project_number}_internal_budget.json")
                if budget_json_file.exists():
                    with open(budget_json_file, 'r', encoding='utf-8') as f:
                        project_data["budget"] = json.load(f)

                template_processor = TemplateProcessor()

                # Process SOV template if exists
                sov_templates = list(templates_folder.glob("*sov*")) + list(templates_folder.glob("*SOV*"))
                if not sov_templates:
                    # Look for any Excel that might be SOV
                    sov_templates = [f for f in templates_folder.glob("*.xlsx") if "budget" not in f.name.lower()]

                if sov_templates:
                    try:
                        sov_template_result = template_processor.process_template(
                            template_path=sov_templates[0],
                            project_number=project_number,
                            project_data=project_data,
                            template_type="sov"
                        )
                        if sov_template_result.get("success"):
                            sov_excel_file = sov_template_result.get("output_path")
                    except Exception as e:
                        print(f"WARNING: SOV template processing failed: {e}")

                # Process Budget template if exists
                budget_templates = list(templates_folder.glob("*budget*")) + list(templates_folder.glob("*Budget*"))
                if budget_templates:
                    try:
                        budget_template_result = template_processor.process_template(
                            template_path=budget_templates[0],
                            project_number=project_number,
                            project_data=project_data,
                            template_type="budget"
                        )
                        if budget_template_result.get("success"):
                            budget_excel_file = budget_template_result.get("output_path")
                    except Exception as e:
                        print(f"WARNING: Budget template processing failed: {e}")

        # Prepare response
        sov_file = Path(f"Output/Draft_SOV/{project_number}_SOV.json")

        return SOVResponse(
            success=True,
            project_number=project_number,
            sov_file=str(sov_file),
            budget_file=budget_file,
            billing_schedule_file=billing_file,
            sov_excel_file=sov_excel_file,
            budget_excel_file=budget_excel_file,
            scopes=[
                {
                    "type": scope['scope_type'],
                    "description": scope['description'],
                    "vendors": [
                        vendor['vendor']
                        for match in scope.get('matched_vendors', [])
                        for vendor in match.get('vendors', [])
                    ]
                }
                for scope in scope_result['scopes']
            ],
            message="SOV generated successfully" + (" (with Excel templates)" if sov_excel_file or budget_excel_file else "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get project list
@app.get("/api/projects")
async def list_projects():
    """List all projects in system"""

    try:
        import csv

        registry_file = Path("Logs/project_registry.csv")
        if not registry_file.exists():
            return {"projects": []}

        projects = []
        with open(registry_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                projects.append({
                    "project_number": row['Project_Number'],
                    "project_name": row['Project_Name'],
                    "status": row['Status'],
                    "created_date": row['Created_Date'],
                    "contract_value": row.get('Contract_Value', '')
                })

        return {"projects": projects}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get project details
@app.get("/api/project/{project_number}")
async def get_project(project_number: str):
    """Get project details"""

    try:
        # Load contract analysis
        analysis_file = Path(f"Output/Reports/{project_number}_contract_analysis.json")
        scope_file = Path(f"Output/Scope_Analysis/{project_number}_scope_analysis.json")
        sov_file = Path(f"Output/Draft_SOV/{project_number}_SOV.json")

        data = {
            "project_number": project_number,
            "has_analysis": analysis_file.exists(),
            "has_scope_analysis": scope_file.exists(),
            "has_sov": sov_file.exists()
        }

        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data['analysis'] = json.load(f)

        if scope_file.exists():
            with open(scope_file, 'r', encoding='utf-8') as f:
                data['scope_analysis'] = json.load(f)

        if sov_file.exists():
            with open(sov_file, 'r', encoding='utf-8') as f:
                data['sov'] = json.load(f)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Download file
@app.get("/api/download/{file_type}/{project_number}")
async def download_file(file_type: str, project_number: str):
    """Download generated files"""

    file_map = {
        "sov_json": f"Output/Draft_SOV/{project_number}_SOV.json",
        "sov_csv": f"Output/Draft_SOV/{project_number}_SOV.csv",
        "sov": f"Output/Draft_SOV/{project_number}_SOV.csv",
        "analysis": f"Output/Reports/{project_number}_contract_analysis.md",
        "scope": f"Output/Scope_Analysis/{project_number}_scope_analysis.md",
        "budget": f"Output/Budgets/{project_number}_internal_budget.csv",
        "billing": f"Output/Billing_Schedules/{project_number}_billing_schedule.csv"
    }

    file_path = Path(file_map.get(file_type, ''))

    # Handle Excel template downloads (find most recent)
    if file_type in ["sov_excel", "budget_excel"]:
        template_type = "sov" if file_type == "sov_excel" else "budget"
        filled_templates = sorted(
            Path("Output/Filled_Templates").glob(f"{project_number}_{template_type}_*.xlsx"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        if filled_templates:
            file_path = filled_templates[0]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_path.name
    )


# Get cost codes
@app.get("/api/cost-codes")
async def get_cost_codes():
    """Get complete cost code structure"""

    try:
        with open("cost_codes.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEW AI-POWERED ENDPOINTS (Separate Budget and SOV)
# ============================================================================

@app.post("/api/budget/generate", response_model=BudgetResponse)
async def generate_budget(request: BudgetRequest):
    """
    Generate internal budget using AI estimation.

    Uses all available context:
    - Contract analysis
    - Vendor quotes
    - Invoices
    - Industry knowledge

    No required documents - works with whatever data is available.
    """
    try:
        project_number = request.project_number

        # Find project folder
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if not project_folders:
            # Create minimal project structure if needed
            project_folders = [Path(f"Projects/{project_number}-Unknown")]
            project_folders[0].mkdir(parents=True, exist_ok=True)

        project_folder = project_folders[0]

        # Determine revision number
        revision = request.revision
        if revision is None:
            # Auto-increment: find highest existing revision
            existing_budgets = list(Path("Output/Budgets").glob(f"{project_number}_budget_rev*.json"))
            if existing_budgets:
                revisions = []
                for f in existing_budgets:
                    try:
                        rev = int(f.stem.split("_rev")[1])
                        revisions.append(rev)
                    except:
                        pass
                revision = max(revisions) + 1 if revisions else 1
            else:
                revision = 1

        # Find budget template if available
        templates_folder = project_folder / "06-Templates"
        budget_template = None
        if templates_folder.exists():
            budget_templates = list(templates_folder.glob("*budget*")) + list(templates_folder.glob("*Budget*"))
            if budget_templates:
                budget_template = budget_templates[0]

        # Run AI estimation
        estimator = AIEstimator()
        result = estimator.generate_budget(
            project_number=project_number,
            project_folder=project_folder,
            template_path=budget_template,
            revision=revision
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Budget generation failed"))

        return BudgetResponse(
            success=True,
            project_number=project_number,
            revision=revision,
            json_file=result.get("json_file"),
            excel_file=result.get("excel_file"),
            summary=result.get("budget_data", {}).get("summary"),
            message=f"Budget Rev {revision} generated successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sov/generate", response_model=SOVGenerateResponse)
async def generate_sov_monthly(request: SOVGenerateRequest):
    """
    Generate Schedule of Values for a specific billing month.

    Uses all available context:
    - Contract analysis
    - Vendor quotes
    - Invoices
    - Previous billings (constrains structure)

    Each SOV chains from the previous month's billing.
    No required documents - works with whatever data is available.
    """
    try:
        project_number = request.project_number
        billing_month = request.billing_month
        billing_year = request.billing_year

        # Find project folder
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if not project_folders:
            # Create minimal project structure if needed
            project_folders = [Path(f"Projects/{project_number}-Unknown")]
            project_folders[0].mkdir(parents=True, exist_ok=True)

        project_folder = project_folders[0]

        # Find SOV template if available
        templates_folder = project_folder / "06-Templates"
        sov_template = None
        if templates_folder.exists():
            sov_templates = list(templates_folder.glob("*sov*")) + list(templates_folder.glob("*SOV*"))
            if not sov_templates:
                # Any Excel that's not a budget
                sov_templates = [f for f in templates_folder.glob("*.xlsx") if "budget" not in f.name.lower()]
            if sov_templates:
                sov_template = sov_templates[0]

        # Run AI estimation
        estimator = AIEstimator()
        result = estimator.generate_sov(
            project_number=project_number,
            project_folder=project_folder,
            billing_month=billing_month,
            billing_year=billing_year,
            template_path=sov_template
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "SOV generation failed"))

        return SOVGenerateResponse(
            success=True,
            project_number=project_number,
            billing_month=billing_month,
            billing_year=billing_year,
            application_number=result.get("sov_data", {}).get("application_number"),
            json_file=result.get("json_file"),
            excel_file=result.get("excel_file"),
            summary=result.get("sov_data", {}).get("summary"),
            message=f"SOV for {billing_month} {billing_year} generated successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/{project_number}/billings")
async def get_project_billings(project_number: str):
    """
    Get list of all billings (previous SOVs) for a project.
    Returns them in chronological order.
    """
    try:
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if not project_folders:
            return {"billings": []}

        project_folder = project_folders[0]
        billings_folder = project_folder / "billings"

        if not billings_folder.exists():
            return {"billings": []}

        billings = []
        for billing_file in sorted(billings_folder.glob("*.json")):
            with open(billing_file, 'r', encoding='utf-8') as f:
                billing_data = json.load(f)
                billings.append({
                    "month": billing_data.get("month"),
                    "year": billing_data.get("year"),
                    "generated_at": billing_data.get("generated_at"),
                    "file": billing_file.name,
                    "summary": billing_data.get("sov_data", {}).get("summary")
                })

        return {"billings": billings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/{project_number}/billings/upload")
async def upload_previous_billing(
    project_number: str,
    billing_month: str,
    billing_year: int,
    billing_file: UploadFile = File(...)
):
    """
    Upload a previous billing (historical SOV) to establish the chain.
    This constrains future SOV generation to match this structure.
    """
    try:
        # Find or create project folder
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if not project_folders:
            project_folders = [Path(f"Projects/{project_number}-Unknown")]
            project_folders[0].mkdir(parents=True, exist_ok=True)

        project_folder = project_folders[0]
        billings_folder = project_folder / "billings"
        billings_folder.mkdir(parents=True, exist_ok=True)

        # Save the uploaded file
        content = await billing_file.read()

        # Save raw file
        month_num = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }.get(billing_month.lower(), 0)

        raw_file_path = billings_folder / f"{billing_year}_{month_num:02d}_{billing_month}_uploaded{Path(billing_file.filename).suffix}"
        with open(raw_file_path, 'wb') as f:
            f.write(content)

        # Create JSON record
        billing_record = {
            "month": billing_month,
            "year": billing_year,
            "uploaded_at": datetime.now().isoformat(),
            "source_file": billing_file.filename,
            "is_uploaded": True,
            "sov_data": {
                "note": "Uploaded historical billing - structure will be extracted on next SOV generation"
            }
        }

        json_file_path = billings_folder / f"{billing_year}_{month_num:02d}_{billing_month}.json"
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(billing_record, f, indent=2)

        return {
            "success": True,
            "message": f"Previous billing for {billing_month} {billing_year} uploaded",
            "file_saved": str(raw_file_path)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/{project_number}/budgets")
async def get_project_budgets(project_number: str):
    """
    Get list of all budget revisions for a project.
    """
    try:
        budgets = []
        budget_files = sorted(
            Path("Output/Budgets").glob(f"{project_number}_budget_rev*.json"),
            key=lambda x: x.stat().st_mtime
        )

        for budget_file in budget_files:
            with open(budget_file, 'r', encoding='utf-8') as f:
                budget_data = json.load(f)
                metadata = budget_data.get("metadata", {})
                budgets.append({
                    "revision": metadata.get("revision", 1),
                    "generated_at": metadata.get("generated_at"),
                    "file": budget_file.name,
                    "summary": budget_data.get("summary")
                })

        return {"budgets": budgets}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUBMITTAL LOG ENDPOINTS
# ============================================================================

class SubmittalLogRequest(BaseModel):
    project_number: str
    include_standard: bool = True  # Include standard glazing submittals
    iterations: int = 2  # Number of AI analysis passes


class SubmittalLogResponse(BaseModel):
    success: bool
    project_number: str
    total_items: int
    json_file: Optional[str] = None
    excel_file: Optional[str] = None
    summary: Optional[dict] = None
    message: str


@app.post("/api/submittal-log/generate", response_model=SubmittalLogResponse)
async def generate_submittal_log(request: SubmittalLogRequest):
    """
    Generate a submittal log from project specs and drawings.

    Uses AI to analyze specifications and identify submittal requirements.
    Runs multiple analysis passes to ensure thoroughness.
    Can include standard glazing submittals as baseline.
    """
    try:
        project_number = request.project_number

        # Find project folder
        project_folders = list(Path("Projects").glob(f"{project_number}-*"))
        if not project_folders:
            # Create minimal project structure if needed
            project_folders = [Path(f"Projects/{project_number}-Unknown")]
            project_folders[0].mkdir(parents=True, exist_ok=True)

        project_folder = project_folders[0]

        # Generate submittal log
        generator = SubmittalGenerator()
        result = generator.generate_submittal_log(
            project_number=project_number,
            project_folder=project_folder,
            include_standard=request.include_standard,
            iterations=request.iterations
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail="Submittal log generation failed")

        # Save JSON output
        output_folder = Path("Output/Submittal_Logs")
        output_folder.mkdir(parents=True, exist_ok=True)

        json_file = output_folder / f"{project_number}_submittal_log.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        # Generate Excel
        excel_file = output_folder / f"{project_number}_submittal_log.xlsx"
        generate_submittal_log_excel(result["submittals"], excel_file)

        return SubmittalLogResponse(
            success=True,
            project_number=project_number,
            total_items=result["summary"]["total_items"],
            json_file=str(json_file),
            excel_file=str(excel_file),
            summary=result["summary"],
            message=f"Generated {result['summary']['total_items']} submittal items"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/{project_number}/submittal-log")
async def get_submittal_log(project_number: str):
    """
    Get the current submittal log for a project.
    """
    try:
        json_file = Path(f"Output/Submittal_Logs/{project_number}_submittal_log.json")

        if not json_file.exists():
            return {"submittals": [], "exists": False}

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            "exists": True,
            "submittals": data.get("submittals", []),
            "summary": data.get("summary", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/project/{project_number}/submittal-log/{item_number}")
async def update_submittal_item(project_number: str, item_number: str, updates: dict):
    """
    Update a specific submittal item (status, dates, notes).
    """
    try:
        json_file = Path(f"Output/Submittal_Logs/{project_number}_submittal_log.json")

        if not json_file.exists():
            raise HTTPException(status_code=404, detail="Submittal log not found")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Find and update the item
        updated = False
        for item in data.get("submittals", []):
            if item.get("item_number") == item_number:
                # Update allowed fields
                for key in ["status", "due_date", "submitted_date", "approved_date", "notes", "vendor_id"]:
                    if key in updates:
                        item[key] = updates[key]
                updated = True
                break

        if not updated:
            raise HTTPException(status_code=404, detail=f"Submittal item {item_number} not found")

        # Save updated data
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return {"success": True, "message": f"Updated {item_number}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/submittal_log/{project_number}")
async def download_submittal_log(project_number: str, format: str = "excel"):
    """
    Download submittal log as Excel or JSON.
    """
    try:
        if format == "json":
            file_path = Path(f"Output/Submittal_Logs/{project_number}_submittal_log.json")
        else:
            file_path = Path(f"Output/Submittal_Logs/{project_number}_submittal_log.xlsx")

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Submittal log not found")

        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=file_path.name
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT REVIEW ENDPOINTS
# ============================================================================

class DocumentReviewRequest(BaseModel):
    document_type: str  # contract, drawings, specs, schedule, proposal, vendor_quotes, vendor_invoices
    document_content: str  # Text extracted from PDF
    file_name: str
    previous_review: Optional[dict] = None  # For re-review iterations
    human_feedback: Optional[str] = None  # Human corrections/notes


class DocumentReviewResponse(BaseModel):
    success: bool
    document_type: str
    file_name: str
    extracted_data: Optional[dict] = None
    summary: Optional[str] = None
    iteration: int = 1
    reviewed_at: Optional[str] = None
    message: str


@app.post("/api/document/review", response_model=DocumentReviewResponse)
async def review_document_endpoint(request: DocumentReviewRequest):
    """
    Review a document and extract structured data based on document type.

    Document types and what they extract:
    - contract: project info, terms, scope, schedule, special conditions
    - drawings: systems, glass schedule, frames, hardware, dimensions
    - specs: sections, products, submittals, materials, warranties
    - schedule: dates, milestones, phasing, dependencies
    - proposal: pricing, scope, assumptions
    - vendor_quotes: vendor info, pricing, materials, terms
    - vendor_invoices: invoice details, line items, amounts

    Supports iteration with human feedback for corrections.
    """
    try:
        reviewer = DocumentReviewer()

        result = reviewer.review_document(
            doc_type=request.document_type,
            doc_content=request.document_content,
            file_name=request.file_name,
            previous_review=request.previous_review,
            human_feedback=request.human_feedback
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Review failed"))

        # Generate human-readable summary
        summary = reviewer.generate_review_summary(
            result.get("extracted_data", {}),
            request.document_type
        )

        return DocumentReviewResponse(
            success=True,
            document_type=request.document_type,
            file_name=request.file_name,
            extracted_data=result.get("extracted_data"),
            summary=summary,
            iteration=result.get("iteration", 1),
            reviewed_at=result.get("reviewed_at"),
            message=f"Document reviewed (iteration {result.get('iteration', 1)})"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document/review-with-file")
async def review_document_with_file(
    document_type: str,
    file: UploadFile = File(...),
    human_feedback: Optional[str] = None
):
    """
    Upload a document file and review it.
    Extracts text from PDF and runs AI review.
    """
    try:
        import fitz  # PyMuPDF for PDF text extraction

        # Read file content
        content = await file.read()

        # Extract text from PDF
        doc_content = ""
        if file.filename.lower().endswith('.pdf'):
            pdf_doc = fitz.open(stream=content, filetype="pdf")
            for page in pdf_doc:
                doc_content += page.get_text()
            pdf_doc.close()
        else:
            # For non-PDF files, try to decode as text
            try:
                doc_content = content.decode('utf-8')
            except:
                doc_content = content.decode('latin-1')

        if not doc_content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from document")

        # Run review
        reviewer = DocumentReviewer()
        result = reviewer.review_document(
            doc_type=document_type,
            doc_content=doc_content,
            file_name=file.filename,
            human_feedback=human_feedback
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Review failed"))

        summary = reviewer.generate_review_summary(
            result.get("extracted_data", {}),
            document_type
        )

        return {
            "success": True,
            "document_type": document_type,
            "file_name": file.filename,
            "extracted_data": result.get("extracted_data"),
            "summary": summary,
            "iteration": result.get("iteration", 1),
            "reviewed_at": result.get("reviewed_at"),
            "text_length": len(doc_content),
            "message": f"Document reviewed successfully"
        }

    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF processing library not available. Install PyMuPDF: pip install pymupdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/document/review-types")
async def get_review_types():
    """Get available document types and what data they extract."""
    return {
        "types": [
            {
                "id": "contract",
                "label": "Contract",
                "extracts": ["Project info", "Contract terms", "Scope of work", "Schedule", "Special conditions"]
            },
            {
                "id": "drawings",
                "label": "Drawings",
                "extracts": ["Systems", "Glass schedule", "Frame/metal specs", "Hardware", "Dimensions", "Quantities"]
            },
            {
                "id": "specs",
                "label": "Specifications",
                "extracts": ["Spec sections", "Products", "Submittals", "Materials", "Warranties", "Quality assurance"]
            },
            {
                "id": "schedule",
                "label": "Schedule",
                "extracts": ["Key dates", "Milestones", "Phasing", "Dependencies", "Durations"]
            },
            {
                "id": "proposal",
                "label": "Proposal/Bid",
                "extracts": ["Pricing", "Scope included", "Assumptions", "Exclusions"]
            },
            {
                "id": "vendor_quotes",
                "label": "Vendor Quote",
                "extracts": ["Vendor info", "Pricing", "Materials", "Lead times", "Terms"]
            },
            {
                "id": "vendor_invoices",
                "label": "Vendor Invoice",
                "extracts": ["Invoice details", "Line items", "Amounts", "References"]
            }
        ]
    }


# Run the server
if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*70)
    print("  GLAZING PM AI - API SERVER")
    print("="*70)
    print("\nStarting server on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("\nPress CTRL+C to stop")
    print("="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
