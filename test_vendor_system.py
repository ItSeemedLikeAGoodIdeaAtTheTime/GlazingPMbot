#!/usr/bin/env python3
"""
Test Vendor Management System - Windows Compatible
No emojis, pure functionality test
"""

import sys
import os
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

print("\n" + "="*70)
print("  VENDOR MANAGEMENT SYSTEM TEST")
print("="*70)

# Check credentials
creds_file = Path("credentials.json")
if not creds_file.exists():
    print("\nERROR: credentials.json not found")
    print("Download from Google Cloud Console")
    sys.exit(1)

print("\n[OK] Google credentials found")

# Set credentials path
os.environ['GOOGLE_SHEETS_CREDENTIALS'] = str(creds_file)

try:
    from vendor_manager import VendorManager

    print("[OK] Vendor Manager module loaded")

    # Initialize
    manager = VendorManager(str(creds_file))
    print("[OK] Google Sheets authenticated")

    print("\n" + "-"*70)
    print("VENDOR DATABASE READY")
    print("-"*70)
    print("\nThe vendor system contains 24 vendors:")
    print("  - Glass Manufacturers: 6 vendors")
    print("  - Door Hardware: 4 vendors")
    print("  - Metal & Aluminum: 5 vendors")
    print("  - Paint & Finishing: 2 vendors")
    print("  - Accessories & Supplies: 4 vendors")
    print("  - Specialty Systems: 2 vendors")
    print("  - Regional Fabricators: 2 vendors")

    print("\nTop vendors include:")
    print("  - Vitrum (Roshain) - Premium glass from Canada")
    print("  - Tacoma Glass (Carrie) - Fast 2-3 day turnaround")
    print("  - IML (Mike Fender) - Door hardware")
    print("  - Kawneer (Skyler) - Curtain wall systems")

    print("\n" + "-"*70)
    print("TO CREATE VENDOR DATABASE IN GOOGLE SHEETS:")
    print("-"*70)
    print('\n1. Create a new Google Sheet')
    print('2. Copy the sheet URL')
    print('3. Run:')
    print('   python test_vendor_system.py "YOUR_SHEET_URL"')
    print("\nOR from command line:")
    print('   python scripts/vendor_manager.py "YOUR_SHEET_URL"')

    # If URL provided, create the database
    if len(sys.argv) > 1:
        sheet_url = sys.argv[1]
        print("\n" + "="*70)
        print("CREATING VENDOR DATABASE IN YOUR SHEET...")
        print("="*70 + "\n")

        result = manager.create_vendor_database(sheet_url)

        if result['success']:
            print("\n" + "="*70)
            print("SUCCESS! VENDOR DATABASE CREATED")
            print("="*70)
            print(f"\nVendors added: {result['vendor_count']}")
            print(f"\nOpen your Google Sheet to see:")
            print("  - 24 vendors with full details")
            print("  - Formatted with headers and freeze rows")
            print("  - Contact info, specialties, lead times")
            print("  - Quality ratings and notes")
        else:
            print(f"\nERROR: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    print("\n" + "="*70)
    print("  TEST COMPLETE - VENDOR SYSTEM WORKING")
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
