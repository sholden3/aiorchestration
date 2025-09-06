#!/usr/bin/env python3
"""
Fix Broken Documentation Links

Part of Emergency Documentation Remediation.
Fixes broken internal links in documentation files.

Created: 2025-01-06
Phase: Emergency Documentation Remediation - Day 2
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class LinkFixer:
    """Fix broken internal documentation links."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.fixes_applied = []
        
        # Map broken patterns to correct paths
        self.link_fixes = {
            # Fix double path in frontend.md
            "../../apps/web/apps/web/": "../../apps/web/",
            
            # Fix governance config path
            "../governance/config.yaml": "../../libs/governance/config.yaml",
            
            # Fix 'Internal' links (should be relative paths)
            r"\[([^\]]+)\]\(Internal\)": self.fix_internal_link,
            
            # Fix security path
            "../../../apps/api/mcp/security/": "../../../apps/api/mcp/",
            
            # Remove references to non-existent claude-sections
            r"\[([^\]]+)\]\(\.\./claude-sections/[^)]+\)": "[\\1](#)",
            
            # Fix MASTER_IMPLEMENTATION_PLAN references
            "../MASTER_IMPLEMENTATION_PLAN.md": "../CURRENT_PHASE_IMPLEMENTATION.md",
            
            # Fix test path
            "../../governance/validators/tests/": "../../tests/unit/governance/",
            
            # Fix processes links
            "./test-implementation-orchestration-plan.md": "./current-phase.md",
            "./three-persona-collaboration-example.md": "#persona-collaboration",
            "./bundle-bloat-crisis-scenario.md": "#crisis-scenarios",
            "./websocket-exhaustion-crisis.md": "#crisis-scenarios",
            "./database-race-condition-crisis.md": "#crisis-scenarios",
            "./ipc-security-boundary-crisis.md": "#crisis-scenarios",
            
            # Fix architecture README
            "../docs/architecture/README.md": "../architecture/",
            
            # Fix testing links
            "../docs/claude-sections/testing-strategy.md": "../testing/testing-strategy.md",
            "../processes/test-implementation-orchestration-plan.md": "#test-orchestration",
            "../processes/ci-cd-pipeline.md": "#ci-cd-pipeline",
            "../architecture/integration-testing.md": "./testing-strategy.md#integration-testing",
            "../../coverage/index.html": "#coverage-reports",
        }
    
    def fix_internal_link(self, match):
        """Convert 'Internal' links to proper relative paths."""
        link_text = match.group(1)
        # Default to section anchor
        return f"[{link_text}](#{link_text.lower().replace(' ', '-')})"
    
    def fix_links_in_file(self, file_path: Path) -> int:
        """Fix broken links in a single file."""
        fixes_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all fixes
            for broken_pattern, fix in self.link_fixes.items():
                if callable(fix):
                    # It's a function - use regex substitution
                    new_content, n = re.subn(broken_pattern, fix, content)
                    if n > 0:
                        content = new_content
                        fixes_count += n
                else:
                    # Simple string replacement
                    if broken_pattern in content:
                        content = content.replace(broken_pattern, fix)
                        fixes_count += content.count(fix) - original_content.count(fix)
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append((file_path, fixes_count))
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return fixes_count
    
    def fix_all_broken_links(self):
        """Fix all broken links in documentation."""
        print("=" * 60)
        print("FIXING BROKEN DOCUMENTATION LINKS")
        print("=" * 60)
        print()
        
        total_fixes = 0
        
        # Process all markdown files
        for md_file in self.docs_dir.rglob("*.md"):
            fixes = self.fix_links_in_file(md_file)
            if fixes > 0:
                total_fixes += fixes
                rel_path = md_file.relative_to(self.project_root)
                print(f"Fixed {fixes} links in {rel_path}")
        
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total fixes applied: {total_fixes}")
        print(f"Files modified: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            print("\nModified files:")
            for file_path, count in self.fixes_applied:
                rel_path = file_path.relative_to(self.project_root)
                print(f"  - {rel_path}: {count} fixes")
        
        return total_fixes

def main():
    """Main entry point."""
    fixer = LinkFixer()
    total_fixes = fixer.fix_all_broken_links()
    
    if total_fixes > 0:
        print(f"\n[SUCCESS] Fixed {total_fixes} broken links!")
        return 0
    else:
        print("\n[INFO] No broken links found to fix.")
        return 0

if __name__ == "__main__":
    exit(main())