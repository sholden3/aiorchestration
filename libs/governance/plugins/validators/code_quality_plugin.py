"""
Sample code quality validator plugin for demonstration.
"""

from typing import Any, Dict
from libs.governance.plugins.base import BaseValidatorPlugin, PluginMetadata, ValidationResult, ValidationSeverity


class CodeQualityValidatorPlugin(BaseValidatorPlugin):
    """
    Validates code quality standards including complexity, naming, and structure.
    """
    
    METADATA = PluginMetadata(
        name="code_quality_validator",
        version="1.0.0",
        description="Validates code quality standards and best practices",
        author="Governance Team",
        license="MIT",
        tags=["code-quality", "standards", "validation"],
        dependencies=[]
    )
    
    def __init__(self):
        super().__init__(self.METADATA)
        self._max_complexity = 10
        self._min_function_length = 3
        self._max_function_length = 50
    
    async def _do_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        self._max_complexity = config.get('max_complexity', 10)
        self._min_function_length = config.get('min_function_length', 3)
        self._max_function_length = config.get('max_function_length', 50)
        self._logger.info(f"Code quality validator initialized with complexity limit: {self._max_complexity}")
    
    async def _validate_async(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform code quality validation."""
        result = ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO
        )
        
        # Example validation logic
        code_content = context.get('code', '')
        file_path = context.get('file_path', '')
        
        if not code_content:
            result.add_message("No code content provided", ValidationSeverity.WARNING)
            result.success = False
            return result
        
        # Check for basic quality issues
        lines = code_content.split('\n')
        
        # Check line length
        for i, line in enumerate(lines):
            if len(line) > 120:
                result.add_message(f"Line {i+1} exceeds 120 characters", ValidationSeverity.WARNING)
        
        # Check for TODO comments
        todo_count = sum(1 for line in lines if 'TODO' in line.upper())
        if todo_count > 0:
            result.add_message(f"Found {todo_count} TODO comments", ValidationSeverity.INFO)
        
        # Check for proper function naming (basic)
        import re
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        functions = re.findall(function_pattern, code_content)
        
        for func_name in functions:
            if not func_name.islower():
                result.add_message(f"Function '{func_name}' should use snake_case", ValidationSeverity.WARNING)
        
        result.add_message(f"Code quality validation completed for {file_path}", ValidationSeverity.INFO)
        result.metadata['functions_checked'] = len(functions)
        result.metadata['lines_checked'] = len(lines)
        
        return result
    
    async def _do_configure(self, config: Dict[str, Any]) -> None:
        """Update plugin configuration."""
        if 'max_complexity' in config:
            self._max_complexity = config['max_complexity']
        if 'min_function_length' in config:
            self._min_function_length = config['min_function_length']
        if 'max_function_length' in config:
            self._max_function_length = config['max_function_length']
