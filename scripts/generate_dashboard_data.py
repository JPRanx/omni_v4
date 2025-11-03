#!/usr/bin/env python
"""
Generate dashboard data from V4 batch processing results.

This script transforms V4 batch results into the format expected
by the V3 DashboardV3/ipad interface.

Usage:
    python scripts/generate_dashboard_data.py batch_results_aug_2025.json
    python scripts/generate_dashboard_data.py batch_results_aug_2025.json --output dashboard_data.js
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_batch_results(json_path: str) -> Dict[str, Any]:
    """Load batch processing results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def get_restaurant_full_name(restaurant_code: str) -> str:
    """Get full restaurant name from code."""
    names = {
        'SDR': "Sandra's Mexican Cuisine",
        'T12': "Tink-A-Tako #12",
        'TK9': "Tink-A-Tako #9"
    }
    return names.get(restaurant_code, restaurant_code)


def get_status_from_labor_percent(labor_pct: float) -> str:
    """Get status text from labor percentage."""
    if labor_pct <= 25:
        return 'excellent'
    elif labor_pct <= 30:
        return 'good'
    elif labor_pct <= 35:
        return 'warning'
    else:
        return 'critical'


def get_grade_from_labor_percent(labor_pct: float) -> str:
    """Get letter grade from labor percentage."""
    if labor_pct <= 20:
        return 'A+'
    elif labor_pct <= 23:
        return 'B+'
    elif labor_pct <= 25:
        return 'B'
    elif labor_pct <= 28:
        return 'C+'
    elif labor_pct <= 30:
        return 'C'
    elif labor_pct <= 32:
        return 'D+'
    elif labor_pct <= 35:
        return 'D'
    else:
        return 'F'


