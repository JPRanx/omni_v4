"""
Toast Employee Name Extractor
Extracts unique employee names from Toast PayrollExport CSV files
"""
import pandas as pd
import json
from pathlib import Path
from typing import Set, List, Dict


def extract_toast_employees(base_folder: str) -> Dict[str, List[str]]:
    """
    Extract unique employee names from Toast PayrollExport CSV files

    Returns:
        Dict mapping location to list of unique employee names
    """
    base_path = Path(base_folder)
    employees_by_location = {}

    # Find all PayrollExport CSV files
    payroll_files = list(base_path.rglob("PayrollExport_*.csv"))

    print(f"Found {len(payroll_files)} PayrollExport files")

    all_employees = set()

    for file_path in payroll_files:
        try:
            # Extract location from path (e.g., "SDR", "T12", "TK9")
            # Path structure: .../2025-10-20/SDR/PayrollExport_2025_10_20.csv
            location = file_path.parent.name

            # Read CSV
            df = pd.read_csv(file_path)

            # Extract employee names (first column)
            if 'Employee' in df.columns:
                employees = df['Employee'].dropna().unique().tolist()

                # Clean up names (remove extra spaces)
                employees = [name.strip() for name in employees if name.strip()]

                if location not in employees_by_location:
                    employees_by_location[location] = set()

                employees_by_location[location].update(employees)
                all_employees.update(employees)

                print(f"  {location}: {len(employees)} employees")

        except Exception as e:
            print(f"  Error reading {file_path}: {e}")

    # Convert sets to sorted lists
    result = {
        loc: sorted(list(emps))
        for loc, emps in employees_by_location.items()
    }

    # Add a special "ALL" key with all unique employees
    result['ALL'] = sorted(list(all_employees))

    return result


def normalize_toast_name(name: str) -> str:
    """
    Normalize Toast employee name for matching

    Handles:
    - "Last, First" -> "First Last"
    - Extra spaces
    - Case normalization
    """
    name = name.strip()

    # If comma format, convert to "First Last"
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            last, first = parts
            name = f"{first.strip()} {last.strip()}"

    return name


if __name__ == "__main__":
    # Extract from test fixtures
    base_folder = r"C:\Users\Jorge Alexander\omni_v4\tests\fixtures\sample_data"
    employees = extract_toast_employees(base_folder)

    # Save results
    output_file = Path(r"C:\Users\Jorge Alexander\omni_v4") / "toast_employees.json"
    with open(output_file, 'w') as f:
        json.dump(employees, f, indent=2)

    print(f"\n\nResults saved to {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("TOAST EMPLOYEE SUMMARY")
    print("="*60)

    for location, emps in sorted(employees.items()):
        print(f"\n{location}: {len(emps)} employees")
        if location != 'ALL':
            for emp in emps[:5]:  # Show first 5
                normalized = normalize_toast_name(emp)
                print(f"  - {emp}")
                if normalized != emp:
                    print(f"    (normalized: {normalized})")
            if len(emps) > 5:
                print(f"  ... and {len(emps) - 5} more")

    print(f"\n\nTotal unique employees across all locations: {len(employees.get('ALL', []))}")
