# Phase 3: Hook Integration Layer - GitHub Copilot Prompts

## Prompt 3.1: Hook-Validator Orchestrator

```
You are a Workflow Orchestration Expert specializing in event-driven systems.

TASK: Create orchestration system for hook-validator coordination

REQUIREMENTS:
1. Create HookValidatorOrchestrator class
2. Dynamic validator assignment per hook
3. Validator execution ordering
4. Parallel and sequential execution modes
5. Result aggregation strategies
6. Conditional validator execution
7. Circuit breaking for failing validators

CONSTRAINTS:
- Support 10+ hooks, 50+ validators
- Maximum 500ms total execution time
- Graceful degradation required
- Memory efficient for large payloads

GOVERNANCE:
- Orchestration rules in config/governance/orchestration.yaml
- Severity score: 85/100 (HIGH)
- Log all orchestration decisions

FOCUS: Flexible and performant validator coordination

VALIDATION:
- Complex workflow tests
- Performance under load
- Failure cascade tests
- Memory pressure tests
```

## Prompt 3.2: Plugin Assignment System

```
You are a Configuration Management Specialist with expertise in dynamic systems.

TASK: Build dynamic plugin assignment to hooks

REQUIREMENTS:
1. Create PluginAssignmentManager class
2. CRUD operations for assignments
3. Priority-based ordering
4. Conditional assignment rules
5. Environment-specific assignments
6. Assignment validation
7. Bulk assignment operations

CONSTRAINTS:
- Atomic assignment changes
- Support 1000+ assignments
- Real-time assignment updates
- Conflict detection and resolution

GOVERNANCE:
- Assignments in config/governance/hook_assignments.yaml
- Severity score: 82/100 (HIGH)
- Audit all assignment changes

FOCUS: Precise control over validator execution

VALIDATION:
- Assignment CRUD tests
- Conflict resolution tests
- Priority ordering tests
- Bulk operation tests
```

## Prompt 3.3: Configuration Management System

```
You are a DevOps Engineer specializing in configuration as code.

TASK: Implement comprehensive configuration management for hooks

REQUIREMENTS:
1. Create HookConfigurationManager class
2. Hierarchical configuration model
3. Environment-specific overrides
4. Secret management integration
5. Configuration validation
6. Change tracking and rollback
7. Configuration templating

CONSTRAINTS:
- Support YAML, JSON, TOML formats
- Encrypt sensitive values
- Maximum 10MB total config size
- Version all configuration changes

GOVERNANCE:
- Master config in config/governance/hooks/
- Severity score: 80/100 (HIGH)
- All changes require approval

FOCUS: Secure and flexible configuration

VALIDATION:
- Configuration inheritance tests
- Secret encryption tests
- Rollback functionality tests
- Template rendering tests
```

## Prompt 3.4: Runtime Plugin Switching

```
You are a High Availability Systems Engineer specializing in zero-downtime operations.

TASK: Enable runtime switching of validator plugins

REQUIREMENTS:
1. Create RuntimePluginSwitcher class
2. Atomic plugin replacement
3. Graceful traffic draining
4. State migration between plugins
5. A/B testing capability
6. Canary deployment support
7. Automatic rollback on errors

CONSTRAINTS:
- Zero validation loss during switch
- Maximum 1 second switch time
- Support gradual rollout
- Preserve audit trail

GOVERNANCE:
- Switch policies in config/governance/runtime_switching.yaml
- Severity score: 78/100 (HIGH)
- Require approval for production switches

FOCUS: Safe runtime plugin updates

VALIDATION:
- Switch under load tests
- State migration tests
- Rollback trigger tests
- A/B testing validation
```

## Prompt 3.5: Hook Event System

```
You are an Event-Driven Architecture Expert specializing in real-time systems.

TASK: Implement comprehensive event system for hooks

REQUIREMENTS:
1. Create HookEventEmitter class
2. Before/after/error events
3. Event filtering and routing
4. Event persistence option
5. Webhook integration
6. Event replay capability
7. Dead letter queue

CONSTRAINTS:
- Support 10,000 events/second
- Maximum 1MB event payload
- 7 day event retention
- Guaranteed delivery mode available

GOVERNANCE:
- Event schemas in config/schemas/events/
- Severity score: 75/100 (MEDIUM)
- Log all event failures

FOCUS: Observable and debuggable hook system

VALIDATION:
- Event throughput tests
- Event ordering tests
- Replay functionality tests
- Webhook delivery tests
```
