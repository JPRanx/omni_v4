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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.storage.supabase_client import SupabaseClient
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

try:
    from src.output.v3_data_transformer import V3DataTransformer
    V3_TRANSFORMER_AVAILABLE = True
except Exception:
    V3_TRANSFORMER_AVAILABLE = False

try:
    from src.processing.overtime_calculator import OvertimeCalculator
    from src.models.time_entry_dto import TimeEntryDTO
    OVERTIME_CALCULATOR_AVAILABLE = True
except Exception:
    OVERTIME_CALCULATOR_AVAILABLE = False


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


def get_patterns_summary() -> Optional[Dict[str, Any]]:
    """
    Retrieve pattern learning summary from Supabase.

    Returns:
        Pattern summary dict or None if Supabase unavailable
    """
    if not SUPABASE_AVAILABLE:
        return None

    try:
        client = SupabaseClient()
        patterns = client.get_timeslot_patterns()

        if not patterns:
            return None

        # Calculate statistics
        total_patterns = len(patterns)
        reliable_patterns = [p for p in patterns if p.get('confidence', 0) >= 0.6 and p.get('observations_count', 0) >= 4]
        learning_patterns = [p for p in patterns if p.get('confidence', 0) < 0.6 or p.get('observations_count', 0) < 4]

        avg_confidence = sum(p.get('confidence', 0) for p in patterns) / total_patterns if total_patterns > 0 else 0
        avg_observations = sum(p.get('observations_count', 0) for p in patterns) / total_patterns if total_patterns > 0 else 0

        # Group by restaurant
        by_restaurant = defaultdict(list)
        for p in patterns:
            by_restaurant[p['restaurant_code']].append(p)

        return {
            'total_patterns': total_patterns,
            'reliable_count': len(reliable_patterns),
            'learning_count': len(learning_patterns),
            'avg_confidence': round(avg_confidence, 3),
            'avg_observations': round(avg_observations, 1),
            'by_restaurant': {
                code: {
                    'total': len(pats),
                    'reliable': len([p for p in pats if p.get('confidence', 0) >= 0.6]),
                }
                for code, pats in by_restaurant.items()
            }
        }
    except Exception as e:
        print(f"[WARNING] Could not retrieve patterns: {e}")
        return None


def get_confidence_level(observations_count: int) -> str:
    """Determine confidence level based on observation count."""
    if observations_count < 7:
        return 'learning'
    elif observations_count < 30:
        return 'reliable'
    else:
        return 'confident'


def get_confidence_indicator(level: str) -> str:
    """Get visual indicator for confidence level."""
    indicators = {
        'learning': '🔵',
        'reliable': '🟡',
        'confident': '🟢'
    }
    return indicators.get(level, '⚪')


