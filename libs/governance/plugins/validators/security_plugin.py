"""
Security validation plugin for detecting security issues.
"""

from typing import Any, Dict
from libs.governance.plugins.base import BaseValidatorPlugin, PluginMetadata, ValidationResult, ValidationSeverity


class SecurityValidatorPlugin(BaseValidatorPlugin):
    """
    Validates code for security vulnerabilities and best practices.
    """
    
    METADATA = PluginMetadata(
        name="security_validator",
        version="1.1.0",
        description="Detects security vulnerabilities and insecure patterns",
        author="Security Team",
        license="MIT",
        tags=["security", "vulnerability", "validation"],
        dependencies=["code_quality_validator"]
    )
    
    def __init__(self):
        super().__init__(self.METADATA)
        self._security_patterns = []
    
    async def _do_initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with security patterns."""
        self._security_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(',
            r'input\s*\(',  # Python 2 input() is dangerous
            r'pickle\.loads?\s*\(',
            r'yaml\.load\s*\(',
        ]
        
        custom_patterns = config.get('custom_patterns', [])
        self._security_patterns.extend(custom_patterns)
        
        self._logger.info(f"Security validator initialized with {len(self._security_patterns)} patterns")
    
    async def _validate_async(self, context: Dict[str, Any]) -> ValidationResult:
        """Perform security validation."""
        result = ValidationResult(
            success=True,
            plugin_name=self.metadata.name,
            severity=ValidationSeverity.INFO
        )
        
        code_content = context.get('code', '')
        file_path = context.get('file_path', '')
        
        if not code_content:
            result.add_message("No code content provided for security check", ValidationSeverity.WARNING)
            return result
        
        import re
        security_issues = []
        
        # Check for security patterns
        lines = code_content.split('\n')
        for i, line in enumerate(lines):
            for pattern in self._security_patterns:
                if re.search(pattern, line):
                    issue = f"Line {i+1}: Potential security issue - {pattern}"
                    security_issues.append(issue)
                    result.add_message(issue, ValidationSeverity.ERROR)
        
        # Check for hardcoded passwords/secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]
        
        for i, line in enumerate(lines):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = f"Line {i+1}: Potential hardcoded secret"
                    security_issues.append(issue)
                    result.add_message(issue, ValidationSeverity.WARNING)
        
        if security_issues:
            result.success = len([i for i in security_issues if "ERROR" in i]) == 0
        
        result.add_message(f"Security validation completed for {file_path}", ValidationSeverity.INFO)
        result.metadata['security_issues'] = len(security_issues)
        result.metadata['patterns_checked'] = len(self._security_patterns)
        
        return result
