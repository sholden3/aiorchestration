#!/usr/bin/env python3
"""
Start Governance System
Launches all governance components

@author Dr. Sarah Chen v1.2 - Backend Systems & Governance Architecture
@architecture System startup orchestrator for governance components
@business_logic Launches monitoring, API server, and dashboard components
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
import threading

def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🛡️  GOVERNANCE SYSTEM STARTUP                      ║
║                                                                  ║
║  Starting all governance components...                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def check_requirements():
    """Check if required packages are installed"""
    required = ['fastapi', 'uvicorn', 'pyyaml', 'aiohttp']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def start_api_server():
    """Start the governance API server"""
    print("\n📡 Starting Governance API Server...")
    
    api_path = Path(__file__).parent / "governance" / "api" / "governance_api.py"
    
    if not api_path.exists():
        print(f"❌ API server not found at {api_path}")
        return None
    
    try:
        # Start API server in subprocess
        process = subprocess.Popen(
            [sys.executable, str(api_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ API Server started on http://localhost:8001")
            print("   API Docs: http://localhost:8001/docs")
            return process
        else:
            print("❌ API Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_web_dashboard():
    """Open the web dashboard"""
    print("\n🌐 Starting Web Dashboard...")
    
    dashboard_path = Path(__file__).parent / "governance" / "dashboard" / "index.html"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at {dashboard_path}")
        return False
    
    try:
        # Open dashboard in browser
        dashboard_url = f"file:///{dashboard_path.absolute()}"
        webbrowser.open(dashboard_url)
        print(f"✅ Dashboard opened in browser")
        print(f"   URL: {dashboard_url}")
        return True
        
    except Exception as e:
        print(f"❌ Error opening dashboard: {e}")
        return False

def start_monitoring():
    """Start the governance monitoring"""
    print("\n📊 Starting Governance Monitor...")
    
    try:
        from governance.core.governance_monitor import get_monitor, show_governance_banner
        
        # Show banner
        show_governance_banner()
        
        # Get monitor instance
        monitor = get_monitor()
        monitor.show_statistics()
        
        print("✅ Governance monitor active")
        return True
        
    except Exception as e:
        print(f"❌ Error starting monitor: {e}")
        return False

def install_git_hooks():
    """Check and install git hooks if needed"""
    print("\n🔗 Checking Git Hooks...")
    
    git_hooks_dir = Path(".git") / "hooks"
    pre_commit = git_hooks_dir / "pre-commit"
    
    if not git_hooks_dir.exists():
        print("⚠️  Not in a git repository - skipping hooks")
        return False
    
    if pre_commit.exists():
        print("✅ Git hooks already installed")
        return True
    
    print("📝 Installing git hooks...")
    
    install_script = Path(__file__).parent / "governance" / "scripts" / "install_git_hooks.py"
    
    if install_script.exists():
        try:
            subprocess.run([sys.executable, str(install_script)], check=True)
            print("✅ Git hooks installed")
            return True
        except:
            print("⚠️  Could not install git hooks automatically")
            print(f"   Run manually: python {install_script}")
            return False
    
    return False

def show_commands():
    """Show available commands"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    GOVERNANCE COMMANDS                          ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  CLI Commands:                                                  ║
║    python gov.py status        - Show governance status         ║
║    python gov.py check <file>  - Check specific file           ║
║    python gov.py validate      - Validate entire system        ║
║    python gov.py events        - Show recent events            ║
║    python gov.py freshness     - Check test freshness          ║
║                                                                  ║
║  API Endpoints:                                                 ║
║    http://localhost:8001       - API root                      ║
║    http://localhost:8001/docs  - API documentation            ║
║                                                                  ║
║  Dashboard:                                                     ║
║    Open governance/dashboard/index.html in browser             ║
║                                                                  ║
║  Monitoring:                                                    ║
║    python run_governance_monitor.py                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def main():
    """Main startup sequence"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing requirements first")
        return 1
    
    # Track what's running
    components = {
        'api_server': None,
        'dashboard': False,
        'monitor': False,
        'git_hooks': False
    }
    
    # Start components
    components['api_server'] = start_api_server()
    components['dashboard'] = start_web_dashboard()
    components['monitor'] = start_monitoring()
    components['git_hooks'] = install_git_hooks()
    
    # Summary
    print("\n" + "="*70)
    print("GOVERNANCE SYSTEM STATUS")
    print("="*70)
    
    if components['api_server']:
        print("✅ API Server: Running on http://localhost:8001")
    else:
        print("❌ API Server: Not running")
    
    if components['dashboard']:
        print("✅ Dashboard: Opened in browser")
    else:
        print("⚠️  Dashboard: Not opened")
    
    if components['monitor']:
        print("✅ Monitor: Active")
    else:
        print("⚠️  Monitor: Not active")
    
    if components['git_hooks']:
        print("✅ Git Hooks: Installed")
    else:
        print("⚠️  Git Hooks: Not installed")
    
    print("\n📊 Current Phase: 2 (Advisory)")
    print("   To change: export GOVERNANCE_PHASE=3")
    
    # Show commands
    show_commands()
    
    # Keep running if API server is active
    if components['api_server']:
        print("\n🔄 Governance system is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
                # Check if API server is still running
                if components['api_server'].poll() is not None:
                    print("\n⚠️  API server stopped unexpectedly")
                    break
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down governance system...")
            if components['api_server']:
                components['api_server'].terminate()
                components['api_server'].wait(timeout=5)
            print("✅ Governance system stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())