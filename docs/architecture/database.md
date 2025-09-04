# Database Architecture

**Last Updated:** January 2025  
**Reviewed By:** Dr. Sarah Chen (Senior Backend/Systems Architect), Alex Novak (Senior Electron/Angular Architect)  
**Next Review:** February 2025  

## Overview
The AI Development Assistant uses a dual-database strategy with PostgreSQL as the primary production database and SQLite as a fallback development/mock data source. The architecture implements sophisticated caching layers, circuit breaker patterns, and real-time capabilities through WebSocket broadcasting.

## Technology Stack

### Database Engine
- **Primary Database:** PostgreSQL 14+ (Production)
- **Fallback Database:** SQLite (Development/Testing)
- **Caching Layer:** Two-tier (Hot: 512MB, Warm: 2048MB)
- **Search Engine:** PostgreSQL Full-Text Search
- **Message Queue:** FastAPI WebSocket Broadcasting

### Tools & Libraries
- **ORM:** AsyncPG (PostgreSQL native driver)
- **Migration Tool:** Custom SQL migrations with version control
- **Connection Pooling:** AsyncPG connection pool (2-10 connections)
- **Monitoring:** Circuit breaker pattern with failure tracking

## Database Design

### Schema Design Principles
- **Normalization:** Third Normal Form with selective denormalization for performance
- **Constraints:** Foreign keys, NOT NULL, unique constraints, check constraints
- **Naming Conventions:** Snake_case for tables/columns, descriptive names
- **Data Types:** JSONB for flexible data, UUID for primary keys where applicable

### Table Structure
#### Core Entities
```sql
-- Rules Management
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('CRITICAL', 'ERROR', 'WARNING', 'INFO')),
    enforcement VARCHAR(20) CHECK (enforcement IN ('mandatory', 'recommended', 'optional')),
    examples JSONB DEFAULT '[]',
    anti_patterns JSONB DEFAULT '[]',
    violations_consequence TEXT,
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- Best Practices
CREATE TABLE practices (
    practice_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    benefits JSONB DEFAULT '[]',
    implementation_guide TEXT,
    anti_patterns JSONB DEFAULT '[]',
    references JSONB DEFAULT '[]',
    examples JSONB DEFAULT '[]',
    effectiveness_score DECIMAL(3,2),
    adoption_rate DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_required BOOLEAN DEFAULT FALSE
);

-- Templates
CREATE TABLE templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    template_content TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    tags JSONB DEFAULT '[]',
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Data Relationships
- **One-to-One:** Each rule has one category association
- **One-to-Many:** Templates can have multiple variable definitions, rules can have multiple violations
- **Many-to-Many:** Rules and practices can share categories, templates can use multiple tags

## Indexing Strategy

### Primary Indexes
- **Primary Keys:** UUID or VARCHAR with meaningful identifiers (rule_id, practice_id, template_id)
- **Foreign Keys:** Indexed for join performance
- **Unique Constraints:** On business identifiers and email fields

### Performance Indexes
```sql
-- Category-based queries (most common access pattern)
CREATE INDEX idx_rules_category ON rules(category) WHERE active = TRUE;
CREATE INDEX idx_practices_category ON practices(category) WHERE is_active = TRUE;
CREATE INDEX idx_templates_category ON templates(category) WHERE is_active = TRUE;

-- Severity-based filtering for rules
CREATE INDEX idx_rules_severity ON rules(severity, created_at DESC) WHERE active = TRUE;

-- Full-text search on titles and descriptions
CREATE INDEX idx_rules_search ON rules USING gin(to_tsvector('english', title || ' ' || description));
CREATE INDEX idx_practices_search ON practices USING gin(to_tsvector('english', title || ' ' || description));

