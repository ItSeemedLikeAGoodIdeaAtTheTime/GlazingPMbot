"""
Vendor Management System
Creates and manages vendor database in Google Sheets
"""

import json
import os
from pathlib import Path
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


class VendorManager:
    """Manages vendor database and tracking"""

    def __init__(self, credentials_path=None):
        """Initialize with Google service account credentials"""
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

        if not self.credentials_path or not Path(self.credentials_path).exists():
            raise ValueError("Google Sheets credentials not found")

        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]

        creds = Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
        self.client = gspread.authorize(creds)

    def create_vendor_database(self, spreadsheet_url):
        """Create comprehensive vendor database sheet"""

        print(f"\n{'='*70}")
        print(f"👥 Creating Vendor Database")
        print(f"{'='*70}\n")

        try:
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            print(f"✅ Opened spreadsheet: {spreadsheet.title}")

            # Create or get vendor sheet
            sheet_name = "Vendors"

            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()
                print(f"✅ Found existing sheet: {sheet_name}")
            except:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20, index=1)
                print(f"✅ Created new sheet: {sheet_name}")

            # Define vendor data
            vendors = [
                # Glass Manufacturers
                {
                    "name": "Vitrum",
                    "contact": "Roshain",
                    "category": "Glass Manufacturer",
                    "location": "Canada",
                    "specialty": "Large high-quality IGUs, excellent edge work, great QC",
                    "lead_time": "4-8 weeks",
                    "notes": "Premium quality, 10-15% more expensive but double the quality",
                    "rating": "Gold Standard"
                },
                {
                    "name": "Hartung",
                    "contact": "Ali",
                    "category": "Glass Manufacturer",
                    "location": "USA (Local)",
                    "specialty": "IGU fabrication, lower cost alternative",
                    "lead_time": "4-8 weeks",
                    "notes": "American company, slightly lower quality than Vitrum but more affordable",
                    "rating": "Good"
                },
                {
                    "name": "Tacoma Glass",
                    "contact": "Carrie",
                    "category": "Glass Manufacturer",
                    "location": "Washington",
                    "specialty": "Monolithic glass shapes, custom work",
                    "lead_time": "2-3 days",
                    "notes": "Amazing quick turnaround, specialty shapes",
                    "rating": "Excellent - Fast"
                },
                {
                    "name": "General Glass",
                    "contact": "Kaylee",
                    "category": "Glass Manufacturer",
                    "location": "",
                    "specialty": "",
                    "lead_time": "",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Allegiant (TGP)",
                    "contact": "Alaina Fox",
                    "category": "Specialty Glass",
                    "location": "",
                    "specialty": "Technical Glass Products - fire-rated, specialty",
                    "lead_time": "",
                    "notes": "Technical Glass Products purchased by Allegiant",
                    "rating": ""
                },
                {
                    "name": "GlassPro",
                    "contact": "Jim Tarman",
                    "category": "Glass Manufacturer",
                    "location": "California",
                    "specialty": "Luxury glass, fancy high-end work",
                    "lead_time": "2 weeks",
                    "notes": "Premium specialty glass fabrication",
                    "rating": "Excellent"
                },

                # Door Hardware
                {
                    "name": "IML (Intermountain Lock)",
                    "contact": "Mike Fender",
                    "category": "Door Hardware",
                    "location": "",
                    "specialty": "Door hardware, panic devices, closers",
                    "lead_time": "8 weeks",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Mayflower",
                    "contact": "Anatoly",
                    "category": "Door Hardware",
                    "location": "",
                    "specialty": "Door hardware",
                    "lead_time": "1 week",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "FHC (Frameless Hardware)",
                    "contact": "",
                    "category": "Specialty Hardware",
                    "location": "",
                    "specialty": "All-glass door hardware, specialty products",
                    "lead_time": "",
                    "notes": "Frameless Hardware Company - specialty specified products",
                    "rating": ""
                },
                {
                    "name": "CRL (CR Laurence)",
                    "contact": "",
                    "category": "Hardware & Accessories",
                    "location": "",
                    "specialty": "All-glass door hardware, specialty products, off-the-shelf",
                    "lead_time": "",
                    "notes": "Large catalog, readily available",
                    "rating": ""
                },

                # Metal & Aluminum
                {
                    "name": "Coast Aluminum",
                    "contact": "Melissa",
                    "category": "Raw Aluminum Supplier",
                    "location": "",
                    "specialty": "Raw aluminum stock",
                    "lead_time": "1 week",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Kawneer",
                    "contact": "Skyler",
                    "category": "Curtain Wall Systems",
                    "location": "",
                    "specialty": "Storefront metal systems",
                    "lead_time": "12 weeks",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Oldcastle",
                    "contact": "",
                    "category": "Storefront/Glass",
                    "location": "",
                    "specialty": "Storefront material, some IGU supply",
                    "lead_time": "8-12 weeks",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "North Clad",
                    "contact": "TJ",
                    "category": "Metal Panel Fabricator",
                    "location": "",
                    "specialty": "Metal panel fabrication",
                    "lead_time": "12 weeks",
                    "notes": "High quality work",
                    "rating": "Excellent"
                },
                {
                    "name": "ABF (Aluminum Bronze Fabricators)",
                    "contact": "Brent Hammer",
                    "category": "Metal Panel Fabricator",
                    "location": "",
                    "specialty": "Metal panel fabrication",
                    "lead_time": "8-12 weeks",
                    "notes": "High quality",
                    "rating": "Excellent"
                },

                # Finishing & Paint
                {
                    "name": "New Finishes",
                    "contact": "TJ",
                    "category": "Paint Shop",
                    "location": "",
                    "specialty": "High-end custom painting",
                    "lead_time": "",
                    "notes": "Really high quality custom work",
                    "rating": "Premium"
                },
                {
                    "name": "Accurate Industries",
                    "contact": "Elizabeth",
                    "category": "Paint Shop",
                    "location": "Auburn",
                    "specialty": "Painting services",
                    "lead_time": "",
                    "notes": "",
                    "rating": ""
                },

                # Accessories & Supplies
                {
                    "name": "Colorado Steel & Sash",
                    "contact": "Jeremiah",
                    "category": "Accessories",
                    "location": "Colorado",
                    "specialty": "GE sealants, shims, accessories",
                    "lead_time": "Off-the-shelf",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Atlas Supply",
                    "contact": "Evan Moran",
                    "category": "Sealants & Supplies",
                    "location": "",
                    "specialty": "Dow Corning sealants",
                    "lead_time": "Off-the-shelf",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Hilti",
                    "contact": "",
                    "category": "Anchors & Fasteners",
                    "location": "",
                    "specialty": "Concrete anchors, fasteners",
                    "lead_time": "Off-the-shelf",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Tacoma Screw",
                    "contact": "",
                    "category": "Hardware & Fasteners",
                    "location": "Washington",
                    "specialty": "Hardware, fasteners, off-the-shelf",
                    "lead_time": "Off-the-shelf",
                    "notes": "",
                    "rating": ""
                },

                # Specialty Systems
                {
                    "name": "AD Systems (Alpha Delta)",
                    "contact": "",
                    "category": "Hospital Doors",
                    "location": "",
                    "specialty": "Hospital door systems",
                    "lead_time": "16 weeks",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Nanawall",
                    "contact": "",
                    "category": "Folding Door Systems",
                    "location": "",
                    "specialty": "Custom folding doors",
                    "lead_time": "",
                    "notes": "",
                    "rating": ""
                },

                # Regional Fabricators
                {
                    "name": "Garibaldi Glass",
                    "contact": "",
                    "category": "Glass Fabricator",
                    "location": "",
                    "specialty": "",
                    "lead_time": "",
                    "notes": "",
                    "rating": ""
                },
                {
                    "name": "Glass Fab",
                    "contact": "",
                    "category": "Glass Fabricator",
                    "location": "",
                    "specialty": "",
                    "lead_time": "",
                    "notes": "",
                    "rating": ""
                }
            ]

            # Create header
            header_data = [
                ["VENDOR DATABASE"],
                [f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                [""],
                ["Vendor Name", "Primary Contact", "Category", "Location", "Specialty",
                 "Lead Time", "Rating", "Phone", "Email", "Address", "Notes"]
            ]

            worksheet.update('A1', header_data)

            # Add vendor data
            start_row = 5
            rows_data = []

            for vendor in vendors:
                row = [
                    vendor['name'],
                    vendor['contact'],
                    vendor['category'],
                    vendor['location'],
                    vendor['specialty'],
                    vendor['lead_time'],
                    vendor['rating'],
                    "",  # Phone (to be added)
                    "",  # Email (to be added)
                    "",  # Address (to be added)
                    vendor['notes']
                ]
                rows_data.append(row)

            worksheet.update(f'A{start_row}', rows_data)

            # Format
            worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 16}})
            worksheet.format('A4:K4', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
            })
            worksheet.freeze(rows=4)

            # Auto-resize columns
            worksheet.columns_auto_resize(0, 10)

            print(f"\n✅ Vendor database created with {len(vendors)} vendors!")
            print(f"   Categories: Glass, Hardware, Metal, Paint, Accessories, Specialty")

            return {'success': True, 'vendor_count': len(vendors)}

        except Exception as e:
            print(f"\nError: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python vendor_manager.py <sheet_url>")
        print('\nExample: python vendor_manager.py "https://docs.google.com/..."')
        sys.exit(1)

    sheet_url = sys.argv[1]

    try:
        manager = VendorManager()
        result = manager.create_vendor_database(sheet_url)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
