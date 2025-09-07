# Configuration Examples

This directory contains example configurations demonstrating the ConfigurationLoader capabilities.

## Files

- `plugin_base.yaml` - Base plugin configuration
- `plugin_development.yaml` - Development environment overrides
- `plugin_production.yaml` - Production environment overrides
- `security_config.json` - Security configuration example
- `complex_merge.yaml` - Complex configuration merge example

## Usage

```python
from libs.governance.plugins.config import ConfigurationLoader, ArrayMergeStrategy

# Initialize loader
loader = ConfigurationLoader(
    schema_dir="config/schemas",
    env_prefix="MY_APP",
    enable_hot_reload=True
)

# Load and merge configurations
base_config = loader.load_config("examples/plugin_base.yaml")
env_config = loader.load_config("examples/plugin_development.yaml")
final_config = loader.merge_configs(base_config, env_config)

# Validate configuration
report = loader.validate_config(final_config, schema_name="plugin")
if not report.valid:
    print("Configuration errors:", report.errors)
```
