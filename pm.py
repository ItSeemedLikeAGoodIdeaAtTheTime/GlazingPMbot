#!/usr/bin/env python3
"""
Glazing PM CLI - Unified Command Line Interface
Main entry point for all project management operations
"""

import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import argparse
from file_mover import FileMover
from contract_processor import ContractProcessor
from sov_generator import SOVGenerator
from email_generator import EmailGenerator
from logger import ProjectRegistry


def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print("  🏗️  GLAZING PM AI - Project Management Command Line")
    print("="*70 + "\n")


def cmd_new_project(args):
    """Create new project from input folder"""
    print_banner()
    print("📂 CREATING NEW PROJECT")
    print("-" * 70 + "\n")

    mover = FileMover()

    if args.name:
        result = mover.initialize_project(args.name)
    else:
        # Interactive: show available projects
        projects = mover.get_input_projects()
        if not projects:
            print("❌ No projects found in Input/ folder")
            print("\nAdd a project folder with PDF/text files first.")
            return False

        print(f"Found {len(projects)} project(s) in Input/:\n")
        for i, proj in enumerate(projects, 1):
            print(f"{i}. {proj['name']} ({proj['file_count']} files)")

        if len(projects) == 1:
            result = mover.initialize_project(projects[0]['name'])
        else:
            print("\nSpecify project: pm new -n \"Project Name\"")
            return False

    if result['success']:
        print(f"\n✅ Project {result['project_number']} created!")
        if hasattr(args, 'full') and args.full:
            print("\n🔄 Running full workflow...")
            # Auto-run analysis
            args.project = result['project_number']
            cmd_analyze(args)
        return True
    return False


