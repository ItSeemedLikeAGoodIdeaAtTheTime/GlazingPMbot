"""
Schedule of Values (SOV) Generator
Creates SOV from contract analysis using Claude API
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
import time
from anthropic import Anthropic
from logger import AgentActivityLog, ProjectRegistry


class SOVGenerator:
    """Generates Schedule of Values from contract analysis"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = Anthropic(api_key=self.api_key)
        self.activity_log = AgentActivityLog()
        self.project_registry = ProjectRegistry()

    def generate_sov(self, project_number, contract_analysis):
        """Generate SOV from contract analysis"""
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"💰 Generating Schedule of Values: {project_number}")
        print(f"{'='*60}\n")

        # Load SOV generator prompt
        prompt_path = Path("Claude_Prompts/sov_generator.md")
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                # Extract system prompt section
                content = f.read()
                system_prompt = content.split("## System Prompt")[1].split("##")[0].strip()
        else:
            # Fallback system prompt
            system_prompt = """You are an expert commercial glazing project manager creating a Schedule of Values (SOV).

Generate a detailed SOV with line items for:
1. General Conditions/Submittals (10-15%)
2. Materials broken down by type (50-60%)
3. Installation Labor by phase (25-35%)
4. Final Retention (5%)

Return as JSON with project_info, line_items array, and summary totals."""

        # Prepare user message with contract analysis
        user_message = f"""Based on the following contract analysis, generate a detailed Schedule of Values:

{json.dumps(contract_analysis, indent=2)}

Please create a comprehensive SOV that:
- Breaks down the scope into billable line items
- Optimizes for early billing opportunities
- Includes clear billing triggers for each item
- Totals exactly to the contract value
- Follows industry best practices for glazing projects

Return the result as a JSON object."""

        try:
            print("🤖 Calling Claude API to generate SOV...")

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_message
                }]
            )

            sov_text = response.content[0].text
            print("✅ SOV generated")

            # Parse JSON response
            try:
                # Try to extract JSON from response (may be wrapped in markdown)
                if "```json" in sov_text:
                    json_start = sov_text.find("```json") + 7
                    json_end = sov_text.find("```", json_start)
                    sov_text = sov_text[json_start:json_end].strip()
                elif "```" in sov_text:
                    json_start = sov_text.find("```") + 3
                    json_end = sov_text.find("```", json_start)
                    sov_text = sov_text[json_start:json_end].strip()

                sov_data = json.loads(sov_text)
            except json.JSONDecodeError as e:
                print(f"⚠️  Could not parse JSON response: {e}")
                print("Saving raw response...")
                sov_data = {
                    "error": "Failed to parse JSON",
                    "raw_response": sov_text
                }

            # Save JSON version
            output_dir = Path("Output") / "Draft_SOV"
            output_dir.mkdir(parents=True, exist_ok=True)

            json_filename = f"{project_number}_SOV.json"
            json_path = output_dir / json_filename

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(sov_data, f, indent=2)

            print(f"📄 JSON saved: {json_path}")

            # Generate CSV version
            if "line_items" in sov_data:
                csv_filename = f"{project_number}_SOV.csv"
                csv_path = output_dir / csv_filename

                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)

                    # Header
                    writer.writerow([
                        "Item #",
                        "Description",
                        "Spec Section",
                        "Category",
                        "Scheduled Value",
                        "Billing Strategy",
                        "Billing Trigger"
                    ])

                    # Line items
                    for item in sov_data["line_items"]:
                        writer.writerow([
                            item.get("item_number", ""),
                            item.get("description", ""),
                            item.get("spec_section", ""),
                            item.get("category", ""),
                            item.get("scheduled_value", ""),
                            item.get("billing_strategy", ""),
                            item.get("billing_trigger", "")
                        ])

                    # Summary row
                    if "summary" in sov_data:
                        summary = sov_data["summary"]
                        writer.writerow([])
                        writer.writerow(["SUMMARY"])
                        writer.writerow(["General Conditions", "", "", "", summary.get("total_general_conditions", "")])
                        writer.writerow(["Materials", "", "", "", summary.get("total_materials", "")])
                        writer.writerow(["Labor", "", "", "", summary.get("total_labor", "")])
                        writer.writerow(["Retention", "", "", "", summary.get("retention_amount", "")])

                print(f"📊 CSV saved: {csv_path}")

                # Print summary
                print(f"\n📋 SOV Summary:")
                if "project_info" in sov_data:
                    info = sov_data["project_info"]
                    print(f"   Project: {info.get('project_name', 'N/A')}")
                    print(f"   Total Value: ${info.get('total_contract_value', 'N/A'):,}" if isinstance(info.get('total_contract_value'), (int, float)) else f"   Total Value: {info.get('total_contract_value', 'N/A')}")

                print(f"   Line Items: {len(sov_data['line_items'])}")

                if "summary" in sov_data:
                    summary = sov_data["summary"]
                    print(f"\n   Breakdown:")
                    for key, value in summary.items():
                        if isinstance(value, (int, float)):
                            print(f"     {key.replace('_', ' ').title()}: ${value:,.2f}")
                        else:
                            print(f"     {key.replace('_', ' ').title()}: {value}")

            else:
                print("⚠️  No line items found in SOV response")
                csv_path = None

            # Log activity
            duration = time.time() - start_time
            line_item_count = len(sov_data.get("line_items", []))
            self.activity_log.log_action(
                agent_name="SOV Generator",
                project_number=project_number,
                action="SOV Generated",
                status="Success",
                details=f"Created {line_item_count} line items",
                duration=round(duration, 2)
            )

            # Update project registry
            self.project_registry.update_project_status(
                project_number=project_number,
                status="SOV Generated",
                phase="Ready for Review"
            )

            print(f"\n{'='*60}")
            print(f"✅ SOV generation complete!")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"{'='*60}\n")

            return {
                'success': True,
                'project_number': project_number,
                'sov_data': sov_data,
                'json_path': str(json_path),
                'csv_path': str(csv_path) if csv_path else None,
                'line_item_count': line_item_count,
                'duration': duration
            }

        except Exception as e:
            duration = time.time() - start_time
            self.activity_log.log_action(
                agent_name="SOV Generator",
                project_number=project_number,
                action="SOV Generation Failed",
                status="Error",
                details=str(e),
                duration=round(duration, 2)
            )

            print(f"\n❌ Error generating SOV: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_number': project_number,
                'duration': duration
            }


def main():
    """CLI interface for SOV generator"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sov_generator.py <project_number>")
        print("\nExample: python sov_generator.py P001")
        sys.exit(1)

    project_number = sys.argv[1]

    # Load contract analysis
    reports_dir = Path("Output/Reports")
    analysis_file = reports_dir / f"{project_number}_contract_analysis.json"

    if not analysis_file.exists():
        print(f"❌ Contract analysis not found: {analysis_file}")
        print("\nRun contract_processor.py first:")
        print(f"  python scripts/contract_processor.py {project_number}")
        sys.exit(1)

    with open(analysis_file, 'r', encoding='utf-8') as f:
        contract_analysis = json.load(f)

    try:
        generator = SOVGenerator()
        result = generator.generate_sov(project_number, contract_analysis)

        if not result['success']:
            sys.exit(1)

    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSet your API key:")
        print('  Windows: set ANTHROPIC_API_KEY=your-key-here')
        sys.exit(1)


if __name__ == "__main__":
    main()
