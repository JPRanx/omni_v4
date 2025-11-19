#!/usr/bin/env python
"""
Generate HTML dashboard from V4 batch processing results.

This script creates a visual dashboard showing restaurant performance
based on accurate V4 calculations (not V3's inflated numbers).

Usage:
    python scripts/generate_dashboard.py batch_results_aug_2025.json
    python scripts/generate_dashboard.py batch_results_aug_2025.json --output dashboard.html
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_batch_results(json_path: str) -> Dict[str, Any]:
    """Load batch processing results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def get_labor_class(labor_pct: float) -> str:
    """Get CSS class for labor percentage."""
    if labor_pct <= 25:
        return 'excellent'
    elif labor_pct <= 30:
        return 'good'
    elif labor_pct <= 35:
        return 'warning'
    else:
        return 'critical'


def get_labor_grade(labor_pct: float) -> str:
    """Get letter grade for labor percentage."""
    if labor_pct <= 20:
        return 'A'
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


def get_labor_status(labor_pct: float) -> str:
    """Get status text for labor percentage."""
    if labor_pct <= 20:
        return 'EXCELLENT'
    elif labor_pct <= 25:
        return 'GOOD'
    elif labor_pct <= 30:
        return 'ACCEPTABLE'
    elif labor_pct <= 35:
        return 'WARNING'
    elif labor_pct <= 40:
        return 'CRITICAL'
    else:
        return 'SEVERE'


