# Configuration Schemas Directory

## Overview
This directory contains JSON Schema definitions for validating configuration files throughout the governance system.

## Contents

### Schema Files
- `plugin.json` - Schema for plugin configuration validation
- `validators_schema.json` - Schema for validators.yaml configuration (to be created)

### Examples Directory
- `examples/` - Sample configuration files demonstrating proper schema usage
  - `plugin_base.yaml` - Basic plugin configuration example
  - `plugin_development.yaml` - Development environment configuration
  - `plugin_production.json` - Production configuration example
  - `complex_merge.yaml` - Advanced configuration merging example

## Schema Structure

### Plugin Schema (`plugin.json`)
Defines the structure for individual plugin configurations:
- Required fields: plugin_name, version, enabled
- Configuration section with plugin-specific settings
- Dependencies and security configurations

### Validators Schema (planned)
Will define the structure for the main validators.yaml file:
- Global settings
- Individual validator configurations
- Hook mappings
- Environment-specific overrides

## Usage

### Validation Example
```python
from libs.governance.plugins.config import ConfigurationLoader

loader = ConfigurationLoader(schema_dir="config/schemas")
config = loader.load_config("config/governance/validators.yaml")
report = loader.validate_config(config, schema_name="validators_schema")
```

### Schema Development
1. Define schema in JSON format
2. Add examples in the examples/ directory
3. Test with the ConfigurationLoader
4. Document required and optional fields

## Standards

### Schema Requirements
- Use JSON Schema Draft 7
- Include descriptions for all fields
- Define default values where appropriate
- Use strict validation (additionalProperties: false)

### Example Requirements
- Cover all major use cases
- Include comments explaining non-obvious configurations
- Test against the schema before committing

## Testing
All schemas must:
- Have at least one valid example
- Have at least one invalid example (for testing validation)
- Be tested with the ConfigurationLoader

## Related Files
- `libs/governance/plugins/config.py` - ConfigurationLoader implementation
- `config/governance/validators.yaml` - Main validator configuration
- `config/governance/plugin_registry.yaml` - Plugin discovery configuration