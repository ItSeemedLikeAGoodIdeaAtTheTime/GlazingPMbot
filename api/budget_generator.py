"""
Internal Budget Generator
Maps scopes to cost codes for internal tracking
"""

import json
import csv
from pathlib import Path
from datetime import datetime


def generate_internal_budget(project_number: str, scopes: list) -> str:
    """
    Generate internal budget with cost codes

    Maps identified scopes to relevant cost codes
    Returns path to generated budget file
    """

    # Load cost code structure
    with open("cost_codes.json", 'r', encoding='utf-8') as f:
        cost_codes = json.load(f)['cost_code_structure']['categories']

    # Map scopes to cost codes
    budget_lines = []

    for scope in scopes:
        scope_type = scope['scope_type'].upper()

        # Add relevant cost codes based on scope
        if 'FIRE-RATED' in scope_type:
            # Fire-rated glass
            add_cost_code(budget_lines, cost_codes, 'GLASS_FIRE_RATED', scope)
            # Door hardware
            add_cost_code(budget_lines, cost_codes, 'HARDWARE_LATCHING', scope)
            # Fire-rated glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_DOOR_GLAZIERS', scope)

        elif 'STOREFRONT' in scope_type:
            # Metal framing
            add_cost_code(budget_lines, cost_codes, 'METAL_WINDOWS', scope)
            # Glass (IGU likely)
            add_cost_code(budget_lines, cost_codes, 'GLASS_IGU', scope)
            # Glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_FIELD_GLAZIERS', scope)
            # Sealants
            add_cost_code(budget_lines, cost_codes, 'SEALANTS_WEATHER', scope)

        elif 'CURTAIN WALL' in scope_type:
            # Metal system
            add_cost_code(budget_lines, cost_codes, 'METAL_WINDOWS', scope)
            # High-performance IGUs
            add_cost_code(budget_lines, cost_codes, 'GLASS_IGU', scope)
            # Structural sealant
            add_cost_code(budget_lines, cost_codes, 'SEALANTS_STRUCTURAL', scope)
            # Glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_FIELD_GLAZIERS', scope)

        elif 'MONOLITHIC' in scope_type:
            # Glass only
            add_cost_code(budget_lines, cost_codes, 'GLASS_MONOLITHIC', scope)
            # Glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_FIELD_GLAZIERS', scope)

        elif 'MIRROR' in scope_type:
            # Mirrors
            add_cost_code(budget_lines, cost_codes, 'GLASS_SPECIALTY', scope)
            # Glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_FIELD_GLAZIERS', scope)

        elif 'ENTRANCE DOOR' in scope_type or 'DOOR' in scope_type:
            # Door hardware
            add_cost_code(budget_lines, cost_codes, 'HARDWARE_HINGES', scope)
            add_cost_code(budget_lines, cost_codes, 'HARDWARE_LATCHING', scope)
            add_cost_code(budget_lines, cost_codes, 'HARDWARE_ACCESSORIES', scope)
            # Door glaziers
            add_cost_code(budget_lines, cost_codes, 'LABOR_DOOR_GLAZIERS', scope)

        # Always add indirect costs
        add_cost_code(budget_lines, cost_codes, 'INDIRECT_DRIVE_TIME', scope, is_indirect=True)
        add_cost_code(budget_lines, cost_codes, 'INDIRECT_TOOLS', scope, is_indirect=True)

        # Add accessories
        add_cost_code(budget_lines, cost_codes, 'ACCESSORIES_SHIMS', scope, is_indirect=True)
        add_cost_code(budget_lines, cost_codes, 'ACCESSORIES_SETTING_BLOCKS', scope, is_indirect=True)

    # Add project-wide indirect costs
    for category in ['INDIRECT_PARKING', 'INDIRECT_SHIPPING', 'INDIRECT_CRATING',
                     'INDIRECT_EQUIPMENT', 'INDIRECT_INSURANCE']:
        add_cost_code(budget_lines, cost_codes, category, None, is_indirect=True)

    # Write budget to CSV
    output_dir = Path("Output/Budgets")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{project_number}_internal_budget.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Cost Code",
            "Description",
            "Unit",
            "Quantity",
            "Unit Cost",
            "Total Cost",
            "Category",
            "Notes"
        ])

        # Data rows
        for line in budget_lines:
            writer.writerow([
                line['code'],
                line['description'],
                line['unit'],
                line['quantity'],
                f"${line['unit_cost']:.2f}",
                f"${line['total_cost']:.2f}",
                line['category'],
                line['notes']
            ])

        # Total row
        total = sum(line['total_cost'] for line in budget_lines)
        writer.writerow([])
        writer.writerow(["", "", "", "", "TOTAL:", f"${total:,.2f}"])

    return str(output_file)


def add_cost_code(budget_lines: list, cost_codes: dict, category_key: str,
                  scope: dict = None, is_indirect: bool = False):
    """Add cost code line items to budget"""

    if category_key not in cost_codes:
        return

    category = cost_codes[category_key]

    for item in category['line_items']:
        # Estimate quantity based on scope (simplified for now)
        quantity = estimate_quantity(item, scope) if scope else 1.0

        budget_lines.append({
            'code': item['code'],
            'description': item['name'],
            'unit': item['unit'],
            'quantity': quantity,
            'unit_cost': item['typical_rate'],
            'total_cost': quantity * item['typical_rate'],
            'category': category_key,
            'notes': scope['description'] if scope else 'Project-wide'
        })


def estimate_quantity(cost_item: dict, scope: dict) -> float:
    """
    Estimate quantity for cost item based on scope

    This is a simplified version - in production, would use
    actual quantities from scope requirements
    """

    unit = cost_item['unit']
    scope_desc = scope.get('description', '').lower()

    # Extract numbers from scope if available
    requirements = scope.get('requirements', {})

    # Labor hours (estimate 40 hours per scope for now)
    if unit == 'hour':
        return 40.0

    # Square footage (estimate 100 sqft per scope)
    if unit == 'sqft':
        return 100.0

    # Each items (estimate 4 per scope)
    if unit == 'each':
        return 4.0

    # Linear feet (estimate 50 lf per scope)
    if unit == 'linft':
        return 50.0

    # Lump sums
    if unit == 'lbsum':
        return 1.0

    # Days (estimate 10 days per scope)
    if unit == 'day':
        return 10.0

    # Sets
    if unit == 'set':
        return 4.0

    return 1.0
