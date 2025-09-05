# Documentation Standards

**Location:** `libs/governance/docs-standards/`  
**Purpose:** Centralized documentation standards and validation rules  
**Last Updated:** September 4, 2025  

## Overview

This directory contains the consolidated documentation standards for the AI Orchestration Platform, migrated from `.docs-metadata/` as part of the enterprise monorepo restructuring.

## Files

### documentation_standards.yaml
The master configuration file containing:
- **Validation Rules:** Markdown and code documentation requirements
- **Code Formats:** Language-specific documentation templates (Python, TypeScript, JavaScript)
- **Templates:** All documentation templates for project files (CLAUDE.md, STATUS.md, etc.)
- **Metadata Configuration:** Required fields for documentation
- **Governance Integration:** Compliance settings and enforcement levels

## Migration History

**September 4, 2025:** Consolidated from `.docs-metadata/`:
- Merged `validation-rules.yaml`
- Merged `code-formats.yaml` 
- Converted all format-templates/*.md to YAML structure
- Created unified configuration in `documentation_standards.yaml`

## Usage

```python
# Load documentation standards
import yaml

with open('libs/governance/docs-standards/documentation_standards.yaml', 'r') as f:
    standards = yaml.safe_load(f)
    
# Access validation rules
markdown_rules = standards['validation_rules']['markdown']

# Access templates
claude_template = standards['templates']['claude_md']
```

## Integration Points

- **Pre-commit Hooks:** Used by governance system for validation
- **Document Validators:** Reference for scoring and compliance
- **Template Generator:** Source for creating new documentation
- **CI/CD Pipeline:** Validation rules for documentation checks

## Governance Compliance

This consolidation maintains 95%+ governance compliance by:
- Centralizing all documentation rules
- Providing single source of truth
- Enabling versioned configuration
- Supporting audit trails

---

*Part of the enterprise monorepo restructuring initiative*