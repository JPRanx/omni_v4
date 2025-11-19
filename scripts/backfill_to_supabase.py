#!/usr/bin/env python3
"""
Backfill batch processing results to Supabase.

Reads JSON batch results and inserts all data into Supabase database.

Usage:
    python scripts/backfill_to_supabase.py <batch_results.json>
    python scripts/backfill_to_supabase.py outputs/pipeline_runs/batch_results_with_cogs.json
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseClient


def transform_daily_operation(run: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a pipeline run into daily_operations table format."""

    # Extract service mix if available
    service_mix = run.get('service_mix', {})
    categorized_orders = run.get('categorized_orders', 0)

    # Extract cash flow totals
    cash_flow = run.get('cash_flow', {})

    return {
        'business_date': run['date'],
        'restaurant_code': run['restaurant'],

        # Sales
        'total_sales': run.get('sales', 0),
        'order_count': run.get('total_orders', categorized_orders) if categorized_orders > 0 else None,

        # Labor
        'labor_cost': run.get('labor_cost', 0),
        'labor_hours': run.get('total_hours', 0),
        'labor_percent': run.get('labor_percentage', 0),
        'employee_count': run.get('employee_count'),

        # Overtime
        'overtime_hours': run.get('overtime_hours', 0),
        'overtime_cost': run.get('overtime_cost', 0),

        # COGS
        'food_cost': cash_flow.get('total_vendor_payouts', 0),
        'food_cost_percent': (cash_flow.get('total_vendor_payouts', 0) / run.get('sales', 1) * 100) if run.get('sales', 0) > 0 else 0,

        # Profitability
        'net_profit': run.get('sales', 0) - run.get('labor_cost', 0) - cash_flow.get('total_vendor_payouts', 0),
        'profit_margin': ((run.get('sales', 0) - run.get('labor_cost', 0) - cash_flow.get('total_vendor_payouts', 0)) / run.get('sales', 1) * 100) if run.get('sales', 0) > 0 else 0,

        # Cash flow
        'cash_collected': cash_flow.get('total_cash', 0),
        'tips_distributed': cash_flow.get('total_tips', 0),
        'vendor_payouts_total': cash_flow.get('total_vendor_payouts', 0),
        'net_cash': cash_flow.get('net_cash', 0),

        # Service mix (optional)
        'lobby_percent': service_mix.get('Lobby') if service_mix else None,
        'drivethru_percent': service_mix.get('Drive-Thru') if service_mix else None,
        'togo_percent': service_mix.get('ToGo') if service_mix else None,
        'categorized_orders': categorized_orders if categorized_orders > 0 else None,

        # Grading
        'labor_status': run.get('labor_status'),
        'labor_grade': run.get('labor_grade'),
    }


