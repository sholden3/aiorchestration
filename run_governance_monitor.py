#!/usr/bin/env python3
"""
Simple runner script for governance monitoring
Run this to see the governance dashboard

@author Dr. Sarah Chen v1.2 - Backend Systems & Governance Architecture
@architecture Runner script for governance monitoring dashboard
@business_logic Initializes and displays real-time governance monitoring
"""

import sys
from pathlib import Path

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the real-time monitoring 
from governance.core.governance_monitor import get_monitor, show_governance_banner

def main():
    """Run the governance monitoring dashboard"""
    try:
        # Show the banner
        show_governance_banner()
        
        # Get the monitor instance
        monitor = get_monitor()
        
        # Show current statistics
        monitor.show_statistics()
        
        # Show some sample events to demonstrate it's working
        print("\n📝 Monitoring governance activities in real-time...")
        print("   (Governance checks will appear here as they happen)")
        print("\n   Try running: git commit -m 'test' in another terminal")
        print("   Or: python gov.py check <file>")
        print("\n   Press Ctrl+C to exit\n")
        
        # Keep running to show events
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
        
        return 0
    except Exception as e:
        print(f"Error running governance monitor: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())