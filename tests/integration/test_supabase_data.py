"""
Test Supabase Data - Check what's in the database
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Connecting to Supabase at {url}...")
supabase = create_client(url, key)

# Check daily_operations
print("\n" + "="*60)
print("DAILY OPERATIONS TABLE")
print("="*60)

try:
    daily_ops = supabase.table('daily_operations')\
        .select('*')\
        .limit(5)\
        .execute()

    print(f"Total rows fetched: {len(daily_ops.data)}")

    if daily_ops.data:
        print("\nSample row:")
        sample = daily_ops.data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
    else:
        print("❌ NO DATA IN daily_operations table!")

except Exception as e:
    print(f"❌ Error querying daily_operations: {e}")

# Check shift_operations
print("\n" + "="*60)
print("SHIFT OPERATIONS TABLE")
print("="*60)

try:
    shift_ops = supabase.table('shift_operations')\
        .select('*')\
        .limit(5)\
        .execute()

    print(f"Total rows fetched: {len(shift_ops.data)}")

    if shift_ops.data:
        print("\nSample row:")
        sample = shift_ops.data[0]
        for key, value in sample.items():
            print(f"  {key}: {value}")
    else:
        print("❌ NO DATA IN shift_operations table!")

except Exception as e:
    print(f"❌ Error querying shift_operations: {e}")

# Count total rows
print("\n" + "="*60)
print("ROW COUNTS")
print("="*60)

try:
    daily_count = supabase.table('daily_operations')\
        .select('*', count='exact')\
        .execute()
    print(f"daily_operations: {daily_count.count} rows")
except Exception as e:
    print(f"Error counting daily_operations: {e}")

try:
    shift_count = supabase.table('shift_operations')\
        .select('*', count='exact')\
        .execute()
    print(f"shift_operations: {shift_count.count} rows")
except Exception as e:
    print(f"Error counting shift_operations: {e}")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)