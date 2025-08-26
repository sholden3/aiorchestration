#!/usr/bin/env python
"""
Unicode and Folder Structure Validator
Ensures Windows compatibility and clean project organization
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

class UnicodeAndStructureValidator:
    """Validates codebase for unicode issues and folder structure problems"""
    
    def __init__(self, config_path: str = "governance_config.json"):
        """Initialize validator with configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.unicode_config = self.config['validation_rules']['global'].get('no_unicode_characters', {})
        self.structure_config = self.config['validation_rules']['global'].get('folder_structure', {})
        
        self.violations = {
            'unicode': [],
            'structure': [],
            'naming': []
        }
        
        self.stats = {
            'files_scanned': 0,
            'unicode_violations': 0,
            'structure_violations': 0,
            'files_fixed': 0
        }
    
    def scan_for_unicode(self, directory: str = '.') -> List[Dict[str, Any]]:
        """Scan directory for unicode/emoji characters"""
        # Common unicode/emoji ranges
        unicode_patterns = [
            (r'[\u2600-\u27BF]', 'Symbol'),  # Misc symbols
            (r'[\U0001F300-\U0001F9FF]', 'Emoji'),  # Emoticons/emoji
            (r'[\u2700-\u27BF]', 'Dingbats'),  # Dingbats
            (r'[\u2122\u2139\u2194-\u2199\u21A9-\u21AA]', 'Arrows'),  # Various symbols
            (r'[\u2300-\u23FF]', 'Technical'),  # Technical symbols
            (r'[\u2B00-\u2BFF]', 'Shapes'),  # Shapes
            (r'[\u2200-\u22FF]', 'Math'),  # Mathematical operators
        ]
        exceptions = self.unicode_config.get('exceptions', [])
        
        violations = []
        
        for root, dirs, files in os.walk(directory):
            # Skip .git and __pycache__
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules'}]
            
            for file in files:
                # Check if file should be excluded
                skip = False
                for exception in exceptions:
                    if exception.startswith('*'):
                        if file.endswith(exception[1:]):
                            skip = True
                            break
                    elif exception.endswith('*'):
                        if file.startswith(exception[:-1]):
                            skip = True
                            break
                
                if skip or not file.endswith(('.py', '.js', '.ts', '.json')):
                    continue
                
                filepath = os.path.join(root, file)
                self.stats['files_scanned'] += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.splitlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern_regex, pattern_type in unicode_patterns:
                            matches = re.findall(pattern_regex, line)
                            for match in matches:
                                violations.append({
                                    'file': filepath,
                                    'line': line_num,
                                    'character': match,
                                    'type': pattern_type,
                                    'content': line.strip()[:100],
                                    'replacement': f'[{pattern_type.upper()}]'
                                })
                                self.stats['unicode_violations'] += 1
                
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
        
        self.violations['unicode'] = violations
        return violations
    
    def check_folder_structure(self, directory: str = '.') -> List[Dict[str, Any]]:
        """Check folder structure compliance"""
        violations = []
        required_folders = self.structure_config.get('required_folders', {})
        max_files = self.structure_config.get('max_files_per_folder', 20)
        naming_conventions = self.structure_config.get('naming_conventions', {})
        
        # Count files per folder
        folder_file_count = defaultdict(list)
        test_files_location = []
        config_files_location = []
        
        for root, dirs, files in os.walk(directory):
            # Skip system folders
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.pytest_cache'}]
            
            rel_root = os.path.relpath(root, directory)
            
            # Count Python files in folder
            py_files = [f for f in files if f.endswith('.py')]
            if len(py_files) > max_files:
                violations.append({
                    'type': 'too_many_files',
                    'folder': rel_root,
                    'file_count': len(py_files),
                    'max_allowed': max_files,
                    'severity': 'warning'
                })
                self.stats['structure_violations'] += 1
            
            # Check for test files outside test folder
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    if 'test' not in rel_root.lower():
                        test_files_location.append({
                            'file': os.path.join(rel_root, file),
                            'suggestion': 'Move to tests/ folder'
                        })
                
                # Check config files
                if file.endswith('_config.json') or file.startswith('config_'):
                    if 'config' not in rel_root.lower() and rel_root != '.':
                        config_files_location.append({
                            'file': os.path.join(rel_root, file),
                            'suggestion': 'Move to config/ folder'
                        })
        
        # Add location violations
        if test_files_location:
            violations.append({
                'type': 'misplaced_test_files',
                'files': test_files_location,
                'severity': 'warning'
            })
            self.stats['structure_violations'] += len(test_files_location)
        
        if config_files_location:
            violations.append({
                'type': 'misplaced_config_files',
                'files': config_files_location,
                'severity': 'warning'
            })
            self.stats['structure_violations'] += len(config_files_location)
        
        # Check if required folders exist
        for folder, description in required_folders.items():
            folder_path = os.path.join(directory, folder)
            if not os.path.exists(folder_path):
                violations.append({
                    'type': 'missing_required_folder',
                    'folder': folder,
                    'description': description,
                    'severity': 'info'
                })
        
        self.violations['structure'] = violations
        return violations
    
    def fix_unicode_violations(self, auto_fix: bool = False) -> int:
        """Fix unicode violations in files"""
        if not auto_fix and not self.unicode_config.get('auto_fix', False):
            print("[INFO] Auto-fix disabled. Set auto_fix=True to fix violations.")
            return 0
        
        fixed_count = 0
        
        # Group violations by file
        file_violations = defaultdict(list)
        for violation in self.violations['unicode']:
            file_violations[violation['file']].append(violation)
        
        for filepath, violations in file_violations.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace unicode characters
                for violation in violations:
                    char = violation['character']
                    replacement = violation['replacement']
                    content = content.replace(char, replacement)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    print(f"[FIXED] {filepath}: Replaced {len(violations)} unicode characters")
            
            except Exception as e:
                print(f"[ERROR] Could not fix {filepath}: {e}")
        
        self.stats['files_fixed'] = fixed_count
        return fixed_count
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("="*60)
        report.append("UNICODE AND FOLDER STRUCTURE VALIDATION REPORT")
        report.append("="*60)
        
        # Statistics
        report.append("\nSTATISTICS:")
        report.append(f"  Files scanned: {self.stats['files_scanned']}")
        report.append(f"  Unicode violations: {self.stats['unicode_violations']}")
        report.append(f"  Structure violations: {self.stats['structure_violations']}")
        report.append(f"  Files fixed: {self.stats['files_fixed']}")
        
        # Unicode violations
        if self.violations['unicode']:
            report.append("\nUNICODE VIOLATIONS:")
            report.append("-"*40)
            
            # Group by file
            by_file = defaultdict(list)
            for v in self.violations['unicode']:
                by_file[v['file']].append(v)
            
            for file, violations in list(by_file.items())[:10]:  # Show first 10 files
                report.append(f"\n{file}:")
                for v in violations[:5]:  # Show first 5 violations per file
                    # Sanitize unicode character for display
                    char_display = repr(v['character'])[1:-1]  # Use repr to escape unicode
                    report.append(f"  Line {v['line']}: {char_display} -> '{v['replacement']}'")
                    # Sanitize content as well
                    content_display = v['content'][:60].encode('ascii', 'replace').decode('ascii')
                    report.append(f"    Content: {content_display}...")
                if len(violations) > 5:
                    report.append(f"  ... and {len(violations)-5} more violations")
        
        # Structure violations
        if self.violations['structure']:
            report.append("\nFOLDER STRUCTURE VIOLATIONS:")
            report.append("-"*40)
            
            for violation in self.violations['structure']:
                if violation['type'] == 'too_many_files':
                    report.append(f"\n[{violation['severity'].upper()}] Too many files in {violation['folder']}")
                    report.append(f"  Found: {violation['file_count']} files (max: {violation['max_allowed']})")
                
                elif violation['type'] == 'misplaced_test_files':
                    report.append(f"\n[{violation['severity'].upper()}] Test files outside test folder:")
                    for file_info in violation['files'][:5]:
                        report.append(f"  - {file_info['file']}")
                        report.append(f"    Suggestion: {file_info['suggestion']}")
                
                elif violation['type'] == 'misplaced_config_files':
                    report.append(f"\n[{violation['severity'].upper()}] Config files outside config folder:")
                    for file_info in violation['files'][:5]:
                        report.append(f"  - {file_info['file']}")
                        report.append(f"    Suggestion: {file_info['suggestion']}")
                
                elif violation['type'] == 'missing_required_folder':
                    report.append(f"\n[{violation['severity'].upper()}] Missing folder: {violation['folder']}")
                    report.append(f"  Purpose: {violation['description']}")
        
        # Recommendations
        report.append("\nRECOMMENDATIONS:")
        report.append("-"*40)
        
        if self.stats['unicode_violations'] > 0:
            report.append("1. Fix unicode violations for Windows compatibility")
            report.append("   Run with --fix flag to auto-fix unicode issues")
        
        if self.stats['structure_violations'] > 0:
            report.append("2. Reorganize folder structure:")
            report.append("   - Move test files to tests/ folder")
            report.append("   - Move config files to config/ folder")
            report.append("   - Split large folders into submodules")
        
        if self.stats['unicode_violations'] == 0 and self.stats['structure_violations'] == 0:
            report.append("[SUCCESS] No violations found! Codebase is clean and well-organized.")
        
        report.append("\n" + "="*60)
        return "\n".join(report)
    
    def suggest_folder_reorganization(self) -> Dict[str, List[str]]:
        """Suggest folder reorganization plan"""
        suggestions = {
            'create_folders': [],
            'move_files': [],
            'rename_files': []
        }
        
        # Suggest folders to create
        required_folders = self.structure_config.get('required_folders', {})
        for folder in required_folders.keys():
            if not os.path.exists(folder):
                suggestions['create_folders'].append(folder)
        
        # Suggest file moves
        for violation in self.violations['structure']:
            if violation['type'] == 'misplaced_test_files':
                for file_info in violation['files']:
                    suggestions['move_files'].append({
                        'from': file_info['file'],
                        'to': f"tests/{os.path.basename(file_info['file'])}"
                    })
            
            elif violation['type'] == 'misplaced_config_files':
                for file_info in violation['files']:
                    suggestions['move_files'].append({
                        'from': file_info['file'],
                        'to': f"config/{os.path.basename(file_info['file'])}"
                    })
        
        return suggestions

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate unicode and folder structure')
    parser.add_argument('--fix', action='store_true', help='Auto-fix unicode violations')
    parser.add_argument('--dir', default='.', help='Directory to scan')
    parser.add_argument('--config', default='governance_config.json', help='Config file path')
    parser.add_argument('--suggest', action='store_true', help='Show reorganization suggestions')
    
    args = parser.parse_args()
    
    # Create validator
    validator = UnicodeAndStructureValidator(args.config)
    
    # Scan for violations
    print("[SCANNING] Checking for unicode violations...")
    unicode_violations = validator.scan_for_unicode(args.dir)
    
    print("[SCANNING] Checking folder structure...")
    structure_violations = validator.check_folder_structure(args.dir)
    
    # Fix if requested
    if args.fix and unicode_violations:
        print("\n[FIXING] Attempting to fix unicode violations...")
        fixed = validator.fix_unicode_violations(auto_fix=True)
        print(f"[COMPLETE] Fixed {fixed} files")
    
    # Generate report
    report = validator.generate_report()
    
    # Write report to file to avoid console encoding issues
    with open('validation_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Try to print to console with error handling
    try:
        print(report)
    except UnicodeEncodeError:
        # If console can't handle unicode, print safe version
        safe_report = report.encode('ascii', 'replace').decode('ascii')
        print(safe_report)
        print("\n[NOTE] Full report saved to validation_report.txt")
    
    # Show suggestions if requested
    if args.suggest:
        suggestions = validator.suggest_folder_reorganization()
        
        if suggestions['create_folders'] or suggestions['move_files']:
            print("\nFOLDER REORGANIZATION SUGGESTIONS:")
            print("="*40)
            
            if suggestions['create_folders']:
                print("\nCreate these folders:")
                for folder in suggestions['create_folders']:
                    print(f"  mkdir {folder}")
            
            if suggestions['move_files']:
                print("\nMove these files:")
                for move in suggestions['move_files'][:10]:
                    print(f"  mv {move['from']} {move['to']}")
                if len(suggestions['move_files']) > 10:
                    print(f"  ... and {len(suggestions['move_files'])-10} more files")
    
    # Return exit code based on violations
    if validator.stats['unicode_violations'] > 0:
        return 1  # Error for unicode violations
    elif validator.stats['structure_violations'] > 0:
        return 0  # Warning for structure violations (non-blocking)
    else:
        return 0  # Success

if __name__ == "__main__":
    exit(main())