"""
Example usage of the PluginMessageBus for inter-plugin communication.

This example demonstrates how to use the message bus for:
1. Publish/Subscribe patterns
2. Request/Response patterns
3. Message filtering
4. Monitoring and metrics
"""

import asyncio
import logging
from libs.governance.plugins.messaging import PluginMessageBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityPlugin:
    """Example security validation plugin."""
    
    def __init__(self, message_bus: PluginMessageBus):
        self.bus = message_bus
        self.name = "SecurityPlugin"
    
    def start(self):
        """Start the plugin and subscribe to relevant topics."""
        # Subscribe to validation requests
        self.validation_sub_id = self.bus.subscribe(
            "request.security.validate",
            self.handle_validation_request
        )
        
        # Subscribe to system events
        self.system_sub_id = self.bus.subscribe(
            "system.*",  # Wildcard subscription
            self.handle_system_event
        )
        
        logger.info(f"{self.name} started and subscribed to topics")
    
    def stop(self):
        """Stop the plugin and cleanup subscriptions."""
        self.bus.unsubscribe(self.validation_sub_id)
        self.bus.unsubscribe(self.system_sub_id)
        logger.info(f"{self.name} stopped")
    
    def handle_validation_request(self, message):
        """Handle security validation requests."""
        logger.info(f"{self.name} validating: {message.payload}")
        
        # Simulate validation logic
        result = {"valid": True, "issues": []}
        
        # Send response back
        if message.correlation_id:
            self.bus.send_response(message.correlation_id, result)
        
        # Publish validation completed event
        self.bus.publish(
            "plugin.security.validated",
            {"validated": message.payload, "result": result},
            priority=5,
            sender=self.name
        )
    
    def handle_system_event(self, message):
        """Handle system events."""
        logger.info(f"{self.name} received system event: {message.topic}")


class GovernancePlugin:
    """Example governance orchestrator plugin."""
    
    def __init__(self, message_bus: PluginMessageBus):
        self.bus = message_bus
        self.name = "GovernancePlugin"
    
    def start(self):
        """Start the plugin and subscribe to validation results."""
        self.result_sub_id = self.bus.subscribe(
            "plugin.*.validated",  # Listen to all validation results
            self.handle_validation_result,
            filter_func=self.filter_high_priority  # Only high priority messages
        )
        
        logger.info(f"{self.name} started")
    
    def stop(self):
        """Stop the plugin."""
        self.bus.unsubscribe(self.result_sub_id)
        logger.info(f"{self.name} stopped")
    
    def filter_high_priority(self, message):
        """Filter to only receive high priority messages."""
        return message.priority >= 5
    
    def handle_validation_result(self, message):
        """Handle validation results from other plugins."""
        logger.info(f"{self.name} received validation result: {message.payload}")
        
        # Publish governance event
        self.bus.publish(
            "system.governance.decision",
            {"action": "approved", "details": message.payload},
            priority=9,  # High priority
            sender=self.name
        )


async def main():
    """Main example demonstrating message bus usage."""
    # Create and start message bus
    message_bus = PluginMessageBus(
        max_queue_size=1000,
        max_message_size=1024 * 1024  # 1MB
    )
    await message_bus.start()
    
    try:
        # Create plugins
        security_plugin = SecurityPlugin(message_bus)
        governance_plugin = GovernancePlugin(message_bus)
        
        # Start plugins
        security_plugin.start()
        governance_plugin.start()
        
        # Wait for plugins to be ready
        await asyncio.sleep(0.1)
        
        # Demonstrate publish/subscribe
        logger.info("=== Publishing system startup event ===")
        message_bus.publish(
            "system.startup",
            {"timestamp": "2025-09-06T23:00:00Z", "version": "1.0.0"},
            priority=7,
            sender="SystemManager"
        )
        
        await asyncio.sleep(0.1)
        
        # Demonstrate request/response
        logger.info("=== Sending validation request ===")
        try:
            response = await message_bus.request(
                "request.security.validate",
                {"code": "def hello(): pass", "file": "example.py"},
                timeout=2.0,
                sender="Client"
            )
            logger.info(f"Validation response: {response}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
        
        await asyncio.sleep(0.1)
        
        # Show metrics
        logger.info("=== Message Bus Metrics ===")
        metrics = message_bus.get_metrics()
        for key, value in metrics.items():
            logger.info(f"  {key}: {value}")
        
        # Show topic statistics
        logger.info("=== Topic Statistics ===")
        topic_stats = message_bus.get_topic_stats()
        for topic, stats in topic_stats.items():
            logger.info(f"  {topic}: {stats}")
        
        # Wait a bit more to process any remaining messages
        await asyncio.sleep(0.2)
        
        # Stop plugins
        security_plugin.stop()
        governance_plugin.stop()
        
    finally:
        # Stop message bus
        await message_bus.stop()
        logger.info("Example completed")


if __name__ == "__main__":
    asyncio.run(main())