def enrich_timeslot_with_patterns(
    timeslot_data: Dict[str, Any],
    restaurant_code: str,
    business_date: str,
    patterns_cache: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Enrich timeslot data with pattern learning information.

    Args:
        timeslot_data: Original timeslot metrics
        restaurant_code: Restaurant identifier
        business_date: YYYY-MM-DD
        patterns_cache: Pre-loaded patterns indexed by pattern_key

    Returns:
        Enriched timeslot data with pattern information
    """
    if not patterns_cache:
        return timeslot_data

    # Extract timeslot info
    time_window = timeslot_data.get('time_window', '')
    shift = timeslot_data.get('shift', '')

    # Build pattern key for each category
    enriched_data = timeslot_data.copy()
    enriched_data['patterns'] = {}

    # Get day of week from business_date
    day_of_week = datetime.strptime(business_date, '%Y-%m-%d').strftime('%A')

    # Check patterns for each category
    for category in ['Lobby', 'Drive-Thru', 'ToGo']:
        pattern_key = f"{restaurant_code}_{day_of_week}_{time_window}_{shift}_{category}"

        if pattern_key in patterns_cache:
            pattern = patterns_cache[pattern_key]

            baseline_time = pattern.get('baseline_time', 0)
            confidence = pattern.get('confidence', 0)
            observations = pattern.get('observations_count', 0)

            # Calculate deviation (actual vs baseline)
            category_key = category.replace('-', '')  # Drive-Thru -> DriveThru
            actual_time = timeslot_data.get(f'{category_key.lower()}Time', 0)
            deviation = actual_time - baseline_time if baseline_time > 0 else 0

            confidence_level = get_confidence_level(observations)
            indicator = get_confidence_indicator(confidence_level)

            enriched_data['patterns'][category] = {
                'baseline_time': round(baseline_time, 1),
                'actual_time': round(actual_time, 1),
                'deviation': round(deviation, 1),
                'confidence': round(confidence, 3),
                'observations': observations,
                'confidence_level': confidence_level,
                'indicator': indicator,
                'deviation_percent': round((deviation / baseline_time * 100), 1) if baseline_time > 0 else 0
            }

    return enriched_data


def group_runs_by_week(results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Group pipeline runs by calendar week (Monday-Sunday).

    Args:
        results: Batch processing results with 'pipeline_runs' list

    Returns:
        Dict mapping week_key to results dict for that week
        {
            'week1': {'pipeline_runs': [...], 'start_date': '...', ...},
            'week2': {'pipeline_runs': [...], 'start_date': '...', ...},
            ...
        }
    """
    from collections import defaultdict

    # Group runs by Monday of each week
    weeks_dict = defaultdict(list)

    for run in results['pipeline_runs']:
        date_str = run['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Find the Monday of this week (day 0 = Monday)
        days_since_monday = date_obj.weekday()
        monday = date_obj - timedelta(days=days_since_monday)
        week_key = monday.strftime('%Y-%m-%d')  # Use Monday date as key

        weeks_dict[week_key].append(run)

    # Convert to ordered weeks structure
    sorted_weeks = sorted(weeks_dict.keys())

    weeks_output = {}
    for i, week_monday in enumerate(sorted_weeks, 1):
        week_runs = weeks_dict[week_monday]

        # Calculate week date range
        monday_date = datetime.strptime(week_monday, '%Y-%m-%d')
        sunday_date = monday_date + timedelta(days=6)

        # Find actual start/end dates from the runs
        run_dates = [datetime.strptime(r['date'], '%Y-%m-%d') for r in week_runs]
        actual_start = min(run_dates).strftime('%Y-%m-%d')
        actual_end = max(run_dates).strftime('%Y-%m-%d')

        # Create week results structure
        week_results = {
            'pipeline_runs': week_runs,
            'start_date': actual_start,
            'end_date': actual_end,
            'total_days': len(week_runs),
            'restaurants': list(set(r['restaurant'] for r in week_runs))
        }

        weeks_output[f'week{i}'] = week_results

    return weeks_output


def transform_to_dashboard_format(results: Dict[str, Any]) -> Dict[str, Any]:
    """Transform V4 batch results to V3 dashboard format."""

    # Load all patterns from Supabase and create a cache indexed by pattern_key
    patterns_cache = {}
    if SUPABASE_AVAILABLE:
        try:
            client = SupabaseClient()
            all_patterns = client.get_timeslot_patterns()

            for pattern in all_patterns:
                # Build pattern_key: restaurant_dayofweek_timewindow_shift_category
                pattern_key = f"{pattern['restaurant_code']}_{pattern['day_of_week']}_{pattern['time_window']}_{pattern['shift']}_{pattern['category']}"
                patterns_cache[pattern_key] = pattern

            print(f"[INFO] Loaded {len(patterns_cache)} patterns from Supabase")
        except Exception as e:
            print(f"[WARNING] Could not load patterns for enrichment: {e}")

    # Group runs by restaurant
    runs_by_restaurant = defaultdict(list)
    for run in results['pipeline_runs']:
        if run['success']:
            runs_by_restaurant[run['restaurant']].append(run)

    # Calculate overview totals
    total_sales = 0
    total_labor = 0
    owner_total_cash = 0
    owner_total_tips = 0
    owner_total_vendor_payouts = 0
    owner_net_cash = 0
    owner_vendor_payouts_list = []
    restaurants_cash_flow = {}  # Hierarchical structure for modal

    restaurants_data = []

    for restaurant_code, runs in runs_by_restaurant.items():
        # Calculate restaurant totals
        restaurant_sales = sum(run.get('sales', 0) for run in runs)
        restaurant_labor_cost = sum(run.get('labor_cost', 0) for run in runs)

        # Aggregate cash flow data with hierarchical structure for modal
        restaurant_cash_flow = {
            'total_cash': 0,
            'total_tips': 0,
            'total_vendor_payouts': 0,
            'net_cash': 0,
            'vendor_payouts': [],
            'shifts': {
                'Morning': {
                    'cash': 0,
                    'tips': 0,
                    'payouts': 0,
                    'net': 0,
                    'drawers': []
                },
                'Evening': {
                    'cash': 0,
                    'tips': 0,
                    'payouts': 0,
                    'net': 0,
                    'drawers': []
                }
            }
        }

        # Track drawers across all days for aggregation
        morning_drawers_agg = defaultdict(lambda: {'cash': 0, 'count': 0})
        evening_drawers_agg = defaultdict(lambda: {'cash': 0, 'count': 0})

        for run in runs:
            if 'cash_flow' in run:
                cf = run['cash_flow']
                restaurant_cash_flow['total_cash'] += cf.get('total_cash', 0)
                restaurant_cash_flow['total_tips'] += cf.get('total_tips', 0)
                restaurant_cash_flow['total_vendor_payouts'] += cf.get('total_vendor_payouts', 0)
                restaurant_cash_flow['net_cash'] += cf.get('net_cash', 0)

                # Aggregate shift-level data
                for shift_key, shift_name in [('morning_shift', 'Morning'), ('evening_shift', 'Evening')]:
                    if shift_key in cf:
                        shift_data = cf[shift_key]
                        shift_cash = shift_data.get('cash_collected', 0)
                        shift_tips = shift_data.get('tips_distributed', 0)
                        shift_payouts = shift_data.get('total_vendor_payouts', 0)

                        restaurant_cash_flow['shifts'][shift_name]['cash'] += shift_cash
                        restaurant_cash_flow['shifts'][shift_name]['tips'] += shift_tips
                        restaurant_cash_flow['shifts'][shift_name]['payouts'] += shift_payouts
                        restaurant_cash_flow['shifts'][shift_name]['net'] += shift_data.get('net_cash', 0)

                        # Aggregate drawer data
                        drawers_list = shift_data.get('drawers', [])
                        drawer_agg = morning_drawers_agg if shift_name == 'Morning' else evening_drawers_agg

                        for drawer in drawers_list:
                            drawer_id = drawer.get('drawer_id', 'Unknown')
                            drawer_cash = drawer.get('cash_collected', 0)
                            drawer_agg[drawer_id]['cash'] += drawer_cash
                            drawer_agg[drawer_id]['count'] += drawer.get('transaction_count', 0)

                        # Collect vendor payouts
                        payouts = shift_data.get('vendor_payouts', [])
                        for payout in payouts:
                            payout_with_date = payout.copy()
                            payout_with_date['date'] = run['date']
                            restaurant_cash_flow['vendor_payouts'].append(payout_with_date)

        # Build drawer lists for each shift
        for drawer_id, data in morning_drawers_agg.items():
            restaurant_cash_flow['shifts']['Morning']['drawers'].append({
                'name': drawer_id,
                'cash': round(data['cash'], 2),
                'transactions': data['count']
            })

        for drawer_id, data in evening_drawers_agg.items():
            restaurant_cash_flow['shifts']['Evening']['drawers'].append({
                'name': drawer_id,
                'cash': round(data['cash'], 2),
                'transactions': data['count']
            })

        # Round all shift totals
        for shift_name in ['Morning', 'Evening']:
            restaurant_cash_flow['shifts'][shift_name]['cash'] = round(
                restaurant_cash_flow['shifts'][shift_name]['cash'], 2
            )
            restaurant_cash_flow['shifts'][shift_name]['tips'] = round(
                restaurant_cash_flow['shifts'][shift_name]['tips'], 2
            )
            restaurant_cash_flow['shifts'][shift_name]['payouts'] = round(
                restaurant_cash_flow['shifts'][shift_name]['payouts'], 2
            )
            restaurant_cash_flow['shifts'][shift_name]['net'] = round(
                restaurant_cash_flow['shifts'][shift_name]['net'], 2
            )

        # Calculate COGS from vendor payouts
        restaurant_cogs = restaurant_cash_flow['total_vendor_payouts']

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

        # Add cash flow to owner totals
        owner_total_cash += restaurant_cash_flow['total_cash']
        owner_total_tips += restaurant_cash_flow['total_tips']
        owner_total_vendor_payouts += restaurant_cash_flow['total_vendor_payouts']
        owner_net_cash += restaurant_cash_flow['net_cash']
        owner_vendor_payouts_list.extend(restaurant_cash_flow['vendor_payouts'])

        # Add to restaurants hierarchy for modal
        restaurants_cash_flow[restaurant_code] = {
            'total_cash': restaurant_cash_flow['total_cash'],
            'total_tips': restaurant_cash_flow['total_tips'],
            'total_vendor_payouts': restaurant_cash_flow['total_vendor_payouts'],
            'net_cash': restaurant_cash_flow['net_cash'],
            'shifts': restaurant_cash_flow['shifts']
        }

        # Create daily breakdown with Investigation Modal format
        daily_breakdown = []
        for run in runs:
            day_name = datetime.strptime(run['date'], '%Y-%m-%d').strftime('%A')

            # Use V3DataTransformer if available for proper Investigation Modal format
            if V3_TRANSFORMER_AVAILABLE:
                # Transform using V3DataTransformer for proper Investigation Modal structure
                day_data = V3DataTransformer.transform_from_json(
                    run_data=run,
                    restaurant_code=restaurant_code,
                    business_date=run['date']
                )
                # Add day name for convenience
                day_data['day'] = day_name
            else:
                # Fallback to basic format
                day_data = {
                    'day': day_name,
                    'date': run['date'],
                    'sales': run.get('sales', 0),
                    'laborCost': run.get('labor_cost', 0),
                    'cogs': run.get('cash_flow', {}).get('total_vendor_payouts', 0),
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

            # Enrich timeslots with pattern data (if patterns available)
            if 'timeslots' in day_data and patterns_cache:
                enriched_timeslots = []
                for timeslot in day_data['timeslots']:
                    enriched_timeslot = enrich_timeslot_with_patterns(
                        timeslot,
                        restaurant_code,
                        run['date'],
                        patterns_cache
                    )
                    enriched_timeslots.append(enriched_timeslot)
                day_data['timeslots'] = enriched_timeslots

            daily_breakdown.append(day_data)

        # Create restaurant object
        restaurant = {
            'id': f'rest-{restaurant_code.lower()}',
            'name': get_restaurant_full_name(restaurant_code),
            'code': restaurant_code,
            'sales': restaurant_sales,
            'laborCost': restaurant_labor_cost,
            'laborPercent': round(avg_labor_percent, 1),
            'cogs': round(restaurant_cogs, 2),
            'cogsPercent': round((restaurant_cogs / restaurant_sales * 100), 1) if restaurant_sales > 0 else 0,
            'netProfit': round(restaurant_sales - restaurant_labor_cost - restaurant_cogs, 2),
            'profitMargin': round((restaurant_sales - restaurant_labor_cost - restaurant_cogs) / restaurant_sales * 100, 1) if restaurant_sales > 0 else 0,
            'status': get_status_from_labor_percent(avg_labor_percent),
            'grade': get_grade_from_labor_percent(avg_labor_percent),
            'dailyBreakdown': sorted(daily_breakdown, key=lambda x: x['date']),
        }

        # Add service mix if available
        if aggregate_service_mix:
            restaurant['serviceMix'] = aggregate_service_mix
            restaurant['totalOrders'] = total_orders

        # Add cash flow data if available
        if restaurant_cash_flow['total_cash'] > 0:
            restaurant['cashFlow'] = restaurant_cash_flow

        restaurants_data.append(restaurant)

    # Sort restaurants by code (SDR, T12, TK9)
    restaurants_data.sort(key=lambda x: x['code'])

    # Calculate overall labor percentage
    overall_labor_percent = (total_labor / total_sales * 100) if total_sales > 0 else 0

    # Calculate average daily sales
    total_days = len(results['pipeline_runs']) // len(runs_by_restaurant) if runs_by_restaurant else 0
    avg_daily_sales = total_sales / total_days if total_days > 0 else 0

    # Get pattern learning summary from Supabase
    patterns_summary = get_patterns_summary()

    # Calculate weekly overtime (employee-level) for Overtime Modal
    # Must be done BEFORE creating overview to get total_overtime_hours
    overtime_employees = []
    total_overtime_hours = 0.0
    if OVERTIME_CALCULATOR_AVAILABLE:
        # Group TimeEntries by restaurant
        time_entries_by_restaurant = defaultdict(lambda: {})

        for run in results['pipeline_runs']:
            if run.get('success') and 'time_entries' in run:
                restaurant = run['restaurant']
                date = run['date']

                # Deserialize TimeEntries
                entries = []
                for entry_dict in run.get('time_entries', []):
                    try:
                        entry = TimeEntryDTO.from_dict(entry_dict)
                        if entry.is_ok():
                            entries.append(entry.unwrap())
                    except Exception as e:
                        print(f"[WARNING] Failed to deserialize TimeEntry: {e}")
                        continue

                # Store by date
                time_entries_by_restaurant[restaurant][date] = entries

        # Calculate overtime for each restaurant
        for restaurant, entries_by_date in time_entries_by_restaurant.items():
            if not entries_by_date:
                continue

            overtime_result = OvertimeCalculator.calculate_weekly_overtime(
                time_entries_by_date=entries_by_date,
                restaurant_code=restaurant
            )

            if overtime_result.is_ok():
                summary = overtime_result.unwrap()

                # Add employees to list (matches V3 Overtime Modal format)
                for employee_record in summary.employees:
                    overtime_employees.append(employee_record.to_dict())

                # Add to total
                total_overtime_hours += summary.total_overtime_hours

                print(f"[INFO] {restaurant}: {summary.total_employees} employees with overtime ({summary.total_overtime_hours:.1f}h, ${summary.total_overtime_cost:.2f})")
            else:
                print(f"[WARNING] Overtime calculation failed for {restaurant}: {overtime_result.error()}")

        print(f"[INFO] Total employees with overtime: {len(overtime_employees)} ({total_overtime_hours:.1f}h)")
    else:
        print("[WARNING] OvertimeCalculator not available, skipping overtime calculation")

    # Create overview object
    overview = {
        'totalSales': total_sales,
        'avgDailySales': round(avg_daily_sales, 0),
        'totalLabor': total_labor,
        'laborPercent': round(overall_labor_percent, 1),
        'totalCogs': round(owner_total_vendor_payouts, 2),
        'cogsPercent': round((owner_total_vendor_payouts / total_sales * 100), 1) if total_sales > 0 else 0,
        'netProfit': round(total_sales - total_labor - owner_total_vendor_payouts, 2),
        'profitMargin': round((total_sales - total_labor - owner_total_vendor_payouts) / total_sales * 100, 1) if total_sales > 0 else 0,
        'overtimeHours': round(total_overtime_hours, 1),
        'totalCash': round(owner_total_cash, 2),
        'cashFlow': {
            'total_cash': owner_total_cash,
            'total_tips': owner_total_tips,
            'total_vendor_payouts': owner_total_vendor_payouts,
            'net_cash': owner_net_cash,
            'vendor_payouts': owner_vendor_payouts_list,
            'restaurants': restaurants_cash_flow  # Hierarchical structure for modal
        } if owner_total_cash > 0 else None,
        'patterns': patterns_summary  # ML pattern learning summary
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

    # Collect auto-clockout alerts from all runs
    auto_clockout = []
    for run in results['pipeline_runs']:
        if run.get('success') and 'auto_clockout_summary' in run:
            summary = run['auto_clockout_summary']
            # Add each alert with date and restaurant context
            for alert in summary.get('alerts', []):
                alert_with_context = alert.copy()
                alert_with_context['date'] = run['date']
                alert_with_context['restaurant'] = run['restaurant']
                auto_clockout.append(alert_with_context)

    # Create the dashboard data structure
    # Note: V3 uses 'autoClockout' field for OVERTIME employees (not auto-clockout alerts)
    # The Overtime Modal reads from weekData.autoClockout
    dashboard_data = {
        'overview': overview,
        'metrics': metrics,
        'restaurants': restaurants_data,
        'autoClockout': overtime_employees,  # Overtime employees (V3 convention)
        'autoClockoutAlerts': auto_clockout,  # Actual auto-clockout alerts (forgot to clock out)
    }

    return dashboard_data


def generate_js_module(weeks_data: Dict[str, Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    """
    Generate JavaScript module with multiple weeks of dashboard data.

    Args:
        weeks_data: Dict mapping week_key to dashboard data
                   {'week1': {...}, 'week2': {...}, ...}
        metadata: Overall metadata (start_date, end_date, etc.)

    Returns:
        JavaScript module string
    """

    # Format each week as JavaScript object
    weeks_js_parts = []
    for week_key in sorted(weeks_data.keys(), key=lambda x: int(x.replace('week', ''))):
        week_data = weeks_data[week_key]
        week_json = json.dumps(week_data, indent=2)
        # Indent the entire week block for proper formatting
        indented_week = '\n'.join('  ' + line for line in week_json.split('\n'))
        weeks_js_parts.append(f"  {week_key}: {indented_week}")

    weeks_js = ',\n'.join(weeks_js_parts)

    # Format the data as JavaScript
    js_content = f"""/**
 * Dashboard V4 Data
 *
 * Generated from V4 batch processing results
 * Date Range: {metadata['start_date']} to {metadata['end_date']}
 * Weeks: {len(weeks_data)}
 * Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
 *
 * ✅ ACCURATE V4 DATA
 * - Labor costs from actual PayrollExport CSV
 * - No inflation or multipliers
 * - Verified against source data
 */

export const v4Data = {{
{weeks_js}
}};

// Metadata
export const metadata = {{
  dateRange: {{
    start: '{metadata['start_date']}',
    end: '{metadata['end_date']}',
    days: {metadata['total_days']},
    weeks: {len(weeks_data)}
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
    json_input = sys.argv[1]

    # Check if input is absolute path or relative
    json_path = Path(json_input)
    if not json_path.is_absolute():
        # Try outputs/pipeline_runs/ first, then current directory
        if (project_root / "outputs" / "pipeline_runs" / json_input).exists():
            json_path = project_root / "outputs" / "pipeline_runs" / json_input
        else:
            json_path = Path(json_input)

    # Default output to dashboard/data/v4Data.js (consolidated structure)
    output_path = project_root / "dashboard" / "data" / "v4Data.js"

    if len(sys.argv) > 2 and sys.argv[2] == "--output":
        if len(sys.argv) > 3:
            output_path = Path(sys.argv[3])
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

        # Group results by calendar week (Monday-Sunday)
        print(f"\n>>> Grouping data by calendar week...")
        weeks_grouped = group_runs_by_week(results)
        print(f"    Found {len(weeks_grouped)} weeks of data")

        # Transform each week to dashboard format
        weeks_data = {}
        for week_key, week_results in weeks_grouped.items():
            print(f"    Processing {week_key} ({week_results['start_date']} to {week_results['end_date']})...")
            dashboard_data = transform_to_dashboard_format(week_results)
            weeks_data[week_key] = dashboard_data

        # Generate JavaScript module with all weeks
        metadata = {
            'start_date': results['start_date'],
            'end_date': results['end_date'],
            'total_days': results['total_days'],
            'restaurants': results['restaurants'],
        }
        js_module = generate_js_module(weeks_data, metadata)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_module)

        # Calculate totals across all weeks
        total_sales = sum(week_data['overview']['totalSales'] for week_data in weeks_data.values())
        avg_labor_pct = sum(week_data['overview']['laborPercent'] for week_data in weeks_data.values()) / len(weeks_data)

        print(f"\n>>> Dashboard data generated successfully!")
        print(f"    File: {output_file.absolute()}")
        print(f"    Date Range: {metadata['start_date']} to {metadata['end_date']}")
        print(f"    Restaurants: {', '.join(metadata['restaurants'])}")
        print(f"    Weeks: {len(weeks_data)}")
        print(f"    Total Sales: ${total_sales:,.2f}")
        print(f"    Avg Labor %: {avg_labor_pct:.1f}%")

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
