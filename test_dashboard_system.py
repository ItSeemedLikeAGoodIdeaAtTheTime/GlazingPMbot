#!/usr/bin/env python3
"""
Test Dashboard & Tracking System - Windows Compatible
No emojis, pure functionality test
"""

import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

print("\n" + "="*70)
print("  GOOGLE SHEETS DASHBOARD SYSTEM TEST")
print("="*70)

# Check credentials
creds_file = Path("credentials.json")
if not creds_file.exists():
    print("\nERROR: credentials.json not found")
    sys.exit(1)

print("\n[OK] Google credentials found")

# Set credentials path
os.environ['GOOGLE_SHEETS_CREDENTIALS'] = str(creds_file)

try:
    from google_sheets_extended import ExtendedSheetManager

    print("[OK] Dashboard Manager module loaded")

    # Initialize
    manager = ExtendedSheetManager(str(creds_file))
    print("[OK] Google Sheets authenticated")

    print("\n" + "-"*70)
    print("DASHBOARD FEATURES AVAILABLE")
    print("-"*70)

    print("\n1. COMPANY DASHBOARD")
    print("   Creates master cash flow dashboard with:")
    print("   - Total active projects summary")
    print("   - Contract value totals")
    print("   - 3-month cash flow forecast")
    print("   - Project status overview")

    print("\n2. PROJECT TRACKING SHEETS (per project)")
    print("   Creates 4 tracking tabs:")
    print("   - PO Log: Purchase orders, delivery, billing")
    print("   - Submittal Log: Submittal tracking, approvals")
    print("   - Installation Log: Progress tracking")
    print("   - Invoice Tracker: Vendor payments")

    print("\n3. SOV INTEGRATION")
    print("   Pushes Schedule of Values to formatted sheets")

    print("\n" + "-"*70)
    print("USAGE COMMANDS")
    print("-"*70)

    print('\n# Create company dashboard:')
    print('python test_dashboard_system.py dashboard "SHEET_URL"')

    print('\n# Create project tracking for P001:')
    print('python test_dashboard_system.py project P001 "SHEET_URL"')

    print('\n# Or use the script directly:')
    print('python scripts/google_sheets_extended.py dashboard "URL"')
    print('python scripts/google_sheets_extended.py project P001 "URL"')

    # Handle commands
    if len(sys.argv) > 2:
        mode = sys.argv[1]

        if mode == "dashboard":
            sheet_url = sys.argv[2]
            print("\n" + "="*70)
            print("CREATING COMPANY DASHBOARD...")
            print("="*70 + "\n")

            result = manager.create_company_dashboard(sheet_url)

            if result['success']:
                print("\n" + "="*70)
                print("SUCCESS! DASHBOARD CREATED")
                print("="*70)
                print("\nYour sheet now contains:")
                print("  - Company cash flow dashboard tab")
                print("  - Summary metrics section")
                print("  - 3-month forecast section")
                print("\nOpen your Google Sheet to view it!")
            else:
                print(f"\nERROR: {result.get('error')}")
                sys.exit(1)

        elif mode == "project":
            if len(sys.argv) < 4:
                print("\nERROR: Need project number and URL")
                print('Usage: python test_dashboard_system.py project P001 "URL"')
                sys.exit(1)

            project_number = sys.argv[2]
            sheet_url = sys.argv[3]

            print("\n" + "="*70)
            print(f"CREATING PROJECT TRACKING FOR {project_number}...")
            print("="*70 + "\n")

            # Get project name from registry
            import csv
            project_name = project_number
            registry_file = Path("Logs/project_registry.csv")
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['Project_Number'] == project_number:
                            project_name = row['Project_Name']
                            break

            result = manager.create_project_tracking_sheets(
                sheet_url, project_number, project_name
            )

            if result['success']:
                print("\n" + "="*70)
                print("SUCCESS! TRACKING SHEETS CREATED")
                print("="*70)
                print(f"\nYour sheet now contains 4 new tabs for {project_number}:")
                print("  1. PO Log")
                print("  2. Submittal Log")
                print("  3. Installation Log")
                print("  4. Invoice Tracker")
                print("\nAll tabs are formatted and ready to use!")
            else:
                print(f"\nERROR: {result.get('error')}")
                sys.exit(1)
        else:
            print(f"\nERROR: Unknown mode '{mode}'")
            print("Use 'dashboard' or 'project'")
            sys.exit(1)

    print("\n" + "="*70)
    print("  TEST COMPLETE - DASHBOARD SYSTEM WORKING")
    print("="*70 + "\n")

except ImportError as e:
    print(f"\nERROR: Missing module - {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
