# Examples Directory

## Overview
This directory contains example implementations and usage demonstrations for the validator plugin architecture.

## Contents

### Plugin Examples
- `messaging_example.py` - Demonstrates usage of the PluginMessageBus for inter-plugin communication

### Future Examples (To Be Added)
- `custom_validator_plugin.py` - How to create a custom validator plugin
- `plugin_integration.py` - Integrating plugins with Claude Code hooks
- `configuration_hot_reload.py` - Demonstrating configuration hot-reload
- `plugin_lifecycle.py` - Managing plugin lifecycle states

## Usage

### Running Examples
```bash
# Run the messaging example
python examples/messaging_example.py

# Run with specific configuration
python examples/messaging_example.py --config config/governance/validators.yaml
```

### Creating New Examples
1. Create a standalone Python script
2. Import necessary components from `libs.governance.plugins`
3. Add comprehensive comments explaining the functionality
4. Include error handling and logging
5. Add a main guard for direct execution

## Example Structure

### Standard Template
```python
#!/usr/bin/env python
"""
Example: [Feature Name]
Description: [What this example demonstrates]
Author: [Your Name]
Date: [Creation Date]
"""

import asyncio
import logging
from libs.governance.plugins import [components]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main example logic"""
    # Implementation here
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## Categories

### Core Features
- Plugin creation and registration
- Configuration management
- Lifecycle management
- Message bus communication

### Integration Examples
- Claude Code hook integration
- Git hook integration
- Database integration
- External tool integration

### Advanced Topics
- Custom serializers
- Performance optimization
- Error recovery patterns
- Testing strategies

## Requirements
- Python 3.10+
- All dependencies from requirements.txt
- Access to libs.governance.plugins module

## Testing
Examples should be:
- Self-contained and runnable
- Include error handling
- Demonstrate best practices
- Include inline documentation

## Contributing
When adding examples:
1. Follow the template structure
2. Include comprehensive comments
3. Test the example independently
4. Update this README with the new example
5. Ensure governance compliance

## Notes
- Examples are meant for learning and demonstration
- Production code should follow more robust patterns
- Always check the latest documentation for API changes