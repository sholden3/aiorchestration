# Phase 1: Core Plugin Architecture - GitHub Copilot Prompts

## Prompt 1.1: Base Plugin Interface

```
You are a Senior Software Architect with expertise in plugin architectures and Python design patterns.

TASK: Create a comprehensive plugin interface system for validators

REQUIREMENTS:
1. Create abstract base class IValidatorPlugin with lifecycle methods
2. Include initialize(), validate(), configure(), teardown() methods
3. Support async and sync validation modes
4. Include metadata properties (name, version, description, author)
5. Support dependency injection for configuration
6. Include health check and status reporting
7. Type hints for all methods and properties

CONSTRAINTS:
- Must be compatible with Python 3.10+
- Must support both file and runtime configuration
- Must handle errors gracefully with fallback behavior
- Maximum 200 lines of code per class

GOVERNANCE:
- Follow coding standards in CLAUDE.md
- Severity score: 95/100 (CRITICAL)
- Priority: Immediate implementation

FOCUS: Create extensible, maintainable, and testable plugin architecture

VALIDATION:
- Unit tests for all interface methods
- Mock plugin implementation for testing
- Performance benchmark < 10ms initialization
- Configuration schema validation
```

## Prompt 1.2: Plugin Registry System

```
You are a Systems Engineer specializing in service discovery and registry patterns.

TASK: Implement a dynamic plugin registry system

REQUIREMENTS:
1. Create PluginRegistry singleton class
2. Support plugin registration/deregistration
3. Plugin discovery from filesystem
4. Plugin validation before registration
5. Dependency resolution between plugins
6. Plugin versioning and compatibility checks
7. Thread-safe operations for concurrent access

CONSTRAINTS:
- Use importlib for dynamic loading
- Support multiple plugin directories
- Handle circular dependencies gracefully
- Memory-efficient for 100+ plugins

GOVERNANCE:
- Configuration in config/governance/plugin_registry.yaml
- Severity score: 92/100 (CRITICAL)
- Audit all registration events

FOCUS: Build robust discovery and management system

VALIDATION:
- Test with 50+ mock plugins
- Concurrent registration tests
- Memory leak tests
- Plugin conflict resolution tests
```

## Prompt 1.3: Plugin Lifecycle Manager

```
You are a DevOps Architect with expertise in service lifecycle management.

TASK: Create plugin lifecycle management system

REQUIREMENTS:
1. Implement PluginLifecycleManager class
2. Handle plugin states: UNLOADED, LOADING, READY, ERROR, STOPPING
3. Support graceful startup/shutdown sequences
4. Implement health monitoring
5. Auto-restart failed plugins with backoff
6. Resource cleanup on teardown
7. Event emission for state changes

CONSTRAINTS:
- State transitions must be atomic
- Maximum 3 restart attempts
- Configurable timeouts per phase
- Must log all state transitions

GOVERNANCE:
- State machine configuration in YAML
- Severity score: 90/100 (CRITICAL)
- Performance metrics collection required

FOCUS: Ensure reliable plugin operation

VALIDATION:
- State transition tests
- Failure recovery tests
- Resource leak tests
- Performance under load tests
```

## Prompt 1.4: Configuration Loader

```
You are a Configuration Management Expert specializing in distributed systems.

TASK: Build data-driven configuration system for plugins

REQUIREMENTS:
1. Create ConfigurationLoader class
2. Support YAML, JSON, and environment variables
3. Schema validation using jsonschema
4. Configuration inheritance and overrides
5. Hot-reload capability with file watching
6. Encrypted sensitive value support
7. Default value management

CONSTRAINTS:
- Configuration precedence: ENV > File > Defaults
- Maximum 1MB configuration file size
- Validate all configurations before apply
- Rollback on invalid configuration

GOVERNANCE:
- Master config in config/governance/validators.yaml
- Severity score: 88/100 (HIGH)
- All changes must be audited

FOCUS: Create flexible, secure configuration management

VALIDATION:
- Schema validation tests
- Hot-reload functionality tests
- Override precedence tests
- Encryption/decryption tests
```

## Prompt 1.5: Plugin Communication Bus

```
You are a Distributed Systems Architect specializing in event-driven architectures.

TASK: Implement inter-plugin communication system

REQUIREMENTS:
1. Create PluginMessageBus class
2. Publish/subscribe pattern implementation
3. Request/response pattern support
4. Message queuing with priorities
5. Dead letter queue for failed messages
6. Message serialization (JSON/MessagePack)
7. Circuit breaker for failing subscribers

CONSTRAINTS:
- In-memory implementation (no external dependencies)
- Maximum 10MB message queue size
- Message TTL of 5 minutes
- Support 1000 msg/sec throughput

GOVERNANCE:
- Message schemas in config/schemas/
- Severity score: 85/100 (HIGH)
- Log all message failures

FOCUS: Enable loose coupling between plugins

VALIDATION:
- Throughput performance tests
- Message ordering tests
- Circuit breaker tests
- Memory pressure tests
```
