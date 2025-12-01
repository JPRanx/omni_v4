"""
Wipe Supabase Data - Delete all data while preserving table structure.

This script deletes all rows from Supabase tables used by OMNI V4.
Table structure and schemas are preserved.

Usage:
    python scripts/wipe_supabase_data.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.storage.supabase_client import SupabaseClient


def wipe_table(client: SupabaseClient, table_name: str) -> int:
    """
    Delete all rows from a table.

    Args:
        client: Supabase client
        table_name: Name of table to wipe

    Returns:
        Number of rows deleted
    """
    try:
        # Delete all rows by using a condition that matches everything
        # We use 'id is not null' which matches all rows (assuming id exists)
        result = client.client.table(table_name).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

        # If that doesn't work, try alternative approach
        if not result.data:
            # Try using created_at >= very old date (matches all rows)
            result = client.client.table(table_name).delete().gte('created_at', '1970-01-01').execute()

        count = len(result.data) if result.data else 0
        return count
    except Exception as e:
        print(f"  [WARNING] Error wiping {table_name}: {e}")
        return 0


def main():
    """Main execution function."""
    print("=" * 60)
    print("SUPABASE DATA WIPE - Deleting all data (preserving structure)")
    print("=" * 60)
    print()

    try:
        # Initialize Supabase client
        print("Connecting to Supabase...")
        client = SupabaseClient()
        print("[OK] Connected\n")

        # Tables to wipe (in order to respect foreign key constraints)
        tables = [
            'timeslot_results',       # Most granular data
            'shift_operations',       # Shift-level data
            'daily_operations',       # Daily-level data
            'vendor_payouts',         # Vendor data
            'timeslot_patterns',      # Pattern learning data
            'daily_labor_patterns',   # Labor patterns
            'batch_runs'              # Batch processing metadata
        ]

        total_deleted = 0

        for table in tables:
            print(f"Wiping table: {table}...")
            count = wipe_table(client, table)
            print(f"  [OK] Deleted {count} rows\n")
            total_deleted += count

        print("=" * 60)
        print(f"[SUCCESS] WIPE COMPLETE - Total rows deleted: {total_deleted}")
        print("=" * 60)
        print("\nTable structures preserved. Database ready for fresh data.")

    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        print("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
