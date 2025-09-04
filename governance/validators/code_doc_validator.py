"""
Code Documentation Validator Module

@description: Validates code documentation against defined standards
@author: Governance System
@version: 1.0.0
@dependencies: ast, re, yaml, pathlib
@exports: CodeDocumentationValidator, CodeValidationResult
@testing: 0% (needs implementation)
@last_review: 2025-09-03
"""

import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import json


@dataclass
class CodeValidationResult:
    """Result of code documentation validation.
    
    Attributes:
        file_path: Path to the validated file
        is_valid: Whether the file passes validation
        score: Documentation quality score (0-1)
        violations: List of validation violations
        warnings: List of warning messages
        suggestions: List of improvement suggestions
        coverage: Documentation coverage metrics
    """
    file_path: str
    is_valid: bool
    score: float
    violations: List[Dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    coverage: Dict = field(default_factory=dict)


class CodeDocumentationValidator:
    """Validates code documentation against language-specific standards.
    
    This validator checks Python, TypeScript, and JavaScript files
    for proper documentation according to configured standards.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validator with configuration.
        
        Args:
            config_path: Path to configuration file, defaults to .docs-metadata/code-formats.yaml
        """
        self.config_path = config_path or Path(".docs-metadata/code-formats.yaml")
        self.config = self._load_config()
        self.enforcement_mode = self.config.get('global', {}).get('enforcement_mode', 'progressive')
        
    def _load_config(self) -> Dict:
        """Load validation configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file not found.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'global': {
                'enabled': True,
                'enforcement_mode': 'warnings_only'
            },
            'python': {
                'style': 'google',
                'file_level': {'required': ['module_docstring']},
                'class_level': {'required': ['class_docstring']},
                'method_level': {'required': ['method_docstring']}
            },
            'typescript': {
                'style': 'jsdoc',
                'file_level': {'required': ['file_comment']},
                'class_level': {'required': ['class_comment']},
                'method_level': {'required': ['method_comment']}
            },
            'scoring': {
                'pass_threshold': 0.7,
                'warning_threshold': 0.85
            }
        }
    
    def validate_file(self, file_path: Path) -> CodeValidationResult:
        """Validate code documentation in a single file.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Validation result with score and violations
        """
        result = CodeValidationResult(
            file_path=str(file_path),
            is_valid=True,
            score=1.0
        )
        
        # Check if file exists
        if not file_path.exists():
            result.is_valid = False
            result.score = 0.0
            result.violations.append({
                'type': 'file_not_found',
                'severity': 'critical',
                'message': f"File not found: {file_path}"
            })
            return result
        
        # Check if file is exempted
        if self._is_exempted(file_path):
            result.suggestions.append("File is exempted from documentation validation")
            return result
        
        # Determine language and validate accordingly
        if file_path.suffix == '.py':
            self._validate_python_file(file_path, result)
        elif file_path.suffix in ['.ts', '.tsx']:
            self._validate_typescript_file(file_path, result)
        elif file_path.suffix in ['.js', '.jsx']:
            self._validate_javascript_file(file_path, result)
        else:
            result.suggestions.append(f"No validation rules for {file_path.suffix} files")
            return result
        
        # Calculate final score
        result.score = self._calculate_score(result)
        result.is_valid = result.score >= self.config.get('scoring', {}).get('pass_threshold', 0.7)
        
        # Add suggestions
        self._add_suggestions(result)
        
        return result
    
    def _validate_python_file(self, file_path: Path, result: CodeValidationResult):
        """Validate Python file documentation.
        
        Args:
            file_path: Path to Python file
            result: Validation result to update
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except Exception as e:
            result.violations.append({
                'type': 'parse_error',
                'severity': 'critical',
                'message': f"Failed to parse Python file: {e}"
            })
            return
        
        config = self.config.get('python', {})
        
        # Check file-level documentation
        module_doc = ast.get_docstring(tree)
        if not module_doc and 'module_docstring' in config.get('file_level', {}).get('required', []):
            result.violations.append({
                'type': 'missing_file_docstring',
                'severity': 'critical',
                'message': 'Missing module-level docstring',
                'line': 1
            })
        elif module_doc:
            self._validate_python_docstring_format(module_doc, 'file', result)
        
        # Check classes and methods
        classes_found = 0
        methods_found = 0
        documented_classes = 0
        documented_methods = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes_found += 1
                class_doc = ast.get_docstring(node)
                if class_doc:
                    documented_classes += 1
                    self._validate_python_docstring_format(class_doc, 'class', result)
                elif not node.name.startswith('_'):  # Public class
                    result.violations.append({
                        'type': 'missing_class_docstring',
                        'severity': 'major',
                        'message': f"Class '{node.name}' missing docstring",
                        'line': node.lineno
                    })
            
            elif isinstance(node, ast.FunctionDef):
                # Skip exempted methods
                if node.name in self.config.get('validation', {}).get('exemptions', {}).get('method_exemptions', []):
                    continue
                
                methods_found += 1
                method_doc = ast.get_docstring(node)
                if method_doc:
                    documented_methods += 1
                    self._validate_python_method_docstring(node, method_doc, result)
                elif not node.name.startswith('_'):  # Public method
                    result.violations.append({
                        'type': 'missing_method_docstring',
                        'severity': 'major',
                        'message': f"Method '{node.name}' missing docstring",
                        'line': node.lineno
                    })
        
        # Update coverage metrics
        result.coverage = {
            'classes': f"{documented_classes}/{classes_found}" if classes_found > 0 else "N/A",
            'methods': f"{documented_methods}/{methods_found}" if methods_found > 0 else "N/A",
            'percentage': (documented_classes + documented_methods) / (classes_found + methods_found) * 100 if (classes_found + methods_found) > 0 else 100
        }
    
    def _validate_python_docstring_format(self, docstring: str, level: str, result: CodeValidationResult):
        """Validate Python docstring format.
        
        Args:
            docstring: The docstring content
            level: 'file', 'class', or 'method'
            result: Validation result to update
        """
        lines = docstring.strip().split('\n')
        
        # Check for brief description (first line)
        if not lines or not lines[0].strip():
            result.warnings.append(f"{level.capitalize()}-level docstring missing brief description")
        
        # Check for specific tags in file-level docstrings
        if level == 'file':
            required_tags = ['@description', '@author']
            found_tags = [tag for tag in required_tags if any(tag in line for line in lines)]
            missing_tags = set(required_tags) - set(found_tags)
            
            for tag in missing_tags:
                result.warnings.append(f"File docstring missing {tag} tag")
    
    def _validate_python_method_docstring(self, node: ast.FunctionDef, docstring: str, result: CodeValidationResult):
        """Validate Python method docstring completeness.
        
        Args:
            node: AST node for the method
            docstring: The method's docstring
            result: Validation result to update
        """
        # Check for Args section if method has parameters
        has_params = len(node.args.args) > 1 if node.args.args and node.args.args[0].arg == 'self' else len(node.args.args) > 0
        
        if has_params:
            if 'Args:' not in docstring and 'Parameters:' not in docstring:
                result.warnings.append(f"Method '{node.name}' has parameters but missing Args section")
        
        # Check for Returns section if method returns value
        has_return = any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(node))
        if has_return:
            if 'Returns:' not in docstring and 'Return:' not in docstring:
                result.warnings.append(f"Method '{node.name}' returns value but missing Returns section")
        
        # Check for Raises section if method raises exceptions
        has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(node))
        if has_raise:
            if 'Raises:' not in docstring and 'Raise:' not in docstring:
                result.warnings.append(f"Method '{node.name}' raises exceptions but missing Raises section")
    
    def _validate_typescript_file(self, file_path: Path, result: CodeValidationResult):
        """Validate TypeScript file documentation.
        
        Args:
            file_path: Path to TypeScript file
            result: Validation result to update
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result.violations.append({
                'type': 'read_error',
                'severity': 'critical',
                'message': f"Failed to read TypeScript file: {e}"
            })
            return
        
        # Check for file-level JSDoc comment
        if not re.match(r'^\s*/\*\*[\s\S]*?\*/', content):
            result.violations.append({
                'type': 'missing_file_comment',
                'severity': 'major',
                'message': 'Missing file-level JSDoc comment'
            })
        
        # Find all classes
        class_pattern = r'(?:export\s+)?class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        
        for class_name in classes:
            # Check if class has JSDoc
            class_doc_pattern = rf'/\*\*[\s\S]*?\*/\s*(?:export\s+)?class\s+{class_name}'
            if not re.search(class_doc_pattern, content):
                result.violations.append({
                    'type': 'missing_class_comment',
                    'severity': 'major',
                    'message': f"Class '{class_name}' missing JSDoc comment"
                })
        
        # Find all methods/functions
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[\w<>[\]|]+)?\s*\{'
        methods = re.findall(method_pattern, content)
        
        documented_methods = 0
        for method_name in methods:
            if method_name in self.config.get('validation', {}).get('exemptions', {}).get('method_exemptions', []):
                continue
            
            # Check if method has JSDoc
            method_doc_pattern = rf'/\*\*[\s\S]*?\*/\s*(?:public\s+|private\s+|protected\s+)?(?:async\s+)?{method_name}\s*\('
            if re.search(method_doc_pattern, content):
                documented_methods += 1
            elif not method_name.startswith('_'):
                result.warnings.append(f"Method '{method_name}' missing JSDoc comment")
        
        # Update coverage
        result.coverage = {
            'classes': f"{len([c for c in classes if f'class {c}' in content])}/{len(classes)}" if classes else "N/A",
            'methods': f"{documented_methods}/{len(methods)}" if methods else "N/A"
        }
    
    def _validate_javascript_file(self, file_path: Path, result: CodeValidationResult):
        """Validate JavaScript file documentation.
        
        Args:
            file_path: Path to JavaScript file
            result: Validation result to update
        """
        # JavaScript validation is similar to TypeScript but with relaxed type requirements
        self._validate_typescript_file(file_path, result)
        
        # Adjust severity for JavaScript (more lenient)
        for violation in result.violations:
            if violation['severity'] == 'major':
                violation['severity'] = 'minor'
    
    def _is_exempted(self, file_path: Path) -> bool:
        """Check if file is exempted from validation.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is exempted
        """
        exemptions = self.config.get('validation', {}).get('exemptions', {}).get('file_exemptions', [])
        
        for pattern in exemptions:
            if any(part in str(file_path) for part in pattern.replace('**', '').replace('*', '').split('/')):
                return True
        
        return False
    
    def _calculate_score(self, result: CodeValidationResult) -> float:
        """Calculate overall documentation score.
        
        Args:
            result: Validation result
            
        Returns:
            Score between 0 and 1
        """
        if not result.violations and not result.warnings:
            return 1.0
        
        score = 1.0
        penalties = self.config.get('scoring', {}).get('penalties', {})
        
        # Apply penalties for violations
        for violation in result.violations:
            severity = violation.get('severity', 'minor')
            if severity == 'critical':
                score -= penalties.get('missing_required', 0.2)
            elif severity == 'major':
                score -= penalties.get('missing_recommended', 0.1)
            else:
                score -= penalties.get('missing_optional', 0.05)
        
        # Small penalty for warnings
        score -= len(result.warnings) * 0.02
        
        return max(0.0, min(1.0, score))
    
    def _add_suggestions(self, result: CodeValidationResult):
        """Add improvement suggestions based on validation results.
        
        Args:
            result: Validation result to update
        """
        score_config = self.config.get('scoring', {})
        
        if result.score < score_config.get('warning_threshold', 0.85):
            result.suggestions.append("Consider improving documentation to meet quality standards")
        
        if result.score >= score_config.get('excellent_threshold', 0.95):
            result.suggestions.append("Excellent code documentation!")
        
        # Specific suggestions
        violation_types = {v.get('type') for v in result.violations}
        
        if 'missing_file_docstring' in violation_types or 'missing_file_comment' in violation_types:
            result.suggestions.append("Add file-level documentation explaining the module's purpose")
        
        if 'missing_class_docstring' in violation_types or 'missing_class_comment' in violation_types:
            result.suggestions.append("Document all public classes with their purpose and usage")
        
        if 'missing_method_docstring' in violation_types or 'missing_method_comment' in violation_types:
            result.suggestions.append("Document public methods with parameters, returns, and examples")
        
        if result.coverage.get('percentage', 100) < 80:
            result.suggestions.append("Increase documentation coverage to at least 80%")
    
    def generate_report(self, results: List[CodeValidationResult]) -> str:
        """Generate validation report for multiple files.
        
        Args:
            results: List of validation results
            
        Returns:
            Formatted report string
        """
        report = ["# Code Documentation Validation Report\n"]
        report.append(f"**Files Validated**: {len(results)}\n")
        
        # Summary statistics
        valid_count = sum(1 for r in results if r.is_valid)
        avg_score = sum(r.score for r in results) / len(results) if results else 0
        
        report.append(f"**Valid Files**: {valid_count}/{len(results)}\n")
        report.append(f"**Average Score**: {avg_score:.2%}\n")
        report.append("\n---\n")
        
        # Detailed results
        for result in results:
            status = "✅" if result.is_valid else "❌"
            report.append(f"\n## {status} {result.file_path}\n")
            report.append(f"**Score**: {result.score:.2%}\n")
            
            if result.coverage:
                report.append(f"**Coverage**: Classes {result.coverage.get('classes', 'N/A')}, ")
                report.append(f"Methods {result.coverage.get('methods', 'N/A')}\n")
            
            if result.violations:
                report.append("\n### Violations\n")
                for violation in result.violations:
                    report.append(f"- [{violation.get('severity', 'unknown').upper()}] ")
                    report.append(f"{violation.get('message', 'Unknown violation')}\n")
            
            if result.warnings:
                report.append("\n### Warnings\n")
                for warning in result.warnings:
                    report.append(f"- {warning}\n")
            
            if result.suggestions:
                report.append("\n### Suggestions\n")
                for suggestion in result.suggestions:
                    report.append(f"- {suggestion}\n")
        
        return "".join(report)