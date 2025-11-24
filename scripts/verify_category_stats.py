"""
Multi-Day Category Stats Verification Script

Checks multiple days to identify if category_stats undercounting is:
1. Systematic (code bug affecting all days)
2. Data-specific (only certain days/restaurants)
3. Isolated (specific dates like power outage)
"""

import pandas as pd
from pathlib import Path
import json
from typing import Dict, List
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.order_categorizer import OrderCategorizer


def verify_day(data_dir: Path, restaurant: str, date: str) -> Dict:
    """
    Verify category stats for a single day.

    Returns dict with counts at each stage.
    """
    result = {
        'restaurant': restaurant,
        'date': date,
        'csv_files': {},
        'categorization': {},
        'error': None
    }

    # Check if directory exists
    day_dir = data_dir / date / restaurant
    if not day_dir.exists():
        result['error'] = f"Directory not found: {day_dir}"
        return result

    try:
        # Step 1: Count CSV files
        kitchen_files = list(day_dir.glob("*Kitchen*Details*.csv"))
        order_files = list(day_dir.glob("*Order*Details*.csv")) or list(day_dir.glob("*OrderDetails*.csv"))
        eod_files = list(day_dir.glob("*EOD*.csv"))

        if not kitchen_files or not order_files or not eod_files:
            result['error'] = f"Missing CSV files in {day_dir}"
            result['csv_files'] = {
                'kitchen_found': len(kitchen_files),
                'order_found': len(order_files),
                'eod_found': len(eod_files)
            }
            return result

        # Read CSV files
        kitchen_df = pd.read_csv(kitchen_files[0])
        order_df = pd.read_csv(order_files[0])
        eod_df = pd.read_csv(eod_files[0])

        result['csv_files'] = {
            'kitchen_details': len(kitchen_df),
            'order_details': len(order_df),
            'eod': len(eod_df)
        }

        # Step 2: Run categorization
        categorizer = OrderCategorizer()
        categorization_result = categorizer.categorize_all_orders(
            kitchen_df,
            eod_df,
            order_df,
            None  # No labor file
        )

        if categorization_result.is_err():
            result['error'] = f"Categorization failed: {categorization_result.unwrap_err()}"
            return result

        order_categories = categorization_result.unwrap()

        # Count by category
        category_counts = {
            'Lobby': 0,
            'Drive-Thru': 0,
            'ToGo': 0
        }

        for check_num, category in order_categories.items():
            if category in category_counts:
                category_counts[category] += 1

        result['categorization'] = {
            'total_categorized': len(order_categories),
            'lobby': category_counts['Lobby'],
            'drive_thru': category_counts['Drive-Thru'],
            'togo': category_counts['ToGo']
        }

        # Step 3: Check if we have pipeline results for this day
        # Look in outputs/pipeline_runs for this date
        pipeline_runs_dir = data_dir.parent / 'outputs' / 'pipeline_runs'
        if pipeline_runs_dir.exists():
            # Find matching pipeline result
            for result_file in pipeline_runs_dir.glob(f"*{restaurant}*{date}*.json"):
                try:
                    with open(result_file, 'r') as f:
                        pipeline_data = json.load(f)

                    # Extract shift_category_stats if available
                    if 'shift_category_stats' in pipeline_data:
                        stats = pipeline_data['shift_category_stats']
                        morning_total = sum(s['total'] for s in stats.get('Morning', {}).values())
                        evening_total = sum(s['total'] for s in stats.get('Evening', {}).values())

                        result['shift_category_stats'] = {
                            'morning_total': morning_total,
                            'evening_total': evening_total,
                            'combined_total': morning_total + evening_total,
                            'missing': len(order_categories) - (morning_total + evening_total)
                        }
                except Exception as e:
                    pass

        return result

    except Exception as e:
        result['error'] = f"Exception: {str(e)}"
        return result


