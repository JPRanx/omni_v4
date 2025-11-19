#!/usr/bin/env python3
"""
Generate a comprehensive directory tree for OMNI V4 project.
Shows file sizes, dates, and marks investigation/experimental files.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

def get_file_size_str(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def is_investigation_file(name, parent_name):
    """Check if file is an investigation/debug file"""
    investigation_prefixes = [
        'investigate_', 'diagnose_', 'verify_', 'compare_',
        'extract_', 'deep_dive_', 'test_current', 'test_ingestion'
    ]
    return any(name.startswith(prefix) for prefix in investigation_prefixes) and parent_name == 'omni_v4'

def is_experimental_file(name):
    """Check if file is experimental (CLEAN, DISCONNECTED, etc.)"""
    return '_CLEAN' in name or '_DISCONNECTED' in name or 'DataBridge' in name

def is_test_html(name, parent_name):
    """Check if file is a test HTML page"""
    return (name.startswith('test_') or name.startswith('debug_')) and name.endswith('.html')

def is_duplicate_v4data(name, parent_name):
    """Check if this is a duplicate v4Data.js file"""
    return 'v4Data' in name and name.endswith('.js') and parent_name != 'data'

def get_marker(item, parent_name):
    """Get marker for suspicious files"""
    name = item.name

    if is_investigation_file(name, parent_name):
        return " [!] INVESTIGATION"
    elif is_experimental_file(name):
        return " [!] EXPERIMENTAL"
    elif is_test_html(name, parent_name):
        return " [!] TEST HTML"
    elif is_duplicate_v4data(name, parent_name):
        return " [!] DUPLICATE?"
    elif name.endswith('_investigation.json') or name.endswith('_forensics.json'):
        return " [!] DEBUG OUTPUT"

    return ""

def generate_tree(directory, prefix="", max_depth=6, current_depth=0, stats=None):
    """Generate a tree structure with file info"""

    if stats is None:
        stats = {
            'total_files': 0,
            'total_dirs': 0,
            'investigation_files': 0,
            'test_htmls': 0,
            'experimental_files': 0,
            'duplicate_v4data': 0,
            'py_files': 0,
            'js_files': 0,
            'test_py_files': 0,
            'recent_files': 0,
            'nov17_files': 0,
            'json_outputs': 0
        }

    if current_depth >= max_depth:
        return stats

    # Skip these directories
    skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', 'htmlcov', '.vscode', '.idea'}

    path = Path(directory)

    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return stats

    # Filter out skip dirs
    items = [item for item in items if item.name not in skip_dirs]

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "`-- " if is_last else "|-- "
        extension = "    " if is_last else "|   "

        # Get file info
        size_str = ""
        date_str = ""
        marker = ""

        if item.is_file():
            stats['total_files'] += 1

            # Get size
            size_bytes = item.stat().st_size
            if size_bytes > 1024:  # Only show size if > 1KB
                size_str = f" ({get_file_size_str(size_bytes)})"

            # Get modification date
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            days_old = (datetime.now() - mtime).days

            # Show date for recent files
            if days_old < 7:
                date_str = f" [{mtime.strftime('%b %d %H:%M')}]"
                stats['recent_files'] += 1

                # Check if modified on Nov 17
                if mtime.strftime('%Y-%m-%d') == '2025-11-17':
                    stats['nov17_files'] += 1

            # Get marker
            parent_name = path.name
            marker = get_marker(item, parent_name)

            # Update stats based on file type/marker
            if 'INVESTIGATION' in marker:
                stats['investigation_files'] += 1
            elif 'EXPERIMENTAL' in marker:
                stats['experimental_files'] += 1
            elif 'TEST HTML' in marker:
                stats['test_htmls'] += 1
            elif 'DUPLICATE' in marker:
                stats['duplicate_v4data'] += 1
            elif 'DEBUG OUTPUT' in marker:
                stats['json_outputs'] += 1

            # Count by extension
            if item.suffix == '.py':
                stats['py_files'] += 1
                if 'test_' in item.name or item.parent.name in ['tests', 'unit', 'integration']:
                    stats['test_py_files'] += 1
            elif item.suffix == '.js':
                stats['js_files'] += 1

        elif item.is_dir():
            stats['total_dirs'] += 1
            size_str = ""
            date_str = ""
            marker = ""

        # Print the line
        print(f"{prefix}{current_prefix}{item.name}{size_str}{date_str}{marker}")

        # Recurse into directories
        if item.is_dir():
            generate_tree(item, prefix + extension, max_depth, current_depth + 1, stats)

    return stats

def print_summary(stats):
    """Print summary statistics"""
    print("\n" + "=" * 80)
    print("DIRECTORY SUMMARY")
    print("=" * 80)
    print(f"\nOverall:")
    print(f"   Total Files: {stats['total_files']}")
    print(f"   Total Directories: {stats['total_dirs']}")

    print(f"\nFiles to Delete (Investigation/Debug):")
    print(f"   Investigation Scripts (root): {stats['investigation_files']} files")
    print(f"   Debug JSON Outputs (root): {stats['json_outputs']} files")
    print(f"   Test HTML Pages (dashboard/): {stats['test_htmls']} files")
    print(f"   Experimental Components: {stats['experimental_files']} files")
    print(f"   Duplicate v4Data.js: {stats['duplicate_v4data']} files")
    total_to_delete = (stats['investigation_files'] + stats['json_outputs'] +
                      stats['test_htmls'] + stats['experimental_files'] +
                      stats['duplicate_v4data'])
    print(f"   >>> TOTAL TO DELETE: {total_to_delete} files")

    print(f"\nCore Project Files:")
    print(f"   Python Files (src/): {stats['py_files']} files")
    print(f"   Test Files (tests/): {stats['test_py_files']} files")
    print(f"   JavaScript Files: {stats['js_files']} files")

    print(f"\nRecent Activity:")
    print(f"   Files Modified in Last 7 Days: {stats['recent_files']} files")
    print(f"   Files Modified on Nov 17 (Investigation Day): {stats['nov17_files']} files")

    print("\n" + "=" * 80)
    print("Legend:")
    print("  [!] INVESTIGATION - Investigation/debug scripts (DELETE)")
    print("  [!] DEBUG OUTPUT - Investigation JSON outputs (DELETE)")
    print("  [!] TEST HTML - Test HTML pages (DELETE)")
    print("  [!] EXPERIMENTAL - Experimental versions (DELETE)")
    print("  [!] DUPLICATE? - Duplicate v4Data.js files (DELETE)")
    print("=" * 80 + "\n")

def main():
    """Main entry point"""
    print("=" * 80)
    print("OMNI V4 PROJECT DIRECTORY TREE")
    print("Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    print()

    # Change to project root if script is in subdirectory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Generate tree
    print("omni_v4/")
    stats = generate_tree(".", prefix="", max_depth=6)

    # Print summary
    print_summary(stats)

if __name__ == "__main__":
    main()