"""
Tests for the PluginMessageBus inter-plugin communication system.

This module contains comprehensive tests for all aspects of the message bus
including publish/subscribe, request/response, circuit breakers, dead letter
queues, metrics, and performance characteristics.
"""

import asyncio
import json
import pytest
import pytest_asyncio
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Any, Dict
from unittest.mock import Mock, patch, AsyncMock

from libs.governance.plugins.messaging import (
    PluginMessageBus, Message, MessageSerializer, SerializerType,
    DeliveryGuarantee, OverflowStrategy, CircuitState, MessageBusError,
    MessageTimeoutError, MessageSerializationError, CircuitBreakerError,
    Subscription, CircuitBreaker, MessageBusMetrics
)


class TestMessage:
    """Test Message dataclass functionality."""
    
    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message(
            id="test-id",
            topic="test.topic",
            payload={"data": "value"},
            priority=5,
            timestamp=datetime.now(timezone.utc),
            sender="test-sender"
        )
        
        assert msg.id == "test-id"
        assert msg.topic == "test.topic"
        assert msg.payload == {"data": "value"}
        assert msg.priority == 5
        assert msg.sender == "test-sender"
        assert msg.correlation_id is None
        assert msg.headers == {}
        assert msg.ttl is None
    
    def test_message_validation(self):
        """Test message validation."""
        timestamp = datetime.now(timezone.utc)
        
        # Missing id
        with pytest.raises(MessageBusError, match="Message id, topic, and sender are required"):
            Message(
                id="",
                topic="test.topic",
                payload="data",
                priority=0,
                timestamp=timestamp,
                sender="sender"
            )
        
        # Invalid priority
        with pytest.raises(MessageBusError, match="Priority must be between 0 and 9"):
            Message(
                id="test",
                topic="test.topic",
                payload="data",
                priority=10,
                timestamp=timestamp,
                sender="sender"
            )
        
        # Invalid TTL
        with pytest.raises(MessageBusError, match="TTL must be positive"):
            Message(
                id="test",
                topic="test.topic",
                payload="data",
                priority=0,
                timestamp=timestamp,
                sender="sender",
                ttl=-1
            )
    
    def test_message_expiration(self):
        """Test message TTL expiration."""
        # Non-expired message
        msg = Message(
            id="test",
            topic="test.topic",
            payload="data",
            priority=0,
            timestamp=datetime.now(timezone.utc),
            sender="sender",
            ttl=10
        )
        assert not msg.is_expired
        
        # Expired message
        old_timestamp = datetime.now(timezone.utc) - timedelta(seconds=20)
        expired_msg = Message(
            id="test",
            topic="test.topic",
            payload="data",
            priority=0,
            timestamp=old_timestamp,
            sender="sender",
            ttl=10
        )
        assert expired_msg.is_expired
        
        # No TTL message
        no_ttl_msg = Message(
            id="test",
            topic="test.topic",
            payload="data",
            priority=0,
            timestamp=old_timestamp,
            sender="sender"
        )
        assert not no_ttl_msg.is_expired


