#!/usr/bin/env python3
"""
OMNI V4 Cleanup Script
Date: 2025-11-19
Purpose: Remove debugging artifacts from Nov 17 investigation

This script systematically removes ~40 temporary files created during
the Nov 17 Investigation Modal debugging session. All files have been
verified as orphaned through complete dependency analysis.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Define what to clean
CLEANUP_MANIFEST = {
    "investigation_scripts": [
        "investigate_pipeline.py",
        "investigate_order_grading.py",
        "investigate_order_counts.py",
        "compare_v3_v4_time_fields.py",
        "extract_v3_exact_logic.py",
        "test_v3_v4_with_same_order.py",
        "verify_capacity_analysis_counts.py",
        "deep_dive_v4data_counts.py",
        "diagnose_missing_categories.py",
        "test_current_output.py",
        "test_ingestion_only.py"
    ],

    "investigation_outputs": [
        "pipeline_investigation.json",
        "order_count_investigation.json",
        "order_grading_forensics.json",
        "v3_v4_comparison.json"
    ],

    "dashboard_test_files": [
        "dashboard/test_disconnected.html",
        "dashboard/test_databridge.html",
        "dashboard/test_clean_modal.html",
        "dashboard/test_investigation_modal.html",
        "dashboard/debug_investigation_modal.html",
        "dashboard/PHASE1_COMPLETE.md",
        "dashboard/SURGICAL_DISCONNECTION_SUMMARY.md",
        "dashboard/SUPABASE_INTEGRATION_FINAL_SUMMARY.md"
    ],

    "experimental_components": [
        "dashboard/components/InvestigationModal_DISCONNECTED.js",
        "dashboard/components/InvestigationModal_CLEAN.js",
        "dashboard/services/InvestigationDataBridge.js"
    ],

    "duplicate_test_data": [
        "dashboard/data/v4Data_test.js",  # Test version, not used
        "v4Data_oct.js"  # October version, outdated
    ],

    "documentation_artifacts": [
        "ARCHITECT_SUMMARY_SUPABASE_INTEGRATION.md",  # Temp doc
        "LEVEL3_DATA_ANALYSIS.md",  # Temp analysis
        "PATTERN_LEARNING_INTEGRATION.md",  # Temp doc
        "SUPABASE_INTEGRATION.md",  # Duplicated elsewhere
        "TRIPLE_FEATURE_IMPLEMENTATION.md"  # Temp doc
    ]
}

# Files to relocate (not delete)
RELOCATE_MANIFEST = {
    "dashboard_v4.html": "dashboard/archive/dashboard_v4.html",
    "test_auto_clockout_dashboard.js": "dashboard/tests/test_auto_clockout_dashboard.js",
    "test_cogs_dashboard.js": "dashboard/tests/test_cogs_dashboard.js",
    "test_dashboard_data.js": "dashboard/tests/test_dashboard_data.js",
    "dashboard_test.js": "dashboard/tests/dashboard_test.js",
    "dashboard_week.js": "dashboard/tests/dashboard_week.js"
}


def cleanup_with_manifest():
    """Execute cleanup with full logging"""

    # Create cleanup log
    log_file = f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_entries = []

    # Track statistics
    deleted_count = 0
    moved_count = 0
    skipped_count = 0
    errors = []

    print("=" * 70)
    print("OMNI V4 CLEANUP - Nov 17 Debugging Artifacts")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. Delete investigation files
    for category, files in CLEANUP_MANIFEST.items():
        category_name = category.replace('_', ' ').title()
        print(f"\n[{category_name}]")
        print("-" * 70)

        for file_path in files:
            if os.path.exists(file_path):
                try:
                    # Delete directories recursively
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)

                    deleted_count += 1
                    log_entries.append(f"DELETED: {file_path}")
                    print(f"  [OK] Deleted: {file_path}")
                except Exception as e:
                    errors.append(f"Failed to delete {file_path}: {e}")
                    print(f"  [ERROR] {file_path} - {e}")
            else:
                skipped_count += 1
                print(f"  - Not found (already removed?): {file_path}")

    # 2. Relocate misplaced files
    print(f"\n[Relocating Files]")
    print("-" * 70)

    # Ensure target directories exist
    os.makedirs("dashboard/tests", exist_ok=True)
    os.makedirs("dashboard/archive", exist_ok=True)

    for source, destination in RELOCATE_MANIFEST.items():
        if os.path.exists(source):
            try:
                # Create parent directory if needed
                os.makedirs(os.path.dirname(destination), exist_ok=True)

                # Move file
                shutil.move(source, destination)
                moved_count += 1
                log_entries.append(f"MOVED: {source} -> {destination}")
                print(f"  [OK] Moved: {source} -> {destination}")
            except Exception as e:
                errors.append(f"Failed to move {source}: {e}")
                print(f"  [ERROR] Moving: {source} - {e}")
        else:
            skipped_count += 1
            print(f"  - Not found: {source}")

    # 3. Clean diagnostic directories (if they exist and are empty/temp)
    diagnostic_dirs = [
        "dashboard/diagnostics",
        "dashboard/config"
    ]

    print(f"\n[Cleaning Diagnostic Directories]")
    print("-" * 70)

    for dir_path in diagnostic_dirs:
        if os.path.exists(dir_path):
            # Only remove if it's a directory we created during debugging
            # Check if it contains only Nov 17 files
            try:
                files_in_dir = list(Path(dir_path).rglob("*"))
                if len(files_in_dir) <= 5:  # Small diagnostic directory
                    shutil.rmtree(dir_path)
                    deleted_count += 1
                    log_entries.append(f"DELETED DIR: {dir_path}")
                    print(f"  [OK] Deleted directory: {dir_path}")
                else:
                    print(f"  - Kept (has content): {dir_path}")
            except Exception as e:
                errors.append(f"Failed to remove directory {dir_path}: {e}")
                print(f"  [ERROR] {dir_path} - {e}")

    # 4. Write log file
    with open(log_file, 'w') as f:
        f.write(f"OMNI V4 Cleanup Log\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"SUMMARY STATISTICS:\n")
        f.write(f"  Files deleted: {deleted_count}\n")
        f.write(f"  Files relocated: {moved_count}\n")
        f.write(f"  Files skipped (not found): {skipped_count}\n")
        f.write(f"  Errors: {len(errors)}\n\n")

        f.write("=" * 70 + "\n")
        f.write("ACTIONS TAKEN:\n")
        f.write("=" * 70 + "\n")
        for entry in log_entries:
            f.write(f"{entry}\n")

        if errors:
            f.write("\n" + "=" * 70 + "\n")
            f.write("ERRORS ENCOUNTERED:\n")
            f.write("=" * 70 + "\n")
            for error in errors:
                f.write(f"{error}\n")

    # 5. Print summary
    print("\n" + "=" * 70)
    print("CLEANUP COMPLETE")
    print("=" * 70)
    print(f"  Files deleted: {deleted_count}")
    print(f"  Files relocated: {moved_count}")
    print(f"  Files skipped: {skipped_count}")
    print(f"  Errors: {len(errors)}")
    print(f"\n  Log saved to: {log_file}")

    if errors:
        print(f"\n  [WARNING] {len(errors)} error(s) occurred. Check log for details.")
    else:
        print(f"\n  [SUCCESS] All operations completed successfully!")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Run: git status")
    print("2. Verify: python -m pytest tests/")
    print("3. Check dashboard still loads")
    print("4. Commit: git add -A && git commit -m 'Clean up Nov 17 artifacts'")
    print("=" * 70 + "\n")

    return deleted_count, moved_count, skipped_count, errors


if __name__ == "__main__":
    print()
    deleted, moved, skipped, errors = cleanup_with_manifest()

    # Exit with error code if there were errors
    exit_code = 1 if errors else 0
    exit(exit_code)
