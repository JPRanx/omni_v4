#!/usr/bin/env python3
"""Test Supabase connection and verify tables exist."""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

def test_connection():
    """Test connection to Supabase and verify tables."""

    # Get credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return False

    print("=" * 80)
    print("SUPABASE CONNECTION TEST")
    print("=" * 80)
    print()
    print(f"Project URL: {url}")
    print()

    # Create client
    try:
        client = create_client(url, key)
        print("[OK] Client created successfully")
    except Exception as e:
        print(f"[ERROR] Failed to create client: {e}")
        return False

    print()
    print("=" * 80)
    print("TABLE ACCESS TEST")
    print("=" * 80)
    print()

    # Test each table
    tables = [
        'restaurants',
        'daily_operations',
        'shift_operations',
        'vendor_payouts',
        'timeslot_patterns',
        'daily_labor_patterns',
        'timeslot_results',
        'batch_runs'
    ]

    accessible_count = 0
    for table_name in tables:
        try:
            result = client.table(table_name).select("*").limit(1).execute()
            print(f"[OK] {table_name:<25} accessible ({len(result.data)} rows)")
            accessible_count += 1
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                print(f"[MISSING] {table_name:<25} table not found")
            else:
                print(f"[ERROR] {table_name:<25} {str(e)[:50]}")

    print()
    print("=" * 80)
    print("REFERENCE DATA TEST")
    print("=" * 80)
    print()

    # Check restaurant reference data
    try:
        restaurants = client.table('restaurants').select("*").execute()
        print(f"[OK] Restaurants loaded: {len(restaurants.data)}")
        for r in restaurants.data:
            print(f"     - {r['code']}: {r['name']}")
    except Exception as e:
        print(f"[ERROR] Could not load restaurants: {e}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Tables accessible: {accessible_count}/{len(tables)}")
    print()

    if accessible_count == len(tables):
        print("[SUCCESS] All tables created and accessible!")
        print()
        print("Next steps:")
        print("  1. Run batch processing to generate data")
        print("  2. Use persistence layer to insert into Supabase")
        print("  3. Query historical data for analytics")
        return True
    elif accessible_count == 0:
        print("[ACTION NEEDED] No tables found - run schema deployment")
        print()
        print("Run: python scripts/deploy_schema.py")
        print("Then follow instructions to deploy SQL in Supabase Dashboard")
        return False
    else:
        print("[WARNING] Some tables missing - check deployment")
        return False

if __name__ == "__main__":
    test_connection()
