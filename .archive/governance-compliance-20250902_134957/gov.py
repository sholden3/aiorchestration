#!/usr/bin/env python3
"""
Governance CLI Tool
Simple command-line interface for all governance operations
Usage: python gov.py [command]

@author Dr. Sarah Chen v1.2 - Backend Systems & Governance Architecture
@architecture CLI interface for governance monitoring and enforcement
@business_logic Provides real-time governance status and validation
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add governance to path
sys.path.insert(0, str(Path(__file__).parent))


def cmd_status():
    """Show governance status dashboard"""
    from governance.core.governance_monitor import get_monitor, show_governance_banner
    
    # Show banner
    show_governance_banner()
    
    # Get monitor and show statistics
    monitor = get_monitor()
    monitor.show_statistics()


def cmd_check(files):
    """Check specific files for governance issues"""
    from governance.scripts.integrated_pre_commit_hook import IntegratedGovernanceHook
    
    hook = IntegratedGovernanceHook()
    file_paths = [Path(f) for f in files]
    
    for file_path in file_paths:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n🔍 Checking {file_path}...")
        result = hook.check_file(file_path)
        
        if result['issues']:
            print(f"  Found {len(result['issues'])} issues:")
            for issue in result['issues']:
                severity = issue.get('severity', 'unknown')
                message = issue.get('message', 'No message')
                print(f"  • [{severity}] {message}")
        else:
            print("  ✅ No issues found")


def cmd_validate():
    """Validate governance system"""
    from governance.scripts.validate_governance import GovernanceValidator
    validator = GovernanceValidator()
    return validator.run_validation()


def cmd_test():
    """Quick test of governance components"""
    from governance.scripts.quick_test import main as quick_test
    return quick_test()


def cmd_events():
    """Show recent governance events"""
    from governance.core.governance_monitor import get_monitor
    
    monitor = get_monitor()
    
    # Show recent events from the monitor's event list
    print(f"\n📊 Recent Governance Events:\n")
    
    if monitor.events:
        for event in monitor.events[-10:]:  # Show last 10
            timestamp = event.timestamp.strftime('%H:%M:%S')
            print(f"[{timestamp}] {event.severity}: {event.description}")
            if event.details:
                for key, value in event.details.items():
                    print(f"         {key}: {value}")
    else:
        print("No events recorded yet. Try running a governance check!")


def cmd_export(output_file):
    """Export governance metrics"""
    import json
    from governance.core.governance_monitor import get_monitor
    
    monitor = get_monitor()
    
    # Create export data
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'start_time': monitor.start_time.isoformat(),
        'event_count': monitor.event_count,
        'statistics': monitor.stats,
        'events': [
            {
                'type': e.event_type.value,
                'timestamp': e.timestamp.isoformat(),
                'description': e.description,
                'severity': e.severity,
                'details': e.details
            }
            for e in monitor.events
        ]
    }
    
    # Save to file
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = Path('.governance') / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Metrics exported to: {output_path}")


def cmd_freshness():
    """Check test freshness"""
    from governance.core.enhanced_governance_engine import TestExecutionTracker
    tracker = TestExecutionTracker()
    status = tracker.get_test_status()
    
    print("\n🧪 Test Freshness Status:")
    
    if status.get('has_runs'):
        last_run = status.get('last_run', {})
        print(f"  Last run: {last_run.get('timestamp', 'Unknown')}")
        print(f"  Suite: {last_run.get('suite', 'Unknown')}")
        print(f"  Coverage: {last_run.get('coverage', 0):.1f}%")
        print(f"  Passed: {last_run.get('passed', 0)}, Failed: {last_run.get('failed', 0)}")
        
        hours_old = status.get('hours_since_last_run', 999)
        if hours_old > 168:  # 7 days
            print(f"  ⚠️  Tests are {hours_old/24:.1f} days old - very stale!")
        elif hours_old > 24:
            print(f"  ⚠️  Tests are {hours_old/24:.1f} days old - consider running them")
        else:
            print(f"  ✅ Tests are fresh ({hours_old:.1f} hours old)")
    else:
        print("  ⚠️  No test runs recorded yet")
        print("  Run: pytest to execute tests")


def cmd_deps(file):
    """Analyze file dependencies"""
    import ast
    import re
    
    print(f"\n🔗 Analyzing dependencies for {file}:")
    
    if not Path(file).exists():
        print(f"  ❌ File not found: {file}")
        return 1
    
    try:
        with open(file, 'r') as f:
            content = f.read()
        
        # Basic dependency analysis
        imports = []
        
        if file.endswith('.py'):
            # Python imports
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        elif file.endswith(('.ts', '.js')):
            # JavaScript/TypeScript imports
            import_pattern = r"import\s+.*?\s+from\s+['\"](.+?)['\"]"
            imports = re.findall(import_pattern, content)
        
        print(f"  Imports found: {len(imports)}")
        if imports:
            print("  Dependencies:")
            for imp in imports[:10]:
                print(f"    • {imp}")
            if len(imports) > 10:
                print(f"    ... and {len(imports) - 10} more")
        
        # Find potential test files
        base_name = Path(file).stem
        test_patterns = [
            f"test_{base_name}.py",
            f"{base_name}_test.py", 
            f"{base_name}.spec.ts",
            f"{base_name}.test.js"
        ]
        
        print("\n  Potential test files:")
        for pattern in test_patterns:
            print(f"    • {pattern}")
        
    except Exception as e:
        print(f"  ❌ Error analyzing file: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Governance CLI - Monitor and manage governance system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gov.py status              # Show dashboard
  python gov.py check file.py       # Check specific file
  python gov.py validate            # Validate system
  python gov.py test                # Quick test
  python gov.py events              # Show recent events
  python gov.py freshness           # Check test freshness
  python gov.py deps src/file.py    # Analyze dependencies
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    subparsers.add_parser('status', help='Show governance dashboard')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check files for issues')
    check_parser.add_argument('files', nargs='+', help='Files to check')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate governance system')
    
    # Test command
    subparsers.add_parser('test', help='Quick test of components')
    
    # Events command
    subparsers.add_parser('events', help='Show recent events')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export metrics')
    export_parser.add_argument('--output', help='Output file')
    
    # Freshness command
    subparsers.add_parser('freshness', help='Check test freshness')
    
    # Dependencies command
    deps_parser = subparsers.add_parser('deps', help='Analyze file dependencies')
    deps_parser.add_argument('file', help='File to analyze')
    
    args = parser.parse_args()
    
    # Default to status if no command
    if not args.command:
        args.command = 'status'
    
    # Execute command
    try:
        if args.command == 'status':
            return cmd_status() or 0
        elif args.command == 'check':
            return cmd_check(args.files) or 0
        elif args.command == 'validate':
            return cmd_validate()
        elif args.command == 'test':
            return cmd_test()
        elif args.command == 'events':
            return cmd_events() or 0
        elif args.command == 'export':
            return cmd_export(args.output) or 0
        elif args.command == 'freshness':
            return cmd_freshness() or 0
        elif args.command == 'deps':
            return cmd_deps(args.file) or 0
        else:
            parser.print_help()
            return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())