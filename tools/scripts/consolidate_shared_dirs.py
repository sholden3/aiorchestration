#!/usr/bin/env python3
"""
Consolidate duplicate shared directories
Part of SDR-001: STRUCTURAL_DEBT_REMEDIATION
Safely merges hyphenated and underscore versions
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def consolidate_shared_directories():
    """Consolidate shared-types/shared-utils into shared_types/shared_utils."""
    
    print("="*50)
    print("SHARED DIRECTORY CONSOLIDATION")
    print("="*50)
    
    libs_path = Path('libs')
    
    consolidations = [
        ('shared-types', 'shared_types'),
        ('shared-utils', 'shared_utils')
    ]
    
    for hyphenated, underscored in consolidations:
        hyphen_path = libs_path / hyphenated
        under_path = libs_path / underscored
        
        print(f"\nProcessing: {hyphenated} -> {underscored}")
        
        if not hyphen_path.exists():
            print(f"  Source {hyphen_path} does not exist, skipping")
            continue
            
        if not under_path.exists():
            print(f"  Target {under_path} does not exist, simple rename")
            shutil.move(str(hyphen_path), str(under_path))
            print(f"  Renamed {hyphenated} to {underscored}")
            continue
        
        # Both exist - need to merge
        print(f"  Both directories exist, merging...")
        
        # Check contents of underscore version
        under_contents = list(under_path.glob('*'))
        under_has_content = any(
            f.name != '__init__.py' and f.name != '__pycache__' 
            for f in under_contents
        )
        
        if not under_has_content:
            # Underscore version only has __init__.py, safe to replace
            print(f"  {underscored} only has __init__.py, replacing with {hyphenated}")
            
            # Save __init__.py if it exists
            init_file = under_path / '__init__.py'
            init_content = None
            if init_file.exists():
                init_content = init_file.read_text()
            
            # Remove underscore version
            shutil.rmtree(under_path)
            
            # Move hyphenated to underscore
            shutil.move(str(hyphen_path), str(under_path))
            
            # Restore __init__.py if needed
            if init_content and not (under_path / '__init__.py').exists():
                (under_path / '__init__.py').write_text(init_content)
            
            print(f"  Successfully consolidated {hyphenated} -> {underscored}")
        else:
            # Both have content - need manual review
            print(f"  WARNING: Both directories have content, manual merge required")
            print(f"    {hyphenated}: {list(hyphen_path.glob('*'))[:3]}")
            print(f"    {underscored}: {list(under_path.glob('*'))[:3]}")
    
    print("\n" + "="*50)
    print("CONSOLIDATION COMPLETE")
    print("="*50)


def update_imports():
    """Update all imports from shared-types/shared-utils to shared_types/shared_utils."""
    
    print("\nUpdating imports...")
    
    replacements = [
        ('from libs.shared_types', 'from libs.shared_types'),
        ('import libs.shared_types', 'import libs.shared_types'),
        ('from libs.shared_utils', 'from libs.shared_utils'),
        ('import libs.shared_utils', 'import libs.shared_utils'),
        ('"libs/shared_types"', '"libs/shared_types"'),
        ("'libs/shared_types'", "'libs/shared_types'"),
        ('"libs/shared_utils"', '"libs/shared_utils"'),
        ("'libs/shared_utils'", "'libs/shared_utils'"),
    ]
    
    updated_files = []
    
    for py_file in Path('.').rglob('*.py'):
        if '__pycache__' in str(py_file) or 'temp' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            original = content
            
            for old, new in replacements:
                content = content.replace(old, new)
            
            if content != original:
                py_file.write_text(content, encoding='utf-8')
                updated_files.append(py_file)
                
        except Exception as e:
            print(f"  Error updating {py_file}: {e}")
    
    if updated_files:
        print(f"  Updated {len(updated_files)} files:")
        for f in updated_files[:5]:
            print(f"    - {f}")
        if len(updated_files) > 5:
            print(f"    ... and {len(updated_files) - 5} more")
    else:
        print("  No files needed import updates")


def verify_consolidation():
    """Verify the consolidation was successful."""
    
    print("\nVerifying consolidation...")
    
    libs_path = Path('libs')
    
    # Check hyphenated versions don't exist
    if (libs_path / 'shared-types').exists():
        print("  ERROR: shared-types still exists!")
        return False
    
    if (libs_path / 'shared-utils').exists():
        print("  ERROR: shared-utils still exists!")
        return False
    
    # Check underscore versions exist
    if not (libs_path / 'shared_types').exists():
        print("  ERROR: shared_types does not exist!")
        return False
        
    if not (libs_path / 'shared_utils').exists():
        print("  ERROR: shared_utils does not exist!")
        return False
    
    # Check content exists
    if not list((libs_path / 'shared_types' / 'python').glob('*.py')):
        print("  WARNING: shared_types/python has no Python files")
    
    if not list((libs_path / 'shared_utils' / 'python').glob('*.py')):
        print("  WARNING: shared_utils/python has no Python files")
    
    print("  ✓ Consolidation verified successfully")
    return True


def main():
    """Main execution."""
    
    # Create backup first
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_shared_dirs_{timestamp}'
    
    print(f"Creating backup: {backup_name}")
    libs_path = Path('libs')
    
    for dirname in ['shared-types', 'shared-utils', 'shared_types', 'shared_utils']:
        source = libs_path / dirname
        if source.exists():
            target = Path(backup_name) / dirname
            target.parent.mkdir(exist_ok=True)
            shutil.copytree(source, target)
            print(f"  Backed up {dirname}")
    
    # Perform consolidation
    consolidate_shared_directories()
    
    # Update imports
    update_imports()
    
    # Verify
    if verify_consolidation():
        print("\n✓ Shared directory consolidation successful!")
        print(f"  Backup saved in: {backup_name}")
    else:
        print("\n✗ Consolidation had issues, please review")
        print(f"  Backup available in: {backup_name}")


if __name__ == '__main__':
    main()