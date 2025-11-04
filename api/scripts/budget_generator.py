#!/usr/bin/env python3
"""
Budget Generator - Internal Cost Code Budget

Generates internal budget with cost codes based on:
1. Scope analysis (what materials/scopes are in project)
2. Contract analysis (quantities, specs, requirements)
3. Cost code structure (rates and categorization)

Output: Detailed internal budget for cost tracking
NOTE: This is separate from client-facing SOV
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class BudgetGenerator:
    """Generates internal cost code budgets"""

    def __init__(self):
        """Initialize with API key and load cost codes"""
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropicAPIkey")
        if not api_key:
            raise ValueError("Anthropic API key not found")

        self.client = Anthropic(api_key=api_key)

        # Load cost codes
        cost_codes_path = Path("cost_codes.json")
        if not cost_codes_path.exists():
            raise FileNotFoundError(f"Cost codes not found: {cost_codes_path}")

        with open(cost_codes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.cost_codes = data['cost_code_structure']

    def generate_budget(self, project_number, contract_analysis, scope_analysis):
        """Generate detailed internal budget"""

        print(f"\n{'='*70}")
        print(f"  BUDGET GENERATION: {project_number}")
        print(f"{'='*70}\n")

        print("[1/4] Analyzing project requirements...")

        # Build budget estimation prompt
        budget_prompt = self._build_budget_prompt(contract_analysis, scope_analysis)

        print("[2/4] Estimating quantities and costs...")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": budget_prompt
            }]
        )

        try:
            response_text = response.content[0].text

            # Extract JSON
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            budget_data = json.loads(response_text)
        except Exception as e:
            print(f"ERROR: Could not parse budget: {e}")
            print(f"\nRaw response:\n{response.content[0].text[:500]}...")
            return {'success': False, 'error': f'Failed to parse budget: {e}'}

        print(f"[OK] Budget estimated with {len(budget_data.get('line_items', []))} line items")

        # Calculate totals
        print("[3/4] Calculating totals...")

        totals = self._calculate_totals(budget_data)
        budget_data['totals'] = totals

        # Save budget
        print("[4/4] Saving budget...")

        output_dir = Path("Output/Budgets")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_file = output_dir / f"{project_number}_internal_budget.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(budget_data, f, indent=2)

        # Save CSV
        csv_file = output_dir / f"{project_number}_internal_budget.csv"
        self._save_budget_csv(budget_data, csv_file)

        # Create readable report
        report_file = output_dir / f"{project_number}_internal_budget.md"
        self._create_budget_report(project_number, budget_data, report_file)

        print(f"\n{'='*70}")
        print(f"  BUDGET GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"\nOutputs:")
        print(f"  JSON: {json_file}")
        print(f"  CSV:  {csv_file}")
        print(f"  Report: {report_file}")
        print(f"\nBudget Summary:")
        print(f"  Line Items: {len(budget_data['line_items'])}")
        print(f"  Labor Total: ${totals['labor_total']:,.2f}")
        print(f"  Materials Total: ${totals['materials_total']:,.2f}")
        print(f"  Indirect Total: ${totals['indirect_total']:,.2f}")
        print(f"  GRAND TOTAL: ${totals['grand_total']:,.2f}")

        return {
            'success': True,
            'budget_data': budget_data,
            'json_file': str(json_file),
            'csv_file': str(csv_file),
            'report_file': str(report_file),
            'totals': totals
        }

    def _build_budget_prompt(self, contract_analysis, scope_analysis):
        """Build prompt for budget estimation"""

        # Get all cost codes in structured format
        cost_code_summary = []
        for category, details in self.cost_codes['categories'].items():
            cost_code_summary.append(f"\n{category} ({details['code_prefix']}):")
            for item in details['line_items']:
                cost_code_summary.append(
                    f"  {item['code']}: {item['name']} @ ${item['typical_rate']}/{item['unit']}"
                )

        prompt = f"""You are a glazing estimator creating an INTERNAL BUDGET for cost tracking.

IMPORTANT: This is NOT the client-facing SOV. This is for internal cost tracking only.

AVAILABLE COST CODES:
{''.join(cost_code_summary)}

CONTRACT ANALYSIS:
{json.dumps(contract_analysis, indent=2)}

