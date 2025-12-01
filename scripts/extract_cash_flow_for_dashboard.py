#!/usr/bin/env python
"""
Extract cash flow data from test fixtures and add to dashboard data.

This script:
1. Reads existing batch_results.json
2. Extracts cash flow from CSV files for each run
3. Adds cash_flow data to runs
4. Saves updated batch_results
5. Regenerates dashboard data

Usage:
    python scripts/extract_cash_flow_for_dashboard.py
    python scripts/extract_cash_flow_for_dashboard.py --input batch_results_aug_2025.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.services.cash_flow_extractor import CashFlowExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_cash_flow_for_run(
    restaurant_code: str,
    business_date: str,
    extractor: CashFlowExtractor
) -> Dict[str, Any]:
    """
    Extract cash flow data for a single run.

    Args:
        restaurant_code: SDR, T12, or TK9
        business_date: YYYY-MM-DD format
        extractor: CashFlowExtractor instance

    Returns:
        Dictionary with cash flow data or None if extraction fails
    """
    # Construct CSV directory path
    csv_dir = project_root / "tests" / "fixtures" / "sample_data" / business_date / restaurant_code

    if not csv_dir.exists():
        logger.warning(f"CSV directory not found: {csv_dir}")
        return None

    # Extract cash flow
    result = extractor.extract_from_csvs(
        csv_dir=csv_dir,
        business_date=business_date,
        restaurant_code=restaurant_code
    )

    if result.is_ok():
        cash_flow = result.unwrap()
        return cash_flow.to_dict()
    else:
        logger.warning(f"Cash flow extraction failed for {restaurant_code} on {business_date}: {result.unwrap_err()}")
        return None


def add_cash_flow_to_batch_results(input_file: str, output_file: str = None):
    """
    Add cash flow data to existing batch results.

    Args:
        input_file: Path to existing batch_results.json
        output_file: Path for output (defaults to same as input)
    """
    input_path = project_root / "outputs" / "pipeline_runs" / input_file

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    # Load existing results
    with open(input_path, 'r') as f:
        batch_results = json.load(f)

    logger.info(f"Loaded {len(batch_results.get('pipeline_runs', []))} pipeline runs")

    # Create extractor
    extractor = CashFlowExtractor()

    # Process each run
    runs_updated = 0
    runs_skipped = 0

    for run in batch_results.get('pipeline_runs', []):
        if not run.get('success', False):
            runs_skipped += 1
            continue

        restaurant = run.get('restaurant')
        date = run.get('date')

        if not restaurant or not date:
            runs_skipped += 1
            continue

        # Skip if already has cash flow
        if 'cash_flow' in run:
            logger.debug(f"{restaurant} {date}: Already has cash flow data")
            runs_updated += 1
            continue

        # Extract cash flow
        logger.info(f"Extracting cash flow for {restaurant} on {date}")
        cash_flow_data = extract_cash_flow_for_run(restaurant, date, extractor)

        if cash_flow_data:
            run['cash_flow'] = cash_flow_data
            runs_updated += 1
            logger.info(f"  Added: ${cash_flow_data['total_cash']:.2f} cash, "
                       f"${cash_flow_data['total_tips']:.2f} tips, "
                       f"${cash_flow_data['net_cash']:.2f} net")
        else:
            runs_skipped += 1

    # Save updated results
    if output_file is None:
        output_file = input_file

    output_path = project_root / "outputs" / "pipeline_runs" / output_file

    with open(output_path, 'w') as f:
        json.dump(batch_results, f, indent=2)

    logger.info(f"\nResults:")
    logger.info(f"  Runs updated: {runs_updated}")
    logger.info(f"  Runs skipped: {runs_skipped}")
    logger.info(f"  Output saved to: {output_path}")

    return output_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract cash flow data and add to batch results",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input',
        default='batch_results_aug_2025_enhanced.json',
        help='Input batch results file (default: batch_results_aug_2025_enhanced.json)'
    )

    parser.add_argument(
        '--output',
        default=None,
        help='Output file (defaults to same as input)'
    )

    args = parser.parse_args()

    # Add cash flow to batch results
    output_path = add_cash_flow_to_batch_results(args.input, args.output)

    if output_path:
        logger.info(f"\nNext steps:")
        logger.info(f"1. Regenerate dashboard data:")
        logger.info(f"   python scripts/generate_dashboard_data.py {args.input}")
        logger.info(f"2. Serve dashboard:")
        logger.info(f"   python scripts/serve_dashboard.py")


if __name__ == "__main__":
    main()
