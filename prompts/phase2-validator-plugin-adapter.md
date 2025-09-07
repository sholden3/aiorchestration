# Phase 2: Validator Plugin Adapter - GitHub Copilot Prompts

## Prompt 2.1: Validator Plugin Adapter

```
You are a Refactoring Specialist with expertise in adapter patterns and legacy system modernization.

TASK: Convert existing validators to plugin architecture

REQUIREMENTS:
1. Create ValidatorPluginAdapter base class
2. Wrap existing validators without breaking changes
3. Map validator methods to plugin interface
4. Preserve all existing functionality
5. Add configuration injection points
6. Implement backward compatibility layer
7. Support gradual migration strategy

CONSTRAINTS:
- Zero breaking changes to existing code
- Maintain existing test coverage
- Performance overhead < 5%
- Support both old and new interfaces

GOVERNANCE:
- Migration plan in docs/migration/validator_plugins.md
- Severity score: 82/100 (HIGH)
- All validators must maintain signatures

FOCUS: Seamless transition to plugin architecture

VALIDATION:
- Regression tests for all validators
- Performance comparison tests
- Backward compatibility tests
- Integration tests with existing hooks
```

## Prompt 2.2: Plugin Discovery Mechanism

```
You are a Senior Python Developer specializing in dynamic module loading and reflection.

TASK: Implement automatic plugin discovery system

REQUIREMENTS:
1. Create PluginDiscovery class
2. Scan multiple directories for plugins
3. Validate plugin structure and interface
4. Extract plugin metadata
5. Handle namespace conflicts
6. Support plugin packages and modules
7. Cache discovery results

CONSTRAINTS:
- Use AST parsing for validation
- Support .py, .pyc, and packages
- Ignore __pycache__ and .git
- Maximum 10 second discovery time

GOVERNANCE:
- Plugin paths in config/governance/plugin_paths.yaml
- Severity score: 80/100 (HIGH)
- Log all discovered plugins

FOCUS: Robust and efficient plugin discovery

VALIDATION:
- Discovery with 100+ plugins
- Malformed plugin handling
- Namespace conflict tests
- Performance benchmarks
```

## Prompt 2.3: Validator Factory Pattern

```
You are a Design Pattern Expert specializing in creational patterns.

TASK: Implement validator factory for plugin instantiation

REQUIREMENTS:
1. Create ValidatorFactory class
2. Support multiple instantiation strategies
3. Dependency injection container
4. Singleton and prototype patterns
5. Lazy loading capability
6. Plugin pooling for performance
7. Factory method registration

CONSTRAINTS:
- Thread-safe instantiation
- Maximum 100 cached instances
- Support async initialization
- Clean shutdown of all instances

GOVERNANCE:
- Factory config in config/governance/factory.yaml
- Severity score: 78/100 (HIGH)
- Track all instantiations

FOCUS: Efficient and flexible plugin creation

VALIDATION:
- Concurrent instantiation tests
- Memory management tests
- Dependency injection tests
- Pool exhaustion tests
```

## Prompt 2.4: Hot-Reload Capability

```
You are a Live Systems Engineer specializing in zero-downtime deployments.

TASK: Implement hot-reload for validator plugins

REQUIREMENTS:
1. Create HotReloadManager class
2. File system monitoring for changes
3. Graceful plugin replacement
4. State preservation during reload
5. Rollback on reload failure
6. Notification system for consumers
7. Reload scheduling and throttling

CONSTRAINTS:
- Maximum 5 second reload time
- Preserve in-flight validations
- No validation loss during reload
- Support development and production modes

GOVERNANCE:
- Reload config in config/governance/hotreload.yaml
- Severity score: 75/100 (HIGH)
- Audit all reload operations

FOCUS: Zero-disruption plugin updates

VALIDATION:
- Reload under load tests
- State preservation tests
- Rollback scenario tests
- Race condition tests
```

## Prompt 2.5: Plugin Validation Framework

```
You are a Quality Assurance Architect specializing in plugin ecosystems.

TASK: Create comprehensive plugin validation framework

REQUIREMENTS:
1. Create PluginValidator class
2. Interface compliance checking
3. Security vulnerability scanning
4. Performance profiling
5. Resource usage monitoring
6. Compatibility testing
7. Documentation completeness check

CONSTRAINTS:
- Validation must complete in < 30 seconds
- Support custom validation rules
- Generate detailed reports
- Non-blocking validation mode

GOVERNANCE:
- Validation rules in config/governance/plugin_validation.yaml
- Severity score: 80/100 (HIGH)
- All plugins must pass before registration

FOCUS: Ensure plugin quality and safety

VALIDATION:
- Validate 50+ diverse plugins
- Security scanner tests
- Performance profiler tests
- Report generation tests
```
