# Documentation Metadata and Validation Configuration

## Purpose
Central repository for documentation templates, validation rules, and metadata configurations.

## Contents
- `code-formats.yaml` - Code documentation format standards for all languages
- `validation-rules.yaml` - Document validation rules and thresholds
- `format-templates/` - Template files for all documentation types
- `*.meta.yaml` - Metadata files defining validation rules for documents

## Dependencies
- PyYAML for parsing YAML configurations
- Markdown parser for document validation
- Governance validators that consume these configurations

## Maintenance
- Update templates when new document types are added
- Keep validation rules synchronized with templates
- Review and adjust thresholds based on team feedback
- Test changes with governance validators before committing