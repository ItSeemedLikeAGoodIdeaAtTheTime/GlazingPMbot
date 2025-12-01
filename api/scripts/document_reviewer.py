"""
Document Reviewer - AI-powered document analysis by type
Extracts structured data from PDFs based on document type.
Supports human review iteration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class DocumentReviewer:
    """Reviews documents and extracts structured data based on document type."""

    def __init__(self):
        self.model = "claude-sonnet-4-20250514"

    def get_extraction_prompt(self, doc_type: str) -> str:
        """Get the extraction prompt based on document type."""

        prompts = {
            "contract": """You are a construction contract analyst for a commercial glazing subcontractor.
Analyze this contract document and extract the following information:

1. **Project Information**
   - Project name
   - Project address
   - Owner name
   - General contractor name
   - Architect name

2. **Contract Terms**
   - Contract value (total amount)
   - Retention percentage
   - Payment terms (net 30, etc.)
   - Contract type (lump sum, T&M, GMP)

3. **Scope of Work**
   - List each scope/system included (curtainwall, storefront, entrances, etc.)
   - For each scope, note any specific requirements mentioned

4. **Schedule**
   - Contract start date
   - Substantial completion date
   - Key milestones mentioned

5. **Insurance/Bond Requirements**
   - Any specific insurance requirements
   - Bond requirements

6. **Special Conditions**
   - Liquidated damages
   - Warranty requirements
   - Any unusual terms

Return as structured JSON.""",

            "drawings": """You are a glazing shop drawing reviewer for a commercial glazing subcontractor.
Analyze these drawings and extract the following information:

1. **Systems Identified**
   - List each glazing system type (curtainwall, storefront, entrances, skylights, etc.)
   - Note the elevation/location for each

2. **Glass Schedule**
   - Glass types called out (clear, tinted, low-e, laminated, etc.)
   - Glass thicknesses
   - IGU configurations (if any)
   - Special coatings or treatments

3. **Frame/Metal**
   - Aluminum system manufacturer/series if specified
   - Finish requirements (anodized, painted, color)
   - Frame depths

4. **Hardware**
   - Door hardware specified
   - Operators, closers, panic devices
   - Lock types

5. **Dimensions**
   - Overall system dimensions
   - Typical unit sizes
   - Any unusually large or small units

6. **Details to Note**
   - Sill conditions
   - Head conditions
   - Jamb conditions
   - Expansion joints
   - Waterproofing details

7. **Quantities** (if discernible)
   - Approximate SF of each system type
   - Door counts
   - Window counts

Return as structured JSON.""",

            "specs": """You are a specification reviewer for a commercial glazing subcontractor.
Analyze these specifications and extract the following information:

1. **Applicable Sections**
   - List all spec sections that apply to glazing work
   - Note the section number and title (e.g., "08 44 13 - Glazed Aluminum Curtain Walls")

2. **Product Requirements**
   - Acceptable manufacturers for each product type
   - Specific product series/models required
   - Performance requirements (U-factor, SHGC, STC, etc.)

3. **Submittal Requirements**
   - List ALL submittals required
   - Note which require samples vs. product data vs. shop drawings
   - Certifications required
   - Test reports required

4. **Material Specifications**
   - Glass specifications (type, thickness, coating)
   - Aluminum specifications (alloy, temper, finish)
   - Sealant specifications
   - Hardware specifications

5. **Quality Assurance**
   - Mock-up requirements
   - Testing requirements (air, water, structural)
   - Inspection requirements
   - Installer qualifications

6. **Warranty Requirements**
   - Glass warranty period
   - Finish warranty period
   - Workmanship warranty
   - Any special warranty terms

7. **Installation Requirements**
   - Special installation procedures noted
   - Coordination requirements
   - Protection requirements

Return as structured JSON.""",

            "schedule": """You are a project scheduler for a commercial glazing subcontractor.
Analyze this schedule document and extract the following information:

1. **Key Dates**
   - Project start date
   - Glazing start date (if specified)
   - Substantial completion
   - Final completion

2. **Glazing Milestones**
   - Submittal due dates
   - Material procurement dates
   - Installation phases/dates
   - Inspection dates

3. **Dependencies**
   - What work precedes glazing installation
   - What work follows glazing installation
   - Any noted constraints

4. **Phasing**
   - Is work phased by building/area?
   - Phase descriptions and dates

5. **Duration**
   - Total project duration
   - Glazing installation duration (if specified)

Return as structured JSON.""",

            "proposal": """You are a proposal analyst for a commercial glazing subcontractor.
Analyze this proposal/bid document and extract the following information:

1. **Pricing Summary**
   - Total bid amount
   - Breakdown by scope (if provided)
   - Alternates included
   - Allowances

2. **Scope Included**
   - What work is included in the price
   - What work is specifically excluded

3. **Assumptions**
   - Key assumptions made
   - Clarifications

4. **Schedule Assumptions**
   - Lead times quoted
   - Installation duration assumed

5. **Vendor Quotes Used**
   - Any vendor names/quotes referenced

Return as structured JSON.""",

            "vendor_quotes": """You are a procurement specialist for a commercial glazing subcontractor.
Analyze this vendor quote and extract the following information:

1. **Vendor Information**
   - Vendor name
   - Contact information
   - Quote number/date

2. **Pricing**
   - Total quoted amount
   - Unit prices (if provided)
   - Line item breakdown

3. **Materials Quoted**
   - Products/materials included
   - Quantities
   - Specifications

