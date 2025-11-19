"""
Compare Toast PayrollExport vs TimeEntries data
Shows the difference between the two data sources
"""
import csv
from pathlib import Path
from typing import List, Dict


def read_payroll_export(file_path: str) -> List[Dict]:
    """Read PayrollExport CSV"""
    employees = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Employee', '').strip():
                employees.append({
                    'name': row['Employee'].strip(),
                    'job_title': row['Job Title'].strip(),
                    'regular_hours': float(row.get('Regular Hours', 0) or 0),
                    'overtime_hours': float(row.get('Overtime Hours', 0) or 0),
                    'total_hours': float(row.get('Regular Hours', 0) or 0) + float(row.get('Overtime Hours', 0) or 0)
                })
    return employees


def read_time_entries(file_path: str) -> List[Dict]:
    """Read TimeEntries CSV"""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Employee', '').strip():
                entries.append({
                    'name': row['Employee'].strip(),
                    'job_title': row['Job Title'].strip(),
                    'in_date': row['In Date'].strip(),
                    'out_date': row['Out Date'].strip(),
                    'payable_hours': float(row.get('Payable Hours', 0) or 0)
                })
    return entries


def compare_sources(location: str, base_path: str, date: str):
    """Compare both data sources for a location"""
    location_path = Path(base_path) / date / location

    payroll_file = location_path / f'PayrollExport_{date.replace("-", "_")}.csv'
    timeentries_file = location_path / f'TimeEntries_{date.replace("-", "_")}.csv'

    print(f"\n{'=' * 80}")
    print(f"LOCATION: {location}")
    print(f"{'=' * 80}")

    # PayrollExport
    print("\n--- PAYROLL EXPORT (Summary) ---")
    payroll_data = read_payroll_export(str(payroll_file))
    print(f"Total rows: {len(payroll_data)}")
    print("\nSample data:")
    for emp in payroll_data[:3]:
        print(f"  {emp['name']:30s} | {emp['job_title']:20s} | {emp['total_hours']:6.2f} hrs")

    # TimeEntries
    print("\n--- TIME ENTRIES (Detailed) ---")
    time_data = read_time_entries(str(timeentries_file))
    print(f"Total rows: {len(time_data)}")
    print("\nSample data:")
    for entry in time_data[:3]:
        print(f"  {entry['name']:30s} | {entry['job_title']:20s} | {entry['payable_hours']:6.2f} hrs")
        print(f"    In: {entry['in_date']:25s} Out: {entry['out_date']}")

    # Compare totals
    print("\n--- COMPARISON ---")
    payroll_total = sum(emp['total_hours'] for emp in payroll_data)
    time_total = sum(entry['payable_hours'] for entry in time_data)
    print(f"PayrollExport total hours: {payroll_total:.2f}")
    print(f"TimeEntries total hours:   {time_total:.2f}")
    print(f"Difference:                {abs(payroll_total - time_total):.2f}")

    # Unique employees
    payroll_names = set(emp['name'] for emp in payroll_data)
    time_names = set(entry['name'] for entry in time_data)
    print(f"\nUnique employees in PayrollExport: {len(payroll_names)}")
    print(f"Unique employees in TimeEntries:   {len(time_names)}")


if __name__ == '__main__':
    base_path = r'C:\Users\Jorge Alexander\omni_v4\tests\fixtures\sample_data'
    date = '2025-10-20'

    # Compare all locations
    for location in ['SDR', 'T12', 'TK9']:
        compare_sources(location, base_path, date)

    print("\n" + "=" * 80)
    print("KEY DIFFERENCES")
    print("=" * 80)
    print("""
1. PAYROLL EXPORT:
   - One row per employee per job title
   - Pre-calculated totals (regular + overtime)
   - Summary view - best for payroll calculations
   - Simpler structure

2. TIME ENTRIES:
   - One row per shift (clock in/out)
   - Individual shift timestamps
   - Detailed view - best for shift analysis
   - Can have multiple entries per employee

RECOMMENDATION: Use PayrollExport for simple employee hours extraction.
                Use TimeEntries if you need shift-level detail or timestamps.
    """)
