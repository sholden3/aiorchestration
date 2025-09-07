"""
Custom documentation validator plugin.
"""

from typing import Any, Dict
from libs.governance.plugins.base import BaseValidatorPlugin, PluginMetadata, ValidationResult, ValidationSeverity


class DocumentationValidatorPlugin(BaseValidatorPlugin):
    """
    Validates documentation standards and completeness.
    """
    
    METADATA = PluginMetadata(
        name="documentation_validator",
        version="2.0.0",
        description="Validates documentation standards and completeness",
        author="Documentation Team",
        license="Apache-2.0",
        tags=["documentation", "standards", "validation"],
        dependencies=[]
    )
    
    def __init__(self):
        super().__init__(self.METADATA)
        self._require_docstrings = True
        self._min_docstring_length = 10
    
    async def _do_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin configuration."""
        self._require_docstrings = config.get('require_docstrings', True)
        self._min_docstring_length = config.get('min_docstring_length', 10)
        self._logger.info(f"Documentation validator initialized - require docstrings: {self._require_docstrings}")
    
    async def _validate_async(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform documentation validation."""
        result = ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO
        )
        
        code_content = context.get('code', '')
        file_path = context.get('file_path', '')
        
        if not code_content:
            result.add_message("No code content provided for documentation check", ValidationSeverity.WARNING)
            return result
        
        import re
        
        # Find all function and class definitions
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]'
        
        functions = [(m.group(1), m.start()) for m in re.finditer(function_pattern, code_content)]
        classes = [(m.group(1), m.start()) for m in re.finditer(class_pattern, code_content)]
        
        # Check for docstrings
        docstring_pattern = r'""".*?"""'
        docstrings = list(re.finditer(docstring_pattern, code_content, re.DOTALL))
        
        missing_docs = []
        
        # Check functions for docstrings
        for func_name, func_pos in functions:
            if not func_name.startswith('_'):  # Skip private functions
                has_docstring = any(
                    doc.start() > func_pos and doc.start() < func_pos + 200
                    for doc in docstrings
                )
                if not has_docstring and self._require_docstrings:
                    missing_docs.append(f"Function '{func_name}' missing docstring")
        
        # Check classes for docstrings
        for class_name, class_pos in classes:
            has_docstring = any(
                doc.start() > class_pos and doc.start() < class_pos + 200
                for doc in docstrings
            )
            if not has_docstring and self._require_docstrings:
                missing_docs.append(f"Class '{class_name}' missing docstring")
        
        # Report missing documentation
        for issue in missing_docs:
            result.add_message(issue, ValidationSeverity.WARNING)
        
        # Check docstring quality
        short_docstrings = []
        for docstring in docstrings:
            content = docstring.group(0).replace('"""', '').strip()
            if len(content) < self._min_docstring_length:
                short_docstrings.append("Docstring too short")
        
        for issue in short_docstrings:
            result.add_message(issue, ValidationSeverity.INFO)
        
        result.add_message(f"Documentation validation completed for {file_path}", ValidationSeverity.INFO)
        result.metadata['functions_checked'] = len(functions)
        result.metadata['classes_checked'] = len(classes)
        result.metadata['docstrings_found'] = len(docstrings)
        
        return result
