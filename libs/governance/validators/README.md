# Governance Validators

## Purpose
Python validators for enforcing documentation and code documentation standards.

## Contents
- `doc_validator.py` - Markdown documentation validator with 85%+ test coverage
- `code_doc_validator.py` - Code documentation validator for Python/TypeScript/JavaScript
- `doc_utils.py` - Shared utilities for document parsing and validation
- `metadata_parser.py` - Parser for YAML metadata configurations
- `document_validator.py` - Base validator with common functionality
- `domain_validators.py` - Domain-specific validation rules
- `basic_hallucination_detector.py` - AI hallucination detection for documentation
- `relaxed_document_validator.py` - Less strict validation for progressive enforcement
- `validation_rules.py` - Centralized validation rule definitions

## Dependencies
- PyYAML for configuration parsing
- markdown for document parsing
- Python 3.8+ with type hints

## Maintenance
- Add new validators as needed for new file types
- Keep test coverage above 85%
- Update validators when metadata formats change
- Review false positive rates monthly