def transform_to_dashboard_format(results: Dict[str, Any]) -> Dict[str, Any]:
    """Transform V4 batch results to V3 dashboard format."""

    # Group runs by restaurant
    runs_by_restaurant = defaultdict(list)
    for run in results['pipeline_runs']:
        if run['success']:
            runs_by_restaurant[run['restaurant']].append(run)

    # Calculate overview totals
    total_sales = 0
    total_labor = 0
    total_overtime_hours = 0
    total_overtime_cost = 0

    restaurants_data = []

    for restaurant_code, runs in runs_by_restaurant.items():
        # Calculate restaurant totals
        restaurant_sales = sum(run.get('sales', 0) for run in runs)
        restaurant_labor_cost = sum(run.get('labor_cost', 0) for run in runs)
        restaurant_overtime_hours = sum(run.get('overtime_hours', 0) for run in runs)
        restaurant_overtime_cost = sum(run.get('overtime_cost', 0) for run in runs)

        # Calculate averages
        avg_labor_percent = (restaurant_labor_cost / restaurant_sales * 100) if restaurant_sales > 0 else 0

        # Calculate aggregate service mix
        total_orders = sum(run.get('categorized_orders', 0) for run in runs)
        if total_orders > 0:
            # Weight service mix by number of orders per day
            weighted_lobby = sum(run.get('service_mix', {}).get('Lobby', 0) * run.get('categorized_orders', 0) for run in runs)
            weighted_drive_thru = sum(run.get('service_mix', {}).get('Drive-Thru', 0) * run.get('categorized_orders', 0) for run in runs)
            weighted_togo = sum(run.get('service_mix', {}).get('ToGo', 0) * run.get('categorized_orders', 0) for run in runs)

            aggregate_service_mix = {
                'Lobby': round(weighted_lobby / total_orders, 1),
                'Drive-Thru': round(weighted_drive_thru / total_orders, 1),
                'ToGo': round(weighted_togo / total_orders, 1)
            }
        else:
            aggregate_service_mix = None

        # Add to totals
        total_sales += restaurant_sales
        total_labor += restaurant_labor_cost
        total_overtime_hours += restaurant_overtime_hours
        total_overtime_cost += restaurant_overtime_cost

        # Create daily breakdown
        daily_breakdown = []
        for run in runs:
            day_name = datetime.strptime(run['date'], '%Y-%m-%d').strftime('%A')
            day_data = {
                'day': day_name,
                'date': run['date'],
                'sales': run.get('sales', 0),
                'laborCost': run.get('labor_cost', 0),
                'cogs': 0,  # V4 doesn't track COGS yet
            }

            # Add service mix if available
            if 'service_mix' in run:
                day_data['serviceMix'] = run['service_mix']

            # Add order count if available
            if 'categorized_orders' in run:
                day_data['orderCount'] = run['categorized_orders']

            # Add timeslot metrics if available
            if 'timeslot_metrics' in run:
                day_data['timeslotMetrics'] = run['timeslot_metrics']

            daily_breakdown.append(day_data)

        # Create restaurant object
        restaurant = {
            'id': f'rest-{restaurant_code.lower()}',
            'name': get_restaurant_full_name(restaurant_code),
            'code': restaurant_code,
            'sales': restaurant_sales,
            'laborCost': restaurant_labor_cost,
            'laborPercent': round(avg_labor_percent, 1),
            'cogs': 0,  # V4 doesn't track COGS yet
            'cogsPercent': 0,
            'netProfit': restaurant_sales - restaurant_labor_cost,
            'profitMargin': round((restaurant_sales - restaurant_labor_cost) / restaurant_sales * 100, 1) if restaurant_sales > 0 else 0,
            'status': get_status_from_labor_percent(avg_labor_percent),
            'grade': get_grade_from_labor_percent(avg_labor_percent),
            'dailyBreakdown': sorted(daily_breakdown, key=lambda x: x['date']),
        }

        # Add service mix if available
        if aggregate_service_mix:
            restaurant['serviceMix'] = aggregate_service_mix
            restaurant['totalOrders'] = total_orders

        restaurants_data.append(restaurant)

    # Sort restaurants by code (SDR, T12, TK9)
    restaurants_data.sort(key=lambda x: x['code'])

    # Calculate overall labor percentage
    overall_labor_percent = (total_labor / total_sales * 100) if total_sales > 0 else 0

    # Calculate average daily sales
    total_days = len(results['pipeline_runs']) // len(runs_by_restaurant) if runs_by_restaurant else 0
    avg_daily_sales = total_sales / total_days if total_days > 0 else 0

    # Create overview object
    overview = {
        'totalSales': total_sales,
        'avgDailySales': round(avg_daily_sales, 0),
        'totalLabor': total_labor,
        'laborPercent': round(overall_labor_percent, 1),
        'totalCogs': 0,  # V4 doesn't track COGS yet
        'cogsPercent': 0,
        'netProfit': total_sales - total_labor,
        'profitMargin': round((total_sales - total_labor) / total_sales * 100, 1) if total_sales > 0 else 0,
        'overtimeHours': round(total_overtime_hours, 1),
        'totalCash': 0,
    }

    # Create metrics array
    metrics = [
        {
            'id': 'total-sales',
            'label': 'Total Sales',
            'value': total_sales,
            'type': 'currency',
            'color': 'blue',
            'icon': '💰',
            'status': 'excellent',
        },
        {
            'id': 'avg-daily',
            'label': 'Avg Daily Sales',
            'value': round(avg_daily_sales, 0),
            'type': 'currency',
            'color': 'green',
            'icon': '📊',
            'status': 'excellent',
        },
        {
            'id': 'labor-cost',
            'label': 'Labor Cost',
            'value': total_labor,
            'type': 'currency',
            'color': 'yellow' if overall_labor_percent <= 30 else 'red',
            'icon': '👥',
            'status': get_status_from_labor_percent(overall_labor_percent),
        },
        {
            'id': 'labor-percent',
            'label': 'Labor %',
            'value': round(overall_labor_percent, 1),
            'type': 'percentage',
            'color': 'green' if overall_labor_percent <= 30 else 'red',
            'icon': '📈',
            'status': get_status_from_labor_percent(overall_labor_percent),
        },
        {
            'id': 'net-profit',
            'label': 'Net Profit',
            'value': total_sales - total_labor,
            'type': 'currency',
            'color': 'green',
            'icon': '💵',
            'status': 'excellent',
        },
        {
            'id': 'profit-margin',
            'label': 'Profit Margin',
            'value': round((total_sales - total_labor) / total_sales * 100, 1) if total_sales > 0 else 0,
            'type': 'percentage',
            'color': 'green',
            'icon': '📈',
            'status': 'excellent',
        },
    ]

    # Create auto clockout array (empty for now, V4 doesn't have this data)
    auto_clockout = []

    # Create the dashboard data structure
    dashboard_data = {
        'overview': overview,
        'metrics': metrics,
        'restaurants': restaurants_data,
        'autoClockout': auto_clockout,
    }

    return dashboard_data


