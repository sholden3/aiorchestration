# Phase 5: Testing & Documentation - GitHub Copilot Prompts

## Prompt 5.1: Comprehensive Integration Tests

```
You are a Test Architect specializing in complex system validation.

TASK: Create comprehensive integration test suite

REQUIREMENTS:
1. Create IntegrationTestSuite class
2. End-to-end hook flow tests
3. Multi-validator chain tests
4. Failure injection tests
5. Performance regression tests
6. Load and stress tests
7. Chaos engineering tests

CONSTRAINTS:
- 85% minimum code coverage
- Tests must run in < 10 minutes
- Support parallel execution
- Generate coverage reports

GOVERNANCE:
- Test config in tests/integration/config.yaml
- Severity score: 85/100 (HIGH)
- All tests must pass before deploy

FOCUS: Validate entire system behavior

VALIDATION:
- Test all hook types
- Test all validator combinations
- Test failure scenarios
- Test performance limits

SUCCESS METRICS:
- 100% critical path coverage
- < 1% test flakiness
- < 10 minute execution time
```

## Prompt 5.2: Performance Benchmarking Suite

```
You are a Performance Engineer specializing in system optimization.

TASK: Implement comprehensive performance benchmarking

REQUIREMENTS:
1. Create PerformanceBenchmark class
2. Latency measurements
3. Throughput testing
4. Resource utilization tracking
5. Bottleneck identification
6. Regression detection
7. Optimization recommendations

CONSTRAINTS:
- Sub-millisecond precision
- Support 1M operations
- Memory profiling included
- CPU profiling included

GOVERNANCE:
- Benchmark config in benchmarks/config.yaml
- Severity score: 80/100 (HIGH)
- Track all performance metrics

FOCUS: Identify and eliminate bottlenecks

VALIDATION:
- Baseline establishment
- Regression detection
- Scalability limits
- Resource efficiency

SUCCESS METRICS:
- < 100ms validation latency
- > 1000 validations/second
- < 100MB memory usage
```

## Prompt 5.3: Documentation Generation System

```
You are a Technical Writer specializing in automated documentation.

TASK: Create automatic documentation generation system

REQUIREMENTS:
1. Create DocumentationGenerator class
2. API documentation from code
3. Configuration reference
4. Plugin development guide
5. Deployment documentation
6. Troubleshooting guide
7. Architecture diagrams

CONSTRAINTS:
- Markdown and HTML output
- Include code examples
- Generate from docstrings
- Version controlled

GOVERNANCE:
- Doc templates in docs/templates/
- Severity score: 75/100 (MEDIUM)
- Review all generated docs

FOCUS: Complete and accurate documentation

VALIDATION:
- Documentation completeness
- Example accuracy
- Link validation
- Format consistency

SUCCESS METRICS:
- 100% API coverage
- All examples tested
- < 5 minute generation
```

## Prompt 5.4: Production Deployment Preparation

```
You are a DevOps Lead specializing in production readiness.

TASK: Prepare system for production deployment

REQUIREMENTS:
1. Create DeploymentValidator class
2. Health check endpoints
3. Rollback procedures
4. Migration scripts
5. Monitoring setup
6. Security hardening
7. Disaster recovery plan

CONSTRAINTS:
- Zero-downtime deployment
- Automated rollback
- Blue-green deployment ready
- Container-ready

GOVERNANCE:
- Deployment config in deploy/production/
- Severity score: 90/100 (CRITICAL)
- Require security review

FOCUS: Production-ready system

VALIDATION:
- Health check tests
- Rollback tests
- Migration tests
- Security scan

SUCCESS METRICS:
- 99.9% uptime SLA
- < 5 minute rollback
- Zero data loss
```

## Prompt 5.5: Plugin Development Kit

```
You are a Developer Experience Expert specializing in SDK design.

TASK: Create plugin development kit for external developers

REQUIREMENTS:
1. Create PluginDevelopmentKit class
2. Project scaffolding tool
3. Testing framework
4. Debug utilities
5. Example plugins
6. Validation tools
7. Publishing pipeline

CONSTRAINTS:
- Support multiple IDEs
- Include VS Code extension
- Comprehensive examples
- Video tutorials

GOVERNANCE:
- SDK config in sdk/config.yaml
- Severity score: 70/100 (MEDIUM)
- Review all SDK releases

FOCUS: Enable easy plugin development

VALIDATION:
- SDK functionality tests
- Example plugin tests
- Tool integration tests
- Documentation tests

SUCCESS METRICS:
- < 30 min to first plugin
- 90% developer satisfaction
- 50+ community plugins
```
