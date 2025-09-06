#!/usr/bin/env python3
"""
Naming Convention Audit Script
Part of SDR-001: STRUCTURAL_DEBT_REMEDIATION
Analyzes codebase for naming convention violations
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class NamingAudit:
    """Comprehensive naming convention auditor."""
    
    def __init__(self, root_path: str = '.'):
        self.root = Path(root_path)
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def audit_all(self) -> Dict:
        """Run complete naming audit."""
        print("Starting comprehensive naming audit...")
        
        # Audit different aspects
        self.audit_directory_names()
        self.audit_file_names()
        self.audit_module_structure()
        self.audit_import_statements()
        self.analyze_duplicates()
        
        return {
            'issues': dict(self.issues),
            'statistics': dict(self.stats),
            'summary': self.generate_summary()
        }
    
    def audit_directory_names(self):
        """Check directory naming conventions."""
        print("\n[1/5] Auditing directory names...")
        
        for path in self.root.rglob('*'):
            if not path.is_dir():
                continue
                
            # Skip hidden and special directories
            if any(part.startswith('.') for part in path.parts):
                continue
            if 'node_modules' in path.parts or '__pycache__' in path.parts:
                continue
                
            dir_name = path.name
            
            # Check for hyphens in Python module directories
            if '-' in dir_name and path.suffix != '.md':
                self.issues['hyphenated_directories'].append({
                    'path': str(path),
                    'name': dir_name,
                    'suggested': dir_name.replace('-', '_'),
                    'severity': 'HIGH' if 'libs' in str(path) or 'apps' in str(path) else 'MEDIUM'
                })
                self.stats['hyphenated_dirs'] += 1
            
            # Check for CamelCase in directories
            if dir_name[0].isupper() and dir_name not in ['README', 'LICENSE']:
                self.issues['camelcase_directories'].append({
                    'path': str(path),
                    'name': dir_name,
                    'suggested': self.to_snake_case(dir_name),
                    'severity': 'MEDIUM'
                })
                self.stats['camelcase_dirs'] += 1
    
    def audit_file_names(self):
        """Check Python file naming conventions."""
        print("[2/5] Auditing Python file names...")
        
        for py_file in self.root.rglob('*.py'):
            # Skip test files and special files
            if '__pycache__' in str(py_file) or 'temp' in str(py_file):
                continue
                
            file_name = py_file.stem
            
            # Check for verbose names (>25 chars)
            if len(file_name) > 25:
                self.issues['verbose_file_names'].append({
                    'path': str(py_file),
                    'name': file_name,
                    'length': len(file_name),
                    'severity': 'LOW'
                })
                self.stats['verbose_files'] += 1
            
            # Check for version indicators in names
            version_patterns = ['updated_', 'enhanced_', 'new_', 'old_', '_v2', '_v3']
            for pattern in version_patterns:
                if pattern in file_name:
                    self.issues['versioned_file_names'].append({
                        'path': str(py_file),
                        'name': file_name,
                        'pattern': pattern,
                        'suggested': file_name.replace(pattern, ''),
                        'severity': 'MEDIUM'
                    })
                    self.stats['versioned_files'] += 1
                    break
            
            # Check for redundant prefixes
            if 'additional_' in file_name or 'extra_' in file_name:
                self.issues['redundant_prefixes'].append({
                    'path': str(py_file),
                    'name': file_name,
                    'severity': 'LOW'
                })
                self.stats['redundant_prefixes'] += 1
    
    def audit_module_structure(self):
        """Analyze module structure and nesting."""
        print("[3/5] Auditing module structure...")
        
        # Check for redundant nesting (e.g., apps/api/api/)
        for path in self.root.rglob('*'):
            if not path.is_dir():
                continue
                
            parts = path.parts
            for i in range(len(parts) - 1):
                if parts[i] == parts[i + 1]:
                    self.issues['redundant_nesting'].append({
                        'path': str(path),
                        'duplicate': parts[i],
                        'severity': 'HIGH'
                    })
                    self.stats['redundant_nesting'] += 1
        
        # Check for too many files at module root
        module_roots = [
            self.root / 'apps' / 'api',
            self.root / 'libs' / 'governance',
        ]
        
        for module_root in module_roots:
            if not module_root.exists():
                continue
                
            root_files = list(module_root.glob('*.py'))
            if len(root_files) > 10:
                self.issues['overcrowded_root'].append({
                    'path': str(module_root),
                    'file_count': len(root_files),
                    'files': [f.name for f in root_files[:10]] + ['...'],
                    'severity': 'MEDIUM'
                })
                self.stats['overcrowded_roots'] += 1
    
    def audit_import_statements(self):
        """Analyze import statements for issues."""
        print("[4/5] Auditing import statements...")
        
        import_pattern = re.compile(r'^(?:from\s+([\w\.-]+)|import\s+([\w\.-]+))', re.MULTILINE)
        
        all_imports = set()
        hyphenated_imports = []
        
        for py_file in self.root.rglob('*.py'):
            if '__pycache__' in str(py_file) or 'temp' in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                matches = import_pattern.findall(content)
                
                for match in matches:
                    import_name = match[0] or match[1]
                    if import_name:
                        all_imports.add(import_name)
                        
                        # Check for hyphenated imports
                        if '-' in import_name:
                            hyphenated_imports.append({
                                'file': str(py_file),
                                'import': import_name,
                                'suggested': import_name.replace('-', '_'),
                                'severity': 'HIGH'
                            })
                            self.stats['hyphenated_imports'] += 1
                            
            except Exception as e:
                self.issues['read_errors'].append({
                    'file': str(py_file),
                    'error': str(e)
                })
        
        if hyphenated_imports:
            self.issues['hyphenated_imports'] = hyphenated_imports
    
    def analyze_duplicates(self):
        """Find potential duplicate modules."""
        print("[5/5] Analyzing for duplicates...")
        
        # Look for similar named directories
        dirs_by_name = defaultdict(list)
        
        for path in self.root.rglob('*'):
            if not path.is_dir():
                continue
            if any(part.startswith('.') for part in path.parts):
                continue
                
            # Normalize name for comparison
            normalized = path.name.replace('-', '_').lower()
            dirs_by_name[normalized].append(str(path))
        
        # Find duplicates
        for name, paths in dirs_by_name.items():
            if len(paths) > 1:
                self.issues['potential_duplicates'].append({
                    'name': name,
                    'paths': paths,
                    'severity': 'HIGH' if 'shared' in name else 'MEDIUM'
                })
                self.stats['potential_duplicates'] += 1
    
    def to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def generate_summary(self) -> Dict:
        """Generate audit summary."""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for issue_list in self.issues.values():
            for issue in issue_list:
                if isinstance(issue, dict) and 'severity' in issue:
                    severity_counts[issue['severity']] += 1
        
        return {
            'total_issues': total_issues,
            'severity_breakdown': severity_counts,
            'categories': list(self.issues.keys()),
            'most_common': max(self.issues.keys(), key=lambda k: len(self.issues[k])) if self.issues else None
        }
    
    def generate_report(self) -> str:
        """Generate formatted report."""
        results = self.audit_all()
        
        report = []
        report.append("# Naming Convention Audit Report")
        report.append("\n## Summary")
        
        summary = results['summary']
        report.append(f"- **Total Issues Found:** {summary['total_issues']}")
        report.append(f"- **High Severity:** {summary['severity_breakdown']['HIGH']}")
        report.append(f"- **Medium Severity:** {summary['severity_breakdown']['MEDIUM']}")
        report.append(f"- **Low Severity:** {summary['severity_breakdown']['LOW']}")
        
        if summary['most_common']:
            report.append(f"- **Most Common Issue:** {summary['most_common']}")
        
        report.append("\n## Statistics")
        for key, value in results['statistics'].items():
            report.append(f"- {key}: {value}")
        
        report.append("\n## Detailed Issues")
        
        for category, issues in results['issues'].items():
            if not issues:
                continue
                
            report.append(f"\n### {category.replace('_', ' ').title()}")
            report.append(f"**Count:** {len(issues)}\n")
            
            # Show first 5 issues in each category
            for issue in issues[:5]:
                if isinstance(issue, dict):
                    report.append(f"- **Path:** `{issue.get('path', issue.get('file', 'N/A'))}`")
                    for key, value in issue.items():
                        if key not in ['path', 'file']:
                            report.append(f"  - {key}: {value}")
                else:
                    report.append(f"- {issue}")
            
            if len(issues) > 5:
                report.append(f"\n...and {len(issues) - 5} more")
        
        return '\n'.join(report)
    
    def save_json_report(self, filename: str = 'naming_audit.json'):
        """Save detailed JSON report."""
        results = self.audit_all()
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed JSON report saved to: {filename}")


def main():
    """Run naming audit."""
    auditor = NamingAudit()
    
    # Generate and print report
    report = auditor.generate_report()
    print(report)
    
    # Save reports
    with open('naming_audit_report.md', 'w') as f:
        f.write(report)
    print("\nMarkdown report saved to: naming_audit_report.md")
    
    auditor.save_json_report()
    
    # Print action items
    print("\n" + "="*50)
    print("ACTION ITEMS:")
    print("="*50)
    
    results = auditor.audit_all()
    if results['summary']['severity_breakdown']['HIGH'] > 0:
        print(f"⚠️  {results['summary']['severity_breakdown']['HIGH']} HIGH severity issues require immediate attention")
    
    if 'hyphenated_directories' in results['issues']:
        print(f"📁 Fix {len(results['issues']['hyphenated_directories'])} hyphenated directory names")
    
    if 'hyphenated_imports' in results['issues']:
        print(f"📦 Update {len(results['issues']['hyphenated_imports'])} import statements")
    
    if 'potential_duplicates' in results['issues']:
        print(f"🔍 Investigate {len(results['issues']['potential_duplicates'])} potential duplicate modules")


if __name__ == '__main__':
    main()