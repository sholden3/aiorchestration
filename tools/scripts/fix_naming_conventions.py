#!/usr/bin/env python3
"""
Naming Convention Fix Script
Part of SDR-001: STRUCTURAL_DEBT_REMEDIATION
Fixes naming convention violations identified by audit
"""

import os
import re
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import subprocess

class NamingConventionFixer:
    """Fix naming convention issues safely and incrementally."""
    
    def __init__(self, dry_run: bool = True, create_backup: bool = True):
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.root = Path('.')
        self.changes = []
        self.rollback_map = {}
        self.import_updates = []
        
    def load_audit_results(self, audit_file: str = 'naming_audit.json') -> Dict:
        """Load audit results from JSON file."""
        if not Path(audit_file).exists():
            print(f"ERROR: Audit file {audit_file} not found. Run naming_audit.py first.")
            sys.exit(1)
            
        with open(audit_file, 'r') as f:
            return json.load(f)
    
    def create_backup(self) -> str:
        """Create timestamped backup of critical directories."""
        if not self.create_backup:
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_naming_{timestamp}.tar.gz'
        
        print(f"Creating backup: {backup_name}")
        
        # Create tar backup of critical directories
        import tarfile
        with tarfile.open(backup_name, 'w:gz') as tar:
            # Backup critical directories but exclude node_modules, temp, etc
            for dir_name in ['apps', 'libs', 'tests', 'tools']:
                if Path(dir_name).exists():
                    tar.add(dir_name, filter=self._tar_filter)
        
        print(f"Backup created: {backup_name}")
        return backup_name
    
    def _tar_filter(self, tarinfo):
        """Filter out unnecessary files from backup."""
        exclude_patterns = [
            'node_modules', '__pycache__', '.git', 
            'temp', 'htmlcov', '.pytest_cache'
        ]
        
        for pattern in exclude_patterns:
            if pattern in tarinfo.name:
                return None
        return tarinfo
    
    def generate_fix_plan(self, audit_results: Dict) -> List[Dict]:
        """Generate a prioritized fix plan from audit results."""
        fixes = []
        
        # Priority 1: Fix redundant nesting (apps/api/api)
        if 'redundant_nesting' in audit_results['issues']:
            for issue in audit_results['issues']['redundant_nesting']:
                fixes.append({
                    'type': 'redundant_nesting',
                    'priority': 1,
                    'old_path': issue['path'],
                    'action': 'merge_to_parent',
                    'severity': 'HIGH'
                })
        
        # Priority 2: Fix critical hyphenated directories in apps/libs
        if 'hyphenated_directories' in audit_results['issues']:
            for issue in audit_results['issues']['hyphenated_directories']:
                if issue['severity'] == 'HIGH':
                    fixes.append({
                        'type': 'hyphenated_directory',
                        'priority': 2,
                        'old_path': issue['path'],
                        'new_path': issue['path'].replace('-', '_'),
                        'severity': 'HIGH'
                    })
        
        # Priority 3: Fix versioned file names
        if 'versioned_file_names' in audit_results['issues']:
            for issue in audit_results['issues']['versioned_file_names']:
                fixes.append({
                    'type': 'versioned_file',
                    'priority': 3,
                    'old_path': issue['path'],
                    'new_name': issue['suggested'] + '.py',
                    'severity': 'MEDIUM'
                })
        
        # Sort by priority
        fixes.sort(key=lambda x: x['priority'])
        
        return fixes
    
    def validate_fix(self, fix: Dict) -> bool:
        """Validate that a fix is safe to apply."""
        old_path = Path(fix['old_path'])
        
        # Check source exists
        if not old_path.exists():
            print(f"WARNING: Source path does not exist: {old_path}")
            return False
        
        # Check for conflicts
        if 'new_path' in fix:
            new_path = Path(fix['new_path'])
            if new_path.exists() and new_path != old_path:
                print(f"ERROR: Target already exists: {new_path}")
                return False
        
        return True
    
    def apply_fix(self, fix: Dict) -> bool:
        """Apply a single fix."""
        if not self.validate_fix(fix):
            return False
        
        if fix['type'] == 'redundant_nesting':
            return self._fix_redundant_nesting(fix)
        elif fix['type'] == 'hyphenated_directory':
            return self._fix_hyphenated_directory(fix)
        elif fix['type'] == 'versioned_file':
            return self._fix_versioned_file(fix)
        
        return False
    
    def _fix_redundant_nesting(self, fix: Dict) -> bool:
        """Fix redundant nesting like apps/api/api."""
        old_path = Path(fix['old_path'])
        parent_path = old_path.parent
        
        print(f"\nFixing redundant nesting: {old_path}")
        
        if self.dry_run:
            print(f"  [DRY RUN] Would merge {old_path} into {parent_path}")
            
            # Show what would be moved
            for item in old_path.iterdir():
                target = parent_path / item.name
                print(f"    {item} -> {target}")
            
            return True
        
        # Actually perform the merge
        try:
            for item in old_path.iterdir():
                target = parent_path / item.name
                
                if target.exists():
                    print(f"  WARNING: {target} already exists, skipping")
                    continue
                
                shutil.move(str(item), str(target))
                self.changes.append({
                    'type': 'move',
                    'from': str(item),
                    'to': str(target)
                })
                print(f"  Moved: {item.name}")
            
            # Remove empty directory
            old_path.rmdir()
            print(f"  Removed empty directory: {old_path}")
            
            return True
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
    
    def _fix_hyphenated_directory(self, fix: Dict) -> bool:
        """Fix hyphenated directory names."""
        old_path = Path(fix['old_path'])
        new_path = Path(fix['new_path'])
        
        print(f"\nFixing hyphenated directory: {old_path}")
        
        if self.dry_run:
            print(f"  [DRY RUN] Would rename to: {new_path}")
            
            # Find affected imports
            affected_imports = self._find_affected_imports(old_path, new_path)
            if affected_imports:
                print(f"  Would update {len(affected_imports)} import statements")
            
            return True
        
        # Actually perform the rename
        try:
            # Rename directory
            shutil.move(str(old_path), str(new_path))
            self.changes.append({
                'type': 'rename',
                'from': str(old_path),
                'to': str(new_path)
            })
            print(f"  Renamed to: {new_path}")
            
            # Update imports
            self._update_imports(old_path, new_path)
            
            return True
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
    
    def _fix_versioned_file(self, fix: Dict) -> bool:
        """Fix versioned file names."""
        old_path = Path(fix['old_path'])
        new_path = old_path.parent / fix['new_name']
        
        print(f"\nFixing versioned file: {old_path}")
        
        if self.dry_run:
            print(f"  [DRY RUN] Would rename to: {new_path}")
            
            # Find affected imports
            affected_imports = self._find_affected_imports(old_path, new_path)
            if affected_imports:
                print(f"  Would update {len(affected_imports)} import statements")
            
            return True
        
        # Actually perform the rename
        try:
            # Check if target exists
            if new_path.exists():
                print(f"  WARNING: Target already exists: {new_path}")
                # Create backup with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = new_path.parent / f"{new_path.stem}_backup_{timestamp}{new_path.suffix}"
                shutil.move(str(new_path), str(backup_path))
                print(f"  Backed up existing file to: {backup_path}")
            
            # Rename file
            shutil.move(str(old_path), str(new_path))
            self.changes.append({
                'type': 'rename',
                'from': str(old_path),
                'to': str(new_path)
            })
            print(f"  Renamed to: {new_path}")
            
            # Update imports
            self._update_imports(old_path, new_path)
            
            return True
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return False
    
    def _find_affected_imports(self, old_path: Path, new_path: Path) -> List[Tuple[Path, str, str]]:
        """Find all imports that would be affected by a rename."""
        affected = []
        
        # Convert paths to module names
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)
        
        # Search all Python files
        for py_file in self.root.rglob('*.py'):
            if '__pycache__' in str(py_file) or 'temp' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Check if this file imports the old module
                if old_module in content:
                    affected.append((py_file, old_module, new_module))
                    
            except Exception:
                pass
        
        return affected
    
    def _update_imports(self, old_path: Path, new_path: Path):
        """Update all import statements affected by a rename."""
        affected = self._find_affected_imports(old_path, new_path)
        
        for py_file, old_module, new_module in affected:
            try:
                content = py_file.read_text(encoding='utf-8')
                updated_content = content.replace(old_module, new_module)
                
                if updated_content != content:
                    py_file.write_text(updated_content, encoding='utf-8')
                    self.import_updates.append({
                        'file': str(py_file),
                        'old': old_module,
                        'new': new_module
                    })
                    print(f"  Updated imports in: {py_file}")
                    
            except Exception as e:
                print(f"  ERROR updating {py_file}: {e}")
    
    def _path_to_module(self, path: Path) -> str:
        """Convert file path to Python module name."""
        # Remove file extension if present
        if path.suffix == '.py':
            path = path.with_suffix('')
        
        # Convert path separators to dots
        parts = []
        for part in path.parts:
            if part not in ['.', '..']:
                parts.append(part.replace('-', '_'))
        
        return '.'.join(parts)
    
    def generate_rollback_script(self) -> str:
        """Generate a rollback script based on changes made."""
        if not self.changes:
            return None
        
        script_name = 'rollback_naming_changes.py'
        
        script_content = '''#!/usr/bin/env python3
"""
Rollback script for naming convention changes
Generated: {timestamp}
"""

import shutil
from pathlib import Path

changes = {changes}

def rollback():
    """Rollback all naming changes."""
    print("Rolling back naming convention changes...")
    
    # Process in reverse order
    for change in reversed(changes):
        if change['type'] == 'rename':
            try:
                shutil.move(change['to'], change['from'])
                print(f"  Reverted: {{change['to']}} -> {{change['from']}}")
            except Exception as e:
                print(f"  ERROR: {{e}}")
        elif change['type'] == 'move':
            try:
                shutil.move(change['to'], change['from'])
                print(f"  Reverted: {{change['to']}} -> {{change['from']}}")
            except Exception as e:
                print(f"  ERROR: {{e}}")
    
    print("Rollback complete!")

if __name__ == '__main__':
    rollback()
'''.format(
            timestamp=datetime.now().isoformat(),
            changes=json.dumps(self.changes, indent=4)
        )
        
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        print(f"\nRollback script created: {script_name}")
        return script_name
    
    def generate_report(self) -> str:
        """Generate execution report."""
        report = []
        report.append("# Naming Convention Fix Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTED'}")
        
        if self.changes:
            report.append(f"\n## Changes Made ({len(self.changes)})")
            for change in self.changes:
                report.append(f"- {change['type']}: `{change['from']}` → `{change['to']}`")
        
        if self.import_updates:
            report.append(f"\n## Import Updates ({len(self.import_updates)})")
            for update in self.import_updates[:10]:
                report.append(f"- {update['file']}: `{update['old']}` → `{update['new']}`")
            if len(self.import_updates) > 10:
                report.append(f"  ...and {len(self.import_updates) - 10} more")
        
        return '\n'.join(report)
    
    def run_tests(self) -> bool:
        """Run tests to validate changes."""
        print("\n" + "="*50)
        print("Running validation tests...")
        print("="*50)
        
        # Test Python imports
        print("\n1. Testing Python imports...")
        test_imports = [
            "import apps.api.main",
            "import libs.governance.core.engine",
        ]
        
        for import_stmt in test_imports:
            try:
                exec(import_stmt)
                print(f"  ✓ {import_stmt}")
            except ImportError as e:
                print(f"  ✗ {import_stmt}: {e}")
                return False
        
        # Run pytest if available
        print("\n2. Running pytest...")
        try:
            result = subprocess.run(
                ['pytest', 'tests/unit/governance', '-q'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ All tests passed")
            else:
                print(f"  ✗ Tests failed: {result.stdout}")
                return False
        except FileNotFoundError:
            print("  ⚠ pytest not found, skipping")
        
        return True


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description='Fix naming convention issues')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed without making changes')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute the changes')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip creating backup')
    parser.add_argument('--validate', action='store_true',
                        help='Run validation tests after changes')
    parser.add_argument('--priority', type=int, default=3,
                        help='Maximum priority level to fix (1=highest)')
    
    args = parser.parse_args()
    
    # Override dry_run if execute is specified
    if args.execute:
        args.dry_run = False
    
    print("="*50)
    print("NAMING CONVENTION FIXER")
    print("="*50)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTION'}")
    print(f"Backup: {'ENABLED' if not args.no_backup else 'DISABLED'}")
    print(f"Priority: <= {args.priority}")
    print("="*50)
    
    fixer = NamingConventionFixer(
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    # Load audit results
    audit_results = fixer.load_audit_results()
    print(f"\nLoaded audit results: {audit_results['summary']['total_issues']} issues found")
    
    # Create backup if executing
    if not args.dry_run and not args.no_backup:
        backup_file = fixer.create_backup()
    
    # Generate fix plan
    fixes = fixer.generate_fix_plan(audit_results)
    fixes = [f for f in fixes if f['priority'] <= args.priority]
    
    print(f"\nGenerated fix plan: {len(fixes)} fixes to apply")
    
    # Apply fixes
    success_count = 0
    for i, fix in enumerate(fixes, 1):
        print(f"\n[{i}/{len(fixes)}] Priority {fix['priority']} - {fix['type']}")
        if fixer.apply_fix(fix):
            success_count += 1
    
    print("\n" + "="*50)
    print(f"SUMMARY: {success_count}/{len(fixes)} fixes {'would be' if args.dry_run else 'were'} applied")
    print("="*50)
    
    # Generate rollback script if changes were made
    if not args.dry_run and fixer.changes:
        fixer.generate_rollback_script()
    
    # Generate report
    report = fixer.generate_report()
    report_file = 'naming_fix_report.md'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")
    
    # Run validation tests if requested and changes were made
    if args.validate and not args.dry_run and fixer.changes:
        if not fixer.run_tests():
            print("\n⚠️  VALIDATION FAILED - Consider rolling back changes")
            sys.exit(1)
    
    print("\n✅ Naming convention fix complete!")


if __name__ == '__main__':
    main()