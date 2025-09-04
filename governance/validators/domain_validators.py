#!/usr/bin/env python3
"""
@fileoverview Domain-specific validators for enhanced governance
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Governance validation layer
@responsibility Enforce domain-specific best practices
@dependencies re, ast, typing, pathlib
@integration_points Governance engine, git hooks, code analysis
@testing_strategy Unit tests for each validator, integration tests with real code
@governance Enforces specialized coding standards per domain

Business Logic Summary:
- Database best practices validation
- Caching strategy enforcement
- Frontend/SCSS standards
- API design patterns
- Security patterns enforcement
- Performance optimization rules

Architecture Integration:
- Plugs into governance engine
- Context-aware validation
- Supports exemption system
- Provides detailed feedback
"""

import re
import ast
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of domain validation"""
    passed: bool
    domain: str
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    risk_score: float


class DatabaseValidator:
    """Validates database-related code for best practices"""
    
    def __init__(self):
        self.connection_pool_pattern = re.compile(r'create_engine\([^)]*pool_size=\d+')
        self.raw_sql_pattern = re.compile(r'(execute|executemany)\s*\(\s*["\'].*SELECT|INSERT|UPDATE|DELETE', re.IGNORECASE)
        self.transaction_pattern = re.compile(r'with\s+.*\.(begin|transaction)\(\)')
        self.index_hint_pattern = re.compile(r'#\s*INDEX:\s*\w+')
        
    def validate(self, content: str, file_path: str) -> ValidationResult:
        """Validate database code"""
        errors = []
        warnings = []
        suggestions = []
        risk_score = 0.0
        
        # Check for connection pooling
        if 'create_engine' in content and not self.connection_pool_pattern.search(content):
            warnings.append("Database connection created without explicit pool_size")
            suggestions.append("Consider setting pool_size and max_overflow for connection pooling")
            risk_score += 2.0
        
        # Check for SQL injection vulnerabilities
        if self.raw_sql_pattern.search(content):
            # Check if using parameterized queries
            if not re.search(r'%s|\?|:\w+', content):
                errors.append("Raw SQL without parameterization detected - SQL injection risk")
                risk_score += 8.0
            else:
                warnings.append("Raw SQL detected - ensure proper parameterization")
                risk_score += 3.0
        
        # Check for transaction management
        if 'session.commit()' in content and not self.transaction_pattern.search(content):
            warnings.append("Commits without explicit transaction boundaries")
            suggestions.append("Use context managers for transaction management")
            risk_score += 2.0
        
        # Check for N+1 query patterns
        if re.search(r'for\s+\w+\s+in\s+.*\.all\(\).*\n.*\.\w+\.filter', content):
            errors.append("Potential N+1 query pattern detected")
            suggestions.append("Consider using joinedload() or selectinload() for eager loading")
            risk_score += 5.0
        
        # Check for missing indexes
        if 'filter_by' in content or 'filter(' in content:
            if not self.index_hint_pattern.search(content):
                warnings.append("Query filters without index documentation")
                suggestions.append("Add # INDEX: comments to document required database indexes")
                risk_score += 1.0
        
        # Check for bulk operations
        if re.search(r'for\s+.*\s+in\s+.*:\s*\n\s*session\.add\(', content):
            warnings.append("Individual inserts in loop - consider bulk operations")
            suggestions.append("Use bulk_insert_mappings() or bulk_save_objects() for better performance")
            risk_score += 3.0
        
        return ValidationResult(
            passed=len(errors) == 0,
            domain='database',
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            risk_score=min(risk_score, 10.0)
        )


class CacheValidator:
    """Validates caching implementation and strategies"""
    
    def __init__(self):
        self.cache_key_pattern = re.compile(r'cache\.(get|set|delete)\(["\']([^"\']+)')
        self.ttl_pattern = re.compile(r'(ttl|expire|timeout)\s*=\s*(\d+)')
        self.cache_invalidation_pattern = re.compile(r'cache\.(delete|invalidate|flush)')
        
    def validate(self, content: str, file_path: str) -> ValidationResult:
        """Validate caching code"""
        errors = []
        warnings = []
        suggestions = []
        risk_score = 0.0
        
        # Check for cache key structure
        cache_keys = self.cache_key_pattern.findall(content)
        for operation, key in cache_keys:
            if not re.match(r'^[a-z0-9:_-]+$', key, re.IGNORECASE):
                warnings.append(f"Non-standard cache key format: {key}")
                suggestions.append("Use consistent key format: 'namespace:entity:id'")
                risk_score += 1.0
            
            if len(key) > 250:
                errors.append(f"Cache key too long: {key[:50]}...")
                risk_score += 3.0
        
        # Check for TTL configuration
        ttl_matches = self.ttl_pattern.findall(content)
        for _, ttl_value in ttl_matches:
            ttl_int = int(ttl_value)
            if ttl_int > 86400:  # More than 24 hours
                warnings.append(f"Long cache TTL detected: {ttl_int} seconds")
                suggestions.append("Consider shorter TTL for frequently changing data")
                risk_score += 1.5
            elif ttl_int < 60:  # Less than 1 minute
                warnings.append(f"Very short cache TTL: {ttl_int} seconds")
                suggestions.append("Short TTLs may reduce cache effectiveness")
                risk_score += 1.0
        
        # Check for cache stampede protection
        if 'cache.get' in content and 'lock' not in content.lower():
            warnings.append("Cache access without apparent stampede protection")
            suggestions.append("Consider implementing cache locks or probabilistic early expiration")
            risk_score += 2.0
        
        # Check for cache invalidation strategy
        if self.cache_invalidation_pattern.search(content):
            if 'transaction' not in content and 'commit' not in content:
                warnings.append("Cache invalidation outside transaction context")
                suggestions.append("Invalidate cache after transaction commit to prevent inconsistency")
                risk_score += 3.0
        
        # Check for cache warming
        if 'cache.set' in content and 'startup' not in content and 'init' not in content:
            suggestions.append("Consider implementing cache warming on application startup")
        
        # Check for cache metrics
        if 'cache.' in content and not re.search(r'(metric|monitor|stat|hit_rate)', content):
            suggestions.append("Add cache hit/miss metrics for monitoring")
            risk_score += 0.5
        
        return ValidationResult(
            passed=len(errors) == 0,
            domain='caching',
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            risk_score=min(risk_score, 10.0)
        )


class FrontendValidator:
    """Validates frontend and SCSS code"""
    
    def __init__(self):
        self.magic_number_pattern = re.compile(r'(padding|margin|width|height|font-size):\s*(\d+)(px|em|rem)')
        self.important_pattern = re.compile(r'!important')
        self.deep_nesting_pattern = re.compile(r'(\s{8,}|\t{2,})[.#]\w+')
        self.inline_style_pattern = re.compile(r'style=["\'](.*?)["\']')
        self.console_log_pattern = re.compile(r'console\.(log|debug|info)')
        
    def validate(self, content: str, file_path: str) -> ValidationResult:
        """Validate frontend code"""
        errors = []
        warnings = []
        suggestions = []
        risk_score = 0.0
        
        # SCSS specific validations
        if file_path.endswith('.scss') or file_path.endswith('.sass'):
            # Check for magic numbers
            magic_numbers = self.magic_number_pattern.findall(content)
            for prop, value, unit in magic_numbers:
                if value not in ['0', '1', '100']:
                    warnings.append(f"Magic number in SCSS: {prop}: {value}{unit}")
                    suggestions.append(f"Define {value}{unit} as a variable: $spacing-{value}")
                    risk_score += 0.5
            
            # Check for !important usage
            important_count = len(self.important_pattern.findall(content))
            if important_count > 0:
                warnings.append(f"Found {important_count} uses of !important")
                suggestions.append("Refactor CSS specificity instead of using !important")
                risk_score += important_count * 0.5
            
            # Check for deep nesting
            if self.deep_nesting_pattern.search(content):
                warnings.append("Deep nesting detected (>3 levels)")
                suggestions.append("Keep SCSS nesting to maximum 3 levels for maintainability")
                risk_score += 1.0
        
        # TypeScript/JavaScript validations
        if file_path.endswith('.ts') or file_path.endswith('.js'):
            # Check for inline styles
            inline_styles = self.inline_style_pattern.findall(content)
            if inline_styles:
                warnings.append(f"Found {len(inline_styles)} inline styles")
                suggestions.append("Move inline styles to CSS classes or styled components")
                risk_score += len(inline_styles) * 0.3
            
            # Check for console.log in production code
            if not 'spec' in file_path and not 'test' in file_path:
                console_logs = self.console_log_pattern.findall(content)
                if console_logs:
                    errors.append(f"Found {len(console_logs)} console.log statements")
                    suggestions.append("Remove console.log or use proper logging service")
                    risk_score += len(console_logs) * 1.0
            
            # Check for memory leaks
            if 'addEventListener' in content and 'removeEventListener' not in content:
                warnings.append("Event listeners without cleanup detected")
                suggestions.append("Add removeEventListener in cleanup/destroy methods")
                risk_score += 3.0
            
            # Check for unhandled promises
            if '.then(' in content and '.catch(' not in content:
                warnings.append("Promises without error handling")
                suggestions.append("Add .catch() blocks or use try/catch with async/await")
                risk_score += 2.0
        
        return ValidationResult(
            passed=len(errors) == 0,
            domain='frontend',
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            risk_score=min(risk_score, 10.0)
        )


class APIValidator:
    """Validates API design and implementation"""
    
    def __init__(self):
        self.rest_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        self.status_codes = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
        
    def validate(self, content: str, file_path: str) -> ValidationResult:
        """Validate API code"""
        errors = []
        warnings = []
        suggestions = []
        risk_score = 0.0
        
        # Check for RESTful conventions
        if any(method in content for method in self.rest_methods):
            # Check for proper status codes
            if 'return' in content or 'response' in content:
                has_status_code = any(str(code) in content for code in self.status_codes.keys())
                if not has_status_code:
                    warnings.append("API responses without explicit status codes")
                    suggestions.append("Always return appropriate HTTP status codes")
                    risk_score += 2.0
            
            # Check for API versioning
            if '/api/' in content and not re.search(r'/api/v\d+/', content):
                warnings.append("API endpoints without versioning")
                suggestions.append("Use API versioning: /api/v1/resource")
                risk_score += 1.5
            
            # Check for pagination
            if 'GET' in content and ('list' in content.lower() or 'all' in content.lower()):
                if 'limit' not in content and 'page' not in content:
                    warnings.append("List endpoint without pagination")
                    suggestions.append("Implement pagination for list endpoints")
                    risk_score += 2.0
        
        # Check for input validation
        if 'request.' in content:
            if not re.search(r'(validate|schema|check|verify)', content, re.IGNORECASE):
                errors.append("Request handling without apparent validation")
                suggestions.append("Validate all input data before processing")
                risk_score += 4.0
        
        # Check for error handling
        if 'def ' in content or 'function ' in content:
            if 'try' not in content and 'catch' not in content:
                warnings.append("Functions without error handling")
                suggestions.append("Implement proper error handling for all endpoints")
                risk_score += 2.0
        
        # Check for rate limiting
        if '@app.route' in content or '@router' in content:
            if 'ratelimit' not in content.lower() and 'throttle' not in content.lower():
                warnings.append("API endpoints without rate limiting")
                suggestions.append("Implement rate limiting to prevent abuse")
                risk_score += 1.5
        
        return ValidationResult(
            passed=len(errors) == 0,
            domain='api',
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            risk_score=min(risk_score, 10.0)
        )


class SecurityValidator:
    """Validates security patterns and practices"""
    
    def __init__(self):
        self.secret_patterns = [
            re.compile(r'(password|secret|key|token|api_key)\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            re.compile(r'(AWS|AZURE|GCP)_[A-Z_]*KEY', re.IGNORECASE)
        ]
        self.unsafe_patterns = [
            re.compile(r'eval\s*\('),
            re.compile(r'exec\s*\('),
            re.compile(r'__import__\s*\('),
            re.compile(r'pickle\.loads?\s*\('),
            re.compile(r'yaml\.load\s*\([^,)]*\)(?!.*Loader)')
        ]
        
    def validate(self, content: str, file_path: str) -> ValidationResult:
        """Validate security practices"""
        errors = []
        warnings = []
        suggestions = []
        risk_score = 0.0
        
        # Check for hardcoded secrets
        for pattern in self.secret_patterns:
            matches = pattern.findall(content)
            if matches:
                errors.append(f"Potential hardcoded secrets detected: {len(matches)} instances")
                suggestions.append("Use environment variables or secret management service")
                risk_score += len(matches) * 3.0
        
        # Check for unsafe functions
        for pattern in self.unsafe_patterns:
            if pattern.search(content):
                errors.append(f"Unsafe function detected: {pattern.pattern}")
                suggestions.append("Replace with safe alternatives")
                risk_score += 5.0
        
        # Check for CORS configuration
        if 'CORS' in content or 'Access-Control' in content:
            if '*' in content:
                warnings.append("Wildcard CORS configuration detected")
                suggestions.append("Specify allowed origins explicitly")
                risk_score += 3.0
        
        # Check for HTTPS enforcement
        if 'http://' in content and 'https://' not in content:
            if not 'localhost' in content and not '127.0.0.1' in content:
                warnings.append("Non-HTTPS URLs detected")
                suggestions.append("Always use HTTPS for external connections")
                risk_score += 2.0
        
        # Check for input sanitization
        if 'innerHTML' in content or 'dangerouslySetInnerHTML' in content:
            errors.append("Direct HTML injection detected")
            suggestions.append("Sanitize user input before rendering HTML")
            risk_score += 4.0
        
        return ValidationResult(
            passed=len(errors) == 0,
            domain='security',
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            risk_score=min(risk_score, 10.0)
        )


class DomainValidatorOrchestrator:
    """Orchestrates all domain validators"""
    
    def __init__(self):
        self.validators = {
            'database': DatabaseValidator(),
            'cache': CacheValidator(),
            'frontend': FrontendValidator(),
            'api': APIValidator(),
            'security': SecurityValidator()
        }
    
    def detect_domains(self, content: str, file_path: str) -> List[str]:
        """Detect which domains apply to this file"""
        domains = []
        
        # Always check security
        domains.append('security')
        
        # Database domain
        if any(keyword in content for keyword in ['session', 'query', 'database', 'sql', 'orm', 'model']):
            domains.append('database')
        
        # Cache domain
        if any(keyword in content for keyword in ['cache', 'redis', 'memcache', 'ttl']):
            domains.append('cache')
        
        # Frontend domain
        if file_path.endswith(('.ts', '.js', '.jsx', '.tsx', '.scss', '.sass', '.css')):
            domains.append('frontend')
        
        # API domain
        if any(keyword in content for keyword in ['@app.route', '@router', 'request', 'response', 'endpoint']):
            domains.append('api')
        
        return list(set(domains))
    
    def validate(self, content: str, file_path: str) -> Dict[str, ValidationResult]:
        """Run all applicable domain validators"""
        results = {}
        domains = self.detect_domains(content, file_path)
        
        for domain in domains:
            if domain in self.validators:
                results[domain] = self.validators[domain].validate(content, file_path)
        
        return results
    
    def get_overall_risk_score(self, results: Dict[str, ValidationResult]) -> float:
        """Calculate overall risk score"""
        if not results:
            return 0.0
        
        total_score = sum(r.risk_score for r in results.values())
        return min(total_score / len(results), 10.0)
    
    def format_report(self, results: Dict[str, ValidationResult]) -> str:
        """Format validation results as a report"""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("DOMAIN-SPECIFIC GOVERNANCE VALIDATION REPORT")
        lines.append("=" * 60)
        
        overall_passed = all(r.passed for r in results.values())
        overall_risk = self.get_overall_risk_score(results)
        
        lines.append(f"\nOverall Status: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
        lines.append(f"Risk Score: {overall_risk:.1f}/10.0")
        lines.append(f"Domains Validated: {', '.join(results.keys())}")
        
        for domain, result in results.items():
            lines.append(f"\n--- {domain.upper()} Domain ---")
            lines.append(f"Status: {'✅' if result.passed else '❌'}")
            lines.append(f"Risk Score: {result.risk_score:.1f}/10.0")
            
            if result.errors:
                lines.append("\nErrors:")
                for error in result.errors:
                    lines.append(f"  ❌ {error}")
            
            if result.warnings:
                lines.append("\nWarnings:")
                for warning in result.warnings:
                    lines.append(f"  ⚠️ {warning}")
            
            if result.suggestions:
                lines.append("\nSuggestions:")
                for suggestion in result.suggestions:
                    lines.append(f"  💡 {suggestion}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


# Integration with governance engine
def integrate_with_governance_engine():
    """Integration point for governance engine"""
    return DomainValidatorOrchestrator()


if __name__ == "__main__":
    # Test the validators
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python domain_validators.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        orchestrator = DomainValidatorOrchestrator()
        results = orchestrator.validate(content, file_path)
        print(orchestrator.format_report(results))
        
        # Exit with error if validation failed
        if not all(r.passed for r in results.values()):
            sys.exit(1)
            
    except Exception as e:
        print(f"Error validating file: {e}")
        sys.exit(1)