def transform_shift_operations(run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transform pipeline run into shift_operations records."""

    cash_flow = run.get('cash_flow', {})
    shifts = []

    # Morning shift
    morning = cash_flow.get('morning_shift', {})
    if morning:
        shifts.append({
            'business_date': run['date'],
            'restaurant_code': run['restaurant'],
            'shift_name': 'Morning',
            'sales': morning.get('sales', 0),
            'labor_cost': morning.get('labor_cost', 0),
            'labor_hours': morning.get('labor_hours', 0),
            'cash_collected': morning.get('cash_collected', 0),
            'tips_distributed': morning.get('tips_distributed', 0),
            'vendor_payouts': morning.get('total_vendor_payouts', 0),
            'net_cash': morning.get('net_cash', 0),
        })

    # Evening shift
    evening = cash_flow.get('evening_shift', {})
    if evening:
        shifts.append({
            'business_date': run['date'],
            'restaurant_code': run['restaurant'],
            'shift_name': 'Evening',
            'sales': evening.get('sales', 0),
            'labor_cost': evening.get('labor_cost', 0),
            'labor_hours': evening.get('labor_hours', 0),
            'cash_collected': evening.get('cash_collected', 0),
            'tips_distributed': evening.get('tips_distributed', 0),
            'vendor_payouts': evening.get('total_vendor_payouts', 0),
            'net_cash': evening.get('net_cash', 0),
        })

    return shifts


def transform_vendor_payouts(run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transform pipeline run into vendor_payouts records."""

    cash_flow = run.get('cash_flow', {})
    payouts = []

    # Get payouts from both shifts
    for shift_key in ['morning_shift', 'evening_shift']:
        shift_data = cash_flow.get(shift_key, {})
        shift_payouts = shift_data.get('vendor_payouts', [])

        for payout in shift_payouts:
            payouts.append({
                'business_date': run['date'],
                'restaurant_code': run['restaurant'],
                'amount': payout.get('amount', 0),
                'reason': payout.get('reason'),
                'comments': payout.get('comments'),
                'vendor_name': payout.get('vendor_name'),
                'shift_name': payout.get('shift'),
                'drawer': payout.get('drawer'),
                'manager': payout.get('manager'),
                'payout_time': payout.get('time'),
            })

    return payouts


def backfill_batch_results(json_path: str):
    """Backfill batch results from JSON file to Supabase."""

    print("=" * 80)
    print("SUPABASE BACKFILL")
    print("=" * 80)
    print()

    # Load batch results
    print(f"Loading: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)

    runs = data.get('pipeline_runs', [])
    successful_runs = [r for r in runs if r.get('success')]

    print(f"Total runs: {len(runs)}")
    print(f"Successful: {len(successful_runs)}")
    print()

    if not successful_runs:
        print("[ERROR] No successful runs to backfill")
        return

    # Connect to Supabase
    print("Connecting to Supabase...")
    try:
        client = SupabaseClient()
        print("[OK] Connected")
        print()
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    # Create batch run record
    start_date = min(r['date'] for r in successful_runs)
    end_date = max(r['date'] for r in successful_runs)
    restaurants = list(set(r['restaurant'] for r in successful_runs))

    print(f"Creating batch run record...")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  Restaurants: {', '.join(restaurants)}")

    try:
        batch_id = client.create_batch_run(start_date, end_date, restaurants)
        print(f"[OK] Batch ID: {batch_id}")
        print()
    except Exception as e:
        print(f"[WARNING] Could not create batch run: {e}")
        batch_id = None
        print()

    # Backfill data
    daily_ops = []
    shift_ops = []
    vendor_payouts = []

    print("Transforming data...")
    for run in successful_runs:
        daily_ops.append(transform_daily_operation(run))
        shift_ops.extend(transform_shift_operations(run))
        vendor_payouts.extend(transform_vendor_payouts(run))

    print(f"  Daily operations: {len(daily_ops)}")
    print(f"  Shift operations: {len(shift_ops)}")
    print(f"  Vendor payouts: {len(vendor_payouts)}")
    print()

    # Insert data
    total_inserted = 0

    print("Inserting daily operations...")
    try:
        count = client.insert_daily_operations_batch(daily_ops)
        print(f"[OK] Inserted {count} records")
        total_inserted += count
    except Exception as e:
        print(f"[ERROR] {e}")

    print()
    print("Inserting shift operations...")
    try:
        count = client.insert_shift_operations_batch(shift_ops)
        print(f"[OK] Inserted {count} records")
        total_inserted += count
    except Exception as e:
        print(f"[ERROR] {e}")

    print()
    print("Inserting vendor payouts...")
    try:
        count = client.insert_vendor_payouts_batch(vendor_payouts)
        print(f"[OK] Inserted {count} records")
        total_inserted += count
    except Exception as e:
        print(f"[ERROR] {e}")

    print()

    # Update batch run status
    if batch_id:
        try:
            client.update_batch_run(
                batch_id,
                status='completed',
                records_processed=total_inserted
            )
            print(f"[OK] Batch run updated")
        except Exception as e:
            print(f"[WARNING] Could not update batch run: {e}")

    print()
    print("=" * 80)
    print("BACKFILL COMPLETE")
    print("=" * 80)
    print()
    print(f"Total records inserted: {total_inserted}")
    print()
    print("Verify in Supabase Dashboard:")
    print("  - daily_operations table")
    print("  - shift_operations table")
    print("  - vendor_payouts table")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/backfill_to_supabase.py <batch_results.json>")
        sys.exit(1)

    json_path = sys.argv[1]

    if not Path(json_path).exists():
        print(f"[ERROR] File not found: {json_path}")
        sys.exit(1)

    backfill_batch_results(json_path)
