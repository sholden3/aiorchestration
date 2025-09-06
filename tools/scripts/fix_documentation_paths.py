#!/usr/bin/env python3
"""
Emergency Documentation Path Fix Script
Part of EMERGENCY_DOCUMENTATION_REMEDIATION

This script fixes all outdated path references in documentation files.
Created: 2025-01-06
Author: Emergency Response Team
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Define path mappings
PATH_MAPPINGS = {
    # Main directory changes
    r'ai-assistant/backend': 'apps/api',
    r'ai-assistant/src': 'apps/web/src',
    r'ai-assistant/electron': 'apps/desktop',
    r'ai-assistant/': 'apps/',
    
    # Specific file mappings
    r'backend/main\.py': 'apps/api/main.py',
    r'backend/config\.py': 'apps/api/config.py',
    r'backend/models/': 'apps/api/models/',
    r'backend/services/': 'apps/api/services/',
    r'backend/endpoints/': 'apps/api/endpoints/',
    r'backend/tests/': 'apps/api/tests/',
    
    # Frontend mappings
    r'src/app/': 'apps/web/src/app/',
    r'src/assets/': 'apps/web/src/assets/',
    r'src/environments/': 'apps/web/src/environments/',
}

def fix_paths_in_file(file_path: Path) -> Tuple[int, List[str]]:
    """Fix all outdated paths in a single file."""
    changes_made = 0
    changes_log = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all path mappings
        for old_path, new_path in PATH_MAPPINGS.items():
            pattern = re.compile(old_path, re.IGNORECASE)
            matches = pattern.findall(content)
            if matches:
                content = pattern.sub(new_path, content)
                changes_made += len(matches)
                changes_log.append(f"  - Replaced '{old_path}' with '{new_path}' ({len(matches)} occurrences)")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {file_path.name}: {changes_made} changes")
            for change in changes_log:
                print(change)
        else:
            print(f"[SKIP] No changes needed in {file_path.name}")
            
    except Exception as e:
        print(f"[ERROR] Error processing {file_path}: {e}")
        
    return changes_made, changes_log

def validate_no_old_references(docs_dir: Path) -> bool:
    """Validate that no old references remain."""
    print("\n[VALIDATION] Checking for old references...")
    
    old_patterns = ['ai-assistant']
    found_issues = False
    
    for pattern in old_patterns:
        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern in content.lower():
                        print(f"[FOUND] '{pattern}' in {md_file}")
                        found_issues = True
            except Exception as e:
                print(f"[WARNING] Could not check {md_file}: {e}")
    
    if not found_issues:
        print("[SUCCESS] No old references found!")
        return True
    else:
        print("[FAILED] Old references still exist!")
        return False

def main():
    """Main execution function."""
    print("=" * 60)
    print("EMERGENCY DOCUMENTATION PATH FIX")
    print("=" * 60)
    print()
    
    # Get docs directory
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("[ERROR] docs/ directory not found!")
        return 1
    
    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    print(f"[INFO] Found {len(md_files)} markdown files to process")
    print()
    
    total_changes = 0
    files_changed = 0
    
    # Process each file
    for md_file in md_files:
        changes, log = fix_paths_in_file(md_file)
        if changes > 0:
            total_changes += changes
            files_changed += 1
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(md_files)}")
    print(f"Files changed: {files_changed}")
    print(f"Total changes made: {total_changes}")
    print()
    
    # Validate no old references remain
    if validate_no_old_references(docs_dir):
        print()
        print("[SUCCESS] All path references have been updated!")
        return 0
    else:
        print()
        print("[WARNING] Some old references may still exist!")
        print("Please review the files listed above.")
        return 1

if __name__ == "__main__":
    exit(main())