def print_report(results: List[Dict]):
    """Print formatted verification report."""

    print("\n" + "="*80)
    print(" MULTI-DAY CATEGORY STATS VERIFICATION REPORT")
    print("="*80 + "\n")

    for i, result in enumerate(results, 1):
        print(f"Day {i}: {result['restaurant']} {result['date']}")
        print("-" * 60)

        if result['error']:
            print(f"  ERROR: {result['error']}\n")
            continue

        csv = result['csv_files']
        cat = result['categorization']

        print(f"  CSV Files:")
        print(f"    Kitchen Details: {csv['kitchen_details']} rows")
        print(f"    Order Details:   {csv['order_details']} rows")
        print(f"    EOD:             {csv['eod']} rows")
        print()

        print(f"  After Categorization:")
        print(f"    Total Categorized: {cat['total_categorized']}")
        print(f"    - Lobby:           {cat['lobby']}")
        print(f"    - Drive-Thru:      {cat['drive_thru']}")
        print(f"    - ToGo:            {cat['togo']}")

        # Calculate missing from CSV to categorized
        csv_vs_cat_missing = csv['order_details'] - cat['total_categorized']
        if csv_vs_cat_missing > 0:
            print(f"    WARNING MISSING: {csv_vs_cat_missing} orders not categorized!")
        print()

        # Check shift_category_stats if available
        if 'shift_category_stats' in result:
            stats = result['shift_category_stats']
            print(f"  In shift_category_stats:")
            print(f"    Morning Total: {stats['morning_total']}")
            print(f"    Evening Total: {stats['evening_total']}")
            print(f"    Combined:      {stats['combined_total']}")

            if stats['missing'] > 0:
                print(f"    ALERT MISSING: {stats['missing']} orders ({stats['missing']/cat['total_categorized']*100:.1f}% lost!)")
        else:
            print(f"  WARNING: No pipeline results found for this day")

        print()

    print("="*80)
    print(" ANALYSIS")
    print("="*80 + "\n")

    # Analyze patterns
    successful = [r for r in results if not r['error']]

    if not successful:
        print("ERROR: All days failed - cannot analyze patterns")
        return

    # Check if all days have same pattern
    missing_percentages = []
    for r in successful:
        if 'shift_category_stats' in r:
            cat_total = r['categorization']['total_categorized']
            stats_total = r['shift_category_stats']['combined_total']
            if cat_total > 0:
                missing_pct = (cat_total - stats_total) / cat_total * 100
                missing_percentages.append(missing_pct)

    if missing_percentages:
        avg_missing = sum(missing_percentages) / len(missing_percentages)

        if all(abs(pct - avg_missing) < 5 for pct in missing_percentages):
            print(f"PATTERN: Consistent ~{avg_missing:.0f}% missing across all days")
            print(f"   -> This indicates a SYSTEMATIC CODE BUG")
        else:
            print(f"PATTERN: Variable missing rates ({min(missing_percentages):.0f}% to {max(missing_percentages):.0f}%)")
            print(f"   -> This indicates a DATA QUALITY ISSUE")

    print()


def main():
    """Run multi-day verification."""

    # Data directory
    data_dir = Path(__file__).parent.parent / 'data'

    # Days to check
    test_cases = [
        ('SDR', '2025-08-20'),  # Early in dataset
        ('SDR', '2025-09-15'),  # Middle of dataset
        ('SDR', '2025-10-20'),  # The Monday with possible power outage
        ('SDR', '2025-10-29'),  # Most recent
    ]

    print("Starting multi-day verification...")
    print(f"Data directory: {data_dir}\n")

    results = []
    for restaurant, date in test_cases:
        print(f"Checking {restaurant} {date}...", end=' ')
        result = verify_day(data_dir, restaurant, date)
        results.append(result)

        if result['error']:
            print(f"ERROR: {result['error']}")
        else:
            cat_total = result['categorization']['total_categorized']
            print(f"OK: {cat_total} orders categorized")

    # Print full report
    print_report(results)


if __name__ == '__main__':
    main()