"""
@fileoverview Validator definitions - Configuration for validation modules
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Validator configuration
@responsibility Configure and manage validator behaviors
@dependencies None - pure configuration
@integration_points Validator implementations, rule engine
@testing_strategy Validator config tests, validation accuracy tests
@governance Validators enforce governance rules

Business Logic Summary:
- Configure validator thresholds
- Define validation pipelines
- Set validator priorities
- Manage validator chains
- Track validator metrics

Architecture Integration:
- Loaded by validator manager
- Used by validation pipeline
- Referenced in results
- Tracked in metrics
- Audited for accuracy

Sarah's Framework Check:
- What breaks first: Validator timeout on large files
- How we know: Validation time metrics exceed threshold
- Plan B: Chunked validation with progress tracking

Validator Types:
- pattern_validator: Regex pattern matching
- semantic_validator: Code meaning analysis
- security_validator: Security vulnerability detection
- hallucination_validator: AI output verification
- documentation_validator: Doc completeness checks

Validator Configuration:
Each validator specifies:
- Activation conditions
- Timeout limits
- Confidence thresholds
- Fallback behavior
"""

# Validator configs loaded dynamically

__all__ = []

__version__ = '1.0.0'