-- JSONB search indexes for flexible querying
CREATE INDEX idx_rules_examples ON rules USING gin(examples);
CREATE INDEX idx_practices_benefits ON practices USING gin(benefits);
```

### Index Maintenance
- **Monitoring:** Query performance tracked via circuit breaker metrics
- **Cleanup:** Unused indexes identified through pg_stat_user_indexes
- **Optimization:** Monthly ANALYZE and VACUUM operations scheduled

## Performance Optimization

### Query Performance
- **Query Analysis:** EXPLAIN ANALYZE used for all critical queries
- **Query Optimization:** Prepared statements, proper join strategies, limited result sets
- **Connection Pooling:** 2-10 connections based on load, command timeout 60 seconds
- **Statement Timeout:** 10-second default timeout to prevent hanging queries

### Caching Strategy
- **Application Cache:** Two-tier system (hot: 512MB, warm: 2GB) with 90% hit rate target
- **Query Cache:** PostgreSQL shared_buffers optimized for working set
- **Connection Cache:** Connection pooling with 5-minute idle timeout

### Database Tuning
```sql
-- PostgreSQL configuration optimizations
shared_buffers = '256MB'
effective_cache_size = '1GB'
work_mem = '8MB'
maintenance_work_mem = '128MB'
max_connections = 100
```

## Data Management

### Backup Strategy
- **Full Backups:** Daily at 2 AM UTC
- **Incremental Backups:** Continuous WAL archiving
- **Point-in-Time Recovery:** 30-day retention period
- **Backup Testing:** Weekly restore validation to test environment

### Data Retention
- **Soft Deletes:** Boolean flags (active, is_active) for logical deletion
- **Hard Deletes:** Manual process for compliance requirements
- **Archive Strategy:** Move inactive records to archive tables after 2 years

### Data Migration
- **Version Control:** SQL migration files in `database/migrations/`
- **Rollback Plan:** Each migration includes rollback script
- **Testing:** All migrations tested on staging environment first

## Security Architecture

### Access Control
- **Role-Based Access:** Application-level RBAC, single database user for application
- **Connection Security:** SSL/TLS required for all connections
- **Authentication:** Database password authentication, planned migration to certificate-based
- **Network Security:** Firewall rules restrict database access to application servers only

### Data Protection
- **Encryption at Rest:** PostgreSQL transparent data encryption planned
- **Encryption in Transit:** SSL/TLS with certificate validation
- **PII Handling:** No PII stored in current schema, JSONB fields sanitized
- **Audit Logging:** Database query logging enabled for security events

### Compliance
- **GDPR:** Right to deletion implemented via soft deletes and archive strategy
- **SOC 2:** Access logging and monitoring in place
- **Data Classification:** All data classified as internal/confidential

## Scalability Strategy

### Vertical Scaling
- **Hardware Scaling:** Monitor CPU, memory, and I/O; scale instance size as needed
- **Performance Monitoring:** Circuit breaker tracks response times and failure rates
- **Capacity Planning:** Monthly capacity reviews based on growth trends

### Horizontal Scaling
- **Read Replicas:** Planned for Phase 2 when read load increases
- **Partitioning:** Table partitioning by category for large tables (future)
- **Sharding:** Not needed at current scale, reassess at 1M+ records

### High Availability
- **Primary/Replica Setup:** Single instance for development, HA planned for production
- **Failover Strategy:** Automatic failover to SQLite mock data during outages
- **Load Balancing:** Application-level load balancing between read replicas (future)

## Monitoring & Observability

### Database Metrics
- **Performance Metrics:** Query response time, throughput, cache hit ratios
- **Resource Metrics:** CPU usage, memory consumption, disk I/O, connection count
- **Error Metrics:** Connection failures, query timeouts, circuit breaker state

### Monitoring Tools
- **Native Tools:** pg_stat_statements, pg_stat_user_indexes, PostgreSQL logs
- **External Tools:** Circuit breaker service metrics, application-level monitoring
- **Alerting:** Circuit breaker opens on 3 consecutive failures, 30-second recovery timeout

### Health Checks
- **Connection Health:** Connection pool status monitored continuously
- **Query Performance:** Slow query detection via circuit breaker pattern
- **Replication Lag:** N/A for single instance, planned for HA setup

## Data Contracts

### Schema Versioning
- **Migration Files:** Sequential numbering (001_initial.sql, 002_add_templates.sql)
- **Schema Registry:** Documentation maintained alongside migration files
- **Breaking Changes:** Backward compatibility maintained for 2 versions

### API Integration
- **Data Models:** Pydantic models for validation and serialization
- **Validation Rules:** Database constraints enforced at application layer
- **Error Handling:** Graceful fallback to mock data on database failures

## Development Workflow

### Database Changes
- **Local Development:** Docker Compose for local PostgreSQL, SQLite fallback
- **Schema Changes:** All changes via migration files, no direct DDL
- **Code Review:** Database changes require senior architect approval
- **Testing:** Unit tests with in-memory SQLite, integration tests with test database

### Data Seeding
- **Development Data:** Seed scripts for common scenarios and testing
- **Staging Data:** Sanitized production data subset for realistic testing
- **Test Data:** Factory pattern for generating test data in automated tests

## Disaster Recovery

### Backup Recovery
- **Recovery Time Objective (RTO):** 4 hours for full system recovery
- **Recovery Point Objective (RPO):** 15 minutes maximum data loss
- **Backup Verification:** Automated restore testing in isolated environment

### Failover Process
- **Automated Failover:** Circuit breaker automatically switches to mock data mode
- **Manual Procedures:** Database restoration procedures documented in runbooks
- **Communication Plan:** Status dashboard shows circuit breaker state to users

## Environment Strategy

### Development
- **Local Database:** Docker PostgreSQL or SQLite for lightweight development
- **Test Data:** Comprehensive seed data covering all use cases
- **Migration Testing:** All migrations tested locally before deployment

### Staging
- **Production Mirror:** Same PostgreSQL version and configuration as production
- **Data Refresh:** Weekly refresh from production with PII scrubbing
- **Performance Testing:** Load testing validates query performance under stress

### Production
- **High Availability:** Single instance with planned HA upgrade
- **Monitoring:** Comprehensive monitoring with circuit breaker protection
- **Maintenance Windows:** Monthly maintenance window for updates and optimization

## Future Considerations

### Planned Improvements
- **Performance Optimizations:** Query optimization based on usage patterns
- **Scaling Preparation:** Read replicas and connection pooling enhancements
- **Technology Upgrades:** PostgreSQL 15+ features, advanced indexing strategies

### Scalability Roadmap
- **Read Replicas:** Phase 2 implementation for read-heavy workloads
- **Partitioning:** Table partitioning when individual tables exceed 10M records
- **Microservices Data:** Event sourcing and CQRS patterns for complex domains

---

## Change Log
| Date | Change | Author | Impact |
|------|--------|--------|--------|
| 2025-01-27 | Initial architecture documentation | Dr. Sarah Chen | Complete database strategy defined |
| 2025-01-27 | Circuit breaker pattern implementation | Dr. Sarah Chen | High availability and resilience |
| 2025-01-27 | Two-tier caching strategy | Dr. Sarah Chen | Performance optimization |

## References
- [Backend Architecture](./backend.md)
- [API Contracts](./api-contracts.md)
- [Security Architecture](./security.md)
- [System Configuration](../../ai-assistant/backend/config.py)
- [Database Service Implementation](../../ai-assistant/backend/database_service.py)