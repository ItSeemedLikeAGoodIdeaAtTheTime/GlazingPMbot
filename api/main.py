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
    scopes: List[dict] = []
    message: str


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
    proposal: Optional[UploadFile] = File(None)
):
    """
    Upload project documents

    Creates project folder and saves uploaded files
    """

    try:
        # Create project folder in Input
        project_folder = Path("Input") / project_name
        project_folder.mkdir(parents=True, exist_ok=True)

        # Save uploaded files
        uploaded_files = []

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

        return {
            "success": True,
            "project_name": project_name,
            "folder": str(project_folder),
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

        # Prepare response
        sov_file = Path(f"Output/Draft_SOV/{project_number}_SOV.json")

        return SOVResponse(
            success=True,
            project_number=project_number,
            sov_file=str(sov_file),
            budget_file=budget_file,
            billing_schedule_file=billing_file,
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
            message="SOV generated successfully"
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
        "analysis": f"Output/Reports/{project_number}_contract_analysis.md",
        "scope": f"Output/Scope_Analysis/{project_number}_scope_analysis.md",
        "budget": f"Output/Budgets/{project_number}_internal_budget.csv",
        "billing": f"Output/Billing_Schedules/{project_number}_billing_schedule.csv"
    }

    file_path = Path(file_map.get(file_type, ''))

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
