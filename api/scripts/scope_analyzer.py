#!/usr/bin/env python3
"""
Scope Analyzer - Intelligent Vendor Matching System

Analyzes contract documents to:
1. Identify scope types (storefront, curtain wall, fire-rated, etc.)
2. Determine material needs per scope
3. Match to capable vendors
4. Generate RFQ recommendations (2 vendors per category)
"""

import os
import sys
import json
import csv
from pathlib import Path
from anthropic import Anthropic

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ScopeAnalyzer:
    """Analyzes project scope and matches to vendors"""

    def __init__(self):
        """Initialize with API key and load vendor data"""
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropicAPIkey")
        if not api_key:
            raise ValueError("Anthropic API key not found")

        self.client = Anthropic(api_key=api_key)

        # Load vendor capability matrix
        matrix_path = Path("Vendor_Data/vendor_capability_matrix.csv")
        if not matrix_path.exists():
            raise FileNotFoundError(f"Vendor capability matrix not found: {matrix_path}")

        self.vendors = []
        with open(matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.vendors = list(reader)

        # Load scope matrix
        scope_path = Path("Vendor_Data/scope_matrix.md")
        if not scope_path.exists():
            raise FileNotFoundError(f"Scope matrix not found: {scope_path}")

        with open(scope_path, 'r', encoding='utf-8') as f:
            self.scope_definitions = f.read()

    def analyze_project_scope(self, project_number, contract_analysis=None, selected_vendors=None):
        """Analyze project and identify scopes with optional vendor filtering"""

        print(f"\n{'='*70}")
        print(f"  SCOPE ANALYSIS: {project_number}")
        print(f"{'='*70}\n")

        # Load contract analysis if not provided
        if not contract_analysis:
            analysis_file = Path(f"Output/Reports/{project_number}_contract_analysis.json")
            if not analysis_file.exists():
                print(f"ERROR: Contract analysis not found: {analysis_file}")
                return {'success': False, 'error': 'Contract analysis not found'}

            with open(analysis_file, 'r', encoding='utf-8') as f:
                contract_analysis = json.load(f)

        # Filter vendors if selection provided
        available_vendors = self.vendors
        if selected_vendors:
            available_vendors = [
                v for v in self.vendors
                if v['Vendor Name'].lower().replace(' ', '_') in selected_vendors
            ]
            print(f"📋 Using {len(available_vendors)} selected vendors (out of {len(self.vendors)} total)\n")
        else:
            print(f"📋 Using all {len(self.vendors)} vendors\n")

        print("[1/4] Analyzing contract requirements...")

        # Build scope identification prompt
        scope_prompt = f"""You are a glazing project manager analyzing a construction contract.

SCOPE DEFINITIONS:
{self.scope_definitions}

CONTRACT ANALYSIS:
{json.dumps(contract_analysis, indent=2)}

Your task:
1. Identify ALL scope types present in this project (from the Scope Matrix)
2. For each scope, extract:
   - Specific requirements (sizes, quantities, ratings, etc.)
   - Relevant spec sections
   - Critical details (fire ratings, performance requirements)
   - Any special conditions

Return JSON with this structure:
{{
  "scopes": [
    {{
      "scope_type": "FIRE-RATED GLAZING",
      "description": "Fire-rated door lites and borrowed lights",
      "requirements": {{
        "fire_ratings": ["60-minute", "90-minute"],
        "quantities": "8 doors with vision lites, 4 sidelites",
        "sizes": "Vision lites 12x18, sidelites 48x96",
        "spec_sections": ["081416", "088313"]
      }},
      "critical_notes": "Must be listed assemblies, labels required",
      "priority": "HIGH"
    }}
  ],
  "summary": "Brief project summary highlighting key scopes"
}}
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": scope_prompt
            }]
        )

        try:
            response_text = response.content[0].text

            # Try to extract JSON if wrapped in markdown
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()

            scope_analysis = json.loads(response_text)
        except Exception as e:
            print(f"ERROR: Could not parse scope analysis: {e}")
            print(f"\nRaw response:\n{response.content[0].text[:500]}...")
            return {'success': False, 'error': f'Failed to parse scope analysis: {e}'}

        print(f"[OK] Identified {len(scope_analysis['scopes'])} scope types")

        # Match vendors to each scope
        print("\n[2/4] Matching vendors to scopes...")

        for scope in scope_analysis['scopes']:
            scope['matched_vendors'] = self._match_vendors_to_scope(scope, available_vendors)

        # Generate RFQ recommendations
        print("\n[3/4] Generating RFQ recommendations...")

        rfq_recommendations = self._generate_rfq_recommendations(scope_analysis)

        # Save results
        print("\n[4/4] Saving analysis...")

        output_dir = Path("Output/Scope_Analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{project_number}_scope_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'project_number': project_number,
                'scope_analysis': scope_analysis,
                'rfq_recommendations': rfq_recommendations
            }, f, indent=2)

        # Create readable report
        report_file = output_dir / f"{project_number}_scope_analysis.md"
        self._create_readable_report(project_number, scope_analysis, rfq_recommendations, report_file)

        print(f"\n{'='*70}")
        print(f"  SCOPE ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f"\nOutputs:")
        print(f"  JSON: {output_file}")
        print(f"  Report: {report_file}")
        print(f"\nScopes identified: {len(scope_analysis['scopes'])}")
        print(f"RFQ packages: {len(rfq_recommendations)}")

        return {
            'success': True,
            'scopes': scope_analysis['scopes'],
            'rfq_recommendations': rfq_recommendations,
            'output_file': str(output_file)
        }

    def _match_vendors_to_scope(self, scope, available_vendors):
        """Match vendors capable of providing materials for this scope"""

        scope_type = scope['scope_type'].upper()
        matched = []

        # Define material needs per scope type
        material_mapping = {
            'STOREFRONT': ['Aluminum Framing', 'Glass Monolithic', 'Glass IGU', 'Door Hardware', 'Sealants'],
            'CURTAIN WALL': ['Aluminum Framing', 'Glass IGU', 'Sealants', 'Metal Panels'],
            'MONOLITHIC GLASS': ['Glass Monolithic'],
            'FIRE-RATED GLAZING': ['Glass Fire-Rated', 'Door Hardware'],
            'INTERIOR GLAZING': ['Glass Monolithic', 'Aluminum Framing', 'All-Glass Hardware'],
            'MIRRORS': ['Glass Monolithic'],
            'ENTRANCE DOORS': ['Glass Monolithic', 'Door Hardware', 'All-Glass Hardware'],
            'SPECIALTY GLASS': ['Glass Specialty'],
            'METAL PANELS': ['Metal Panels', 'Paint Finishing'],
            'GLASS RAILING': ['Glass Monolithic']
        }

        needed_materials = material_mapping.get(scope_type, [])

        # Find vendors for each material
        for material in needed_materials:
            material_vendors = []

            for vendor in available_vendors:
                # Check if vendor provides this material
                if vendor.get(material, 'No') == 'Yes':
                    material_vendors.append({
                        'vendor': vendor['Vendor Name'],
                        'contact': vendor['Primary Contact'],
                        'lead_time': vendor['Lead Time'],
                        'notes': vendor['Notes']
                    })

            if material_vendors:
                matched.append({
                    'material_category': material,
                    'vendors': material_vendors
                })

        return matched

    def _generate_rfq_recommendations(self, scope_analysis):
        """Generate RFQ package recommendations - 2 vendors per category"""

        recommendations = []

        for scope in scope_analysis['scopes']:
            for material_match in scope['matched_vendors']:
                vendors = material_match['vendors']

                # Select top 2 vendors (if available)
                selected_vendors = vendors[:2] if len(vendors) >= 2 else vendors

                if selected_vendors:
                    recommendations.append({
                        'scope': scope['scope_type'],
                        'material_category': material_match['material_category'],
                        'vendors_to_quote': selected_vendors,
                        'requirements': scope['requirements'],
                        'notes': scope.get('critical_notes', '')
                    })

        return recommendations

    def _create_readable_report(self, project_number, scope_analysis, rfq_recommendations, output_file):
        """Create human-readable markdown report"""

        report = [
            f"# Scope Analysis Report",
            f"## Project: {project_number}",
            "",
            f"## Summary",
            scope_analysis.get('summary', ''),
            "",
            f"## Identified Scopes ({len(scope_analysis['scopes'])})",
            ""
        ]

        for i, scope in enumerate(scope_analysis['scopes'], 1):
            report.extend([
                f"### {i}. {scope['scope_type']}",
                "",
                f"**Description:** {scope['description']}",
                "",
                "**Requirements:**",
                f"```json",
                json.dumps(scope['requirements'], indent=2),
                "```",
                ""
            ])

            if scope.get('critical_notes'):
                report.extend([
                    f"**Critical Notes:** {scope['critical_notes']}",
                    ""
                ])

            report.extend([
                "**Matched Vendors:**",
                ""
            ])

            for match in scope['matched_vendors']:
                report.append(f"- **{match['material_category']}:**")
                for vendor in match['vendors']:
                    report.append(f"  - {vendor['vendor']} ({vendor['contact']}) - {vendor['lead_time']}")
                report.append("")

        report.extend([
            "---",
            "",
            f"## RFQ Recommendations ({len(rfq_recommendations)} packages)",
            ""
        ])

        for i, rfq in enumerate(rfq_recommendations, 1):
            report.extend([
                f"### RFQ Package {i}: {rfq['material_category']}",
                f"**Scope:** {rfq['scope']}",
                "",
                "**Request quotes from:**"
            ])

            for vendor in rfq['vendors_to_quote']:
                report.extend([
                    f"- **{vendor['vendor']}** (Contact: {vendor['contact']})",
                    f"  - Lead time: {vendor['lead_time']}",
                    f"  - Notes: {vendor['notes']}",
                    ""
                ])

            if rfq.get('notes'):
                report.extend([
                    f"**Special Requirements:** {rfq['notes']}",
                    ""
                ])

            report.append("---")
            report.append("")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("\nUsage: python scope_analyzer.py PROJECT_NUMBER")
        print("\nExample: python scope_analyzer.py P001")
        print("\nThis will:")
        print("  1. Analyze contract documents")
        print("  2. Identify scope types")
        print("  3. Match to capable vendors")
        print("  4. Generate RFQ recommendations (2 vendors per category)")
        sys.exit(1)

    project_number = sys.argv[1]

    try:
        analyzer = ScopeAnalyzer()
        result = analyzer.analyze_project_scope(project_number)

        if result['success']:
            print("\n[OK] Analysis complete!")
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
