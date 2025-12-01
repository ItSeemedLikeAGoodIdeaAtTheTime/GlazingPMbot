"""
File Mover Agent
Handles project initialization, file organization, and archiving
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import time
from scripts.logger import ProjectRegistry, AgentActivityLog, EmailIntakeLog


class FileMover:
    """Moves files from Input to Projects folder with proper organization"""

    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / "Input"
        self.projects_dir = self.base_dir / "Projects"
        self.archive_dir = self.base_dir / "Archive" / "Input-Processed"

        # Initialize loggers
        self.project_registry = ProjectRegistry()
        self.activity_log = AgentActivityLog()

        # Ensure directories exist
        self.input_dir.mkdir(exist_ok=True)
        self.projects_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)

    def get_input_projects(self):
        """Scan Input directory for project folders"""
        if not self.input_dir.exists():
            return []

        projects = []
        for item in self.input_dir.iterdir():
            if item.is_dir():
                # Check if folder has PDF or text files (for testing)
                pdf_files = list(item.glob("*.pdf")) + list(item.glob("*.PDF")) + list(item.glob("*.txt"))
                if pdf_files:
                    projects.append({
                        'name': item.name,
                        'path': item,
                        'file_count': len(pdf_files),
                        'files': [f.name for f in pdf_files]
                    })
        return projects

    def initialize_project(self, project_name):
        """Initialize a new project from Input folder"""
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"🚀 Initializing Project: {project_name}")
        print(f"{'='*60}\n")

        # Get next project number
        project_number = self.project_registry.get_next_project_number()
        print(f"📋 Assigned Project Number: {project_number}")

        # Create project folder structure
        project_folder_name = f"{project_number}-{project_name}"
        project_path = self.projects_dir / project_folder_name

        try:
            # Create main project folder
            project_path.mkdir(exist_ok=True)

            # Create subfolders
            subfolders = [
                "01-Contract-Documents",
                "02-Generated-SOV",
                "03-Purchase-Orders",
                "04-Shop-Drawings",
                "05-Correspondence",
                "06-Templates"
            ]

            for folder in subfolders:
                (project_path / folder).mkdir(exist_ok=True)

            print(f"✅ Created project folder structure: {project_folder_name}")

            # Copy files from Input
            input_path = self.input_dir / project_name
            if not input_path.exists():
                raise FileNotFoundError(f"Input folder not found: {input_path}")

            contract_docs_path = project_path / "01-Contract-Documents"
            # Accept PDF or text files (for testing)
            pdf_files = list(input_path.glob("*.pdf")) + list(input_path.glob("*.PDF")) + list(input_path.glob("*.txt"))

            if not pdf_files:
                raise FileNotFoundError(f"No document files found in {input_path}")

            print(f"\n📄 Copying files:")
            copied_files = []
            for pdf_file in pdf_files:
                dest = contract_docs_path / pdf_file.name
                shutil.copy2(pdf_file, dest)
                file_size = pdf_file.stat().st_size / (1024 * 1024)  # MB
                print(f"  ✓ {pdf_file.name} ({file_size:.2f} MB)")
                copied_files.append({
                    'name': pdf_file.name,
                    'size': file_size
                })

            # Verify files copied correctly (include txt for testing)
            copied_count = len(list(contract_docs_path.glob("*.pdf"))) + len(list(contract_docs_path.glob("*.txt")))
            if copied_count != len(pdf_files):
                raise Exception(f"File count mismatch: expected {len(pdf_files)}, got {copied_count}")

            print(f"\n✅ All {len(pdf_files)} files copied successfully")

            # Copy templates if they exist
            templates_input_path = input_path / "Templates"
            templates_dest_path = project_path / "06-Templates"
            template_files = []

            if templates_input_path.exists():
                excel_files = list(templates_input_path.glob("*.xlsx")) + list(templates_input_path.glob("*.xls"))
                if excel_files:
                    print(f"\n📋 Copying templates:")
                    for template_file in excel_files:
                        dest = templates_dest_path / template_file.name
                        shutil.copy2(template_file, dest)
                        file_size = template_file.stat().st_size / 1024  # KB
                        print(f"  ✓ {template_file.name} ({file_size:.1f} KB)")
                        template_files.append({
                            'name': template_file.name,
                            'size_kb': file_size
                        })
                    print(f"✅ {len(template_files)} template(s) copied")

            # Archive original input folder
            archive_path = self.archive_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{project_name}"
            shutil.move(str(input_path), str(archive_path))
            print(f"📦 Input folder archived to: {archive_path.name}")

            # Log to project registry
            self.project_registry.add_project(
                project_number=project_number,
                project_name=project_name,
                folder_path=str(project_path.relative_to(self.base_dir)),
                notes=f"{len(copied_files)} contract documents processed"
            )

            # Log activity
            duration = time.time() - start_time
            file_details = ", ".join([f"{f['name']} ({f['size']:.1f}MB)" for f in copied_files])
            self.activity_log.log_action(
                agent_name="File Mover",
                project_number=project_number,
                action="Project Initialized",
                status="Success",
                details=f"Created {project_folder_name}, copied {len(copied_files)} files: {file_details}",
                duration=round(duration, 2)
            )

            print(f"\n{'='*60}")
            print(f"✅ Project {project_number} initialized successfully!")
            print(f"   Location: {project_path.relative_to(self.base_dir)}")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'project_number': project_number,
                'project_name': project_name,
                'project_path': project_path,
                'files_copied': copied_files,
                'templates_copied': template_files,
                'templates_path': str(templates_dest_path) if template_files else None,
                'duration': duration
            }

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            self.activity_log.log_action(
                agent_name="File Mover",
                project_number=project_number,
                action="Project Initialization Failed",
                status="Error",
                details=str(e),
                duration=round(duration, 2)
            )

            print(f"\n❌ Error initializing project: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_number': project_number,
                'project_name': project_name
            }


def main():
    """CLI interface for file mover"""
    import sys

    mover = FileMover()

    if len(sys.argv) > 1:
        # Project name provided as argument
        project_name = " ".join(sys.argv[1:])
        result = mover.initialize_project(project_name)
        if not result['success']:
            sys.exit(1)
    else:
        # Interactive mode: show available projects
        projects = mover.get_input_projects()

        if not projects:
            print("📭 No projects found in Input/ folder")
            print("\nTo add a project:")
            print("  1. Create a folder in Input/ with your project name")
            print("  2. Add PDF files (contract, specs, drawings, etc.)")
            print("  3. Run this script again")
            sys.exit(0)

        print(f"\n📂 Found {len(projects)} project(s) in Input/:\n")
        for i, proj in enumerate(projects, 1):
            print(f"{i}. {proj['name']}")
            print(f"   Files: {proj['file_count']} PDFs")
            for f in proj['files']:
                print(f"     - {f}")
            print()

        if len(projects) == 1:
            print(f"Processing: {projects[0]['name']}")
            result = mover.initialize_project(projects[0]['name'])
            if not result['success']:
                sys.exit(1)
        else:
            print("Multiple projects found. Specify which to process:")
            print(f"  python scripts/file_mover.py \"Project Name\"")


if __name__ == "__main__":
    main()
