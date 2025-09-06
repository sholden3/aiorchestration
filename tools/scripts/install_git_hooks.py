#!/usr/bin/env python3
"""
Git Hooks Installation Script
Installs the pre-commit hook for extreme governance validation.

@fileoverview Git hooks installer for governance system
@author DevOps Team
@version 1.0.0
@description Automated installation of pre-commit hooks with backup support
@dependencies Python 3.10+, Git 2.0+
@exports install_pre_commit_hook, verify_installation, test_hook
@testing Run with --force flag for automated testing
@last_review 2025-01-10

Usage:
    python tools/scripts/install_git_hooks.py [--force]
    
Options:
    --force: Overwrite existing hooks without confirmation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def get_repo_root():
    """Get the repository root directory."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository")
        sys.exit(1)

def check_git_hooks_dir(repo_root):
    """Ensure .git/hooks directory exists."""
    hooks_dir = repo_root / '.git' / 'hooks'
    if not hooks_dir.exists():
        print(f"Creating hooks directory: {hooks_dir}")
        hooks_dir.mkdir(parents=True, exist_ok=True)
    return hooks_dir

def backup_existing_hook(hook_path):
    """Backup existing hook if it exists."""
    if hook_path.exists():
        backup_path = hook_path.with_suffix('.backup')
        counter = 1
        while backup_path.exists():
            backup_path = hook_path.with_suffix(f'.backup.{counter}')
            counter += 1
        
        print(f"Backing up existing hook to: {backup_path}")
        shutil.copy2(hook_path, backup_path)
        return backup_path
    return None

def install_pre_commit_hook(repo_root, hooks_dir, force=False):
    """Install the pre-commit hook."""
    # Source and destination paths
    source_hook = repo_root / 'tools' / 'hooks' / 'pre-commit'
    dest_hook = hooks_dir / 'pre-commit'
    
    # Check if source exists
    if not source_hook.exists():
        print(f"Error: Pre-commit hook source not found at {source_hook}")
        print("Please ensure the governance system is properly installed.")
        return False
    
    # Handle existing hook
    if dest_hook.exists() and not force:
        print(f"\nExisting pre-commit hook found at {dest_hook}")
        response = input("Do you want to replace it? (y/n): ").lower()
        if response != 'y':
            print("Installation cancelled.")
            return False
        backup_existing_hook(dest_hook)
    
    # Install the hook
    try:
        if platform.system() == 'Windows':
            # On Windows, copy the file
            shutil.copy2(source_hook, dest_hook)
            print(f"Copied pre-commit hook to {dest_hook}")
        else:
            # On Unix-like systems, create a symlink
            if dest_hook.exists() or dest_hook.is_symlink():
                dest_hook.unlink()
            
            # Create relative symlink
            relative_source = os.path.relpath(source_hook, hooks_dir)
            dest_hook.symlink_to(relative_source)
            print(f"Created symlink from {dest_hook} to {relative_source}")
        
        # Make executable (Unix-like systems)
        if platform.system() != 'Windows':
            dest_hook.chmod(0o755)
            print("Made pre-commit hook executable")
        
        return True
        
    except Exception as e:
        print(f"Error installing pre-commit hook: {e}")
        return False

def verify_installation(hooks_dir):
    """Verify the hook is properly installed."""
    hook_path = hooks_dir / 'pre-commit'
    
    if not hook_path.exists():
        print("[ERROR] Pre-commit hook not found")
        return False
    
    # Check if it's executable (Unix-like systems)
    if platform.system() != 'Windows':
        if not os.access(hook_path, os.X_OK):
            print("[WARNING] Pre-commit hook is not executable")
            hook_path.chmod(0o755)
            print("[FIXED] Made pre-commit hook executable")
    
    # Try to read the hook to verify it's valid
    try:
        with open(hook_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'EXTREME GOVERNANCE' in content:
                print("[OK] Pre-commit hook verified successfully")
                return True
            else:
                print("[WARNING] Pre-commit hook content looks incorrect")
                return False
    except Exception as e:
        print(f"[ERROR] Error verifying pre-commit hook: {e}")
        return False

def test_hook():
    """Run a basic test of the hook."""
    print("\n" + "="*50)
    print("Testing pre-commit hook...")
    print("="*50)
    
    try:
        # Try to import the governance system
        repo_root = get_repo_root()
        sys.path.insert(0, str(repo_root))
        
        governance_hook = repo_root / 'libs' / 'governance' / 'hooks' / 'pre-commit.py'
        if governance_hook.exists():
            print("[OK] Governance system found")
        else:
            print("[ERROR] Governance system not found")
            return False
        
        # Check for validators
        validators_dir = repo_root / 'libs' / 'governance' / 'hooks' / 'validators'
        if validators_dir.exists() and validators_dir.is_dir():
            validator_count = len(list(validators_dir.glob('*_validator.py')))
            print(f"[OK] Found {validator_count} validator modules")
        else:
            print("[WARNING] Modular validators not found (will use fallback)")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing hook: {e}")
        return False

def main():
    """Main installation process."""
    print("\n" + "="*70)
    print("EXTREME GOVERNANCE - Git Hook Installation")
    print("="*70)
    
    # Parse arguments
    force = '--force' in sys.argv
    
    # Get repository root
    repo_root = get_repo_root()
    print(f"Repository root: {repo_root}")
    
    # Check hooks directory
    hooks_dir = check_git_hooks_dir(repo_root)
    print(f"Hooks directory: {hooks_dir}")
    
    # Install pre-commit hook
    print("\nInstalling pre-commit hook...")
    if install_pre_commit_hook(repo_root, hooks_dir, force):
        print("[OK] Pre-commit hook installed successfully")
    else:
        print("[ERROR] Failed to install pre-commit hook")
        sys.exit(1)
    
    # Verify installation
    print("\nVerifying installation...")
    if not verify_installation(hooks_dir):
        print("[ERROR] Installation verification failed")
        sys.exit(1)
    
    # Test the hook
    if test_hook():
        print("\n" + "="*70)
        print("[OK] Git hooks installation complete!")
        print("="*70)
        print("\nThe extreme governance system is now active.")
        print("All commits will be validated against governance rules.")
        print("\nTo test, try making a commit:")
        print("  git add .")
        print("  git commit -m 'Test commit'")
    else:
        print("\n[WARNING] Installation complete but testing failed")
        print("The hook is installed but may need configuration.")
    
    print("\nFor more information, see:")
    print("  docs/architecture/governance/pre-commit-hook.md")

if __name__ == "__main__":
    main()