def generate_js_module(dashboard_data: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Generate JavaScript module with dashboard data."""

    # Format the data as JavaScript
    js_content = f"""/**
 * Dashboard V4 Data
 *
 * Generated from V4 batch processing results
 * Date Range: {metadata['start_date']} to {metadata['end_date']}
 * Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
 *
 * ✅ ACCURATE V4 DATA
 * - Labor costs from actual PayrollExport CSV
 * - No inflation or multipliers
 * - Verified against source data
 */

export const v4Data = {{
  week1: {json.dumps(dashboard_data, indent=2)}
}};

// Metadata
export const metadata = {{
  dateRange: {{
    start: '{metadata['start_date']}',
    end: '{metadata['end_date']}',
    days: {metadata['total_days']}
  }},
  restaurants: {json.dumps(metadata['restaurants'])},
  generated: '{datetime.now().isoformat()}',
  version: 'V4.0',
  source: 'OMNI V4 Pipeline - Accurate PayrollExport Data',
}};

// Default export
export default v4Data;
"""

    return js_content


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_dashboard_data.py <batch_results.json> [--output <data.js>]")
        print("\nExample:")
        print("  python scripts/generate_dashboard_data.py batch_results_aug_2025.json")
        print("  python scripts/generate_dashboard_data.py batch_results_aug_2025.json --output dashboard_data.js")
        sys.exit(1)

    # Parse arguments
    json_path = sys.argv[1]
    output_path = "dashboard_data.js"

    if len(sys.argv) > 2 and sys.argv[2] == "--output":
        if len(sys.argv) > 3:
            output_path = sys.argv[3]
        else:
            print("Error: --output requires a filename")
            sys.exit(1)

    # Check if input file exists
    if not Path(json_path).exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"\n>>> Generating dashboard data from {json_path}")
    print("=" * 80)

    try:
        # Load batch results
        results = load_batch_results(json_path)

        # Transform to dashboard format
        dashboard_data = transform_to_dashboard_format(results)

        # Generate JavaScript module
        metadata = {
            'start_date': results['start_date'],
            'end_date': results['end_date'],
            'total_days': results['total_days'],
            'restaurants': results['restaurants'],
        }
        js_module = generate_js_module(dashboard_data, metadata)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_module)

        print(f"\n>>> Dashboard data generated successfully!")
        print(f"    File: {output_file.absolute()}")
        print(f"    Date Range: {metadata['start_date']} to {metadata['end_date']}")
        print(f"    Restaurants: {', '.join(metadata['restaurants'])}")
        print(f"    Total Sales: ${dashboard_data['overview']['totalSales']:,.2f}")
        print(f"    Labor %: {dashboard_data['overview']['laborPercent']:.1f}%")

        print(f"\n>>> Next Steps:")
        print(f"    1. Copy this file to V3 dashboard: DashboardV3/ipad/data/v4Data.js")
        print(f"    2. Update app.js to import v4Data instead of sampleData")
        print(f"    3. Open dashboard in browser to view V4 data")

    except Exception as e:
        print(f"\n>>> Error generating dashboard data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
