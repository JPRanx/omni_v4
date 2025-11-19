#!/usr/bin/env python
"""
Serve the dashboard on localhost for development and testing.

This script starts a simple HTTP server from the dashboard directory,
making it accessible at http://localhost:8080

Usage:
    python scripts/serve_dashboard.py
    python scripts/serve_dashboard.py --port 8080
"""

import sys
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import time


def serve_dashboard(port=8080):
    """Start HTTP server and open browser."""
    # Get dashboard directory
    project_root = Path(__file__).parent.parent
    dashboard_dir = project_root / "dashboard"

    if not dashboard_dir.exists():
        print(f"Error: Dashboard directory not found: {dashboard_dir}")
        print("\nPlease ensure the dashboard has been set up correctly.")
        return False

    # Change to dashboard directory
    import os
    os.chdir(dashboard_dir)

    # Create server
    handler = SimpleHTTPRequestHandler
    server = HTTPServer(('localhost', port), handler)

    print("\n" + "="*80)
    print("Restaurant Analytics Dashboard Server")
    print("="*80)
    print(f"\nServing from: {dashboard_dir}")
    print(f"URL:          http://localhost:{port}/index.html")
    print(f"Press Ctrl+C to stop the server")
    print("\n" + "="*80 + "\n")

    # Open browser after short delay
    def open_browser():
        time.sleep(1.5)
        url = f'http://localhost:{port}/index.html'
        print(f"Opening browser: {url}")
        webbrowser.open(url)

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
        return True


def main():
    """Main entry point."""
    port = 8080

    # Parse port argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "--port" and len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print(f"Error: Invalid port number: {sys.argv[2]}")
                sys.exit(1)
        elif sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("\nUsage: python scripts/serve_dashboard.py [--port 8080]")
            sys.exit(1)

    success = serve_dashboard(port)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
