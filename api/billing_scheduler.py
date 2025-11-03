"""
Predictive Billing Schedule Generator
Creates month-by-month billing predictions based on scope lead times
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def generate_billing_schedule(project_number: str, scopes: list) -> str:
    """
    Generate predictive billing schedule

    Creates month-by-month forecast of billable milestones:
    - General Conditions/Submittals
    - Materials Purchased
    - Materials Stored
    - Installation Labor
    - Final Retention
    """

    # Load contract analysis to get start date
    analysis_file = Path(f"Output/Reports/{project_number}_contract_analysis.json")
    start_date = datetime.now()

    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
            # Try to extract start date
            schedule = analysis.get('schedule', {})
            if 'start_date' in schedule:
                try:
                    start_date = datetime.strptime(schedule['start_date'], '%Y-%m-%d')
                except:
                    pass

    # Build billing schedule
    billing_events = []

    for scope in scopes:
        scope_type = scope['scope_type']
        description = scope['description']

        # Extract lead times from matched vendors
        lead_times = extract_lead_times(scope)
        max_lead_time_weeks = max(lead_times) if lead_times else 12

        # Create billing milestones for this scope

        # 1. General Conditions / Submittals (Month 1-2)
        submittal_date = start_date + timedelta(weeks=2)
        submittal_amount = estimate_scope_value(scope) * 0.12  # 12% for general conditions

        billing_events.append({
            'scope': scope_type,
            'milestone': 'General Conditions / Submittals',
            'date': submittal_date,
            'amount': submittal_amount,
            'percentage': 12,
            'trigger': 'Submittal package complete',
            'notes': f'Product data submitted for {description}'
        })

        # 2. Materials Purchased (based on lead time)
        purchase_date = submittal_date + timedelta(weeks=max_lead_time_weeks)
        purchase_amount = estimate_scope_value(scope) * 0.55  # 55% for materials

        billing_events.append({
            'scope': scope_type,
            'milestone': 'Materials Purchased',
            'date': purchase_date,
            'amount': purchase_amount,
            'percentage': 55,
            'trigger': 'Purchase order issued and materials ordered',
            'notes': f'Materials on order with {max_lead_time_weeks}-week lead time'
        })

        # 3. Materials Stored (2 weeks after purchase)
        storage_date = purchase_date + timedelta(weeks=2)
        storage_amount = estimate_scope_value(scope) * 0.10  # Additional 10% for stored materials

        billing_events.append({
            'scope': scope_type,
            'milestone': 'Materials Stored on Site',
            'date': storage_date,
            'amount': storage_amount,
            'percentage': 10,
            'trigger': 'Materials delivered and stored',
            'notes': 'Materials received and secured on site'
        })

        # 4. Installation Labor (4 weeks after storage)
        install_date = storage_date + timedelta(weeks=4)
        install_amount = estimate_scope_value(scope) * 0.18  # 18% for labor

        billing_events.append({
            'scope': scope_type,
            'milestone': 'Installation Labor',
            'date': install_date,
            'amount': install_amount,
            'percentage': 18,
            'trigger': 'Installation substantially complete',
            'notes': f'Installation of {description} complete'
        })

    # 5. Final Retention (all scopes, at project end)
    final_date = max(event['date'] for event in billing_events) + timedelta(weeks=8)
    retention_amount = sum(estimate_scope_value(scope) for scope in scopes) * 0.05  # 5% retention

    billing_events.append({
        'scope': 'ALL SCOPES',
        'milestone': 'Final Retention',
        'date': final_date,
        'amount': retention_amount,
        'percentage': 5,
        'trigger': 'Project substantial completion',
        'notes': 'Final retention release after punchlist completion'
    })

    # Sort by date
    billing_events.sort(key=lambda x: x['date'])

    # Aggregate by month
    monthly_schedule = aggregate_by_month(billing_events, start_date)

    # Write to CSV
    output_dir = Path("Output/Billing_Schedules")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{project_number}_billing_schedule.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Month",
            "Date",
            "Scope",
            "Milestone",
            "Amount",
            "Cumulative",
            "Trigger",
            "Notes"
        ])

        cumulative = 0
        for event in billing_events:
            cumulative += event['amount']
            month_year = event['date'].strftime('%B %Y')

            writer.writerow([
                month_year,
                event['date'].strftime('%Y-%m-%d'),
                event['scope'],
                event['milestone'],
                f"${event['amount']:,.2f}",
                f"${cumulative:,.2f}",
                event['trigger'],
                event['notes']
            ])

        # Monthly summary section
        writer.writerow([])
        writer.writerow(["MONTHLY SUMMARY"])
        writer.writerow(["Month", "Total Billing", "Cumulative"])

        cumulative = 0
        for month_data in monthly_schedule:
            cumulative += month_data['total']
            writer.writerow([
                month_data['month'],
                f"${month_data['total']:,.2f}",
                f"${cumulative:,.2f}"
            ])

    return str(output_file)


def extract_lead_times(scope: dict) -> list:
    """Extract lead times from matched vendors (in weeks)"""

    lead_times = []

    for match in scope.get('matched_vendors', []):
        for vendor in match.get('vendors', []):
            lead_time_str = vendor.get('lead_time', '')

            # Parse lead time string (e.g., "8 weeks", "2-3 days", "16 weeks")
            if 'week' in lead_time_str.lower():
                # Extract number
                parts = lead_time_str.lower().split()
                for part in parts:
                    try:
                        weeks = int(part)
                        lead_times.append(weeks)
                        break
                    except:
                        continue

    return lead_times


def estimate_scope_value(scope: dict) -> float:
    """
    Estimate dollar value of scope

    Simplified - in production, would calculate from actual quantities
    """

    scope_type = scope['scope_type'].upper()

    # Typical values by scope type (rough estimates)
    scope_values = {
        'FIRE-RATED': 50000,
        'STOREFRONT': 150000,
        'CURTAIN WALL': 300000,
        'MONOLITHIC': 25000,
        'INTERIOR': 40000,
        'MIRRORS': 15000,
        'ENTRANCE DOOR': 30000,
        'SPECIALTY': 75000,
        'METAL PANELS': 100000,
        'GLASS RAILING': 45000
    }

    # Find matching scope
    for key, value in scope_values.items():
        if key in scope_type:
            return value

    # Default
    return 50000


def aggregate_by_month(events: list, start_date: datetime) -> list:
    """Aggregate billing events by month"""

    monthly = {}

    for event in events:
        month_key = event['date'].strftime('%Y-%m')
        month_label = event['date'].strftime('%B %Y')

        if month_key not in monthly:
            monthly[month_key] = {
                'month': month_label,
                'total': 0,
                'events': []
            }

        monthly[month_key]['total'] += event['amount']
        monthly[month_key]['events'].append(event)

    # Convert to sorted list
    return sorted(monthly.values(), key=lambda x: x['month'])
