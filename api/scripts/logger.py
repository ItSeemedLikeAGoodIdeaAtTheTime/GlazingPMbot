"""
Logging utilities for Glazing PM AI
Handles CSV-based logging for all agents
"""

import csv
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Base logger class for CSV logging"""

    def __init__(self, log_dir="Logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

    def _ensure_file_exists(self, filename, headers):
        """Create log file with headers if it doesn't exist"""
        filepath = self.log_dir / filename
        if not filepath.exists():
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
        return filepath

    def _append_row(self, filename, row_data):
        """Append a row to the log file"""
        filepath = self.log_dir / filename
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row_data)


class ProjectRegistry(Logger):
    """Logs all projects and their metadata"""

    HEADERS = [
        'Project_Number', 'Project_Name', 'Created_Date', 'Created_By',
        'Drive_Folder_Path', 'Status', 'Contract_Value', 'Spec_Sections',
        'Current_Phase', 'Notes'
    ]

    def __init__(self):
        super().__init__()
        self.filename = "project_registry.csv"
        self.filepath = self._ensure_file_exists(self.filename, self.HEADERS)

    def get_next_project_number(self):
        """Get the next available project number"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                project_numbers = [row['Project_Number'] for row in reader if row['Project_Number'].startswith('P')]
                if not project_numbers:
                    return "P001"

                # Extract numeric part and find max
                nums = [int(pn[1:]) for pn in project_numbers]
                next_num = max(nums) + 1
                return f"P{next_num:03d}"
        except Exception as e:
            print(f"Error getting next project number: {e}")
            return "P001"

    def add_project(self, project_number, project_name, folder_path, created_by="PM",
                    contract_value="", spec_sections="", notes=""):
        """Add a new project to the registry"""
        row = [
            project_number,
            project_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            created_by,
            folder_path,
            "Initializing",
            contract_value,
            spec_sections,
            "Project Created",
            notes
        ]
        self._append_row(self.filename, row)
        print(f"✅ Project {project_number} logged to registry")
        return project_number

    def update_project_status(self, project_number, status, phase="", contract_value="", spec_sections=""):
        """Update project status (reads all, rewrites with update)"""
        # For MVP, we'll just append a note. Full update can be added later if needed.
        note = f"Status updated to {status}"
        if phase:
            note += f", Phase: {phase}"
        if contract_value:
            note += f", Value: {contract_value}"
        if spec_sections:
            note += f", Specs: {spec_sections}"

        # Simple implementation: log status changes to activity log
        activity = AgentActivityLog()
        activity.log_action("Project Registry", project_number, f"Status Update: {status}", "Success", note)


class AgentActivityLog(Logger):
    """Logs all agent actions"""

    HEADERS = [
        'Timestamp', 'Agent_Name', 'Project_Number', 'Action_Taken',
        'Status', 'Details', 'Duration_Seconds'
    ]

    def __init__(self):
        super().__init__()
        self.filename = "agent_activity.csv"
        self._ensure_file_exists(self.filename, self.HEADERS)

    def log_action(self, agent_name, project_number, action, status, details="", duration=0):
        """Log an agent action"""
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            agent_name,
            project_number,
            action,
            status,
            details,
            duration
        ]
        self._append_row(self.filename, row)


class EmailIntakeLog(Logger):
    """Logs email intake (for future email integration)"""

    HEADERS = [
        'Timestamp', 'Email_From', 'Email_Subject', 'Email_Body',
        'AI_Classification', 'Project_Number', 'Project_Name',
        'Agent_Assigned', 'Status', 'AI_Response_Sent', 'Notes'
    ]

    def __init__(self):
        super().__init__()
        self.filename = "email_intake.csv"
        self._ensure_file_exists(self.filename, self.HEADERS)

    def log_email(self, email_from, subject, body, classification="Manual",
                  project_number="", project_name="", agent="File Mover", status="Assigned"):
        """Log an incoming email (or manual trigger)"""
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            email_from,
            subject,
            body[:500],  # Truncate long bodies
            classification,
            project_number,
            project_name,
            agent,
            status,
            "",  # AI response sent
            ""   # Notes
        ]
        self._append_row(self.filename, row)
        print(f"📧 Email logged: {subject}")


if __name__ == "__main__":
    # Test the loggers
    print("Testing loggers...")

    registry = ProjectRegistry()
    next_num = registry.get_next_project_number()
    print(f"Next project number: {next_num}")

    registry.add_project(
        project_number=next_num,
        project_name="Test Project",
        folder_path="/Projects/P001-Test",
        notes="Testing logger system"
    )

    activity = AgentActivityLog()
    activity.log_action(
        agent_name="Test Agent",
        project_number=next_num,
        action="Test Action",
        status="Success",
        details="This is a test"
    )

    email_log = EmailIntakeLog()
    email_log.log_email(
        email_from="test@example.com",
        subject="Test Email",
        body="This is a test email",
        project_name="Test Project"
    )

    print("\n✅ All loggers initialized and tested!")
    print(f"Check the Logs/ directory for CSV files")
