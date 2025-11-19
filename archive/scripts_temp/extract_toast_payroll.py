"""
Simple Toast PayrollExport Extractor
Extracts employee names and hours from Toast PayrollExport CSV files
"""
import csv
import json
from pathlib import Path
from typing import Dict, List


def extract_payroll_data(payroll_file: str) -> List[Dict]:
    """
    Extract employee names and hours from Toast PayrollExport CSV

    Args:
        payroll_file: Path to PayrollExport_YYYY_MM_DD.csv

    Returns:
        List of dicts with employee name, regular hours, overtime hours, total hours
    """
    employees = []

    with open(payroll_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            employee_name = row.get('Employee', '').strip()
            regular_hours = float(row.get('Regular Hours', 0) or 0)
            overtime_hours = float(row.get('Overtime Hours', 0) or 0)
            total_hours = regular_hours + overtime_hours
            job_title = row.get('Job Title', '').strip()
            location = row.get('Location', '').strip()

            if employee_name:  # Skip empty rows
                employees.append({
                    'name': employee_name,
                    'job_title': job_title,
                    'regular_hours': regular_hours,
                    'overtime_hours': overtime_hours,
                    'total_hours': total_hours,
                    'location': location
                })

    return employees


def extract_all_locations(base_path: str, date_folder: str) -> Dict[str, List[Dict]]:
    """
    Extract payroll data from all restaurant locations

    Args:
        base_path: Path to tests/fixtures/sample_data
        date_folder: Date folder (e.g., '2025-10-20')

    Returns:
        Dict mapping location codes to employee data
    """
    base_dir = Path(base_path) / date_folder
    results = {}

    # Find all PayrollExport files
    for payroll_file in base_dir.glob('*/PayrollExport_*.csv'):
        location_code = payroll_file.parent.name
        employees = extract_payroll_data(str(payroll_file))
        results[location_code] = employees

        print(f"\n{location_code}: Found {len(employees)} employees")
        for emp in employees:
            print(f"  {emp['name']}: {emp['total_hours']:.2f} hours ({emp['job_title']})")

    return results


if __name__ == '__main__':
    # Extract from test fixtures
    base_path = r'C:\Users\Jorge Alexander\omni_v4\tests\fixtures\sample_data'
    date = '2025-10-20'

    print("=" * 80)
    print("TOAST PAYROLL EXPORT EXTRACTION")
    print("=" * 80)

    results = extract_all_locations(base_path, date)

    # Save to JSON
    output_file = r'C:\Users\Jorge Alexander\omni_v4\toast_payroll_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nData saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for location, employees in results.items():
        total_hours = sum(emp['total_hours'] for emp in employees)
        print(f"{location}: {len(employees)} employees, {total_hours:.2f} total hours")
