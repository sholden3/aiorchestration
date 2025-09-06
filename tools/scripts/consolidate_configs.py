#!/usr/bin/env python3
"""
Configuration Consolidation Script
Part of SDR-001 H3: Configuration Management
Consolidates scattered configs into centralized hierarchy
"""

import os
import shutil
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ConfigurationConsolidator:
    """Consolidate scattered configurations into centralized structure."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.root = Path('.')
        self.config_dir = self.root / 'config'
        self.backup_dir = None
        self.migrations = []
        
    def create_backup(self) -> Path:
        """Create backup of all configuration files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path(f'backup_configs_{timestamp}')
        
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            
        print(f"{'[DRY RUN] Would create' if self.dry_run else 'Creating'} backup: {self.backup_dir}")
        
        # Backup configuration files
        config_patterns = ['*.yaml', '*.yml', '*.json', '*.ini', '.env*']
        configs_to_backup = []
        
        for pattern in config_patterns:
            for config_file in self.root.rglob(pattern):
                # Skip node_modules, .git, temp, etc.
                if any(skip in str(config_file) for skip in ['node_modules', '.git', 'temp', '__pycache__']):
                    continue
                    
                if 'config' in config_file.name.lower() or 'env' in config_file.name.lower():
                    configs_to_backup.append(config_file)
        
        for config_file in configs_to_backup:
            relative_path = config_file.relative_to(self.root)
            backup_path = self.backup_dir / relative_path
            
            if not self.dry_run:
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_file, backup_path)
                
            print(f"  {'Would backup' if self.dry_run else 'Backed up'}: {relative_path}")
        
        return self.backup_dir
    
    def create_config_structure(self):
        """Create the new centralized config directory structure."""
        print(f"\n{'[DRY RUN] Would create' if self.dry_run else 'Creating'} config directory structure...")
        
        directories = [
            'config',
            'config/base',
            'config/governance',
            'config/backend',
            'config/frontend',
            'config/deployment',
            'config/schemas',
            'config/schemas/examples',
        ]
        
        for dir_path in directories:
            path = self.root / dir_path
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
            print(f"  {'Would create' if self.dry_run else 'Created'}: {dir_path}/")
    
    def consolidate_governance_configs(self):
        """Consolidate governance configurations."""
        print("\nConsolidating governance configs...")
        
        governance_configs = {
            'libs/governance/config.yaml': 'config/governance/rules.yaml',
            'libs/governance/personas.yaml': 'config/governance/personas.yaml',
            'libs/governance/documentation_standards.yaml': 'config/governance/standards.yaml',
        }
        
        for source, target in governance_configs.items():
            source_path = self.root / source
            target_path = self.root / target
            
            if source_path.exists():
                if not self.dry_run:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    
                self.migrations.append({
                    'source': str(source),
                    'target': str(target),
                    'type': 'governance'
                })
                
                print(f"  {'Would move' if self.dry_run else 'Moved'}: {source} -> {target}")
    
    def consolidate_backend_configs(self):
        """Consolidate backend configurations."""
        print("\nConsolidating backend configs...")
        
        # Read and merge backend configs
        backend_config = {
            'api': {},
            'database': {},
            'cache': {},
            'mcp': {}
        }
        
        # Load MCP config
        mcp_config_path = self.root / 'apps/api/mcp/mcp_config.yaml'
        if mcp_config_path.exists():
            with open(mcp_config_path, 'r') as f:
                mcp_data = yaml.safe_load(f)
                backend_config['mcp'] = mcp_data
        
        # Save consolidated backend config
        target_path = self.root / 'config/backend/backend.yaml'
        
        if not self.dry_run:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'w') as f:
                yaml.dump(backend_config, f, default_flow_style=False, sort_keys=False)
        
        self.migrations.append({
            'source': 'apps/api/mcp/mcp_config.yaml',
            'target': 'config/backend/backend.yaml',
            'type': 'backend'
        })
        
        print(f"  {'Would create' if self.dry_run else 'Created'}: config/backend/backend.yaml")
    
    def create_config_readme(self):
        """Create comprehensive configuration documentation."""
        readme_content = """# Configuration Management

## Overview

Centralized configuration management for the AI Orchestration Platform.

## Structure

```
config/
├── base/           # Base project configurations
├── governance/     # Governance rules and standards
├── backend/        # Backend service configurations
├── frontend/       # Frontend application settings
├── deployment/     # Deployment and infrastructure
└── schemas/        # Validation schemas
```

## Configuration Loading Order

1. Base defaults (config/base/defaults.yaml)
2. Environment-specific overrides
3. Environment variables
4. Runtime parameters

## Environment Variables

See `.env.example` for all available environment variables.

## Validation

All configurations are validated against JSON schemas in `config/schemas/`.

## Best Practices

1. Keep secrets in environment variables only
2. Use YAML for human-readable configs
3. Validate all configs before deployment
4. Document every configuration option
5. Version control non-sensitive configs

## Migration Notes

Configuration consolidated from:
- libs/governance/config.yaml -> config/governance/rules.yaml
- apps/api/mcp/mcp_config.yaml -> config/backend/backend.yaml
- Various scattered configs -> centralized structure

---

Generated: {datetime.now().isoformat()}
"""
        
        target_path = self.root / 'config/README.md'
        
        if not self.dry_run:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
        
        print(f"\n{'Would create' if self.dry_run else 'Created'}: config/README.md")
    
    def update_imports(self):
        """Update all references to old configuration paths."""
        print("\nUpdating configuration imports...")
        
        replacements = [
            ('libs/governance/config.yaml', 'config/governance/rules.yaml'),
            ('libs/governance/personas.yaml', 'config/governance/personas.yaml'),
            ('apps/api/mcp/mcp_config.yaml', 'config/backend/backend.yaml'),
        ]
        
        updated_files = []
        
        for py_file in self.root.rglob('*.py'):
            if any(skip in str(py_file) for skip in ['node_modules', '.git', 'temp', '__pycache__']):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                original = content
                
                for old_path, new_path in replacements:
                    content = content.replace(old_path, new_path)
                
                if content != original and not self.dry_run:
                    py_file.write_text(content, encoding='utf-8')
                    updated_files.append(py_file)
                    
            except Exception as e:
                print(f"  Error updating {py_file}: {e}")
        
        if updated_files:
            print(f"  {'Would update' if self.dry_run else 'Updated'} {len(updated_files)} files")
    
    def generate_migration_report(self) -> str:
        """Generate a report of all migrations performed."""
        report = []
        report.append("# Configuration Consolidation Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTED'}")
        
        if self.backup_dir:
            report.append(f"\n## Backup")
            report.append(f"Location: {self.backup_dir}")
        
        if self.migrations:
            report.append(f"\n## Migrations ({len(self.migrations)})")
            for migration in self.migrations:
                report.append(f"- {migration['type']}: `{migration['source']}` -> `{migration['target']}`")
        
        report.append("\n## New Structure")
        report.append("```")
        report.append("config/")
        report.append("|-- README.md")
        report.append("|-- base/")
        report.append("|-- governance/")
        report.append("|   |-- rules.yaml")
        report.append("|   |-- personas.yaml")
        report.append("|   +-- standards.yaml")
        report.append("|-- backend/")
        report.append("|   +-- backend.yaml")
        report.append("|-- frontend/")
        report.append("|-- deployment/")
        report.append("+-- schemas/")
        report.append("```")
        
        return '\n'.join(report)
    
    def run(self):
        """Execute the configuration consolidation."""
        print("="*50)
        print("CONFIGURATION CONSOLIDATION")
        print("="*50)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTION'}")
        print("="*50)
        
        # Create backup
        self.create_backup()
        
        # Create new structure
        self.create_config_structure()
        
        # Consolidate configs
        self.consolidate_governance_configs()
        self.consolidate_backend_configs()
        
        # Create documentation
        self.create_config_readme()
        
        # Update imports
        self.update_imports()
        
        # Generate report
        report = self.generate_migration_report()
        
        report_file = 'config_consolidation_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n" + "="*50)
        print(f"Report saved to: {report_file}")
        print("="*50)
        
        if self.dry_run:
            print("\n[OK] Dry run complete. Run with --execute to apply changes.")
        else:
            print("\n[OK] Configuration consolidation complete!")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Consolidate configuration files')
    parser.add_argument('--execute', action='store_true',
                        help='Actually execute the consolidation (default is dry-run)')
    
    args = parser.parse_args()
    
    consolidator = ConfigurationConsolidator(dry_run=not args.execute)
    consolidator.run()


if __name__ == '__main__':
    main()