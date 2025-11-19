#!/usr/bin/env python3
"""
Deploy database schema to Supabase.

This script provides the SQL to run in Supabase Dashboard SQL Editor.
The Supabase Python client doesn't support raw SQL execution, so you'll
need to copy/paste the SQL into the dashboard.

Usage:
    python scripts/deploy_schema.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def display_schema_instructions():
    """Display instructions for deploying schema to Supabase."""

    url = os.getenv('SUPABASE_URL')
    if not url:
        print("[ERROR] SUPABASE_URL not found in .env file")
        return

    print("=" * 80)
    print("OMNI V4 - SUPABASE SCHEMA DEPLOYMENT")
    print("=" * 80)
    print()
    print(f"Target Database: {url}")
    print()
    print("The Supabase Python client doesn't support raw SQL execution.")
    print("You'll need to run the SQL files manually in the Supabase Dashboard.")
    print()
    print("STEPS:")
    print()
    print("1. Open Supabase Dashboard:")
    print(f"   {url.replace('https://', 'https://supabase.com/dashboard/project/')}")
    print()
    print("2. Click 'SQL Editor' in left sidebar")
    print()
    print("3. Click 'New query'")
    print()
    print("4. Copy the contents of this file:")
    print("   src/storage/migrations/001_create_schema.sql")
    print()
    print("5. Paste into SQL Editor and click 'Run'")
    print("   Expected: 'Success. No rows returned'")
    print()
    print("6. Click 'New query' again")
    print()
    print("7. Copy the contents of this file:")
    print("   src/storage/migrations/002_create_indexes.sql")
    print()
    print("8. Paste into SQL Editor and click 'Run'")
    print("   Expected: 'Success. No rows returned'")
    print()
    print("9. Verify tables were created:")
    print("   Click 'Table Editor' in left sidebar")
    print("   You should see:")
    print("     - restaurants (3 rows)")
    print("     - daily_operations (0 rows)")
    print("     - shift_operations (0 rows)")
    print("     - vendor_payouts (0 rows)")
    print("     - timeslot_patterns (0 rows)")
    print("     - daily_labor_patterns (0 rows)")
    print("     - timeslot_results (0 rows)")
    print("     - batch_runs (0 rows)")
    print()
    print("=" * 80)
    print("SCHEMA DETAILS")
    print("=" * 80)
    print()

    # Show schema file paths
    migrations_dir = Path('src/storage/migrations')
    schema_file = migrations_dir / '001_create_schema.sql'
    indexes_file = migrations_dir / '002_create_indexes.sql'

    print(f"Schema SQL: {schema_file.absolute()}")
    print(f"Size: {schema_file.stat().st_size} bytes")
    print()
    print(f"Indexes SQL: {indexes_file.absolute()}")
    print(f"Size: {indexes_file.stat().st_size} bytes")
    print()
    print("=" * 80)
    print()
    print("After deployment, run:")
    print("  python scripts/test_supabase_connection.py")
    print()
    print("To verify all tables are accessible.")
    print("=" * 80)

if __name__ == "__main__":
    display_schema_instructions()
