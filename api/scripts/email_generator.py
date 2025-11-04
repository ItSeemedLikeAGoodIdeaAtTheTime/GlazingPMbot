"""
Email Generator
Creates draft emails for various project communications
"""

import json
from pathlib import Path
from datetime import datetime


class EmailGenerator:
    """Generates draft emails ready for PM review and sending"""

    def __init__(self):
        self.output_dir = Path("Output/Draft_Emails")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_project_kickoff_email(self, project_number, project_data):
        """Generate internal project kickoff email"""

        template = f"""DRAFT EMAIL - Internal Project Kickoff
================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_number}

TO: [INTERNAL TEAM - Add recipients]
CC: [PROJECT STAKEHOLDERS]
SUBJECT: New Project Kickoff - {project_data.get('project_name', '[PROJECT NAME]')}

Hi Team,

We have a new glazing project starting up. Here are the key details:

PROJECT INFORMATION
-------------------
Project Name: {project_data.get('project_name', '[PROJECT NAME]')}
Project Number: {project_number}
Client: {project_data.get('client_name', '[CLIENT NAME]')}
Contract Value: {project_data.get('contract_value', '[CONTRACT VALUE]')}

SCOPE OF WORK
-------------
{project_data.get('scope_summary', '[SCOPE DETAILS]')}

KEY DATES
---------
Start Date: {project_data.get('start_date', '[START DATE]')}
Substantial Completion: {project_data.get('completion_date', '[COMPLETION DATE]')}

NEXT STEPS
----------
1. Review contract documents in project folder
2. Begin submittal preparation
3. Request vendor quotes for materials
4. Schedule project coordination meeting

Project files are located in: {project_data.get('project_folder', '[FOLDER PATH]')}

Please review and let me know if you have any questions.

Best regards,
[YOUR NAME]
Project Manager

================================================
REVIEW CHECKLIST:
□ Verify all [PLACEHOLDERS] are filled in
□ Add appropriate team member email addresses
□ Confirm project details are accurate
□ Customize next steps as needed
================================================
"""
        filename = f"{project_number}_internal_kickoff.txt"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"  ✓ Internal kickoff email: {filename}")
        return str(filepath)

    def generate_client_sov_submission_email(self, project_number, sov_data):
        """Generate email to client submitting SOV"""

        project_name = sov_data.get('project_info', {}).get('project_name', '[PROJECT NAME]')
        total_value = sov_data.get('project_info', {}).get('total_contract_value', '[CONTRACT VALUE]')

        template = f"""DRAFT EMAIL - SOV Submission to Client
================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_number}

TO: [CLIENT PROJECT MANAGER]
CC: [CLIENT STAKEHOLDERS], [INTERNAL CC]
SUBJECT: Schedule of Values Submission - {project_name}

Dear [CLIENT NAME],

Please find attached the Schedule of Values for the {project_name} glazing package.

PROJECT DETAILS
---------------
Project: {project_name}
Contract Value: ${total_value:,}" if isinstance(total_value, (int, float)) else f"Contract Value: {total_value}
Line Items: {len(sov_data.get('line_items', []))}

The Schedule of Values breaks down our contract scope into the following categories:
- General Conditions & Submittals
- Materials (by component type)
- Installation Labor
- Final Retention (5%)

Each line item includes clear billing triggers and follows industry standard practices for glazing project billing.

NEXT STEPS
----------
1. Please review the attached SOV
2. Let us know if you have any questions or require modifications
3. Upon your approval, we will begin processing based on this billing schedule

We are excited to begin work on this project and look forward to a successful partnership.

Best regards,
[YOUR NAME]
[YOUR TITLE]
[COMPANY NAME]
[PHONE]
[EMAIL]

Attachment: {project_number}_SOV.csv

================================================
REVIEW CHECKLIST:
□ Verify all [PLACEHOLDERS] are filled in
□ Attach the SOV CSV file
□ Confirm total contract value matches contract
□ Add appropriate client contacts
□ Customize messaging to match client relationship
================================================
"""
        filename = f"{project_number}_client_sov_submission.txt"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"  ✓ Client SOV submission email: {filename}")
        return str(filepath)

    def generate_vendor_quote_request_email(self, project_number, project_data, vendor_type="[VENDOR TYPE]"):
        """Generate email to vendor requesting quote"""

        template = f"""DRAFT EMAIL - Vendor Quote Request
================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Project: {project_number}

TO: [VENDOR CONTACT]
CC: [INTERNAL TEAM]
SUBJECT: Quote Request - {project_data.get('project_name', '[PROJECT NAME]')} - {vendor_type}

Hi [VENDOR CONTACT NAME],

We have an upcoming glazing project and would like to request a quote for {vendor_type}.

PROJECT INFORMATION
-------------------
Project: {project_data.get('project_name', '[PROJECT NAME]')}
Location: {project_data.get('location', '[PROJECT LOCATION]')}
Scope: {project_data.get('scope_summary', '[SCOPE SUMMARY]')}

SPECIFICATIONS
--------------
Spec Sections: {project_data.get('spec_sections', '[SPEC SECTIONS]')}

[ADD SPECIFIC PRODUCT REQUIREMENTS FROM SPECIFICATIONS]
[ADD QUANTITIES IF KNOWN]
[ADD SPECIAL REQUIREMENTS OR PREFERENCES]

SCHEDULE
--------
Quote Due Date: [DATE - typically 2 weeks]
Project Start: {project_data.get('start_date', '[START DATE]')}
Required On-Site: [DATE - coordinate with project schedule]

DELIVERABLES REQUESTED
----------------------
1. Itemized pricing breakdown
2. Product data sheets for all proposed materials
3. Lead times for each component
4. Delivery schedule
5. Warranty information
6. References for similar projects

Please let me know if you need any additional information or have questions about the project scope.

We look forward to working with you on this project.

Best regards,
[YOUR NAME]
Project Manager
[COMPANY NAME]
[PHONE]
[EMAIL]

================================================
REVIEW CHECKLIST:
□ Verify all [PLACEHOLDERS] are filled in
□ Attach relevant specification sections
□ Attach drawings if needed for quote
□ Specify clear quote due date
□ Add specific product requirements from specs
□ Confirm vendor contact information
================================================
"""
        filename = f"{project_number}_vendor_quote_request_{vendor_type.replace(' ', '_')}.txt"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"  ✓ Vendor quote request email: {filename}")
        return str(filepath)

    def generate_all_emails(self, project_number, contract_analysis=None, sov_data=None):
        """Generate all standard emails for a project"""

        print(f"\n{'='*60}")
        print(f"📧 Generating Draft Emails: {project_number}")
        print(f"{'='*60}\n")

        generated_emails = []

        # Extract project data from contract analysis
        project_data = {}
        if contract_analysis:
            if "project_information" in contract_analysis:
                info = contract_analysis["project_information"]
            elif "Project Information" in contract_analysis:
                info = contract_analysis["Project Information"]
            else:
                info = {}

            project_data = {
                'project_name': info.get('project_name') or info.get('Project name', '[PROJECT NAME]'),
                'client_name': info.get('client_owner_name') or info.get('Client/owner name', '[CLIENT NAME]'),
                'location': info.get('project_location_address') or info.get('Project location/address', '[LOCATION]'),
                'contract_value': '[CONTRACT VALUE]',
                'scope_summary': '[SCOPE SUMMARY]',
                'start_date': '[START DATE]',
                'completion_date': '[COMPLETION DATE]',
                'spec_sections': '[SPEC SECTIONS]',
                'project_folder': f"Projects/{project_number}-[PROJECT NAME]"
            }

            # Try to extract financial info
            if "financial_details" in contract_analysis:
                fin = contract_analysis["financial_details"]
            elif "Financial Details" in contract_analysis:
                fin = contract_analysis["Financial Details"]
            else:
                fin = {}

            if isinstance(fin, dict):
                project_data['contract_value'] = fin.get('total_contract_value') or fin.get('Total contract value', '[CONTRACT VALUE]')

            # Try to extract scope
            if "scope_of_work" in contract_analysis:
                scope = contract_analysis["scope_of_work"]
            elif "Scope of Work" in contract_analysis:
                scope = contract_analysis["Scope of Work"]
            else:
                scope = {}

            if isinstance(scope, dict):
                specs = scope.get('specification_sections_included') or scope.get('Specification sections included', [])
                if isinstance(specs, list):
                    project_data['spec_sections'] = ", ".join(specs)
                elif isinstance(specs, str):
                    project_data['spec_sections'] = specs

            # Try to extract schedule
            if "schedule" in contract_analysis:
                sched = contract_analysis["schedule"]
            elif "Schedule" in contract_analysis:
                sched = contract_analysis["Schedule"]
            else:
                sched = {}

            if isinstance(sched, dict):
                project_data['start_date'] = sched.get('project_start_date') or sched.get('Project start date', '[START DATE]')
                project_data['completion_date'] = sched.get('substantial_completion_date') or sched.get('Substantial completion date', '[COMPLETION DATE]')

        # Generate emails
        generated_emails.append(self.generate_project_kickoff_email(project_number, project_data))

        if sov_data:
            generated_emails.append(self.generate_client_sov_submission_email(project_number, sov_data))

        # Generate vendor quote request templates for common vendor types
        vendor_types = ["Glass", "Aluminum Framing", "Hardware"]
        for vendor_type in vendor_types:
            generated_emails.append(self.generate_vendor_quote_request_email(project_number, project_data, vendor_type))

        print(f"\n✅ Generated {len(generated_emails)} draft emails")
        print(f"   Location: {self.output_dir.relative_to(Path.cwd())}")
        print(f"\n{'='*60}\n")

        return generated_emails


def main():
    """CLI interface for email generator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python email_generator.py <project_number>")
        print("\nExample: python email_generator.py P001")
        sys.exit(1)

    project_number = sys.argv[1]

    # Load contract analysis if available
    contract_analysis = None
    analysis_file = Path("Output/Reports") / f"{project_number}_contract_analysis.json"
    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            contract_analysis = json.load(f)

    # Load SOV if available
    sov_data = None
    sov_file = Path("Output/Draft_SOV") / f"{project_number}_SOV.json"
    if sov_file.exists():
        with open(sov_file, 'r', encoding='utf-8') as f:
            sov_data = json.load(f)

    generator = EmailGenerator()
    generator.generate_all_emails(project_number, contract_analysis, sov_data)


if __name__ == "__main__":
    main()
