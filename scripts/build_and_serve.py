#!/usr/bin/env python
"""
Build dashboard data and serve it - One command workflow.

This script automates the complete workflow:
1. Process CSVs with run_date_range.py (optional)
2. Generate dashboard data from batch results
3. Start local server and open browser

Usage:
    # Serve existing data
    python scripts/build_and_serve.py

    # Process new data and serve
    python scripts/build_and_serve.py --dates 2025-08-20 2025-08-31

    # Specify batch results file
    python scripts/build_and_serve.py --batch batch_results_aug_2025.json
"""

import sys
import subprocess
from pathlib import Path
import argparse


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description='Build and serve dashboard')
    parser.add_argument('--dates', nargs=2, metavar=('START', 'END'),
                        help='Process CSVs for date range (YYYY-MM-DD)')
    parser.add_argument('--batch', type=str, default='outputs/pipeline_runs/batch_results_aug_2025_enhanced.json',
                        help='Batch results JSON file (default: outputs/pipeline_runs/batch_results_aug_2025_enhanced.json)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Server port (default: 8080)')
    parser.add_argument('--skip-generation', action='store_true',
                        help='Skip data generation, just serve existing dashboard')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("Restaurant Analytics Dashboard Builder")
    print("="*80 + "\n")

    # Step 1: Process CSVs (optional)
    if args.dates:
        start_date, end_date = args.dates
        batch_output = f"batch_results_{start_date.replace('-', '')}_to_{end_date.replace('-', '')}.json"

        print(f"Step 1: Processing CSVs from {start_date} to {end_date}...")
        cmd = [
            sys.executable,
            str(project_root / "scripts" / "run_date_range.py"),
            "ALL",  # Process all restaurants
            start_date,
            end_date,
            "--output",
            batch_output
        ]

        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode != 0:
            print("\nError: CSV processing failed")
            return False

        args.batch = batch_output
        print(f"CSV processing complete: {batch_output}\n")

    # Step 2: Generate dashboard data
    if not args.skip_generation:
        batch_path = project_root / args.batch

        if not batch_path.exists():
            print(f"Error: Batch results file not found: {batch_path}")
            print("\nAvailable batch files:")
            pipeline_runs_dir = project_root / "outputs" / "pipeline_runs"
            if pipeline_runs_dir.exists():
                for f in pipeline_runs_dir.glob("batch_results_*.json"):
                    print(f"  - outputs/pipeline_runs/{f.name}")
            return False

        print(f"Step 2: Generating dashboard data from {args.batch}...")
        cmd = [
            sys.executable,
            str(project_root / "scripts" / "generate_dashboard_data.py"),
            str(batch_path)
        ]

        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode != 0:
            print("\nError: Dashboard data generation failed")
            return False

        print("Dashboard data generated\n")

    # Step 3: Serve dashboard
    print(f"Step 3: Starting dashboard server on port {args.port}...")
    cmd = [
        sys.executable,
        str(project_root / "scripts" / "serve_dashboard.py"),
        "--port",
        str(args.port)
    ]

    subprocess.run(cmd, cwd=project_root)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
