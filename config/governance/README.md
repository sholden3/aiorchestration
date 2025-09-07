# Governance Configuration Directory

## Purpose
Centralized configuration for all governance and plugin system components.

## Contents
- **validators.yaml** - Validator plugin configuration and mappings
- **plugin_registry.yaml** - Plugin registry settings
- **lifecycle.yaml** - Plugin lifecycle configuration
- **personas.yaml** - AI persona definitions
- **rules.yaml** - Governance rules and policies
- **standards.yaml** - Documentation and code standards

## Dependencies
- YAML parser for configuration loading
- libs/governance/plugins/config.py for hot-reload support

## Maintenance
Configuration files are validated on load and support hot-reload for development.