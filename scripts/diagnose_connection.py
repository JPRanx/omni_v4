#!/usr/bin/env python3
"""Diagnose Supabase connection issues."""

import os
import socket
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env from project root explicitly
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(env_path, override=True)

def diagnose():
    """Run connection diagnostics."""

    print("=" * 80)
    print("SUPABASE CONNECTION DIAGNOSTICS")
    print("=" * 80)
    print()

    # Check environment variables
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    print("1. ENVIRONMENT VARIABLES")
    print("-" * 80)
    print(f"SUPABASE_URL: {url}")
    print(f"SUPABASE_KEY: {'Set (' + str(len(key)) + ' chars)' if key else 'NOT SET'}")
    print()

    if not url:
        print("[ERROR] SUPABASE_URL not set in .env")
        return

    # Parse URL
    parsed = urlparse(url)
    hostname = parsed.netloc

    print("2. URL PARSING")
    print("-" * 80)
    print(f"Protocol: {parsed.scheme}")
    print(f"Hostname: {hostname}")
    print(f"Path: {parsed.path}")
    print()

    # Test DNS resolution
    print("3. DNS RESOLUTION")
    print("-" * 80)
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"[OK] Resolved {hostname} to {ip_address}")
    except socket.gaierror as e:
        print(f"[ERROR] DNS resolution failed: {e}")
        print()
        print("POSSIBLE FIXES:")
        print("  1. Check internet connection")
        print("  2. Try flushing DNS cache: ipconfig /flushdns")
        print("  3. Try different DNS server (8.8.8.8 or 1.1.1.1)")
        print("  4. Check if firewall is blocking DNS")
        return
    print()

    # Test TCP connection
    print("4. TCP CONNECTION")
    print("-" * 80)
    port = 443  # HTTPS
    try:
        sock = socket.create_connection((hostname, port), timeout=5)
        sock.close()
        print(f"[OK] Successfully connected to {hostname}:{port}")
    except socket.timeout:
        print(f"[ERROR] Connection timeout to {hostname}:{port}")
        print("  Firewall may be blocking HTTPS connections")
        return
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return
    print()

    # Test HTTP request
    print("5. HTTP REQUEST")
    print("-" * 80)
    try:
        import urllib.request
        req = urllib.request.Request(url + '/rest/v1/')
        req.add_header('apikey', key)

        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            print(f"[OK] HTTP {status} from {url}/rest/v1/")
    except Exception as e:
        print(f"[ERROR] HTTP request failed: {e}")
        return
    print()

    # Test Supabase client
    print("6. SUPABASE CLIENT")
    print("-" * 80)
    try:
        from supabase import create_client
        client = create_client(url, key)
        print("[OK] Supabase client created")

        # Try to query restaurants
        result = client.table('restaurants').select('*').limit(1).execute()
        print(f"[OK] Query successful - {len(result.data)} rows returned")

        if result.data:
            print(f"     Sample: {result.data[0]}")

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Supabase client failed: {e}")

        if "does not exist" in error_msg.lower():
            print()
            print("DIAGNOSIS: Tables not created yet")
            print("  Run the schema SQL in Supabase Dashboard")
        elif "policy" in error_msg.lower() or "permission" in error_msg.lower():
            print()
            print("DIAGNOSIS: RLS/Permissions issue")
            print("  Run: 003_configure_permissions.sql in Supabase Dashboard")
        return

    print()
    print("=" * 80)
    print("[SUCCESS] All diagnostics passed!")
    print("=" * 80)

if __name__ == "__main__":
    diagnose()
