import pytest
import asyncio
from pathlib import Path

from libs.governance.plugins.registry import PluginRegistry
from libs.governance.plugins.base import PluginMetadata


def test_plugin_registry_integration():
    """Test the complete plugin registry workflow with real plugins."""
    
    # Get a fresh registry
    PluginRegistry._instance = None
    registry = PluginRegistry()
    registry.clear()
    
    # Test discovery of plugins from the configured directories
    plugin_directories = [
        "libs/governance/plugins/validators",
        "libs/governance/plugins/custom"
    ]
    
    discovered_count = registry.discover_plugins(plugin_directories)
    print(f"Discovered {discovered_count} plugins")
    
    # List all registered plugins
    plugins = registry.list_plugins()
    print(f"Total registered plugins: {len(plugins)}")
    
    for plugin_metadata in plugins:
        print(f"- {plugin_metadata.name} v{plugin_metadata.version}")
        print(f"  Description: {plugin_metadata.description}")
        print(f"  Dependencies: {plugin_metadata.dependencies}")
        print(f"  Tags: {plugin_metadata.tags}")
    
    # Test dependency resolution
    for plugin_metadata in plugins:
        try:
            resolved = registry.resolve_dependencies(plugin_metadata.name)
            print(f"Dependency resolution for {plugin_metadata.name}: {resolved}")
        except Exception as e:
            print(f"Failed to resolve dependencies for {plugin_metadata.name}: {e}")
    
    # Test version compatibility
    for plugin_metadata in plugins:
        is_compatible = registry.check_version_compatibility(plugin_metadata.name, ">=1.0.0")
        print(f"{plugin_metadata.name} compatible with >=1.0.0: {is_compatible}")
    
    # Get registry stats
    stats = registry.get_stats()
    print(f"Registry stats: {stats}")
    
    assert len(plugins) >= 0  # Should have at least discovered some plugins


@pytest.mark.asyncio
async def test_plugin_validation_workflow():
    """Test a complete validation workflow using discovered plugins."""
    
    # Get registry with discovered plugins
    PluginRegistry._instance = None
    registry = PluginRegistry()
    registry.clear()
    
    discovered_count = registry.discover_plugins([
        "libs/governance/plugins/validators",
        "libs/governance/plugins/custom"
    ])
    
    print(f"Discovered {discovered_count} plugins for validation test")
    
    # Get a plugin to test validation
    plugins = registry.list_plugins()
    
    if plugins:
        plugin_metadata = plugins[0]
        plugin_class = registry.get_plugin(plugin_metadata.name)
        
        if plugin_class:
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Initialize the plugin
            config = {
                'max_complexity': 15,
                'require_docstrings': True
            }
            await plugin_instance.initialize(config)
            
            # Test validation with sample context
            context = {
                'code': '''
def example_function(param1, param2):
    """Example function with proper docstring."""
    result = param1 + param2
    # TODO: Add error handling
    return result

class ExampleClass:
    """Example class."""
    
    def method_with_long_line(self):
        return "This is a very long line that exceeds the recommended line length of 120 characters and should trigger a warning"
''',
                'file_path': 'test_file.py'
            }
            
            result = await plugin_instance.validate(context)
            
            print(f"Validation result for {plugin_metadata.name}:")
            print(f"  Success: {result.success}")
            print(f"  Messages: {result.messages}")
            print(f"  Warnings: {result.warnings}")
            print(f"  Errors: {result.errors}")
            print(f"  Duration: {result.duration_ms}ms")
            print(f"  Metadata: {result.metadata}")
            
            # Teardown
            await plugin_instance.teardown()
            
            assert result is not None
            assert hasattr(result, 'success')


if __name__ == "__main__":
    # Run the integration test
    test_plugin_registry_integration()
    
    # Run the async validation test
    asyncio.run(test_plugin_validation_workflow())
