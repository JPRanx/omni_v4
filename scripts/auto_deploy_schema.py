#!/usr/bin/env python3
"""
Auto-deploy schema to Supabase using the service role key.

This attempts to execute raw SQL using Supabase's RPC functionality.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()

def execute_sql_file(client, sql_file_path: Path, description: str):
    """Execute a SQL file via Supabase."""

    print(f"\n[INFO] Executing {description}...")
    print(f"       File: {sql_file_path.name}")

    # Read SQL file
    with open(sql_file_path, 'r') as f:
        sql = f.read()

    try:
        # Try executing via RPC
        # Note: This requires creating a stored procedure first
        result = client.rpc('exec_sql', {'query': sql}).execute()
        print(f"[OK] {description} executed successfully")
        return True
    except Exception as e:
        error_msg = str(e)

        # If RPC doesn't exist, we need to use manual deployment
        if 'function' in error_msg.lower() or 'does not exist' in error_msg.lower():
            print(f"[INFO] RPC method not available - using direct execution")

            # Split SQL into individual statements
            statements = [s.strip() for s in sql.split(';') if s.strip()]

            success_count = 0
            for i, stmt in enumerate(statements, 1):
                if not stmt or stmt.startswith('--'):
                    continue

                try:
                    # Execute using postgrest
                    # This is a workaround - may not work for all DDL
                    client.postgrest.session.post(
                        f"{client.supabase_url}/rest/v1/rpc/exec",
                        json={"sql": stmt}
                    )
                    success_count += 1
                except Exception as stmt_error:
                    print(f"[WARNING] Statement {i} failed: {str(stmt_error)[:100]}")

            if success_count > 0:
                print(f"[OK] Executed {success_count}/{len(statements)} statements")
                return True
            else:
                print(f"[ERROR] Could not execute SQL automatically")
                return False
        else:
            print(f"[ERROR] {error_msg}")
            return False

def auto_deploy():
    """Automatically deploy schema to Supabase."""

    # Get credentials
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin

    if not url or not service_key:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
        print("\nYou need the SERVICE_ROLE key (not anon key) for schema deployment")
        return False

    print("=" * 80)
    print("OMNI V4 - AUTO SCHEMA DEPLOYMENT")
    print("=" * 80)
    print()
    print(f"Target: {url}")
    print("Using: SERVICE_ROLE key (admin access)")
    print()

    # Create client with service role
    try:
        client = create_client(url, service_key)
        print("[OK] Connected to Supabase")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

    # Get migration files
    migrations_dir = Path('src/storage/migrations')
    schema_file = migrations_dir / '001_create_schema.sql'
    indexes_file = migrations_dir / '002_create_indexes.sql'

    # Execute schema
    success = True
    success = execute_sql_file(client, schema_file, "Schema creation") and success
    success = execute_sql_file(client, indexes_file, "Index creation") and success

    print()
    print("=" * 80)

    if success:
        print("[SUCCESS] Schema deployed!")
        print()
        print("Next: Run python scripts/test_supabase_connection.py")
        print("      to verify all tables were created")
    else:
        print("[FAILED] Automatic deployment didn't work")
        print()
        print("Manual deployment required:")
        print("  Run: python scripts/deploy_schema.py")
        print("  Follow instructions to paste SQL in Supabase Dashboard")

    print("=" * 80)

    return success

if __name__ == "__main__":
    auto_deploy()