4. **Terms**
   - Lead time
   - Payment terms
   - Quote validity period
   - Freight terms

5. **Exclusions/Notes**
   - What's excluded
   - Special conditions

Return as structured JSON.""",

            "vendor_invoices": """You are an accounts payable specialist for a commercial glazing subcontractor.
Analyze this vendor invoice and extract the following information:

1. **Invoice Details**
   - Invoice number
   - Invoice date
   - Due date
   - Vendor name

2. **Amounts**
   - Subtotal
   - Tax
   - Freight
   - Total due

3. **Line Items**
   - Description of each item
   - Quantities
   - Unit prices
   - Extended amounts

4. **Reference Information**
   - PO number referenced
   - Project name/number
   - Delivery information

Return as structured JSON."""
        }

        return prompts.get(doc_type, """Analyze this document and extract all relevant information.
Return as structured JSON with appropriate categories.""")

    def review_document(
        self,
        doc_type: str,
        doc_content: str,
        file_name: str,
        previous_review: Optional[Dict] = None,
        human_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review a document and extract structured data.

        Args:
            doc_type: Type of document (contract, drawings, specs, etc.)
            doc_content: Text content extracted from the document
            file_name: Original file name
            previous_review: Previous AI review (for iteration)
            human_feedback: Human markup/feedback on previous review

        Returns:
            Dictionary with extracted data and metadata
        """

        base_prompt = self.get_extraction_prompt(doc_type)

        # Build the prompt
        if previous_review and human_feedback:
            # This is a re-review with human feedback
            prompt = f"""{base_prompt}

PREVIOUS AI REVIEW:
{json.dumps(previous_review.get('extracted_data', {}), indent=2)}

HUMAN FEEDBACK/CORRECTIONS:
{human_feedback}

Please update your extraction based on the human feedback. Pay special attention to:
1. Any corrections noted
2. Any missing items the human identified
3. Any items the human marked as incorrect

DOCUMENT CONTENT:
{doc_content[:100000]}"""  # Limit content size
        else:
            # First review
            prompt = f"""{base_prompt}

DOCUMENT: {file_name}

DOCUMENT CONTENT:
{doc_content[:100000]}"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()

            # Try to parse as JSON
            extracted_data = {}
            try:
                # Handle markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                extracted_data = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, store as raw text
                extracted_data = {"raw_analysis": content}

            return {
                "success": True,
                "document_type": doc_type,
                "file_name": file_name,
                "extracted_data": extracted_data,
                "iteration": (previous_review.get("iteration", 0) + 1) if previous_review else 1,
                "reviewed_at": datetime.now().isoformat(),
                "human_reviewed": False,
                "human_feedback": human_feedback
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": doc_type,
                "file_name": file_name
            }

    def generate_review_summary(self, extracted_data: Dict, doc_type: str) -> str:
        """Generate a human-readable summary of the extracted data."""

        if doc_type == "contract":
            summary_parts = []
            if "Project Information" in extracted_data:
                pi = extracted_data["Project Information"]
                summary_parts.append(f"Project: {pi.get('Project name', 'Unknown')}")
                summary_parts.append(f"GC: {pi.get('General contractor name', 'Unknown')}")

            if "Contract Terms" in extracted_data:
                ct = extracted_data["Contract Terms"]
                if ct.get("Contract value"):
                    summary_parts.append(f"Value: {ct['Contract value']}")

            if "Scope of Work" in extracted_data:
                scopes = extracted_data["Scope of Work"]
                if isinstance(scopes, list):
                    summary_parts.append(f"Scopes: {', '.join(str(s) for s in scopes[:5])}")

            return " | ".join(summary_parts) if summary_parts else "Contract document reviewed"

        elif doc_type == "drawings":
            summary_parts = []
            if "Systems Identified" in extracted_data:
                systems = extracted_data["Systems Identified"]
                if isinstance(systems, list):
                    summary_parts.append(f"Systems: {', '.join(str(s) for s in systems[:5])}")

            if "Glass Schedule" in extracted_data:
                glass = extracted_data["Glass Schedule"]
                if isinstance(glass, dict) and glass.get("Glass types"):
                    summary_parts.append(f"Glass: {glass['Glass types']}")

            return " | ".join(summary_parts) if summary_parts else "Drawings reviewed"

        elif doc_type == "specs":
            summary_parts = []
            if "Applicable Sections" in extracted_data:
                sections = extracted_data["Applicable Sections"]
                if isinstance(sections, list):
                    summary_parts.append(f"{len(sections)} spec sections")

            if "Submittal Requirements" in extracted_data:
                submittals = extracted_data["Submittal Requirements"]
                if isinstance(submittals, list):
                    summary_parts.append(f"{len(submittals)} submittals required")

            return " | ".join(summary_parts) if summary_parts else "Specifications reviewed"

        else:
            return f"{doc_type.replace('_', ' ').title()} document reviewed"


# Convenience function for API
def review_document(
    doc_type: str,
    doc_content: str,
    file_name: str,
    previous_review: Optional[Dict] = None,
    human_feedback: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to review a document."""
    reviewer = DocumentReviewer()
    return reviewer.review_document(
        doc_type=doc_type,
        doc_content=doc_content,
        file_name=file_name,
        previous_review=previous_review,
        human_feedback=human_feedback
    )


if __name__ == "__main__":
    reviewer = DocumentReviewer()
    print("Document Reviewer initialized")
    print(f"Supported document types: contract, drawings, specs, schedule, proposal, vendor_quotes, vendor_invoices")
