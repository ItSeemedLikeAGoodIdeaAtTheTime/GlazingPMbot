"""
Google Sheets Push - Upload SOV to Google Sheets
Creates and formats a Schedule of Values spreadsheet
"""

import json
import os
from pathlib import Path
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from logger import AgentActivityLog


class GoogleSheetsPusher:
    """Push SOV data to Google Sheets"""

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
            'https://www.googleapis.com/auth/drive'
        ]

        # Authenticate
        creds = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )

        self.client = gspread.authorize(creds)
        self.activity_log = AgentActivityLog()

    def create_sov_spreadsheet(self, project_number, sov_data, share_with=None):
        """Create a new Google Sheet with SOV data"""

        print(f"\n{'='*60}")
        print(f"📊 Creating Google Sheet: {project_number} SOV")
        print(f"{'='*60}\n")

        # Extract project info
        sov = sov_data.get("schedule_of_values", sov_data)
        project_info = sov.get("project_information", {})
        line_items = sov.get("line_items", [])
        summary = sov.get("summary", {})

        # Create spreadsheet
        sheet_title = f"{project_number} - {project_info.get('project_name', 'Schedule of Values')}"
        print(f"Creating spreadsheet: {sheet_title[:50]}...")

        try:
            spreadsheet = self.client.create(sheet_title)
            worksheet = spreadsheet.sheet1
            worksheet.update_title("Schedule of Values")

            print(f"✅ Spreadsheet created: {spreadsheet.url}")

            # Format header section
            self._format_header(worksheet, project_info, project_number)

            # Add SOV line items
            self._add_line_items(worksheet, line_items)

            # Add summary section
            self._add_summary(worksheet, summary, len(line_items))

            # Format the sheet
            self._apply_formatting(worksheet, len(line_items))

            # Share with user if email provided
            if share_with:
                spreadsheet.share(share_with, perm_type='user', role='writer')
                print(f"✅ Shared with: {share_with}")

            # Log activity
            self.activity_log.log_action(
                agent_name="Google Sheets Pusher",
                project_number=project_number,
                action="SOV Uploaded to Google Sheets",
                status="Success",
                details=f"Sheet URL: {spreadsheet.url}"
            )

            print(f"\n{'='*60}")
            print(f"✅ Google Sheet created successfully!")
            print(f"   URL: {spreadsheet.url}")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'spreadsheet_id': spreadsheet.id,
                'url': spreadsheet.url,
                'title': sheet_title
            }

        except Exception as e:
            self.activity_log.log_action(
                agent_name="Google Sheets Pusher",
                project_number=project_number,
                action="SOV Upload Failed",
                status="Error",
                details=str(e)
            )

            print(f"\n❌ Error creating Google Sheet: {e}")
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
            [f"Project Number:", project_number],
            [f"Project Name:", project_info.get('project_name', 'N/A')],
            [f"Contract Number:", project_info.get('contract_number', 'N/A')],
            [f"Total Contract Value:", project_info.get('total_contract_value', 'N/A')],
            [f"Retention:", project_info.get('retention_percentage', '5%')],
            [f"Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            [""],
            [""]  # Spacer before line items
        ]

        worksheet.update('A1', header_data)

    def _add_line_items(self, worksheet, line_items):
        """Add SOV line items"""
        # Column headers (starting at row 11)
        headers = [
            "Item #",
            "Description",
            "Spec Section",
            "Unit",
            "Qty",
            "Unit Price",
            "Total Amount",
            "% of Contract",
            "Billing Trigger",
            "Est. Billing Date"
        ]

        worksheet.update('A11', [headers])

        # Line item data
        start_row = 12
        rows_data = []

        for item in line_items:
            row = [
                item.get('item_number', ''),
                item.get('description', ''),
                item.get('specification_section', ''),
                item.get('unit', 'LS'),
                item.get('quantity', 1),
                item.get('unit_price', ''),
                item.get('total_amount', ''),
                item.get('percentage_of_contract', ''),
                item.get('billing_trigger', ''),
                item.get('estimated_billing_date', '')
            ]
            rows_data.append(row)

        if rows_data:
            worksheet.update(f'A{start_row}', rows_data)

        print(f"✅ Added {len(line_items)} line items")

    def _add_summary(self, worksheet, summary, line_item_count):
        """Add summary section"""
        summary_start_row = 12 + line_item_count + 2

        summary_data = [
            [""],
            ["SUMMARY"],
            [f"Total Line Items:", summary.get('total_line_items', '')],
            [f"Retention Amount:", summary.get('retention_amount', '')],
            [f"Net Payment:", summary.get('net_final_payment', '')],
            [""],
            [f"Early Billing %:", summary.get('early_billing_percentage', '')],
            [f"Early Billing $:", summary.get('early_billing_amount', '')]
        ]

        worksheet.update(f'A{summary_start_row}', summary_data)
        print(f"✅ Added summary section")

    def _apply_formatting(self, worksheet, line_item_count):
        """Apply formatting to the sheet"""
        # Bold headers
        worksheet.format('A1', {'textFormat': {'bold': True, 'fontSize': 14}})
        worksheet.format('A11:J11', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})

        # Column widths
        worksheet.columns_auto_resize(0, 9)

        # Freeze header rows
        worksheet.freeze(rows=11)

        print(f"✅ Applied formatting")


def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python google_sheets_push.py <project_number> [email_to_share]")
        print("\nExample: python google_sheets_push.py P001 user@example.com")
        print("\nNeed Google Sheets credentials:")
        print("  1. Go to: https://console.cloud.google.com/")
        print("  2. Create a service account")
        print("  3. Download JSON credentials")
        print("  4. Set GOOGLE_SHEETS_CREDENTIALS environment variable")
        sys.exit(1)

    project_number = sys.argv[1]
    share_with = sys.argv[2] if len(sys.argv) > 2 else None

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
        result = pusher.create_sov_spreadsheet(project_number, sov_data, share_with)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSet up Google Sheets credentials:")
        print("  1. Create service account: https://console.cloud.google.com/")
        print("  2. Download credentials JSON")
        print("  3. Set environment variable:")
        print('     Windows: set GOOGLE_SHEETS_CREDENTIALS=path\\to\\credentials.json')
        print('     Mac/Linux: export GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json')
        sys.exit(1)


if __name__ == "__main__":
    main()
