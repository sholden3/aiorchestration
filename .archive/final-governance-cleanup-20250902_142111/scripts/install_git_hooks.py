#!/usr/bin/env python3
"""
Install Governance Git Hooks
Installs the governance pre-commit hook into the repository
"""

import os
import sys
import shutil
import stat
from pathlib import Path


def install_pre_commit_hook():
    """Install the pre-commit hook into .git/hooks/"""
    
    # Find the git directory
    current_dir = Path.cwd()
    git_dir = None
    
    # Search for .git directory
    for parent in [current_dir] + list(current_dir.parents):
        potential_git = parent / ".git"
        if potential_git.exists() and potential_git.is_dir():
            git_dir = potential_git
            break
    
    if not git_dir:
        print("[ERROR] Not in a git repository")
        return False
    
    # Source hook script
    script_dir = Path(__file__).parent
    source_hook = script_dir / "git_pre_commit_hook.py"
    
    if not source_hook.exists():
        print(f"[ERROR] Hook script not found: {source_hook}")
        return False
    
    # Target location
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    target_hook = hooks_dir / "pre-commit"
    
    # Backup existing hook if it exists
    if target_hook.exists():
        backup_path = target_hook.with_suffix(".backup")
        print(f"[INFO] Backing up existing hook to: {backup_path}")
        shutil.copy2(target_hook, backup_path)
    
    # Create wrapper script that calls our Python hook
    wrapper_content = f"""#!/bin/sh
# Governance Pre-Commit Hook Wrapper
# This script calls the Python governance hook

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Set PYTHONPATH to include the repo root
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

# Execute the Python hook
python3 "{source_hook.absolute()}" "$@"
exit_code=$?

# Pass through the exit code
exit $exit_code
"""
    
    # Write the wrapper script
    print(f"[INFO] Installing governance hook to: {target_hook}")
    with open(target_hook, 'w', newline='\n') as f:  # Force Unix line endings
        f.write(wrapper_content)
    
    # Make executable on Unix-like systems
    if os.name != 'nt':  # Not Windows
        st = os.stat(target_hook)
        os.chmod(target_hook, st.st_mode | stat.S_IEXEC)
        print("[INFO] Made hook executable")
    else:
        print("[INFO] On Windows - hook will run through git bash")
    
    print("[SUCCESS] Git pre-commit hook installed successfully!")
    print("\nThe hook will:")
    print("  - Analyze your staged changes")
    print("  - Check for risky patterns and times")
    print("  - Validate against governance rules")
    print("  - Log all decisions for audit")
    print("\nTo bypass in emergencies: GOVERNANCE_BYPASS=true git commit")
    
    return True


def verify_installation():
    """Verify the hook is properly installed"""
    
    # Find the git directory
    current_dir = Path.cwd()
    git_dir = None
    
    for parent in [current_dir] + list(current_dir.parents):
        potential_git = parent / ".git"
        if potential_git.exists() and potential_git.is_dir():
            git_dir = potential_git
            break
    
    if not git_dir:
        return False
    
    hook_path = git_dir / "hooks" / "pre-commit"
    
    if hook_path.exists():
        print(f"\n[VERIFIED] Hook installed at: {hook_path}")
        
        # Check if it references our Python script
        with open(hook_path, 'r') as f:
            content = f.read()
            if 'git_pre_commit_hook.py' in content:
                print("[VERIFIED] Hook properly configured")
                return True
            else:
                print("[WARNING] Hook exists but may not be our governance hook")
                return False
    else:
        print("[ERROR] Hook not found")
        return False


def test_hook():
    """Test the hook with a dry run"""
    print("\n" + "=" * 60)
    print("TESTING GOVERNANCE HOOK")
    print("=" * 60)
    
    # Import and run the hook directly
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir.parent.parent))
    
    try:
        from governance.scripts import git_pre_commit_hook
        
        print("\n[TEST] Running hook in test mode...")
        # The hook will analyze current git state
        git_pre_commit_hook.main()
        
    except SystemExit as e:
        if e.code == 0:
            print("\n[TEST PASSED] Hook would allow commit")
        else:
            print("\n[TEST INFO] Hook would block/review commit (this is expected for testing)")
        return True
    except Exception as e:
        print(f"\n[TEST FAILED] Error running hook: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main installation process"""
    print("=" * 60)
    print("GOVERNANCE GIT HOOK INSTALLER")
    print("=" * 60)
    
    # Install the hook
    if not install_pre_commit_hook():
        print("\n[FAILED] Could not install hook")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n[WARNING] Installation may have issues")
    
    # Test the hook
    print("\nWould you like to test the hook now? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        test_hook()
    
    print("\n" + "=" * 60)
    print("Installation complete!")
    print("The governance hook will run on your next commit.")
    print("=" * 60)


if __name__ == "__main__":
    main()