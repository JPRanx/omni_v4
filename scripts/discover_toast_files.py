"""
Discovery script for analyzing all Toast POS CSV file types.

Scans all 30 CSV file types across all 3 restaurants (SDR, T12, TK9)
to identify:
- Universal vs restaurant-specific files
- Schema variations
- Data volumes
- Criticality categorization

Usage:
    python scripts/discover_toast_files.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
import pandas as pd
from collections import defaultdict


# File criticality prioritization
PRIORITY_CATEGORIES = {
    1: {  # Core Operations (already integrated)
        'TimeEntries': 'Labor tracking - required for all calculations',
        'Net sales summary': 'Revenue tracking - required for performance metrics',
        'OrderDetails': 'Transaction details - required for sales analysis'
    },
    2: {  # Efficiency & Management
        'Kitchen Details': 'Kitchen prep/void tracking - needed for efficiency metrics',
        'Server Details': 'Server performance - needed for labor efficiency',
        'Cash Activity': 'Cash handling - needed for accountability tracking'
    },
    3: {  # Enhanced Analytics
        'Discounts and Comps': 'Discount analysis',
        'Menu Item Details': 'Item-level sales',
        'Payment Details': 'Payment method breakdown',
        'Tax Details': 'Tax reporting'
    },
    4: {  # Advanced Features
        'Voids': 'Void pattern analysis',
        'Pre Modifiers': 'Order customization tracking',
        'Employees': 'Employee master data',
        'Revenue Center': 'Location-based sales'
    },
    5: {  # Future/Optional
        # Everything else
    }
}


def get_priority(filename: str) -> int:
    """Determine priority category for a file."""
    for priority, files in PRIORITY_CATEGORIES.items():
        for key in files.keys():
            if key.lower() in filename.lower():
                return priority
    return 5  # Default to lowest priority


def scan_restaurants(base_path: Path) -> Dict:
    """Scan all restaurants and collect file inventory."""
    restaurants = ['SDR', 'T12', 'TK9']
    date = '2025-10-20'

    inventory = {
        'restaurants': {},
        'universal_files': [],
        'restaurant_specific': {},
        'file_schemas': defaultdict(dict),
        'file_volumes': defaultdict(dict),
        'missing_files': defaultdict(list)
    }

    # Collect all unique filenames
    all_filenames: Set[str] = set()

    for restaurant in restaurants:
        restaurant_path = base_path / date / restaurant

        if not restaurant_path.exists():
            print(f"⚠️  Warning: {restaurant} directory not found at {restaurant_path}")
            continue

        csv_files = sorted([f.name for f in restaurant_path.glob("*.csv")])
        all_filenames.update(csv_files)

        inventory['restaurants'][restaurant] = {
            'path': str(restaurant_path),
            'file_count': len(csv_files),
            'files': csv_files
        }

    # Determine universal vs restaurant-specific files
    for filename in sorted(all_filenames):
        present_in = [r for r in restaurants if filename in inventory['restaurants'].get(r, {}).get('files', [])]

        if len(present_in) == 3:
            inventory['universal_files'].append(filename)
        else:
            inventory['restaurant_specific'][filename] = present_in
            # Track which restaurants are missing this file
            missing_in = [r for r in restaurants if r not in present_in]
            for restaurant in missing_in:
                inventory['missing_files'][restaurant].append(filename)

    return inventory


def analyze_schemas(base_path: Path, inventory: Dict) -> Dict:
    """Analyze schema variations for universal files."""
    date = '2025-10-20'
    schema_analysis = {}

    for filename in inventory['universal_files']:
        schema_analysis[filename] = {
            'columns': {},
            'variations': [],
            'is_consistent': True
        }

        restaurant_schemas = {}

        for restaurant in ['SDR', 'T12', 'TK9']:
            file_path = base_path / date / restaurant / filename

            try:
                # Read just first row for schema
                df = pd.read_csv(file_path, nrows=1)
                columns = df.columns.tolist()
                restaurant_schemas[restaurant] = columns
            except Exception as e:
                schema_analysis[filename]['variations'].append(
                    f"{restaurant}: Error reading file - {str(e)}"
                )
                schema_analysis[filename]['is_consistent'] = False

        # Check if all schemas match
        if len(restaurant_schemas) == 3:
            schemas = list(restaurant_schemas.values())
            if schemas[0] == schemas[1] == schemas[2]:
                schema_analysis[filename]['columns'] = schemas[0]
            else:
                schema_analysis[filename]['is_consistent'] = False
                schema_analysis[filename]['variations'] = restaurant_schemas

    return schema_analysis


def analyze_volumes(base_path: Path, inventory: Dict) -> Dict:
    """Analyze data volumes for universal files."""
    date = '2025-10-20'
    volume_analysis = {}

    for filename in inventory['universal_files']:
        volume_analysis[filename] = {}

        for restaurant in ['SDR', 'T12', 'TK9']:
            file_path = base_path / date / restaurant / filename

            try:
                df = pd.read_csv(file_path)
                volume_analysis[filename][restaurant] = {
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                }
            except Exception as e:
                volume_analysis[filename][restaurant] = {
                    'error': str(e)
                }

    return volume_analysis


def categorize_by_priority(inventory: Dict) -> Dict:
    """Categorize files by priority."""
    categorized = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }

    for filename in inventory['universal_files']:
        priority = get_priority(filename)
        categorized[priority].append(filename)

    return categorized


def generate_report(inventory: Dict, schema_analysis: Dict, volume_analysis: Dict, categorized: Dict) -> str:
    """Generate comprehensive discovery report."""
    report_lines = []

    report_lines.append("=" * 80)
    report_lines.append("TOAST POS CSV FILES - DISCOVERY REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # Summary
    report_lines.append("SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Total unique files found: {len(inventory['universal_files']) + len(inventory['restaurant_specific'])}")
    report_lines.append(f"Universal files (all 3 restaurants): {len(inventory['universal_files'])}")
    report_lines.append(f"Restaurant-specific files: {len(inventory['restaurant_specific'])}")
    report_lines.append("")

    # Restaurant inventory
    report_lines.append("RESTAURANT INVENTORY")
    report_lines.append("-" * 80)
    for restaurant, data in inventory['restaurants'].items():
        report_lines.append(f"{restaurant}: {data['file_count']} files")
    report_lines.append("")

    # Priority categorization
    report_lines.append("PRIORITY CATEGORIZATION")
    report_lines.append("-" * 80)
    for priority in sorted(categorized.keys()):
        files = categorized[priority]
        if files:
            report_lines.append(f"\nPriority {priority}: {len(files)} files")
            if priority in PRIORITY_CATEGORIES and PRIORITY_CATEGORIES[priority]:
                report_lines.append("  Purpose:")
                for filename, purpose in PRIORITY_CATEGORIES[priority].items():
                    report_lines.append(f"    - {filename}: {purpose}")
            report_lines.append("  Files:")
            for filename in files:
                report_lines.append(f"    - {filename}")
    report_lines.append("")

    # Schema consistency
    report_lines.append("SCHEMA ANALYSIS")
    report_lines.append("-" * 80)
    consistent_schemas = sum(1 for s in schema_analysis.values() if s['is_consistent'])
    report_lines.append(f"Files with consistent schemas: {consistent_schemas}/{len(schema_analysis)}")

    inconsistent = [f for f, s in schema_analysis.items() if not s['is_consistent']]
    if inconsistent:
        report_lines.append("\nWARNING - Files with schema variations:")
        for filename in inconsistent:
            report_lines.append(f"  - {filename}")
    report_lines.append("")

    # Priority 2 files (next to integrate)
    report_lines.append("PRIORITY 2 FILES - RECOMMENDED FOR IMMEDIATE INTEGRATION")
    report_lines.append("-" * 80)
    priority2_files = categorized.get(2, [])
    if priority2_files:
        for filename in priority2_files:
            report_lines.append(f"\n{filename}")

            # Schema
            if filename in schema_analysis:
                schema = schema_analysis[filename]
                if schema['is_consistent']:
                    report_lines.append(f"  Schema: Consistent across all restaurants")
                    report_lines.append(f"  Columns ({len(schema['columns'])}): {', '.join(schema['columns'][:5])}...")
                else:
                    report_lines.append(f"  Schema: Variations detected")

            # Volumes
            if filename in volume_analysis:
                volumes = volume_analysis[filename]
                report_lines.append("  Data volumes:")
                for restaurant, vol in volumes.items():
                    if 'row_count' in vol:
                        report_lines.append(f"    {restaurant}: {vol['row_count']} rows, {vol['column_count']} cols, {vol['memory_mb']:.2f} MB")
    else:
        report_lines.append("No Priority 2 files found.")
    report_lines.append("")

    # Restaurant-specific files
    if inventory['restaurant_specific']:
        report_lines.append("RESTAURANT-SPECIFIC FILES")
        report_lines.append("-" * 80)
        for filename, restaurants in inventory['restaurant_specific'].items():
            report_lines.append(f"{filename}: Present in {', '.join(restaurants)}")
        report_lines.append("")

    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-" * 80)
    report_lines.append(f"Priority 1 (3 files): ALREADY INTEGRATED")
    report_lines.append(f"Priority 2 ({len(categorized.get(2, []))} files): INTEGRATE NOW (Week 4 Day 4)")
    report_lines.append(f"Priority 3 ({len(categorized.get(3, []))} files): Week 5")
    report_lines.append(f"Priority 4 ({len(categorized.get(4, []))} files): Week 6")
    report_lines.append(f"Priority 5 ({len(categorized.get(5, []))} files): Future/Optional")
    report_lines.append("")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main():
    """Main discovery execution."""
    base_path = Path("tests/fixtures/sample_data")

    print("Starting Toast POS CSV discovery scan...")
    print("")

    # Scan restaurants
    print("Step 1/4: Scanning restaurant directories...")
    inventory = scan_restaurants(base_path)

    # Analyze schemas
    print("Step 2/4: Analyzing schemas...")
    schema_analysis = analyze_schemas(base_path, inventory)

    # Analyze volumes
    print("Step 3/4: Analyzing data volumes...")
    volume_analysis = analyze_volumes(base_path, inventory)

    # Categorize by priority
    print("Step 4/4: Categorizing by priority...")
    categorized = categorize_by_priority(inventory)

    # Generate report
    print("")
    report = generate_report(inventory, schema_analysis, volume_analysis, categorized)
    print(report)

    # Save detailed JSON
    output_path = Path("scripts/discovery_report.json")
    detailed_output = {
        'inventory': inventory,
        'schema_analysis': schema_analysis,
        'volume_analysis': volume_analysis,
        'categorized': categorized
    }

    with open(output_path, 'w') as f:
        json.dump(detailed_output, f, indent=2, default=str)

    print(f"\nDetailed JSON report saved to: {output_path}")
    print("")
    print("Discovery scan complete!")


if __name__ == '__main__':
    main()
