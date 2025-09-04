#!/usr/bin/env python3
"""
Template Renderer for Documentation Standards

Renders documentation from YAML configuration templates.
Designed for UI-driven template management.

Author: Alex Novak & Dr. Sarah Chen
Created: 2025-09-03
Version: 1.0.0
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from functools import lru_cache


class DocumentTemplateRenderer:
    """
    Renders documentation templates from configuration.
    
    This class:
    - Loads templates from YAML configuration
    - Renders templates with variable substitution
    - Validates rendered content
    - Provides API-ready template data
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the template renderer.
        
        Args:
            config_path: Path to documentation standards YAML
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "documentation_standards.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        self._compile_templates()
    
    @lru_cache(maxsize=1)
    def _load_config(self) -> Dict[str, Any]:
        """Load and cache the documentation standards configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading documentation standards: {e}")
            return {}
    
    def _compile_templates(self):
        """Pre-compile templates for performance."""
        self.compiled_templates = {}
        
        for doc_type, config in self.config.get('document_types', {}).items():
            self.compiled_templates[doc_type] = {
                'sections': [],
                'metadata': {
                    'description': config.get('description', ''),
                    'file_pattern': config.get('file_pattern', ''),
                    'priority': config.get('priority', 1)
                }
            }
            
            for section in config.get('required_sections', []):
                compiled_section = {
                    'name': section.get('section', ''),
                    'level': section.get('level', 2),
                    'required': section.get('required', True),
                    'weight': section.get('weight', 10),
                    'template': section.get('template', ''),
                    'validation': section.get('validation', {}),
                    'description': section.get('description', '')
                }
                self.compiled_templates[doc_type]['sections'].append(compiled_section)
    
    def render_document(self, 
                       document_type: str, 
                       variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a complete document from template.
        
        Args:
            document_type: Type of document (README, CLAUDE, STATUS, etc.)
            variables: Variables to substitute in template
            
        Returns:
            Rendered document content
        """
        if document_type not in self.compiled_templates:
            raise ValueError(f"Unknown document type: {document_type}")
        
        # Merge with default variables
        render_vars = self._get_render_variables(variables)
        
        # Build document
        sections = []
        for section in self.compiled_templates[document_type]['sections']:
            rendered_section = self._render_section(section, render_vars)
            if rendered_section:
                sections.append(rendered_section)
        
        # Add metadata header
        header = self._render_header(document_type, render_vars)
        
        return f"{header}\n\n" + "\n\n".join(sections)
    
    def _render_section(self, 
                        section: Dict[str, Any], 
                        variables: Dict[str, Any]) -> str:
        """
        Render a single section with variable substitution.
        
        Args:
            section: Section configuration
            variables: Variables to substitute
            
        Returns:
            Rendered section content
        """
        template = section.get('template', '')
        
        if not template:
            # Generate default template
            level_marker = '#' * section.get('level', 2)
            template = f"{level_marker} {section.get('name', 'Section')}\n\n[Content]"
        
        # Substitute variables
        return self._substitute_variables(template, variables)
    
    def _substitute_variables(self, 
                              template: str, 
                              variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template string.
        
        Args:
            template: Template string with {{variable}} markers
            variables: Variables to substitute
            
        Returns:
            String with variables substituted
        """
        rendering_config = self.config.get('rendering', {})
        start_marker = rendering_config.get('variable_markers', {}).get('start', '{{')
        end_marker = rendering_config.get('variable_markers', {}).get('end', '}}')
        
        # Escape regex special characters
        start_escaped = re.escape(start_marker)
        end_escaped = re.escape(end_marker)
        
        # Pattern to match variables
        pattern = f"{start_escaped}\\s*([^}}]+?)\\s*{end_escaped}"
        
        def replacer(match):
            var_name = match.group(1).strip()
            return str(variables.get(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, template)
    
    def _get_render_variables(self, 
                              custom_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get complete set of render variables.
        
        Args:
            custom_vars: Custom variables to merge
            
        Returns:
            Complete variable dictionary
        """
        # Start with defaults
        variables = self.config.get('rendering', {}).get('default_variables', {}).copy()
        
        # Add system variables
        variables.update({
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M UTC'),
            'year': datetime.now().year
        })
        
        # Merge custom variables
        if custom_vars:
            variables.update(custom_vars)
        
        return variables
    
    def _render_header(self, 
                       document_type: str, 
                       variables: Dict[str, Any]) -> str:
        """
        Render document header with metadata.
        
        Args:
            document_type: Type of document
            variables: Variables for substitution
            
        Returns:
            Rendered header
        """
        metadata = self.compiled_templates[document_type]['metadata']
        
        header_lines = []
        
        # Add description as comment
        if metadata['description']:
            header_lines.append(f"<!-- {metadata['description']} -->")
        
        # Add generation timestamp
        header_lines.append(f"<!-- Generated: {variables['current_time']} -->")
        header_lines.append(f"<!-- Template: {document_type} v{self.config.get('version', '1.0.0')} -->")
        
        return '\n'.join(header_lines)
    
    def get_document_structure(self, document_type: str) -> Dict[str, Any]:
        """
        Get the structure of a document type for UI rendering.
        
        Args:
            document_type: Type of document
            
        Returns:
            Document structure suitable for API response
        """
        if document_type not in self.compiled_templates:
            return {}
        
        template = self.compiled_templates[document_type]
        
        return {
            'type': document_type,
            'metadata': template['metadata'],
            'sections': [
                {
                    'name': section['name'],
                    'level': section['level'],
                    'required': section['required'],
                    'weight': section['weight'],
                    'description': section['description'],
                    'validation': section['validation']
                }
                for section in template['sections']
            ],
            'total_weight': sum(s['weight'] for s in template['sections'])
        }
    
    def list_document_types(self) -> List[str]:
        """
        List all available document types.
        
        Returns:
            List of document type names
        """
        return list(self.compiled_templates.keys())
    
    def validate_document(self, 
                         document_type: str, 
                         content: str) -> Dict[str, Any]:
        """
        Validate a document against its template.
        
        Args:
            document_type: Type of document
            content: Document content to validate
            
        Returns:
            Validation result with score and issues
        """
        if document_type not in self.compiled_templates:
            return {
                'valid': False,
                'score': 0,
                'error': f'Unknown document type: {document_type}'
            }
        
        template = self.compiled_templates[document_type]
        issues = []
        total_score = 0
        max_score = 0
        
        for section in template['sections']:
            max_score += section['weight']
            
            # Check if section exists
            section_pattern = f"#{{1,6}}\\s+{re.escape(section['name'])}"
            if re.search(section_pattern, content, re.IGNORECASE):
                # Section found
                section_score = section['weight']
                
                # Apply validation rules if any
                if section.get('validation'):
                    # Extract section content for validation
                    # (Simplified - would need proper section extraction)
                    section_score *= 0.8  # Placeholder validation
                
                total_score += section_score
            elif section['required']:
                issues.append(f"Missing required section: {section['name']}")
        
        score_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'valid': score_percentage >= self.config.get('validation_rules', {}).get('scoring', {}).get('pass_threshold', 70),
            'score': round(score_percentage, 2),
            'issues': issues,
            'total_weight': max_score,
            'achieved_weight': total_score
        }
    
    def reload_config(self):
        """Reload configuration from file."""
        self._load_config.cache_clear()
        self.config = self._load_config()
        self._compile_templates()
    
    def get_api_response(self) -> Dict[str, Any]:
        """
        Get complete configuration for API response.
        
        Returns:
            Configuration suitable for API endpoint
        """
        return {
            'version': self.config.get('version', '1.0.0'),
            'document_types': self.list_document_types(),
            'structures': {
                doc_type: self.get_document_structure(doc_type)
                for doc_type in self.list_document_types()
            },
            'validation_rules': self.config.get('validation_rules', {}),
            'exemptions': self.config.get('exemptions', {}),
            'ui_config': self.config.get('ui_config', {})
        }


def main():
    """Example usage and testing."""
    renderer = DocumentTemplateRenderer()
    
    # List available document types
    print("Available document types:")
    for doc_type in renderer.list_document_types():
        print(f"  - {doc_type}")
    
    # Render a README template
    print("\n" + "="*50)
    print("README Template:")
    print("="*50)
    readme = renderer.render_document('README', {
        'component_name': 'Test Component',
        'author': 'Test Author'
    })
    print(readme)
    
    # Get API response
    print("\n" + "="*50)
    print("API Response Structure:")
    print("="*50)
    import json
    api_response = renderer.get_api_response()
    print(json.dumps(api_response, indent=2)[:500] + "...")


if __name__ == "__main__":
    main()