def cmd_analyze(args):
    """Analyze contract documents"""
    print_banner()
    print(f"📄 ANALYZING CONTRACT: {args.project}")
    print("-" * 70 + "\n")

    try:
        # Find project folder
        projects_dir = Path("Projects")
        project_folders = list(projects_dir.glob(f"{args.project}-*"))

        if not project_folders:
            print(f"❌ Project not found: {args.project}")
            return False

        processor = ContractProcessor()
        result = processor.analyze_contract_documents(project_folders[0], args.project)

        if result['success']:
            print(f"\n✅ Analysis complete!")
            if args.sov:
                print("\n🔄 Generating SOV...")
                cmd_generate_sov(args)
            return True
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_generate_sov(args):
    """Generate Schedule of Values"""
    print_banner()
    print(f"💰 GENERATING SOV: {args.project}")
    print("-" * 70 + "\n")

    try:
        # Load contract analysis
        import json
        analysis_file = Path("Output/Reports") / f"{args.project}_contract_analysis.json"

        if not analysis_file.exists():
            print(f"❌ Contract analysis not found. Run: pm analyze {args.project}")
            return False

        with open(analysis_file, 'r', encoding='utf-8') as f:
            contract_analysis = json.load(f)

        generator = SOVGenerator()
        result = generator.generate_sov(args.project, contract_analysis)

        if result['success']:
            print(f"\n✅ SOV generated!")
            if args.sheet:
                print("\n🔄 Pushing to Google Sheets...")
                cmd_push_sheets(args)
            return True
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_push_sheets(args):
    """Push SOV to Google Sheets"""
    print_banner()
    print(f"📊 PUSHING TO GOOGLE SHEETS: {args.project}")
    print("-" * 70 + "\n")

    if not args.url:
        print("❌ Sheet URL required: pm sheets {args.project} -u \"SHEET_URL\"")
        return False

    try:
        import json
        from google_sheets_push_v2 import GoogleSheetsPusher

        # Load SOV
        sov_file = Path("Output/Draft_SOV") / f"{args.project}_SOV.json"
        if not sov_file.exists():
            print(f"❌ SOV not found. Run: pm sov {args.project}")
            return False

        with open(sov_file, 'r', encoding='utf-8') as f:
            sov_data = json.load(f)

        pusher = GoogleSheetsPusher()
        result = pusher.update_sov_spreadsheet(args.url, args.project, sov_data)

        if result['success']:
            print(f"\n✅ Pushed to sheets!")
            print(f"   {result['url']}")

            if args.tracking:
                print("\n🔄 Creating tracking sheets...")
                cmd_create_tracking(args)
            return True
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_create_tracking(args):
    """Create project tracking sheets"""
    print_banner()
    print(f"📋 CREATING TRACKING SHEETS: {args.project}")
    print("-" * 70 + "\n")

    if not args.url:
        print("❌ Sheet URL required")
        return False

    try:
        from google_sheets_extended import ExtendedSheetManager
        import csv

        # Get project name
        project_name = args.project
        registry_file = Path("Logs/project_registry.csv")
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Project_Number'] == args.project:
                        project_name = row['Project_Name']
                        break

        manager = ExtendedSheetManager()
        result = manager.create_project_tracking_sheets(args.url, args.project, project_name)

        if result['success']:
            print(f"\n✅ Tracking sheets created!")
            return True
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_dashboard(args):
    """Create/update company dashboard"""
    print_banner()
    print("💼 CREATING COMPANY DASHBOARD")
    print("-" * 70 + "\n")

    if not args.url:
        print("❌ Sheet URL required: pm dashboard -u \"SHEET_URL\"")
        return False

    try:
        from google_sheets_extended import ExtendedSheetManager

        manager = ExtendedSheetManager()
        result = manager.create_company_dashboard(args.url)

        if result['success']:
            print(f"\n✅ Dashboard created!")
            return True
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def cmd_list_projects(args):
    """List all projects"""
    print_banner()
    print("📋 ACTIVE PROJECTS")
    print("-" * 70 + "\n")

    import csv
    registry_file = Path("Logs/project_registry.csv")

    if not registry_file.exists():
        print("No projects yet.")
        return

    with open(registry_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        projects = list(reader)

    for proj in projects:
        print(f"{proj['Project_Number']} - {proj['Project_Name']}")
        print(f"  Status: {proj['Status']} | Phase: {proj['Current_Phase']}")
        if proj['Contract_Value']:
            print(f"  Value: {proj['Contract_Value']}")
        print()


def cmd_full_workflow(args):
    """Run complete workflow"""
    print_banner()
    print("🚀 RUNNING FULL WORKFLOW")
    print("="*70 + "\n")

    # Step 1: Create project
    if not cmd_new_project(args):
        return False

    # Get the project number from the last operation
    registry = ProjectRegistry()
    project_number = registry.get_next_project_number()
    # Actually get the last one created
    import csv
    with open(Path("Logs/project_registry.csv"), 'r') as f:
        projects = list(csv.DictReader(f))
        if projects:
            project_number = projects[-1]['Project_Number']

    args.project = project_number

    # Step 2: Analyze
    print("\n" + "="*70)
    print("STEP 2: CONTRACT ANALYSIS")
    print("="*70)
    if not cmd_analyze(args):
        return False

    # Step 3: SOV
    print("\n" + "="*70)
    print("STEP 3: GENERATE SOV")
    print("="*70)
    if not cmd_generate_sov(args):
        return False

    # Step 4: Sheets (if URL provided)
    if args.url:
        print("\n" + "="*70)
        print("STEP 4: PUSH TO GOOGLE SHEETS")
        print("="*70)
        if not cmd_push_sheets(args):
            return False

        print("\n" + "="*70)
        print("STEP 5: CREATE TRACKING SHEETS")
        print("="*70)
        cmd_create_tracking(args)

    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE!")
    print("="*70 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Glazing PM AI - Project Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pm new -n "Project Name"              Create new project
  pm workflow -n "Project" -u "URL"     Run full workflow
  pm analyze P001                        Analyze contract
  pm sov P001                            Generate SOV
  pm sheets P001 -u "URL"                Push to sheets
  pm tracking P001 -u "URL"              Create tracking sheets
  pm dashboard -u "URL"                  Create dashboard
  pm list                                List all projects
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # New project
    new_parser = subparsers.add_parser('new', help='Create new project')
    new_parser.add_argument('-n', '--name', help='Project name')
    new_parser.add_argument('-f', '--full', action='store_true', help='Run full workflow')

    # Analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analyze contract')
    analyze_parser.add_argument('project', help='Project number (e.g., P001)')
    analyze_parser.add_argument('-s', '--sov', action='store_true', help='Auto-generate SOV after')

    # SOV
    sov_parser = subparsers.add_parser('sov', help='Generate Schedule of Values')
    sov_parser.add_argument('project', help='Project number')
    sov_parser.add_argument('-s', '--sheet', action='store_true', help='Auto-push to sheets')
    sov_parser.add_argument('-u', '--url', help='Google Sheets URL')

    # Sheets
    sheets_parser = subparsers.add_parser('sheets', help='Push SOV to Google Sheets')
    sheets_parser.add_argument('project', help='Project number')
    sheets_parser.add_argument('-u', '--url', required=True, help='Google Sheets URL')
    sheets_parser.add_argument('-t', '--tracking', action='store_true', help='Also create tracking sheets')

    # Tracking
    tracking_parser = subparsers.add_parser('tracking', help='Create tracking sheets')
    tracking_parser.add_argument('project', help='Project number')
    tracking_parser.add_argument('-u', '--url', required=True, help='Google Sheets URL')

    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Create company dashboard')
    dashboard_parser.add_argument('-u', '--url', required=True, help='Google Sheets URL')

    # List
    list_parser = subparsers.add_parser('list', help='List all projects')

    # Full workflow
    workflow_parser = subparsers.add_parser('workflow', help='Run complete workflow')
    workflow_parser.add_argument('-n', '--name', help='Project name')
    workflow_parser.add_argument('-u', '--url', help='Google Sheets URL')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to command handlers
    commands = {
        'new': cmd_new_project,
        'analyze': cmd_analyze,
        'sov': cmd_generate_sov,
        'sheets': cmd_push_sheets,
        'tracking': cmd_create_tracking,
        'dashboard': cmd_dashboard,
        'list': cmd_list_projects,
        'workflow': cmd_full_workflow
    }

    handler = commands.get(args.command)
    if handler:
        success = handler(args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
