#!/usr/bin/env python3
"""
Sample Contract PDF Generator
Creates realistic glazing project contracts for testing
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path


def create_sample_contract_1():
    """Simple door lite project"""

    output_dir = Path("Test_Contracts")
    output_dir.mkdir(exist_ok=True)

    filename = output_dir / "Sample_Contract_Door_Lites.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=30,
        alignment=1  # Center
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Title
    elements.append(Paragraph("CONSTRUCTION CONTRACT", title_style))
    elements.append(Paragraph("Glass & Glazing Division 08 Work", styles['Heading3']))
    elements.append(Spacer(1, 0.3*inch))

    # Project Info
    elements.append(Paragraph("PROJECT INFORMATION", heading_style))

    project_data = [
        ['Project Name:', 'Downtown Medical Office Building'],
        ['Project Number:', 'P2025-001'],
        ['Owner:', 'MedCenter Development LLC'],
        ['Architect:', 'Smith & Associates Architecture'],
        ['Location:', '456 Medical Plaza, Seattle, WA 98101'],
        ['Contract Date:', datetime.now().strftime('%B %d, %Y')],
        ['Contract Value:', '$42,500.00']
    ]

    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(project_table)
    elements.append(Spacer(1, 0.3*inch))

    # Scope of Work
    elements.append(Paragraph("SCOPE OF WORK", heading_style))

    scope_text = """
    <para>
    Contractor shall furnish all labor, materials, equipment, and supervision necessary to complete
    the following glazing work in accordance with Division 08 specifications:
    </para>
    """
    elements.append(Paragraph(scope_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))

    # Scope items
    scope_items = """
    <para>
    <b>Division 088000 - GLAZING</b><br/>
    <br/>
    <b>1.1 GLASS DOOR LITES</b><br/>
    <br/>
    <b>A. Quantity:</b> Twenty-four (24) door vision lites<br/>
    <br/>
    <b>B. Size:</b> 12" x 18" rectangular<br/>
    <br/>
    <b>C. Glass Type:</b><br/>
    - 1/4" clear tempered glass<br/>
    - Meets safety glazing requirements per ANSI Z97.1<br/>
    - Polished edges<br/>
    <br/>
    <b>D. Application:</b> Interior office door lites in wood door frames<br/>
    <br/>
    <b>E. Installation:</b><br/>
    - Install with glazing tape and stops<br/>
    - Interior beauty bead sealant<br/>
    - All lites to be plumb, level, and square<br/>
    <br/>
    <b>1.2 RELITE FRAMES</b><br/>
    <br/>
    <b>A. Quantity:</b> Eight (8) relite assemblies<br/>
    <br/>
    <b>B. Size:</b> 36" x 48" each<br/>
    <br/>
    <b>C. Frame:</b> Aluminum relite frame, clear anodized finish<br/>
    <br/>
    <b>D. Glass:</b> 1/4" clear tempered monolithic glass<br/>
    <br/>
    <b>E. Location:</b> Adjacent to entry doors in corridors<br/>
    <br/>
    <b>1.3 MATERIALS</b><br/>
    <br/>
    - All glass to be manufactured in accordance with ASTM C1036<br/>
    - Tempered glass to meet requirements of ASTM C1048<br/>
    - Glazing tape and sealants to be compatible with frame materials<br/>
    - Interior sealant to be low-VOC, clear silicone<br/>
    </para>
    """
    elements.append(Paragraph(scope_items, styles['BodyText']))

    # Schedule
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("PROJECT SCHEDULE", heading_style))

    schedule_data = [
        ['Phase', 'Duration', 'Description'],
        ['Submittals', '2 weeks', 'Glass samples and shop drawings'],
        ['Fabrication', '3 weeks', 'Glass cutting and tempering'],
        ['Installation', '1 week', 'Field installation of all lites'],
        ['Punch List', '3 days', 'Final touch-up and cleaning']
    ]

    schedule_table = Table(schedule_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(schedule_table)

    # Build PDF
    doc.build(elements)
    print(f"[OK] Created: {filename}")
    return filename


def create_sample_contract_2():
    """Storefront project"""

    output_dir = Path("Test_Contracts")
    output_dir.mkdir(exist_ok=True)

    filename = output_dir / "Sample_Contract_Storefront.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=30,
        alignment=1
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Title
    elements.append(Paragraph("CONSTRUCTION CONTRACT", title_style))
    elements.append(Paragraph("Aluminum Storefront System", styles['Heading3']))
    elements.append(Spacer(1, 0.3*inch))

    # Project Info
    elements.append(Paragraph("PROJECT INFORMATION", heading_style))

    project_data = [
        ['Project Name:', 'Riverside Retail Plaza - Phase 1'],
        ['Project Number:', 'P2025-002'],
        ['Owner:', 'Riverside Development Group'],
        ['General Contractor:', 'BuildRight Construction'],
        ['Location:', '789 Commerce St, Bellevue, WA 98004'],
        ['Contract Date:', datetime.now().strftime('%B %d, %Y')],
        ['Contract Value:', '$285,000.00']
    ]

    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(project_table)
    elements.append(Spacer(1, 0.3*inch))

    # Scope
    elements.append(Paragraph("SCOPE OF WORK", heading_style))

    scope_items = """
    <para>
    <b>Division 084113 - ALUMINUM-FRAMED STOREFRONTS</b><br/>
    <br/>
    <b>1.1 STOREFRONT SYSTEM</b><br/>
    <br/>
    <b>A. Total Area:</b> Approximately 2,500 square feet of storefront<br/>
    <br/>
    <b>B. System:</b> Kawneer 451T thermal storefront system<br/>
    - Clear anodized aluminum finish<br/>
    - Thermal break construction<br/>
    - 2" x 4-1/2" framing members<br/>
    <br/>
    <b>C. Glazing:</b><br/>
    - 1" insulated glass units (IGUs)<br/>
    - Low-E coating on surface #2<br/>
    - Clear tempered outer lite<br/>
    - Clear tempered inner lite<br/>
    - Argon gas fill<br/>
    - U-value: 0.29, SHGC: 0.37<br/>
    <br/>
    <b>1.2 ENTRANCE DOORS</b><br/>
    <br/>
    <b>A. Quantity:</b> Two (2) pairs of entrance doors<br/>
    <br/>
    <b>B. Type:</b> Medium stile aluminum entrance doors<br/>
    - Clear anodized finish to match storefront<br/>
    - 3' x 7' door size<br/>
    - Panic hardware with key override<br/>
    - Surface-applied door closers<br/>
    - Threshold and weatherstripping<br/>
    <br/>
    <b>1.3 HARDWARE</b><br/>
    <br/>
    - Panic devices: IML P8900 series, aluminum finish<br/>
    - Closers: LCN 4040XP surface closers<br/>
    - Threshold: Pemko aluminum threshold with integral weatherseal<br/>
    <br/>
    <b>1.4 SEALANTS</b><br/>
    <br/>
    - Perimeter sealant: Dow Corning 795 structural silicone, aluminum color<br/>
    - Joint width: 1/2" minimum<br/>
    - All joints to be tooled smooth and uniform<br/>
    <br/>
    <b>1.5 PERFORMANCE REQUIREMENTS</b><br/>
    <br/>
    - Air infiltration: 0.06 cfm/sq ft @ 6.24 psf per ASTM E283<br/>
    - Water penetration: No leakage @ 12.0 psf per ASTM E331<br/>
    - Structural: Withstand 50 psf design load per ASTM E330<br/>
    - Thermal: Assembly U-value 0.45 or better<br/>
    </para>
    """
    elements.append(Paragraph(scope_items, styles['BodyText']))

    # Schedule of Values Preview
    elements.append(PageBreak())
    elements.append(Paragraph("SCHEDULE OF VALUES (DRAFT)", heading_style))

    sov_data = [
        ['Item', 'Description', 'Value'],
        ['1', 'General Conditions & Submittals', '$28,500'],
        ['2', 'Aluminum Storefront Framing', '$95,000'],
        ['3', 'Insulated Glass Units', '$105,000'],
        ['4', 'Entrance Doors & Hardware', '$42,500'],
        ['5', 'Sealants & Installation', '$14,000'],
        ['', '<b>TOTAL CONTRACT VALUE</b>', '<b>$285,000</b>']
    ]

    sov_table = Table(sov_data, colWidths=[0.75*inch, 4*inch, 1.5*inch])
    sov_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(sov_table)

    doc.build(elements)
    print(f"[OK] Created: {filename}")
    return filename


def main():
    """Generate sample contracts"""

    print("\n" + "="*70)
    print("  SAMPLE CONTRACT PDF GENERATOR")
    print("="*70 + "\n")

    print("Generating sample contracts...\n")

    # Generate contracts
    contract1 = create_sample_contract_1()
    contract2 = create_sample_contract_2()

    print("\n" + "="*70)
    print("  SAMPLE CONTRACTS CREATED")
    print("="*70)
    print(f"\nFiles created in: Test_Contracts/")
    print(f"\n1. {contract1.name}")
    print(f"   - Simple door lite project ($42,500)")
    print(f"   - 24 door lites + 8 relites")
    print(f"   - 1/4\" tempered glass")
    print(f"\n2. {contract2.name}")
    print(f"   - Storefront system ($285,000)")
    print(f"   - 2,500 SF Kawneer storefront")
    print(f"   - IGUs with Low-E glass")
    print(f"   - Entrance doors with hardware")
    print("\nUse these PDFs to test the upload workflow!\n")


if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        import reportlab
        main()
    except ImportError:
        print("\nERROR: reportlab not installed")
        print("\nInstall with: pip install reportlab")
        print("\nThen run this script again.")
        exit(1)
