#!/usr/bin/env python3
"""
Glazing PM AI - Main Orchestrator
Automates commercial glazing project management workflows
"""

import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from file_mover import FileMover
from contract_processor import ContractProcessor
from sov_generator import SOVGenerator
from email_generator import EmailGenerator
from logger import ProjectRegistry


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  GLAZING PM AI - Project Management Automation")
    print("="*60 + "\n")


def check_api_key():
    """Check if API key is set"""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("\nContract analysis and SOV generation require Claude API.")
        print("Set your API key:")
        print("  Windows: set ANTHROPIC_API_KEY=your-key-here")
        print("  Mac/Linux: export ANTHROPIC_API_KEY=your-key-here")
        print("\nYou can still use file organization features.\n")
        return False
    return True


def process_new_project(project_name=None):
    """Complete workflow: initialize, analyze, generate SOV & emails"""

    print_banner()
    has_api_key = check_api_key()

    # Step 1: File Mover
    print("STEP 1: PROJECT INITIALIZATION")
    print("-" * 60)

    mover = FileMover()

    if project_name:
        result = mover.initialize_project(project_name)
    else:
        # Interactive mode
        projects = mover.get_input_projects()

        if not projects:
            print("📭 No projects found in Input/ folder")
            print("\nTo add a project:")
            print("  1. Create a folder in Input/ with your project name")
            print("  2. Add PDF files (contract, specs, drawings, etc.)")
            print("  3. Run: python main.py process")
            return False

        print(f"Found {len(projects)} project(s):\n")
        for i, proj in enumerate(projects, 1):
            print(f"{i}. {proj['name']} ({proj['file_count']} PDFs)")

        if len(projects) == 1:
            result = mover.initialize_project(projects[0]['name'])
        else:
            print("\nMultiple projects found. Specify which to process:")
            print('  python main.py process "Project Name"')
            return False

    if not result['success']:
        print("\n❌ Project initialization failed")
        return False

    project_number = result['project_number']
    project_path = result['project_path']

    if not has_api_key:
        print("\n✅ Project initialized successfully!")
        print("⚠️  Skipping contract analysis and SOV generation (no API key)")
        return True

    # Step 2: Contract Processor
    print("\nSTEP 2: CONTRACT ANALYSIS")
    print("-" * 60)

    try:
        processor = ContractProcessor()
        analysis_result = processor.analyze_contract_documents(project_path, project_number)

        if not analysis_result['success']:
            print("\n⚠️  Contract analysis failed, continuing anyway...")
            return True

        contract_analysis = analysis_result['analysis']

        # Step 3: SOV Generator
        print("\nSTEP 3: SCHEDULE OF VALUES GENERATION")
        print("-" * 60)

        sov_gen = SOVGenerator()
        sov_result = sov_gen.generate_sov(project_number, contract_analysis)

        if not sov_result['success']:
            print("\n⚠️  SOV generation failed, continuing anyway...")
            sov_data = None
        else:
            sov_data = sov_result['sov_data']

        # Step 4: Email Generator
        print("\nSTEP 4: DRAFT EMAIL GENERATION")
        print("-" * 60)

        email_gen = EmailGenerator()
        email_gen.generate_all_emails(project_number, contract_analysis, sov_data)

        # Final summary
        print("\n" + "="*60)
        print("  ✅ PROJECT PROCESSING COMPLETE!")
        print("="*60)
        print(f"\nProject Number: {project_number}")
        print(f"Project Folder: {project_path.relative_to(Path.cwd())}")
        print(f"\nGenerated Outputs:")
        print(f"  📊 Contract Analysis: Output/Reports/{project_number}_contract_analysis.md")
        print(f"  💰 Schedule of Values: Output/Draft_SOV/{project_number}_SOV.csv")
        print(f"  📧 Draft Emails: Output/Draft_Emails/{project_number}_*.txt")
        print(f"  📝 Activity Logs: Logs/*.csv")
        print(f"\nNext Steps:")
        print(f"  1. Review contract analysis report")
        print(f"  2. Review and edit SOV CSV as needed")
        print(f"  3. Review draft emails and fill in [PLACEHOLDERS]")
        print(f"  4. Copy/paste emails into Gmail when ready to send")
        print("\n" + "="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        return False


def list_projects():
    """List all projects in the system"""
    print_banner()
    print("📋 PROJECT REGISTRY\n")

    registry_file = Path("Logs/project_registry.csv")

    if not registry_file.exists():
        print("No projects registered yet.")
        return

    import csv
    with open(registry_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        projects = list(reader)

    if not projects:
        print("No projects registered yet.")
        return

    for proj in projects:
        print(f"{proj['Project_Number']} - {proj['Project_Name']}")
        print(f"  Status: {proj['Status']}")
        print(f"  Phase: {proj['Current_Phase']}")
        print(f"  Created: {proj['Created_Date']}")
        if proj['Contract_Value']:
            print(f"  Value: {proj['Contract_Value']}")
        print()


def show_help():
    """Show help message"""
    print_banner()
    print("USAGE")
    print("-" * 60)
    print("\nProcess a new project:")
    print('  python main.py process ["Project Name"]')
    print("\nList all projects:")
    print("  python main.py list")
    print("\nShow help:")
    print("  python main.py help")
    print("\nRun individual agents:")
    print("  python scripts/file_mover.py \"Project Name\"")
    print("  python scripts/contract_processor.py P001")
    print("  python scripts/sov_generator.py P001")
    print("  python scripts/email_generator.py P001")
    print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "process":
        project_name = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        process_new_project(project_name)

    elif command == "list":
        list_projects()

    elif command == "help":
        show_help()

    else:
        print(f"Unknown command: {command}")
        print('Run "python main.py help" for usage information')


if __name__ == "__main__":
    main()
