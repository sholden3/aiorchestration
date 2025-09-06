# Configuration Management

## Overview

Centralized configuration management for the AI Orchestration Platform.

## Structure

```
config/
|-- base/           # Base project configurations
|-- governance/     # Governance rules and standards
|-- backend/        # Backend service configurations
|-- frontend/       # Frontend application settings
|-- deployment/     # Deployment and infrastructure
+-- schemas/        # Validation schemas
```

## Configuration Loading Order

1. Base defaults (config/base/defaults.yaml)
2. Environment-specific overrides
3. Environment variables
4. Runtime parameters

## Environment Variables

See `.env.example` for all available environment variables.

## Validation

All configurations are validated against JSON schemas in `config/schemas/`.

## Best Practices

1. Keep secrets in environment variables only
2. Use YAML for human-readable configs
3. Validate all configs before deployment
4. Document every configuration option
5. Version control non-sensitive configs

## Migration Notes

Configuration consolidated from:
- libs/governance/config.yaml -> config/governance/rules.yaml
- libs/governance/personas.yaml -> config/governance/personas.yaml
- libs/governance/documentation_standards.yaml -> config/governance/standards.yaml
- apps/api/mcp/mcp_config.yaml -> config/backend/backend.yaml
- Various scattered configs -> centralized structure

## Configuration Files

### Governance Configurations
- **config/governance/rules.yaml** - Main governance validation rules
- **config/governance/personas.yaml** - AI persona definitions (12 personas)
- **config/governance/standards.yaml** - Documentation and code standards

### Backend Configurations
- **config/backend/backend.yaml** - Consolidated backend settings including API, database, cache, and MCP

### Frontend Configurations
- To be migrated in next iteration

### Deployment Configurations
- To be migrated in next iteration

---

Generated: 2025-01-10
Part of SDR-001 H3 Configuration Management