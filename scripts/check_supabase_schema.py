"""
Check Supabase table schemas to understand what columns exist.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseClient


def get_table_columns(client: SupabaseClient, table_name: str):
    """Get column names from a table by querying with select *."""
    try:
        # Try to get one row to see the columns
        result = client.client.table(table_name).select('*').limit(1).execute()

        if result.data and len(result.data) > 0:
            return list(result.data[0].keys())

        # If no data, try inserting empty dict to see what columns are required
        print(f"  No data in {table_name}, attempting schema introspection...")

        # Use PostgREST introspection endpoint
        # This won't work directly, so we'll try a minimal insert to get error
        try:
            client.client.table(table_name).insert({'_test': 'test'}).execute()
        except Exception as e:
            error_msg = str(e)
            print(f"  Error trying minimal insert: {error_msg}")
            return None

    except Exception as e:
        print(f"  Error accessing {table_name}: {e}")
        return None


def main():
    print("=" * 70)
    print("SUPABASE SCHEMA CHECK")
    print("=" * 70)
    print()

    try:
        client = SupabaseClient()
        print("Connected to Supabase\n")

        tables = [
            'daily_operations',
            'shift_operations',
            'timeslot_results',
            'vendor_payouts',
            'timeslot_patterns',
            'daily_labor_patterns',
            'batch_runs'
        ]

        for table in tables:
            print(f"Table: {table}")
            columns = get_table_columns(client, table)

            if columns:
                print(f"  Columns ({len(columns)}):")
                for col in sorted(columns):
                    print(f"    - {col}")
            else:
                print(f"  Could not determine columns (table is empty)")

            print()

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()