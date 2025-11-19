"""Quick test script to verify Supabase connection."""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(override=True)

from supabase import create_client

# Create client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"Testing connection to: {url}")
client = create_client(url, key)
print("[OK] Client created successfully")

# Try to query a table (might not exist yet)
try:
    result = client.table('restaurants').select('*').limit(1).execute()
    print("[OK] Database query successful!")
    print(f"  Found {len(result.data)} rows")
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)

    if "relation" in error_msg.lower() or "does not exist" in error_msg.lower():
        print("[OK] Database accessible (no tables exist yet)")
    else:
        print(f"[ERROR] Query failed: {error_type}")
        print(f"  Message: {error_msg[:200]}")

print("\nConnection test complete!")
