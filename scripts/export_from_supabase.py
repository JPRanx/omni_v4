#!/usr/bin/env python3
"""
Export pipeline data from Supabase to batch_results JSON format.

This script retrieves all data from Supabase and reconstructs the batch_results
structure expected by generate_dashboard_data.py.

Usage:
    python scripts/export_from_supabase.py
    python scripts/export_from_supabase.py --output outputs/pipeline_runs/batch_results_from_supabase.json
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.storage.supabase_client import SupabaseClient


def reconstruct_pipeline_run(
    daily_op: Dict[str, Any],
    shifts: List[Dict[str, Any]],
    timeslots: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Reconstruct a pipeline run from Supabase data.

    Args:
        daily_op: Daily operation record
        shifts: Shift operation records for this day
        timeslots: Timeslot results for this day

    Returns:
        Pipeline run dict compatible with generate_dashboard_data.py
    """

    # Build shifts structure
    shifts_data = {}
    shift_category_stats = {}

    for shift in shifts:
        shift_name = shift['shift_name']

        # Build shift data
        shifts_data[shift_name.lower()] = {
            'sales': shift.get('sales', 0),
            'labor_cost': shift.get('labor_cost', 0),
            'labor_hours': shift.get('labor_hours', 0),
            'order_count': shift.get('order_count', 0),
        }

        # Extract category_stats if available
        if 'category_stats' in shift and shift['category_stats']:
            shift_category_stats[shift_name] = shift['category_stats']

    # Build timeslots structure
    timeslot_data = []
    for slot in timeslots:
        timeslot_data.append({
            'time_window': slot.get('timeslot_label', ''),
            'shift': slot.get('shift_name', ''),
            'orders': slot.get('orders', 0),
            'sales': slot.get('sales', 0),
            'labor_cost': slot.get('labor_cost', 0),
            'efficiency_score': slot.get('efficiency_score', 0),
            'grade': slot.get('grade', ''),
            'pass_fail': slot.get('pass_fail', ''),
        })

    # Build cash flow structure (if available)
    cash_flow = {}
    if daily_op.get('cash_collected') or daily_op.get('vendor_payouts_total'):
        cash_flow = {
            'total_cash': daily_op.get('cash_collected', 0),
            'total_tips': daily_op.get('tips_distributed', 0),
            'total_vendor_payouts': daily_op.get('vendor_payouts_total', 0),
            'net_cash': daily_op.get('net_cash', 0),
        }

        # Add shift-level cash flow
        for shift in shifts:
            shift_key = f"{shift['shift_name'].lower()}_shift"
            cash_flow[shift_key] = {
                'cash_collected': shift.get('cash_collected', 0),
                'tips_distributed': shift.get('tips_distributed', 0),
                'total_vendor_payouts': shift.get('vendor_payouts', 0),
                'net_cash': shift.get('net_cash', 0),
                'sales': shift.get('sales', 0),
                'labor_cost': shift.get('labor_cost', 0),
                'labor_hours': shift.get('labor_hours', 0),
            }

    # Build service mix if available
    service_mix = {}
    if daily_op.get('lobby_percent') is not None:
        service_mix = {
            'Lobby': daily_op.get('lobby_percent', 0),
            'Drive-Thru': daily_op.get('drivethru_percent', 0),
            'ToGo': daily_op.get('togo_percent', 0),
        }

    # Build the pipeline run
    pipeline_run = {
        'date': daily_op['business_date'],
        'restaurant': daily_op['restaurant_code'],
        'success': True,

        # Sales & Labor
        'sales': daily_op.get('total_sales') or 0,
        'labor_cost': daily_op.get('labor_cost') or 0,
        'total_hours': daily_op.get('labor_hours') or 0,
        'labor_percentage': daily_op.get('labor_percent') or 0,
        'employee_count': daily_op.get('employee_count') or 0,

        # Orders
        'total_orders': daily_op.get('order_count') or 0,
        'categorized_orders': daily_op.get('categorized_orders') or 0,

        # Overtime
        'overtime_hours': daily_op.get('overtime_hours') or 0,
        'overtime_cost': daily_op.get('overtime_cost') or 0,

        # Grading
        'labor_status': daily_op.get('labor_status'),
        'labor_grade': daily_op.get('labor_grade'),

        # Structured data
        'shift_metrics': shifts_data,  # V3DataTransformer expects 'shift_metrics' not 'shifts'
        'shift_category_stats': shift_category_stats,
        'timeslot_metrics': timeslot_data,
    }

    # Add optional fields
    if cash_flow:
        pipeline_run['cash_flow'] = cash_flow

    if service_mix:
        pipeline_run['service_mix'] = service_mix

    return pipeline_run