SCOPE ANALYSIS:
{json.dumps(scope_analysis, indent=2)}

Your task:
1. Review the project requirements and scopes
2. For each scope, estimate the quantities needed for relevant cost codes
3. Calculate costs using typical rates (you can adjust rates if justified)
4. Include labor, materials, and indirect costs
5. Be thorough - include all categories that apply to this project

ESTIMATION GUIDELINES:
- Labor: Estimate hours based on scope complexity and square footage
  - Glaziers: ~0.5-1.5 hrs/sqft for installation depending on complexity
  - Caulkers: ~0.3-0.8 hrs/lnft for perimeter sealing
  - Shop: ~0.3-0.8 hrs/sqft for fabrication
- Materials: Use actual quantities from contract when available
- Glass: Include all glass types identified (monolithic, IGU, fire-rated, specialty)
- Hardware: Count doors/windows that need hardware
- Sealants: Estimate linear feet of joints
- Indirect: Include drive time, shipping, equipment as applicable

Return JSON with this structure:
{{
  "project_number": "{contract_analysis.get('project_number', 'Unknown')}",
  "line_items": [
    {{
      "cost_code": "L-GLZ-002",
      "description": "Glaziers - Journeyman",
      "quantity": 450,
      "unit": "hour",
      "unit_cost": 65.00,
      "total_cost": 29250.00,
      "notes": "Installation of 2,500 SF storefront @ 0.18 hrs/SF"
    }},
    {{
      "cost_code": "M-IGU-002",
      "description": "IGU - Low-E",
      "quantity": 2500,
      "unit": "sqft",
      "unit_cost": 42.00,
      "total_cost": 105000.00,
      "notes": "Low-E IGUs for storefront system per spec"
    }}
  ],
  "assumptions": [
    "List any key assumptions made in the estimate",
    "Note any missing information or areas needing clarification"
  ]
}}