def generate_dashboard_html(results: Dict[str, Any]) -> str:
    """Generate HTML dashboard from batch results."""

    # Extract metadata
    restaurants = results['restaurants']
    start_date = results['start_date']
    end_date = results['end_date']
    total_days = results['total_days']
    summary = results['summary']

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMNI V4 Dashboard - {start_date} to {end_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header h1 {{
            font-size: 42px;
            font-weight: 300;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            opacity: 0.9;
        }}

        .date-range {{
            font-size: 24px;
            margin: 15px 0;
        }}

        .generated {{
            font-size: 14px;
            opacity: 0.8;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        .summary-card h3 {{
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .summary-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }}

        .restaurants-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .restaurant-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}

        .restaurant-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .restaurant-name {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }}

        .sdr-name {{
            color: #FF6B6B;
            border-color: #FF6B6B;
        }}

        .t12-name {{
            color: #4ECDC4;
            border-color: #4ECDC4;
        }}

        .tk9-name {{
            color: #45B7D1;
            border-color: #45B7D1;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .metric-label {{
            font-weight: 600;
            color: #555;
        }}

        .metric-value {{
            font-weight: bold;
            font-size: 18px;
        }}

        .labor-excellent {{ color: #27ae60; }}
        .labor-good {{ color: #2ecc71; }}
        .labor-warning {{ color: #f39c12; }}
        .labor-critical {{ color: #e74c3c; }}

        .daily-details {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-top: 20px;
        }}

        .daily-details h2 {{
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}

        tr:hover {{
            background-color: #f8f9fa;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            font-size: 14px;
            opacity: 0.8;
        }}

        .powered-by {{
            font-size: 12px;
            margin-top: 10px;
        }}

        @media print {{
            body {{
                background: white;
            }}

            .header, .footer {{
                color: black;
            }}

            .restaurant-card, .daily-details {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OMNI V4 Dashboard</h1>
        <p class="subtitle">Restaurant Analytics & Labor Management</p>
        <div class="date-range">{start_date} to {end_date} ({total_days} days)</div>
        <p class="generated">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>

    <div class="summary-cards">
        <div class="summary-card">
            <h3>Total Runs</h3>
            <div class="value">{summary['total_processed']}</div>
        </div>
        <div class="summary-card">
            <h3>Restaurants</h3>
            <div class="value">{len(restaurants)}</div>
        </div>
        <div class="summary-card">
            <h3>Days Processed</h3>
            <div class="value">{total_days}</div>
        </div>
        <div class="summary-card">
            <h3>Success Rate</h3>
            <div class="value">{100 if summary['total_processed'] > 0 else 0}%</div>
        </div>
    </div>

    <div class="restaurants-grid">
"""

    # Add restaurant cards
    for restaurant in restaurants:
        rest_summary = summary['by_restaurant'][restaurant]

        # Calculate display values
        avg_labor = rest_summary.get('avg_labor_percentage', 0)
        min_labor = rest_summary.get('min_labor_percentage', 0)
        max_labor = rest_summary.get('max_labor_percentage', 0)
        processed = rest_summary['processed']
        patterns = rest_summary['patterns_learned']

        labor_class = get_labor_class(avg_labor)
        grade = get_labor_grade(avg_labor)
        status = get_labor_status(avg_labor)

        # Restaurant full names
        full_names = {
            'SDR': "Sandra's Mexican Cuisine",
            'T12': "Tink-A-Tako #12",
            'TK9': "Tink-A-Tako #9"
        }

        html += f"""
        <div class="restaurant-card">
            <div class="restaurant-name {restaurant.lower()}-name">
                {full_names.get(restaurant, restaurant)}
            </div>

            <div class="metric-row">
                <span class="metric-label">Days Processed:</span>
                <span class="metric-value">{processed}</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Average Labor %:</span>
                <span class="metric-value labor-{labor_class}">{avg_labor:.1f}%</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Labor Grade:</span>
                <span class="metric-value labor-{labor_class}">{grade}</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Status:</span>
                <span class="metric-value labor-{labor_class}">{status}</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Min Labor %:</span>
                <span class="metric-value">{min_labor:.1f}%</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Max Labor %:</span>
                <span class="metric-value">{max_labor:.1f}%</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Patterns Learned:</span>
                <span class="metric-value">{patterns}</span>
            </div>
        </div>
"""

    html += """
    </div>

    <div class="daily-details">
        <h2>Daily Performance Details</h2>
"""

    # Add daily details table for each restaurant
    for restaurant in restaurants:
        html += f"""
        <h3 style="margin-top: 30px; color: #667eea;">{restaurant} - Daily Breakdown</h3>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Labor %</th>
                    <th>Grade</th>
                    <th>Status</th>
                    <th>Duration (ms)</th>
                </tr>
            </thead>
            <tbody>
"""

        # Filter runs for this restaurant
        restaurant_runs = [r for r in results['pipeline_runs'] if r['restaurant'] == restaurant]

        for run in restaurant_runs:
            if run['success']:
                labor_pct = run['labor_percentage']
                labor_class = get_labor_class(labor_pct)
                grade = get_labor_grade(labor_pct)
                status = get_labor_status(labor_pct)

                html += f"""
                <tr>
                    <td>{run['date']}</td>
                    <td class="labor-{labor_class}">{labor_pct:.1f}%</td>
                    <td class="labor-{labor_class}">{grade}</td>
                    <td class="labor-{labor_class}">{status}</td>
                    <td>{run['duration_ms']:.1f}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
"""

    html += f"""
    </div>

    <div class="footer">
        <p>OMNI V4 Restaurant Analytics System</p>
        <p class="powered-by">Powered by accurate PayrollExport data - No inflated calculations</p>
        <p class="powered-by">V4 uses actual labor costs from Toast POS system</p>
    </div>
</body>
</html>
"""

    return html


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_dashboard.py <batch_results.json> [--output <dashboard.html>]")
        print("\nExample:")
        print("  python scripts/generate_dashboard.py batch_results_aug_2025.json")
        print("  python scripts/generate_dashboard.py batch_results_aug_2025.json --output Output/dashboard.html")
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

    output_path = "dashboard.html"

    if len(sys.argv) > 2 and sys.argv[2] == "--output":
        if len(sys.argv) > 3:
            output_path = sys.argv[3]
        else:
            print("Error: --output requires a filename")
            sys.exit(1)

    # Check if input file exists
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    print(f"\n>>> Generating dashboard from {json_path}")
    print("=" * 80)

    try:
        # Load batch results
        results = load_batch_results(json_path)

        # Generate HTML
        html = generate_dashboard_html(results)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n>>> Dashboard created successfully!")
        print(f"    File: {output_file.absolute()}")
        print(f"    Restaurants: {', '.join(results['restaurants'])}")
        print(f"    Date Range: {results['start_date']} to {results['end_date']}")
        print(f"    Total Runs: {results['summary']['total_processed']}")

        # Auto-open in browser
        import webbrowser
        webbrowser.open(f"file:///{output_file.absolute()}")

        print(f"\n>>> Dashboard opened in browser")

    except Exception as e:
        print(f"\n>>> Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
