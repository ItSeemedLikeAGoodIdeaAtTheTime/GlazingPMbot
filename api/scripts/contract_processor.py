"""
Contract Processor Agent
Extracts contract details using Claude API and generates reports
"""

import os
import json
from pathlib import Path
from datetime import datetime
import time
from anthropic import Anthropic
from PyPDF2 import PdfReader
from scripts.logger import AgentActivityLog, ProjectRegistry


class ContractProcessor:
    """Processes contract documents and extracts key information"""

    def __init__(self, api_key=None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in environment or pass as parameter.")

        self.client = Anthropic(api_key=self.api_key)
        self.activity_log = AgentActivityLog()
        self.project_registry = ProjectRegistry()

    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file or text file"""
        try:
            # Handle text files (for testing)
            if pdf_path.suffix.lower() == '.txt':
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    return f.read()

            # Handle PDF files
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"⚠️  Error reading {pdf_path.name}: {e}")
            return ""

    def analyze_contract_documents(self, project_path, project_number):
        """Analyze all contract documents in a project folder"""
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"📄 Processing Contract Documents: {project_number}")
        print(f"{'='*60}\n")

        contract_docs_path = Path(project_path) / "01-Contract-Documents"

        if not contract_docs_path.exists():
            raise FileNotFoundError(f"Contract documents folder not found: {contract_docs_path}")

        # Get all PDF or text files (for testing)
        pdf_files = list(contract_docs_path.glob("*.pdf")) + list(contract_docs_path.glob("*.PDF")) + list(contract_docs_path.glob("*.txt"))

        if not pdf_files:
            raise FileNotFoundError(f"No document files found in {contract_docs_path}")

        print(f"Found {len(pdf_files)} document(s):")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")

        # Extract text from all PDFs
        print(f"\n📖 Extracting text from PDFs...")
        documents = {}
        for pdf_file in pdf_files:
            print(f"  Reading: {pdf_file.name}...", end=" ")
            text = self.extract_text_from_pdf(pdf_file)
            documents[pdf_file.name] = text
            word_count = len(text.split())
            print(f"✓ ({word_count:,} words)")

        # Combine all document text
        combined_text = "\n\n=== DOCUMENT SEPARATOR ===\n\n".join(
            [f"DOCUMENT: {name}\n\n{text}" for name, text in documents.items()]
        )

        # Prepare prompt for Claude
        print(f"\n🤖 Analyzing with Claude API...")

        system_prompt = """You are an expert commercial glazing project manager analyzing contract documents.

Extract and structure the following information from the contract documents provided:

1. **Project Information**
   - Project name
   - Project location/address
   - Client/owner name
   - General contractor (if mentioned)
   - Contract number

2. **Financial Details**
   - Total contract value
   - Payment terms
   - Retention percentage
   - Billing schedule or milestones

3. **Scope of Work**
   - Specification sections included (e.g., 088000 Glazing)
   - Types of work (curtain wall, storefront, doors, etc.)
   - Key materials mentioned (glass types, framing, hardware)
   - Approximate quantities (if available)

4. **Schedule**
   - Project start date
   - Substantial completion date
   - Final completion date
   - Key milestones

5. **Key Requirements**
   - Submittal requirements
   - Shop drawing requirements
   - Testing requirements
   - Warranty requirements

6. **Risk Factors & Notes**
   - Unusual contract terms
   - Tight deadlines
   - Complex coordination requirements
   - Special materials or finishes

Return your analysis as a structured JSON object with these sections."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Please analyze these contract documents:\n\n{combined_text[:100000]}"  # Limit to ~100k chars
                }]
            )

            analysis = response.content[0].text
            print(f"✅ Analysis complete")

            # Try to parse as JSON, fallback to plain text
            try:
                analysis_json = json.loads(analysis)
            except json.JSONDecodeError:
                print("⚠️  Response is not JSON, using plain text format")
                analysis_json = {"analysis": analysis}

            # Save analysis report (use absolute path to avoid Windows issues)
            reports_dir = Path.cwd() / "Output" / "Reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            report_filename = f"{project_number}_contract_analysis.json"
            report_path = reports_dir / report_filename

            with open(str(report_path), 'w', encoding='utf-8') as f:
                json.dump(analysis_json, f, indent=2)

            # Also save markdown version
            md_filename = f"{project_number}_contract_analysis.md"
            md_path = reports_dir / md_filename

            with open(str(md_path), 'w', encoding='utf-8') as f:
                f.write(f"# Contract Analysis: {project_number}\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                if isinstance(analysis_json, dict) and "analysis" not in analysis_json:
                    # Structured JSON
                    for section, content in analysis_json.items():
                        f.write(f"## {section.replace('_', ' ').title()}\n\n")
                        if isinstance(content, dict):
                            for key, value in content.items():
                                f.write(f"**{key.replace('_', ' ').title()}:** {value}\n\n")
                        elif isinstance(content, list):
                            for item in content:
                                f.write(f"- {item}\n")
                            f.write("\n")
                        else:
                            f.write(f"{content}\n\n")
                else:
                    # Plain text analysis
                    f.write(analysis if isinstance(analysis_json, str) else analysis_json.get("analysis", analysis))

            print(f"\n📊 Reports saved:")
            print(f"   JSON: {report_path.relative_to(Path.cwd())}")
            print(f"   Markdown: {md_path.relative_to(Path.cwd())}")

            # Extract key details for logging
            contract_value = ""
            spec_sections = ""

            if isinstance(analysis_json, dict):
                # Try to extract common fields
                financial = analysis_json.get("financial_details", {}) or analysis_json.get("Financial Details", {})
                if isinstance(financial, dict):
                    contract_value = str(financial.get("total_contract_value", "") or financial.get("Total contract value", ""))

                scope = analysis_json.get("scope_of_work", {}) or analysis_json.get("Scope of Work", {})
                if isinstance(scope, dict):
                    specs = scope.get("specification_sections_included", []) or scope.get("Specification sections included", [])
                    if isinstance(specs, list):
                        spec_sections = ", ".join(specs)
                    elif isinstance(specs, str):
                        spec_sections = specs

            # Log activity
            duration = time.time() - start_time
            self.activity_log.log_action(
                agent_name="Contract Processor",
                project_number=project_number,
                action="Contract Analysis Complete",
                status="Success",
                details=f"Analyzed {len(pdf_files)} documents, generated report",
                duration=round(duration, 2)
            )

            # Update project registry
            self.project_registry.update_project_status(
                project_number=project_number,
                status="Contract Analyzed",
                phase="Analysis Complete",
                contract_value=contract_value,
                spec_sections=spec_sections
            )

            print(f"\n{'='*60}")
            print(f"✅ Contract processing complete!")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'project_number': project_number,
                'analysis': analysis_json,
                'report_path': str(report_path),
                'markdown_path': str(md_path),
                'contract_value': contract_value,
                'spec_sections': spec_sections,
                'duration': duration
            }

        except Exception as e:
            duration = time.time() - start_time
            self.activity_log.log_action(
                agent_name="Contract Processor",
                project_number=project_number,
                action="Contract Analysis Failed",
                status="Error",
                details=str(e),
                duration=round(duration, 2)
            )

            print(f"\n❌ Error during contract analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_number': project_number,
                'duration': duration
            }


def main():
    """CLI interface for contract processor"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python contract_processor.py <project_number>")
        print("\nExample: python contract_processor.py P001")
        sys.exit(1)

    project_number = sys.argv[1]

    # Find project folder
    projects_dir = Path("Projects")
    project_folders = list(projects_dir.glob(f"{project_number}-*"))

    if not project_folders:
        print(f"❌ No project found with number: {project_number}")
        sys.exit(1)

    project_path = project_folders[0]

    try:
        processor = ContractProcessor()
        result = processor.analyze_contract_documents(project_path, project_number)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSet your API key:")
        print('  Windows: set ANTHROPIC_API_KEY=your-key-here')
        print('  Mac/Linux: export ANTHROPIC_API_KEY=your-key-here')
        sys.exit(1)


if __name__ == "__main__":
    main()
