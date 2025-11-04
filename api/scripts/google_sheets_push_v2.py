"""
Google Sheets Push V2 - Update existing Google Sheet with SOV data
Works by updating a template sheet you create and share with the service account
"""

import json
import os
from pathlib import Path
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from scripts.logger import AgentActivityLog


class GoogleSheetsPusher:
    """Push SOV data to existing Google Sheet"""

    def __init__(self, credentials_path=None):
        """Initialize with Google service account credentials"""
        self.credentials_path = credentials_path or os.environ.get("GOOGLE_SHEETS_CREDENTIALS")

        if not self.credentials_path or not Path(self.credentials_path).exists():
            raise ValueError(
                "Google Sheets credentials not found. "
                "Set GOOGLE_SHEETS_CREDENTIALS environment variable or pass credentials_path"
            )

        # Define the required scopes
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]

        # Authenticate
        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )

        self.client = gspread.authorize(creds)
        self.activity_log = AgentActivityLog()

    def get_service_account_email(self):
        """Get the service account email for sharing instructions"""
        with open(self.credentials_path, 'r') as f:
            creds_data = json.load(f)
            return creds_data.get('client_email')

    def update_sov_spreadsheet(self, spreadsheet_url, project_number, sov_data):
        """Update an existing Google Sheet with SOV data - creates new tab for each project"""

        print(f"\n{'='*60}")
        print(f"📊 Updating Google Sheet with {project_number} SOV")
        print(f"{'='*60}\n")

        try:
            # Open the spreadsheet by URL
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            print(f"✅ Opened spreadsheet: {spreadsheet.title}")

            # Extract project info for tab name
            sov = sov_data.get("schedule_of_values", sov_data)
            project_info = sov.get("project_information", {})
            project_name = project_info.get('project_name', 'Unknown Project')[:30]  # Limit length

            # Create or get worksheet for this project
            sheet_name = f"{project_number} - SOV"

            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"✅ Found existing sheet: {sheet_name}")
                worksheet.clear()  # Clear existing content
            except:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
                print(f"✅ Created new sheet: {sheet_name}")

            # Extract project info (already extracted above)
            project_info = sov.get("project_information", {})
            line_items = sov.get("line_items", [])
            summary = sov.get("summary", {})

            # Format header section
            self._format_header(worksheet, project_info, project_number)

            # Add SOV line items
            self._add_line_items(worksheet, line_items)

            # Add summary section
            self._add_summary(worksheet, summary, len(line_items))

            # Format the sheet
            self._apply_formatting(worksheet, len(line_items))

            # Log activity
            self.activity_log.log_action(
                agent_name="Google Sheets Pusher",
                project_number=project_number,
                action="SOV Updated in Google Sheets",
                status="Success",
                details=f"Sheet URL: {spreadsheet.url}"
            )

            print(f"\n{'='*60}")
            print(f"✅ Google Sheet updated successfully!")
            print(f"   URL: {spreadsheet.url}")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'spreadsheet_id': spreadsheet.id,
                'url': spreadsheet.url,
                'title': spreadsheet.title
            }

        except gspread.exceptions.SpreadsheetNotFound:
            print(f"\n❌ Error: Spreadsheet not found or not accessible")
            print(f"\nMake sure you:")
            print(f"1. Created a Google Sheet")
            print(f"2. Shared it with: {self.get_service_account_email()}")
            print(f"   (Give 'Editor' access)")
            return {'success': False, 'error': 'Spreadsheet not found'}

        except Exception as e:
            self.activity_log.log_action(
                agent_name="Google Sheets Pusher",
                project_number=project_number,
                action="SOV Upload Failed",
                status="Error",
                details=str(e)
            )

            print(f"\n❌ Error updating Google Sheet: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_header(self, worksheet, project_info, project_number):
        """Format the header section"""
        # Project information
        header_data = [
            ["SCHEDULE OF VALUES"],
            [""],
            ["Project Number:", project_number],
            ["Project Name:", project_info.get('project_name', 'N/A')],
            ["Contract Number:", project_info.get('contract_number', 'N/A')],
            ["Total Contract Value:", project_info.get('total_contract_value', 'N/A')],
            ["Retention:", project_info.get('retention_percentage', '5%')],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            [""],
            [""]  # Spacer before line items
        ]

        worksheet.update('A1', header_data)

    def _add_line_items(self, worksheet, line_items):
        """Add SOV line items with monthly billing columns"""
        from dateutil import parser
        from dateutil.relativedelta import relativedelta

        # Parse all billing dates and find date range
        billing_dates = []
        for item in line_items:
            date_str = item.get('estimated_billing_date', '')
            if date_str and date_str != 'Distributed':
                try:
                    date_obj = parser.parse(date_str)
                    billing_dates.append(date_obj)
                except:
                    pass

        if not billing_dates:
            # Fallback if no dates found
            start_date = datetime.now()
            end_date = start_date + relativedelta(months=3)
        else:
            start_date = min(billing_dates)
            end_date = max(billing_dates) + relativedelta(months=1)  # Plus one month

        # Generate month columns
        months = []
        current = start_date.replace(day=1)
        end = end_date.replace(day=1)

        while current <= end:
            months.append(current.strftime("%b %Y"))
            current += relativedelta(months=1)

        # Column headers (starting at row 11)
        headers = ["Item #", "Description", "Total Amount", "% Contract"] + months

        worksheet.update('A11', [headers])

        # Line item data
        start_row = 12
        rows_data = []

        for item in line_items:
            # Parse total amount
            total_str = item.get('total_amount', '$0')
            try:
                total_val = float(total_str.replace('$', '').replace(',', ''))
            except:
                total_val = 0

            # Start row with basic info
            row = [
                item.get('item_number', ''),
                item.get('description', ''),
                item.get('total_amount', ''),
                item.get('percentage_of_contract', '')
            ]

            # Add monthly billing amounts
            item_date_str = item.get('estimated_billing_date', '')

            for month in months:
                if item_date_str == 'Distributed':
                    # Distribute evenly across all months
                    monthly_amount = total_val / len(months)
                    row.append(f"${monthly_amount:,.2f}")
                elif item_date_str:
                    try:
                        item_date = parser.parse(item_date_str)
                        month_formatted = item_date.strftime("%b %Y")

                        if month == month_formatted:
                            row.append(item.get('total_amount', ''))
                        else:
                            row.append('')
                    except:
                        row.append('')
                else:
                    row.append('')

            rows_data.append(row)

        if rows_data:
            worksheet.update(f'A{start_row}', rows_data)

        print(f"✅ Added {len(line_items)} line items across {len(months)} months")

    def _add_summary(self, worksheet, summary, line_item_count):
        """Add summary section"""
        summary_start_row = 12 + line_item_count + 2

        summary_data = [
            [""],
            ["SUMMARY"],
            ["Total Line Items:", summary.get('total_line_items', '')],
            ["Retention Amount:", summary.get('retention_amount', '')],
            ["Net Payment:", summary.get('net_final_payment', '')],
            [""],
            ["Early Billing %:", summary.get('early_billing_percentage', '')],
            ["Early Billing $:", summary.get('early_billing_amount', '')]
        ]

        worksheet.update(f'A{summary_start_row}', summary_data)
        print(f"✅ Added summary section")

    def _apply_formatting(self, worksheet, line_item_count):
        """Apply formatting to the sheet"""
        try:
            # Bold headers
            worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
            worksheet.format('A11:J11', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })

            # Freeze header rows
            worksheet.freeze(rows=11)

            print(f"✅ Applied formatting")
        except Exception as e:
            print(f"⚠️  Warning: Could not apply all formatting: {e}")


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 3:
        print("\n" + "="*60)
        print("  Google Sheets SOV Updater")
        print("="*60)
        print("\nUsage: python google_sheets_push_v2.py <project_number> <sheet_url>")
        print("\nExample:")
        print('  python scripts\\google_sheets_push_v2.py P001 "https://docs.google.com/spreadsheets/d/..."')
        print("\n" + "="*60)
        print("  SETUP INSTRUCTIONS")
        print("="*60)

        try:
            pusher = GoogleSheetsPusher()
            service_email = pusher.get_service_account_email()

            print("\n1. Create a new Google Sheet (any name)")
            print("2. Click 'Share' button")
            print(f"3. Share with this email: {service_email}")
            print("4. Give 'Editor' access")
            print("5. Copy the sheet URL")
            print("6. Run this script with the URL\n")
        except:
            print("\nCould not load credentials. Make sure GOOGLE_SHEETS_CREDENTIALS is set.\n")

        sys.exit(1)

    project_number = sys.argv[1]
    spreadsheet_url = sys.argv[2]

    # Load SOV data
    sov_file = Path("Output/Draft_SOV") / f"{project_number}_SOV.json"

    if not sov_file.exists():
        print(f"❌ SOV file not found: {sov_file}")
        print(f"\nGenerate SOV first:")
        print(f"  python scripts/sov_generator.py {project_number}")
        sys.exit(1)

    with open(sov_file, 'r', encoding='utf-8') as f:
        sov_data = json.load(f)

    try:
        pusher = GoogleSheetsPusher()
        result = pusher.update_sov_spreadsheet(spreadsheet_url, project_number, sov_data)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSet up Google Sheets credentials:")
        print("  1. Create service account: https://console.cloud.google.com/")
        print("  2. Download credentials JSON")
        print("  3. Set environment variable:")
        print('     Windows: $env:GOOGLE_SHEETS_CREDENTIALS="path\\to\\credentials.json"')
        sys.exit(1)


if __name__ == "__main__":
    main()
