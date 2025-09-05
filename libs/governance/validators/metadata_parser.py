#!/usr/bin/env python
"""
Metadata Parser for Documentation Validation System
@description: Parse and validate document metadata files (.meta.yaml)
@author: Governance System v2.0
@version: 2.0.0
@dependencies: yaml, pathlib, typing
@exports: MetadataParser class
@testing: 0% (needs implementation)
@last_review: 2025-09-03
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class PlaceholderRule:
    """Definition of a placeholder validation rule"""
    name: str
    type: str
    required: bool = True
    format_pattern: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SectionRule:
    """Definition of a required section rule"""
    name: str
    level: int = 2
    required: bool = True
    description: Optional[str] = None


@dataclass
class DocumentTemplate:
    """Parsed document template metadata"""
    name: str
    version: str
    category: str
    description: str
    required_sections: List[SectionRule]
    required_placeholders: List[PlaceholderRule]
    validation_rules: Dict[str, Any]
    custom_validators: Dict[str, Any]


class MetadataParser:
    """
    Parses document metadata files and validation configurations
    """
    
    def __init__(self, metadata_dir: Path):
        self.metadata_dir = Path(metadata_dir)
        self._template_cache: Dict[str, DocumentTemplate] = {}
        self._validation_config: Optional[Dict[str, Any]] = None
    
    def parse_document_template(self, template_name: str) -> Optional[DocumentTemplate]:
        """
        Parse a document template metadata file
        
        Args:
            template_name: Name of the template (without .meta.yaml extension)
            
        Returns:
            DocumentTemplate if found and valid, None otherwise
        """
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        meta_file = self.metadata_dir / f"{template_name}.meta.yaml"
        
        if not meta_file.exists():
            return None
        
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
            
            template = self._parse_template_data(raw_data)
            self._template_cache[template_name] = template
            return template
            
        except Exception as e:
            print(f"[WARNING] Failed to parse template {template_name}: {e}")
            return None
    
    def _parse_template_data(self, data: Dict[str, Any]) -> DocumentTemplate:
        """Parse raw YAML data into DocumentTemplate"""
        
        # Parse template info
        template_info = data.get('template', {})
        name = template_info.get('name', 'Unknown')
        version = template_info.get('version', '1.0.0')
        category = template_info.get('category', 'general')
        description = template_info.get('description', '')
        
        # Parse validation rules
        validation = data.get('validation', {})
        
        # Parse required sections
        required_sections = []
        sections_data = validation.get('required_sections', [])
        for section_data in sections_data:
            if isinstance(section_data, str):
                required_sections.append(SectionRule(name=section_data))
            elif isinstance(section_data, dict):
                required_sections.append(SectionRule(
                    name=section_data.get('name', ''),
                    level=section_data.get('level', 2),
                    required=section_data.get('required', True),
                    description=section_data.get('description')
                ))
        
        # Parse required placeholders
        required_placeholders = []
        placeholders_data = validation.get('required_placeholders', [])
        for placeholder_data in placeholders_data:
            if isinstance(placeholder_data, str):
                required_placeholders.append(PlaceholderRule(
                    name=placeholder_data,
                    type='string'
                ))
            elif isinstance(placeholder_data, dict):
                required_placeholders.append(PlaceholderRule(
                    name=placeholder_data.get('name', ''),
                    type=placeholder_data.get('type', 'string'),
                    required=placeholder_data.get('required', True),
                    format_pattern=placeholder_data.get('format'),
                    description=placeholder_data.get('description')
                ))
        
        # Parse validation rules
        validation_rules = validation.get('validation_rules', {})
        
        # Parse custom validators
        custom_validators = data.get('custom_validators', {})
        
        return DocumentTemplate(
            name=name,
            version=version,
            category=category,
            description=description,
            required_sections=required_sections,
            required_placeholders=required_placeholders,
            validation_rules=validation_rules,
            custom_validators=custom_validators
        )
    
    def load_validation_config(self) -> Dict[str, Any]:
        """Load the main validation configuration"""
        if self._validation_config is not None:
            return self._validation_config
        
        config_file = self.metadata_dir / "validation-rules.yaml"
        
        if not config_file.exists():
            self._validation_config = self._get_default_config()
            return self._validation_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self._validation_config = yaml.safe_load(f)
            return self._validation_config
        except Exception as e:
            print(f"[WARNING] Failed to load validation config: {e}")
            self._validation_config = self._get_default_config()
            return self._validation_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default validation configuration"""
        return {
            "schema_version": "1.0.0",
            "global_settings": {
                "progressive_enforcement": True,
                "auto_fix_enabled": False,
                "report_generation": True
            },
            "document_types": {
                "general_docs": {
                    "patterns": ["*.md"],
                    "validation_rules": ["check_basic_structure"],
                    "severity": "low"
                }
            },
            "severity_levels": {
                "critical": {"block_commit": False, "penalty_points": 20},
                "high": {"block_commit": False, "penalty_points": 10},
                "medium": {"block_commit": False, "penalty_points": 5},
                "low": {"block_commit": False, "penalty_points": 2}
            }
        }
    
    def get_document_type_config(self, doc_type: str) -> Dict[str, Any]:
        """Get configuration for a specific document type"""
        config = self.load_validation_config()
        doc_types = config.get('document_types', {})
        return doc_types.get(doc_type, doc_types.get('general_docs', {}))
    
    def get_severity_config(self, severity: str) -> Dict[str, Any]:
        """Get configuration for a severity level"""
        config = self.load_validation_config()
        severity_levels = config.get('severity_levels', {})
        return severity_levels.get(severity, {'block_commit': False, 'penalty_points': 5})
    
    def list_available_templates(self) -> List[str]:
        """List all available document templates"""
        if not self.metadata_dir.exists():
            return []
        
        templates = []
        for meta_file in self.metadata_dir.glob("*.meta.yaml"):
            template_name = meta_file.stem.replace('.meta', '')
            templates.append(template_name)
        
        return sorted(templates)
    
    def validate_metadata_file(self, template_name: str) -> List[str]:
        """
        Validate a metadata file for correctness
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        meta_file = self.metadata_dir / f"{template_name}.meta.yaml"
        
        if not meta_file.exists():
            errors.append(f"Metadata file not found: {meta_file}")
            return errors
        
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate structure
            if 'template' not in data:
                errors.append("Missing 'template' section")
            else:
                template_section = data['template']
                required_fields = ['name', 'version', 'category']
                for field in required_fields:
                    if field not in template_section:
                        errors.append(f"Missing required field in template: {field}")
            
            if 'validation' in data:
                validation_section = data['validation']
                
                # Validate required_sections structure
                if 'required_sections' in validation_section:
                    sections = validation_section['required_sections']
                    if not isinstance(sections, list):
                        errors.append("required_sections must be a list")
                    else:
                        for i, section in enumerate(sections):
                            if isinstance(section, dict):
                                if 'name' not in section:
                                    errors.append(f"Section {i} missing 'name' field")
                            elif not isinstance(section, str):
                                errors.append(f"Section {i} must be string or object")
                
                # Validate required_placeholders structure
                if 'required_placeholders' in validation_section:
                    placeholders = validation_section['required_placeholders']
                    if not isinstance(placeholders, list):
                        errors.append("required_placeholders must be a list")
                    else:
                        for i, placeholder in enumerate(placeholders):
                            if isinstance(placeholder, dict):
                                if 'name' not in placeholder:
                                    errors.append(f"Placeholder {i} missing 'name' field")
                            elif not isinstance(placeholder, str):
                                errors.append(f"Placeholder {i} must be string or object")
            
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"Failed to validate metadata: {e}")
        
        return errors
    
    def create_sample_template(self, template_name: str, doc_type: str = "general") -> bool:
        """
        Create a sample template metadata file
        
        Args:
            template_name: Name for the new template
            doc_type: Type of document (affects default rules)
            
        Returns:
            True if created successfully, False otherwise
        """
        meta_file = self.metadata_dir / f"{template_name}.meta.yaml"
        
        if meta_file.exists():
            return False  # Don't overwrite existing files
        
        sample_data = {
            "template": {
                "name": template_name.replace('_', ' ').title(),
                "version": "1.0.0",
                "category": doc_type,
                "description": f"Template for {template_name} documents"
            },
            "validation": {
                "required_sections": [
                    {
                        "name": "Overview",
                        "level": 2,
                        "required": True
                    },
                    {
                        "name": "Details",
                        "level": 2,
                        "required": True
                    }
                ],
                "required_placeholders": [
                    {
                        "name": "DATE",
                        "type": "date",
                        "required": True,
                        "format": r"^\d{4}-\d{2}-\d{2}$"
                    },
                    {
                        "name": "STATUS",
                        "type": "status",
                        "required": True,
                        "format": r"^(Draft|Review|Final)$"
                    }
                ],
                "validation_rules": {
                    "check_sections": True,
                    "check_placeholders": True,
                    "check_formatting": True
                }
            }
        }
        
        try:
            with open(meta_file, 'w', encoding='utf-8') as f:
                yaml.dump(sample_data, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create sample template: {e}")
            return False