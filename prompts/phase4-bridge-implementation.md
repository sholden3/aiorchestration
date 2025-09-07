# Phase 4: Bridge Implementation - GitHub Copilot Prompts

## Prompt 4.1: Claude Code to Git Hook Bridge

```
You are a Systems Integration Architect specializing in heterogeneous system bridging.

TASK: Build bridge between Claude Code native hooks and Git hooks

REQUIREMENTS:
1. Create UniversalHookBridge class
2. Bidirectional communication protocol
3. Hook type translation layer
4. Context normalization
5. Result format conversion
6. Error propagation
7. Performance monitoring

CONSTRAINTS:
- Support all 9 Claude Code hooks
- Support all Git hook types
- Maximum 50ms bridge overhead
- Maintain hook semantics

GOVERNANCE:
- Bridge config in config/governance/bridge.yaml
- Severity score: 88/100 (CRITICAL)
- Full audit trail required

FOCUS: Seamless hook interoperability

VALIDATION:
- Cross-hook communication tests
- Context translation tests
- Error propagation tests
- Performance benchmarks
```

## Prompt 4.2: Unified Validator Interface

```
You are an API Design Expert specializing in abstraction layers.

TASK: Create unified interface for all validator types

REQUIREMENTS:
1. Create UnifiedValidatorInterface class
2. Abstract validator differences
3. Standard input/output formats
4. Metadata enrichment
5. Cross-validator communication
6. Caching layer
7. Metrics collection

CONSTRAINTS:
- Zero breaking changes
- Support async and sync validators
- Language agnostic design
- Extensible for future validators

GOVERNANCE:
- Interface spec in docs/api/unified_validator.md
- Severity score: 85/100 (HIGH)
- Version all interface changes

FOCUS: Single interface for all validation needs

VALIDATION:
- Interface compliance tests
- Cross-validator tests
- Performance tests
- Backward compatibility tests
```

## Prompt 4.3: Cross-Hook Communication

```
You are a Distributed Systems Engineer specializing in inter-process communication.

TASK: Implement communication between different hook types

REQUIREMENTS:
1. Create CrossHookMessenger class
2. Message passing protocol
3. Shared state management
4. Event synchronization
5. Deadlock prevention
6. Message ordering guarantees
7. Failure isolation

CONSTRAINTS:
- Support 100+ concurrent hooks
- Maximum 10ms message latency
- No message loss
- Handle network partitions

GOVERNANCE:
- Protocol spec in docs/protocols/cross_hook.md
- Severity score: 82/100 (HIGH)
- Monitor all communications

FOCUS: Reliable inter-hook coordination

VALIDATION:
- Concurrent messaging tests
- Deadlock detection tests
- Message ordering tests
- Partition tolerance tests
```

## Prompt 4.4: State Persistence Layer

```
You are a Database Architect specializing in high-performance storage systems.

TASK: Implement state persistence for hook and validator data

REQUIREMENTS:
1. Create StatePersistenceManager class
2. Multiple backend support (Redis, SQLite, PostgreSQL)
3. Automatic schema migration
4. Transaction support
5. Point-in-time recovery
6. Data compression
7. Encryption at rest

CONSTRAINTS:
- Support 10,000 writes/second
- Maximum 5ms write latency
- 99.99% durability
- 30 day retention minimum

GOVERNANCE:
- Storage config in config/governance/persistence.yaml
- Severity score: 80/100 (HIGH)
- Encrypt all sensitive data

FOCUS: Reliable and performant state storage

VALIDATION:
- Write throughput tests
- Transaction tests
- Recovery tests
- Encryption validation
```

## Prompt 4.5: Hook Bridge Monitoring

```
You are a Site Reliability Engineer specializing in observability.

TASK: Create comprehensive monitoring for hook bridge system

REQUIREMENTS:
1. Create BridgeMonitor class
2. Real-time metrics collection
3. Performance profiling
4. Error tracking
5. SLA monitoring
6. Alerting system
7. Dashboard generation

CONSTRAINTS:
- < 1% performance overhead
- 1 second metric granularity
- 90 day metric retention
- Support Prometheus/Grafana

GOVERNANCE:
- Monitoring config in config/governance/monitoring.yaml
- Severity score: 78/100 (HIGH)
- Alert on SLA violations

FOCUS: Complete system observability

VALIDATION:
- Metric accuracy tests
- Alert trigger tests
- Dashboard render tests
- Performance impact tests
```
