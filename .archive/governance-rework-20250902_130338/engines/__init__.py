"""
@fileoverview Engines package - Specialized governance evaluation engines
@author Dr. Sarah Chen v1.0 - 2025-08-29
@architecture Backend - Evaluation engines
@responsibility Provide specialized engines for different governance contexts
@dependencies Core governance modules, rule definitions
@integration_points Core engine, validators, decision pipeline
@testing_strategy Engine unit tests, performance tests, accuracy tests
@governance Engines are validated before deployment

Business Logic Summary:
- Specialized evaluation logic
- Context-specific processing
- Performance optimizations
- Caching strategies
- Parallel evaluation

Architecture Integration:
- Extend core engine
- Plugin architecture
- Strategy pattern
- Chain of responsibility
- Observer pattern

Sarah's Framework Check:
- What breaks first: Engine initialization with bad config
- How we know: Startup validation failures
- Plan B: Fallback to core engine

Planned Engines:
- FastEngine: Optimized for speed
- ThoroughEngine: Complete analysis
- SecurityEngine: Security-focused
- PerformanceEngine: Performance validation
- ComplianceEngine: Regulatory compliance

Note: Currently using core engine.
Specialized engines planned for future.
"""

# Future engine implementations

__all__ = []

__version__ = '0.1.0'
__status__ = 'planned'