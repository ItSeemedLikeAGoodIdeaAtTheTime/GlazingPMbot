"""
Google Sheets Extended - Add project tracking sheets
Creates comprehensive project management tabs beyond just SOV
"""

import json
import os
from pathlib import Path
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from scripts.logger import AgentActivityLog


class ExtendedSheetManager:
    """Manages comprehensive project tracking sheets"""

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
        self.activity_log = AgentActivityLog()

    def create_project_tracking_sheets(self, spreadsheet_url, project_number, project_name):
        """Create all tracking sheets for a project"""

        print(f"\n{'='*60}")
        print(f"📊 Creating Project Tracking Sheets: {project_number}")
        print(f"{'='*60}\n")

        try:
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            print(f"✅ Opened spreadsheet: {spreadsheet.title}")

            # Create tracking sheets
            self._create_po_log(spreadsheet, project_number)
            self._create_submittal_log(spreadsheet, project_number)
            self._create_installation_log(spreadsheet, project_number)
            self._create_invoice_tracker(spreadsheet, project_number)

            print(f"\n✅ All tracking sheets created!")
            return {'success': True}

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return {'success': False, 'error': str(e)}

    def _create_po_log(self, spreadsheet, project_number):
        """Create Purchase Order Log"""
        sheet_name = f"{project_number} - PO Log"

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=15)

        # Header
        header_data = [
            ["PURCHASE ORDER LOG"],
            [f"Project: {project_number}"],
            [""],
            ["PO #", "Vendor", "Description", "PO Amount", "Date Issued", "Expected Delivery",
             "Date Received", "Packing Slip #", "Billable?", "Amount to Bill", "Billed?",
             "Date Billed", "Notes"]
        ]

        worksheet.update('A1', header_data)

        # Format
        worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
        worksheet.format('A4:M4', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
        worksheet.freeze(rows=4)

        print(f"  ✅ Created: {sheet_name}")

    def _create_submittal_log(self, spreadsheet, project_number):
        """Create Submittal Log"""
        sheet_name = f"{project_number} - Submittals"

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=12)

        # Header
        header_data = [
            ["SUBMITTAL LOG"],
            [f"Project: {project_number}"],
            [""],
            ["Item #", "Description", "Spec Section", "Date Submitted", "Submitted To",
             "Date Approved", "Revision #", "Status", "Can Bill?", "Billed?", "Notes"]
        ]

        worksheet.update('A1', header_data)

        # Format
        worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
        worksheet.format('A4:K4', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
        worksheet.freeze(rows=4)

        print(f"  ✅ Created: {sheet_name}")

    def _create_installation_log(self, spreadsheet, project_number):
        """Create Installation Progress Log"""
        sheet_name = f"{project_number} - Installation"

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=12)

        # Header
        header_data = [
            ["INSTALLATION PROGRESS LOG"],
            [f"Project: {project_number}"],
            [""],
            ["Item #", "Description", "Location/Area", "Scheduled Date", "Actual Start",
             "Actual Complete", "% Complete", "Billable?", "Amount to Bill", "Billed?",
             "Date Billed", "Notes"]
        ]

        worksheet.update('A1', header_data)

        # Format
        worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
        worksheet.format('A4:L4', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
        worksheet.freeze(rows=4)

        print(f"  ✅ Created: {sheet_name}")

    def _create_invoice_tracker(self, spreadsheet, project_number):
        """Create Invoice Tracker"""
        sheet_name = f"{project_number} - Invoices"

        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)

        # Header
        header_data = [
            ["INVOICE TRACKER (Expenses)"],
            [f"Project: {project_number}"],
            [""],
            ["Vendor", "Invoice #", "Invoice Date", "Amount", "Due Date", "Date Paid",
             "Check #", "Related PO #", "Category", "Notes"]
        ]

        worksheet.update('A1', header_data)

        # Format
        worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
        worksheet.format('A4:J4', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
        worksheet.freeze(rows=4)

        print(f"  ✅ Created: {sheet_name}")

    def create_company_dashboard(self, spreadsheet_url):
        """Create company-wide cash flow dashboard"""

        print(f"\n{'='*60}")
        print(f"💰 Creating Company Cash Flow Dashboard")
        print(f"{'='*60}\n")

        try:
            spreadsheet = self.client.open_by_url(spreadsheet_url)

            sheet_name = "Company Dashboard"

            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                worksheet.clear()
            except:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=50, cols=10, index=0)

            # Get current and next 2 months
            from dateutil.relativedelta import relativedelta
            now = datetime.now()
            month1 = now.strftime("%B %Y")
            month2 = (now + relativedelta(months=1)).strftime("%B %Y")
            month3 = (now + relativedelta(months=2)).strftime("%B %Y")

            # Dashboard header
            header_data = [
                ["COMPANY CASH FLOW DASHBOARD"],
                [f"Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}"],
                [""],
                ["SUMMARY"],
                ["Total Active Projects:", "=COUNTA(A10:A100)"],  # Formula placeholder
                ["Total Contract Value:", "=SUM(B10:B100)"],
                [""],
                ["MONTHLY CASH FLOW FORECAST"],
                ["Project", "Total Value", month1, month2, month3, "Status"],
                # Data rows will be populated by pulling from project SOV sheets
            ]

            worksheet.update('A1', header_data)

            # Format
            worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 16}})
            worksheet.format('A4', {'textFormat': {'bold': True, 'fontSize': 14}})
            worksheet.format('A8', {'textFormat': {'bold': True, 'fontSize': 14}})
            worksheet.format('A9:F9', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
            })
            worksheet.freeze(rows=9)

            print(f"  ✅ Created: {sheet_name}")
            print(f"\n💡 Next: Manually add project summaries or build auto-aggregation")

            return {'success': True}

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 3:
        print("\n" + "="*60)
        print("  Extended Project Tracking Setup")
        print("="*60)
        print("\nUsage:")
        print('  python google_sheets_extended.py dashboard "SHEET_URL"')
        print('  python google_sheets_extended.py project P001 "SHEET_URL"')
        print("\nExamples:")
        print('  # Create company dashboard')
        print('  python scripts\\google_sheets_extended.py dashboard "https://..."')
        print()
        print('  # Create tracking sheets for P001')
        print('  python scripts\\google_sheets_extended.py project P001 "https://..."')
        print("\n" + "="*60 + "\n")
        sys.exit(1)

    mode = sys.argv[1]

    try:
        manager = ExtendedSheetManager()

        if mode == "dashboard":
            sheet_url = sys.argv[2]
            result = manager.create_company_dashboard(sheet_url)

        elif mode == "project":
            project_number = sys.argv[2]
            sheet_url = sys.argv[3]

            # Try to get project name from logs
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

            result = manager.create_project_tracking_sheets(sheet_url, project_number, project_name)

        else:
            print(f"❌ Unknown mode: {mode}")
            sys.exit(1)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