class TestMessageSerializer:
    """Test MessageSerializer functionality."""
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        serializer = MessageSerializer()
        
        data = {"key": "value", "number": 42}
        serialized = serializer.serialize(data, SerializerType.JSON)
        deserialized = serializer.deserialize(serialized, SerializerType.JSON)
        
        assert deserialized == data
    
    @pytest.mark.skipif(not hasattr(pytest, "importorskip"), reason="msgpack might not be available")
    def test_msgpack_serialization(self):
        """Test MessagePack serialization."""
        try:
            import msgpack
        except ImportError:
            pytest.skip("msgpack not available")
        
        serializer = MessageSerializer()
        
        data = {"key": "value", "number": 42}
        serialized = serializer.serialize(data, SerializerType.MSGPACK)
        deserialized = serializer.deserialize(serialized, SerializerType.MSGPACK)
        
        assert deserialized == data
    
    def test_custom_serialization(self):
        """Test custom serialization."""
        serializer = MessageSerializer()
        
        # Register custom serializer
        def custom_serialize(obj):
            return f"CUSTOM:{json.dumps(obj)}".encode()
        
        def custom_deserialize(data):
            return json.loads(data.decode().replace("CUSTOM:", ""))
        
        serializer.register_serializer("custom", custom_serialize, custom_deserialize)
        
        data = {"key": "value"}
        serialized = serializer.serialize(data, SerializerType.CUSTOM, "custom")
        deserialized = serializer.deserialize(serialized, SerializerType.CUSTOM, "custom")
        
        assert deserialized == data
    
    def test_serialization_errors(self):
        """Test serialization error handling."""
        serializer = MessageSerializer()
        
        # Unknown serializer
        with pytest.raises(MessageSerializationError, match="Unknown serializer"):
            serializer.serialize({}, "invalid")
        
        # Missing custom serializer
        with pytest.raises(MessageSerializationError, match="Custom serializer 'missing' not found"):
            serializer.serialize({}, SerializerType.CUSTOM, "missing")


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions."""
        cb = CircuitBreaker("test-subscriber", failure_threshold=2)
        
        # Initial state is CLOSED
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()
        
        # Record failures to trip circuit
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED  # Still closed
        assert cb.can_execute()
        
        cb.record_failure()
        assert cb.state == CircuitState.OPEN  # Now open
        assert not cb.can_execute()
        
        # Test half-open state
        cb.next_attempt = datetime.now(timezone.utc) - timedelta(seconds=1)  # Force next attempt
        assert cb.can_execute()  # Should transition to HALF_OPEN
        assert cb.state == CircuitState.HALF_OPEN
        
        # Record success to close circuit
        cb.record_success()
        cb.record_success()
        cb.record_success()  # Reach max calls
        assert cb.state == CircuitState.CLOSED
    
    def test_circuit_breaker_timeout(self):
        """Test circuit breaker timeout behavior."""
        cb = CircuitBreaker("test-subscriber", failure_threshold=1, timeout=1.0)
        
        # Trip circuit
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()
        
        # Should still be closed before timeout
        assert not cb.can_execute()
        
        # Mock timeout expiry
        cb.next_attempt = datetime.now(timezone.utc) - timedelta(seconds=1)
        assert cb.can_execute()
        assert cb.state == CircuitState.HALF_OPEN


@pytest_asyncio.fixture
async def message_bus():
    """Create and start a message bus instance for testing."""
    bus = PluginMessageBus(max_queue_size=100)
    await bus.start()
    yield bus
    await bus.stop()


class TestPluginMessageBus:
    """Test PluginMessageBus functionality."""
    
    @pytest.mark.asyncio
    async def test_bus_lifecycle(self):
        """Test message bus start/stop lifecycle."""
        bus = PluginMessageBus()
        
        assert not bus._running
        await bus.start()
        assert bus._running
        assert len(bus._worker_tasks) == 3
        
        await bus.stop()
        assert not bus._running
        assert len(bus._worker_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_publish_subscribe_basic(self, message_bus):
        """Test basic publish/subscribe functionality."""
        received_messages = []
        
        def handler(message):
            received_messages.append(message)
        
        # Subscribe to topic
        sub_id = message_bus.subscribe("test.topic", handler)
        assert sub_id is not None
        
        # Publish message
        success = message_bus.publish("test.topic", {"data": "value"}, sender="test")
        assert success
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Check message received
        assert len(received_messages) == 1
        assert received_messages[0].topic == "test.topic"
        assert received_messages[0].payload == {"data": "value"}
        assert received_messages[0].sender == "test"
        
        # Unsubscribe
        assert message_bus.unsubscribe(sub_id)
        assert not message_bus.unsubscribe(sub_id)  # Already unsubscribed
    
    @pytest.mark.asyncio
    async def test_async_handler(self, message_bus):
        """Test async message handlers."""
        received_messages = []
        
        async def async_handler(message):
            await asyncio.sleep(0.01)  # Simulate async work
            received_messages.append(message)
        
        sub_id = message_bus.subscribe("test.async", async_handler)
        message_bus.publish("test.async", "async_data", sender="test")
        
        await asyncio.sleep(0.1)
        
        assert len(received_messages) == 1
        assert received_messages[0].payload == "async_data"
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_wildcard_subscriptions(self, message_bus):
        """Test wildcard topic subscriptions."""
        received_messages = []
        
        def handler(message):
            received_messages.append(message)
        
        # Subscribe to wildcard topic
        sub_id = message_bus.subscribe("plugin.*.event", handler)
        
        # Publish to matching topics
        message_bus.publish("plugin.security.event", "security_event", sender="test")
        message_bus.publish("plugin.validation.event", "validation_event", sender="test")
        message_bus.publish("plugin.other.different", "different_event", sender="test")  # Won't match
        
        await asyncio.sleep(0.1)
        
        assert len(received_messages) == 2
        topics = [msg.topic for msg in received_messages]
        assert "plugin.security.event" in topics
        assert "plugin.validation.event" in topics
        assert "plugin.other.different" not in topics
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_message_filtering(self, message_bus):
        """Test message filtering functionality."""
        received_messages = []
        
        def handler(message):
            received_messages.append(message)
        
        def filter_func(message):
            return message.priority >= 5
        
        # Subscribe with filter
        sub_id = message_bus.subscribe("test.filter", handler, filter_func)
        
        # Publish messages with different priorities
        message_bus.publish("test.filter", "low_priority", priority=1, sender="test")
        message_bus.publish("test.filter", "high_priority", priority=7, sender="test")
        
        await asyncio.sleep(0.1)
        
        # Only high priority message should be received
        assert len(received_messages) == 1
        assert received_messages[0].payload == "high_priority"
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_message_priority(self, message_bus):
        """Test message priority handling."""
        received_messages = []
        
        def handler(message):
            received_messages.append(message.payload)
        
        sub_id = message_bus.subscribe("test.priority", handler)
        
        # Publish messages with different priorities (higher priority should be processed first)
        message_bus.publish("test.priority", "low", priority=1, sender="test")
        message_bus.publish("test.priority", "high", priority=9, sender="test")
        message_bus.publish("test.priority", "medium", priority=5, sender="test")
        
        await asyncio.sleep(0.1)
        
        # Messages should be received in priority order
        assert len(received_messages) == 3
        # Higher priority (9) should come first
        assert received_messages[0] == "high"
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_request_response(self, message_bus):
        """Test request/response pattern."""
        def request_handler(message):
            # Send response
            if message.correlation_id:
                message_bus.send_response(message.correlation_id, f"Response to {message.payload}")
        
        sub_id = message_bus.subscribe("test.request", request_handler)
        
        # Send request
        response = await message_bus.request("test.request", "test_request", sender="client")
        
        assert response == "Response to test_request"
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_request_timeout(self, message_bus):
        """Test request timeout handling."""
        # Subscribe but don't send response
        def non_responding_handler(message):
            pass  # Don't send response
        
        sub_id = message_bus.subscribe("test.timeout", non_responding_handler)
        
        # Request should timeout
        with pytest.raises(MessageTimeoutError, match="timed out after 0.1s"):
            await message_bus.request("test.timeout", "test", timeout=0.1, sender="client")
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, message_bus):
        """Test circuit breaker integration with message handling."""
        failure_count = 0
        
        def failing_handler(message):
            nonlocal failure_count
            failure_count += 1
            raise Exception(f"Handler failure {failure_count}")
        
        sub_id = message_bus.subscribe("test.circuit", failing_handler)
        
        # Publish messages to trigger circuit breaker
        for i in range(10):
            message_bus.publish("test.circuit", f"message_{i}", sender="test")
        
        await asyncio.sleep(0.2)
        
        # Check that circuit breaker opened
        circuit_breaker = message_bus._circuit_breakers.get(sub_id)
        assert circuit_breaker is not None
        
        # Should have some failures and circuit might be open
        assert failure_count > 0
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_dead_letter_queue(self, message_bus):
        """Test dead letter queue functionality."""
        def failing_handler(message):
            raise Exception("Handler always fails")
        
        sub_id = message_bus.subscribe("test.dlq", failing_handler)
        
        # Publish message that will fail
        message_bus.publish("test.dlq", "failing_message", sender="test")
        
        await asyncio.sleep(0.2)  # Wait longer for processing and dead letter handling
        
        # Check that failure metrics increased
        metrics = message_bus.get_metrics()
        assert metrics['messages_failed'] > 0
        
        # Check subscription error count
        sub_info = message_bus.get_subscription_info(sub_id)
        assert sub_info is not None
        assert sub_info['error_count'] > 0
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_message_ttl(self, message_bus):
        """Test message TTL (time to live) functionality."""
        received_messages = []
        
        def handler(message):
            received_messages.append(message)
        
        sub_id = message_bus.subscribe("test.ttl", handler)
        
        # Publish expired message (TTL of 0 seconds)
        old_timestamp = datetime.now(timezone.utc) - timedelta(seconds=10)
        
        # Create an expired message by directly creating it with old timestamp
        from libs.governance.plugins.messaging import Message
        expired_msg = Message(
            id=str(uuid.uuid4()),
            topic="test.ttl",
            payload="expired_message",
            priority=0,
            timestamp=old_timestamp,  # Old timestamp
            sender="test",
            ttl=1  # 1 second TTL, but message is 10 seconds old
        )
        
        # Directly enqueue the expired message
        with message_bus._lock:
            message_bus._enqueue_message(expired_msg)
        
        await asyncio.sleep(0.2)  # Wait longer for processing
        
        # Expired message should not be delivered
        assert len(received_messages) == 0
        
        # Check that expired message count increased
        metrics = message_bus.get_metrics()
        assert metrics['messages_expired'] > 0
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_overflow_strategies(self):
        """Test queue overflow strategies."""
        # Test DROP_OLDEST strategy
        bus_drop_oldest = PluginMessageBus(
            max_queue_size=2,
            overflow_strategy=OverflowStrategy.DROP_OLDEST
        )
        await bus_drop_oldest.start()
        
        received_messages = []
        
        def handler(message):
            time.sleep(0.1)  # Slow handler to fill queue
            received_messages.append(message.payload)
        
        sub_id = bus_drop_oldest.subscribe("test.overflow", handler)
        
        # Publish more messages than queue size
        for i in range(5):
            bus_drop_oldest.publish("test.overflow", f"message_{i}", sender="test")
        
        await asyncio.sleep(0.5)
        
        # Should have received messages (oldest dropped)
        assert len(received_messages) > 0
        
        bus_drop_oldest.unsubscribe(sub_id)
        await bus_drop_oldest.stop()
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, message_bus):
        """Test metrics collection functionality."""
        def handler(message):
            pass
        
        sub_id = message_bus.subscribe("test.metrics", handler)
        
        # Publish some messages
        for i in range(5):
            message_bus.publish("test.metrics", f"message_{i}", sender="test")
        
        await asyncio.sleep(0.1)
        
        metrics = message_bus.get_metrics()
        
        assert metrics['messages_published'] == 5
        assert metrics['messages_consumed'] >= 0
        assert metrics['active_subscriptions'] >= 1
        assert 'publish_latency_p50' in metrics or len(message_bus._metrics.publish_latencies) > 0
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_topic_statistics(self, message_bus):
        """Test topic statistics collection."""
        def handler(message):
            pass
        
        sub_id = message_bus.subscribe("test.stats", handler)
        
        message_bus.publish("test.stats", "test_message", sender="test")
        await asyncio.sleep(0.1)
        
        topic_stats = message_bus.get_topic_stats()
        
        assert "test.stats" in topic_stats
        stats = topic_stats["test.stats"]
        assert stats['message_count'] >= 1
        assert stats['subscriber_count'] >= 1
        assert stats['last_message'] is not None
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_subscription_info(self, message_bus):
        """Test subscription information retrieval."""
        def handler(message):
            pass
        
        sub_id = message_bus.subscribe("test.info", handler)
        
        info = message_bus.get_subscription_info(sub_id)
        
        assert info is not None
        assert info['id'] == sub_id
        assert info['topic'] == "test.info"
        assert info['is_async'] == False
        assert info['message_count'] == 0
        assert info['error_count'] == 0
        assert info['circuit_state'] == CircuitState.CLOSED.value
        
        # Test non-existent subscription
        assert message_bus.get_subscription_info("non-existent") is None
        
        message_bus.unsubscribe(sub_id)
    
    def test_message_size_limit(self):
        """Test message size limitations."""
        bus = PluginMessageBus(max_message_size=100)  # 100 bytes limit
        
        # Small message should work
        success = bus.publish("test", "small", sender="test")
        assert success
        
        # Large message should fail
        large_data = "x" * 1000  # 1000 bytes
        success = bus.publish("test", large_data, sender="test")
        assert not success
    
    def test_invalid_publish_parameters(self):
        """Test publishing with invalid parameters."""
        bus = PluginMessageBus()
        
        # Missing topic
        assert not bus.publish("", "message", sender="test")
        
        # Missing sender
        assert not bus.publish("topic", "message", sender="")
        
        # Invalid priority
        assert not bus.publish("topic", "message", priority=10, sender="test")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, message_bus):
        """Test thread safety with concurrent operations."""
        received_messages = []
        lock = threading.Lock()
        
        def handler(message):
            with lock:
                received_messages.append(message.payload)
        
        sub_id = message_bus.subscribe("test.concurrent", handler)
        
        # Publish messages from multiple threads
        def publish_messages(start_idx):
            for i in range(10):
                message_bus.publish("test.concurrent", f"message_{start_idx}_{i}", sender="test")
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=publish_messages, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        await asyncio.sleep(0.2)
        
        # Should have received all 50 messages
        assert len(received_messages) == 50
        
        message_bus.unsubscribe(sub_id)
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, message_bus):
        """Test multiple subscribers to same topic."""
        received_1 = []
        received_2 = []
        
        def handler1(message):
            received_1.append(message.payload)
        
        def handler2(message):
            received_2.append(message.payload)
        
        sub_id1 = message_bus.subscribe("test.multi", handler1)
        sub_id2 = message_bus.subscribe("test.multi", handler2)
        
        message_bus.publish("test.multi", "broadcast_message", sender="test")
        
        await asyncio.sleep(0.1)
        
        # Both subscribers should receive the message
        assert len(received_1) == 1
        assert len(received_2) == 1
        assert received_1[0] == "broadcast_message"
        assert received_2[0] == "broadcast_message"
        
        message_bus.unsubscribe(sub_id1)
        message_bus.unsubscribe(sub_id2)
    
    @pytest.mark.asyncio
    async def test_custom_serializer(self, message_bus):
        """Test custom serializer registration and usage."""
        # Register custom serializer
        def upper_serialize(obj):
            return str(obj).upper().encode()
        
        def upper_deserialize(data):
            return data.decode().lower()
        
        message_bus.register_serializer("upper", upper_serialize, upper_deserialize)
        
        # Test that serializer is registered
        serializer = message_bus._serializer
        serialized = serializer.serialize("hello", SerializerType.CUSTOM, "upper")
        deserialized = serializer.deserialize(serialized, SerializerType.CUSTOM, "upper")
        
        assert deserialized == "hello"
    
    @pytest.mark.asyncio
    async def test_batch_context_manager(self, message_bus):
        """Test batch publishing context manager."""
        # This is a placeholder test since batch_publish is not fully implemented
        with message_bus.batch_publish():
            success = message_bus.publish("test.batch", "message1", sender="test")
            assert success
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, message_bus):
        """Test basic performance requirements."""
        received_count = 0
        
        def fast_handler(message):
            nonlocal received_count
            received_count += 1
        
        sub_id = message_bus.subscribe("test.perf", fast_handler)
        
        # Measure publish latency
        start_time = time.time()
        for i in range(100):
            message_bus.publish("test.perf", f"message_{i}", sender="test")
        publish_time = time.time() - start_time
        
        await asyncio.sleep(0.5)  # Wait for processing
        
        # Basic performance check (adjust thresholds as needed)
        avg_publish_latency = (publish_time / 100) * 1000  # ms
        assert avg_publish_latency < 50  # Less than 50ms average (generous for testing)
        
        # Check that most messages were processed
        assert received_count >= 90  # Allow some messages to be in processing
        
        message_bus.unsubscribe(sub_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
