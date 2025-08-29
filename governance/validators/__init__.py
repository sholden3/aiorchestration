"""
@fileoverview Validators package - Validation implementations for governance rules
@author Dr. Sarah Chen v1.0 & Alex Novak v1.0 - 2025-08-29
@architecture Backend - Validation layer
@responsibility Implement specific validation logic for governance rules
@dependencies regex, ast, semantic analysis libraries
@integration_points Core engine, rule definitions, decision pipeline
@testing_strategy Validator unit tests, accuracy tests, performance tests
@governance Validators are the enforcement mechanism of governance

Business Logic Summary:
- Pattern-based validation
- Semantic code analysis
- Security vulnerability detection
- Hallucination detection
- Documentation validation

Architecture Integration:
- Plugin architecture
- Strategy pattern
- Chain of validators
- Async validation
- Result aggregation

Sarah's Framework Check:
- What breaks first: Validator chain timeout
- How we know: Validation time exceeds threshold
- Plan B: Parallel validation with timeout per validator

Available Validators:
- BasicHallucinationDetector: Detect AI hallucinations
- PatternValidator: Regex-based pattern matching
- SemanticValidator: Code meaning analysis (planned)
- SecurityValidator: Security issue detection (planned)
- DocumentationValidator: Doc completeness (planned)

Validator Interface:
All validators implement:
- validate(context, content) -> ValidationResult
- get_confidence() -> float
- get_metrics() -> dict

Usage Example:
    from governance.validators import BasicHallucinationDetector
    
    detector = BasicHallucinationDetector()
    result = detector.detect_hallucination(
        "The Python GIL was removed in 2005"
    )
"""

# Current validators
from .basic_hallucination_detector import BasicHallucinationDetector

__all__ = [
    'BasicHallucinationDetector'
]

__version__ = '1.0.0'