Be detailed and thorough. Include ALL applicable cost categories."""

        return prompt

    def _calculate_totals(self, budget_data):
        """Calculate category and grand totals"""

        labor_total = 0
        materials_total = 0
        indirect_total = 0

        for item in budget_data.get('line_items', []):
            cost = item.get('total_cost', 0)
            code = item.get('cost_code', '')

            if code.startswith('L-'):
                labor_total += cost
            elif code.startswith('M-') or code.startswith('HARDWARE-') or code.startswith('SEALANTS-') or code.startswith('ACCESSORIES-'):
                materials_total += cost
            elif code.startswith('INDIRECT-'):
                indirect_total += cost

        return {
            'labor_total': labor_total,
            'materials_total': materials_total,
            'indirect_total': indirect_total,
            'grand_total': labor_total + materials_total + indirect_total
        }

    def _save_budget_csv(self, budget_data, csv_file):
        """Save budget as CSV for import to accounting system"""

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Cost Code',
                'Description',
                'Quantity',
                'Unit',
                'Unit Cost',
                'Total Cost',
                'Notes'
            ])

            # Line items
            for item in budget_data.get('line_items', []):
                writer.writerow([
                    item.get('cost_code', ''),
                    item.get('description', ''),
                    item.get('quantity', 0),
                    item.get('unit', ''),
                    f"${item.get('unit_cost', 0):.2f}",
                    f"${item.get('total_cost', 0):.2f}",
                    item.get('notes', '')
                ])

            # Totals
            totals = budget_data.get('totals', {})
            writer.writerow([])
            writer.writerow(['', '', '', '', 'LABOR TOTAL:', f"${totals.get('labor_total', 0):,.2f}", ''])
            writer.writerow(['', '', '', '', 'MATERIALS TOTAL:', f"${totals.get('materials_total', 0):,.2f}", ''])
            writer.writerow(['', '', '', '', 'INDIRECT TOTAL:', f"${totals.get('indirect_total', 0):,.2f}", ''])
            writer.writerow(['', '', '', '', 'GRAND TOTAL:', f"${totals.get('grand_total', 0):,.2f}", ''])

    def _create_budget_report(self, project_number, budget_data, report_file):
        """Create human-readable budget report"""

        totals = budget_data.get('totals', {})

        report = [
            f"# Internal Budget Report",
            f"## Project: {project_number}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "**NOTE:** This is an INTERNAL budget for cost tracking. Do NOT share with client.",
            "",
            "---",
            "",
            "## Budget Summary",
            "",
            f"| Category | Total |",
            f"|----------|------:|",
            f"| Labor | ${totals.get('labor_total', 0):,.2f} |",
            f"| Materials | ${totals.get('materials_total', 0):,.2f} |",
            f"| Indirect Costs | ${totals.get('indirect_total', 0):,.2f} |",
            f"| **GRAND TOTAL** | **${totals.get('grand_total', 0):,.2f}** |",
            "",
            "---",
            "",
            "## Detailed Line Items",
            ""
        ]

        # Group by category
        labor_items = []
        material_items = []
        indirect_items = []

        for item in budget_data.get('line_items', []):
            code = item.get('cost_code', '')
            if code.startswith('L-'):
                labor_items.append(item)
            elif code.startswith('INDIRECT-'):
                indirect_items.append(item)
            else:
                material_items.append(item)

        # Labor section
        if labor_items:
            report.extend([
                "### Labor",
                "",
                "| Code | Description | Qty | Unit | Unit Cost | Total | Notes |",
                "|------|-------------|----:|------|----------:|------:|-------|"
            ])
            for item in labor_items:
                report.append(
                    f"| {item['cost_code']} | {item['description']} | "
                    f"{item['quantity']:,.0f} | {item['unit']} | "
                    f"${item['unit_cost']:.2f} | ${item['total_cost']:,.2f} | "
                    f"{item.get('notes', '')} |"
                )
            report.append("")

        # Materials section
        if material_items:
            report.extend([
                "### Materials",
                "",
                "| Code | Description | Qty | Unit | Unit Cost | Total | Notes |",
                "|------|-------------|----:|------|----------:|------:|-------|"
            ])
            for item in material_items:
                report.append(
                    f"| {item['cost_code']} | {item['description']} | "
                    f"{item['quantity']:,.0f} | {item['unit']} | "
                    f"${item['unit_cost']:.2f} | ${item['total_cost']:,.2f} | "
                    f"{item.get('notes', '')} |"
                )
            report.append("")

        # Indirect section
        if indirect_items:
            report.extend([
                "### Indirect Costs",
                "",
                "| Code | Description | Qty | Unit | Unit Cost | Total | Notes |",
                "|------|-------------|----:|------|----------:|------:|-------|"
            ])
            for item in indirect_items:
                report.append(
                    f"| {item['cost_code']} | {item['description']} | "
                    f"{item['quantity']:,.0f} | {item['unit']} | "
                    f"${item['unit_cost']:.2f} | ${item['total_cost']:,.2f} | "
                    f"{item.get('notes', '')} |"
                )
            report.append("")

        # Assumptions
        if budget_data.get('assumptions'):
            report.extend([
                "---",
                "",
                "## Assumptions & Notes",
                ""
            ])
            for assumption in budget_data['assumptions']:
                report.append(f"- {assumption}")
            report.append("")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("\nUsage: python budget_generator.py PROJECT_NUMBER")
        print("\nExample: python budget_generator.py P001")
        print("\nThis will generate internal budget with cost codes")
        sys.exit(1)

    project_number = sys.argv[1]

    try:
        # Load contract analysis
        analysis_file = Path(f"Output/Reports/{project_number}_contract_analysis.json")
        if not analysis_file.exists():
            print(f"ERROR: Contract analysis not found: {analysis_file}")
            sys.exit(1)

        with open(analysis_file, 'r', encoding='utf-8') as f:
            contract_analysis = json.load(f)

        # Load scope analysis
        scope_file = Path(f"Output/Scope_Analysis/{project_number}_scope_analysis.json")
        if not scope_file.exists():
            print(f"ERROR: Scope analysis not found: {scope_file}")
            sys.exit(1)

        with open(scope_file, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
            scope_analysis = scope_data.get('scope_analysis', {})

        # Generate budget
        generator = BudgetGenerator()
        result = generator.generate_budget(project_number, contract_analysis, scope_analysis)

        if result['success']:
            print("\n[OK] Budget generation complete!")
            sys.exit(0)
        else:
            print(f"\n[ERROR] {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