def export_from_supabase() -> Dict[str, Any]:
    """
    Export all data from Supabase to batch_results structure.

    Returns:
        Batch results dict with 'pipeline_runs' list
    """

    print("=" * 80)
    print("EXPORTING DATA FROM SUPABASE")
    print("=" * 80)

    # Connect to Supabase
    client = SupabaseClient()

    # Fetch all data
    print("\n>>> Fetching daily operations...")
    response = client.client.table('daily_operations').select('*').order('business_date').execute()
    daily_operations = response.data
    print(f"    Found {len(daily_operations)} daily operations")

    print("\n>>> Fetching shift operations...")
    response = client.client.table('shift_operations').select('*').order('business_date').execute()
    shift_operations = response.data
    print(f"    Found {len(shift_operations)} shift operations")

    print("\n>>> Fetching timeslot results...")
    response = client.client.table('timeslot_results').select('*').order('business_date, timeslot_index').execute()
    timeslot_results = response.data
    print(f"    Found {len(timeslot_results)} timeslot results")

    # Group data by date and restaurant
    print("\n>>> Grouping data by date and restaurant...")
    shifts_by_key = defaultdict(list)
    for shift in shift_operations:
        key = f"{shift['business_date']}_{shift['restaurant_code']}"
        shifts_by_key[key].append(shift)

    timeslots_by_key = defaultdict(list)
    for slot in timeslot_results:
        key = f"{slot['business_date']}_{slot['restaurant_code']}"
        timeslots_by_key[key].append(slot)

    # Reconstruct pipeline runs
    print("\n>>> Reconstructing pipeline runs...")
    pipeline_runs = []

    for daily_op in daily_operations:
        key = f"{daily_op['business_date']}_{daily_op['restaurant_code']}"

        shifts = shifts_by_key.get(key, [])
        timeslots = timeslots_by_key.get(key, [])

        run = reconstruct_pipeline_run(daily_op, shifts, timeslots)
        pipeline_runs.append(run)

    print(f"    Reconstructed {len(pipeline_runs)} pipeline runs")

    # Calculate metadata
    dates = [run['date'] for run in pipeline_runs]
    restaurants = list(set(run['restaurant'] for run in pipeline_runs))

    batch_results = {
        'pipeline_runs': pipeline_runs,
        'start_date': min(dates) if dates else None,
        'end_date': max(dates) if dates else None,
        'total_days': len(set(dates)),
        'restaurants': sorted(restaurants),
        'generated_at': datetime.now().isoformat(),
        'source': 'Supabase Export'
    }

    return batch_results


def main():
    """Main entry point."""

    # Parse output path
    output_path = Path('outputs/pipeline_runs/batch_results_from_supabase.json')

    if len(sys.argv) > 1 and sys.argv[1] == "--output":
        if len(sys.argv) > 2:
            output_path = Path(sys.argv[2])
        else:
            print("Error: --output requires a filename")
            sys.exit(1)

    try:
        # Export data
        batch_results = export_from_supabase()

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2)

        # Summary
        print("\n" + "=" * 80)
        print("EXPORT COMPLETE")
        print("=" * 80)
        print(f"\n>>> Exported {len(batch_results['pipeline_runs'])} pipeline runs")
        print(f"    Date Range: {batch_results['start_date']} to {batch_results['end_date']}")
        print(f"    Restaurants: {', '.join(batch_results['restaurants'])}")
        print(f"    Output: {output_path.absolute()}")

        print(f"\n>>> Next Step:")
        print(f"    python scripts/generate_dashboard_data.py {output_path}")

    except Exception as e:
        print(f"\n>>> Error exporting from Supabase: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
