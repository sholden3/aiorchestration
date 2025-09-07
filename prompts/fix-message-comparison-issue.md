# GitHub Copilot Prompt: Fix Message Comparison for Priority Queue

## Context
The `PluginMessageBus` uses a priority queue (`heapq`) to handle messages with different priorities. However, the `Message` dataclass doesn't implement comparison methods, causing a TypeError when the heap tries to compare messages with the same priority.

## Current Issue
```
ERROR: '<' not supported between instances of 'Message' and 'Message'
```

This occurs in `libs/governance/plugins/messaging.py` when messages with the same priority need to be ordered in the heap.

## Root Cause
Python's `heapq` module uses tuples like `(priority, message)` for the priority queue. When two items have the same priority, it tries to compare the messages themselves to break the tie, but the `Message` dataclass doesn't support comparison.

## Required Fix
Add comparison methods to the `Message` dataclass in `libs/governance/plugins/messaging.py` (around line 119).

### Option 1: Use total_ordering decorator (Recommended)
```python
from functools import total_ordering

@total_ordering
@dataclass(frozen=True)
class Message:
    """Message format for inter-plugin communication."""
    id: str
    topic: str
    payload: Any
    priority: int
    timestamp: datetime
    sender: str
    correlation_id: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    ttl: Optional[int] = None  # seconds
    
    def __lt__(self, other):
        """Compare messages for priority queue ordering.
        
        Order by:
        1. Priority (lower number = higher priority)
        2. Timestamp (earlier = higher priority)
        3. ID (for stable ordering)
        """
        if not isinstance(other, Message):
            return NotImplemented
        
        # First compare by priority
        if self.priority != other.priority:
            return self.priority < other.priority
        
        # Then by timestamp (earlier messages first)
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        
        # Finally by ID for stable ordering
        return self.id < other.id
    
    def __eq__(self, other):
        """Check message equality based on ID."""
        if not isinstance(other, Message):
            return NotImplemented
        return self.id == other.id
```

### Option 2: Use a wrapper for heap items
```python
# In the PluginMessageBus class, modify how items are added to the heap

# Current (problematic):
heapq.heappush(self._message_queue, (message.priority, message))

# Fixed with wrapper:
@dataclass
class PrioritizedMessage:
    """Wrapper for messages in priority queue."""
    priority: int
    counter: int  # Tie-breaker for same priority
    message: Message
    
    def __lt__(self, other):
        # Compare by priority, then counter (FIFO for same priority)
        return (self.priority, self.counter) < (other.priority, other.counter)

# Usage:
self._counter = 0  # Instance variable
self._counter += 1
heapq.heappush(self._message_queue, 
               PrioritizedMessage(message.priority, self._counter, message))
```

## Governance Requirements
1. **Documentation**: Add docstrings to comparison methods
2. **Type Hints**: Maintain proper type hints
3. **Thread Safety**: Ensure comparison is thread-safe
4. **Performance**: Keep comparison lightweight
5. **Test Coverage**: Update tests to verify comparison logic

## Testing the Fix
After implementing, verify:

```python
# Test that messages can be compared
msg1 = Message(id="1", topic="test", payload="data", priority=1, 
               timestamp=datetime.now(), sender="test")
msg2 = Message(id="2", topic="test", payload="data", priority=2, 
               timestamp=datetime.now(), sender="test")

assert msg1 < msg2  # Higher priority (lower number) comes first

# Test heap operations
import heapq
queue = []
heapq.heappush(queue, (msg1.priority, msg1))
heapq.heappush(queue, (msg2.priority, msg2))
# Should not raise TypeError
```

## Run Tests
```bash
# Run the specific failing test
python -m pytest tests/unit/governance/plugins/test_messaging.py::TestPluginMessageBus::test_circuit_breaker_integration -xvs

# Run all messaging tests
python -m pytest tests/unit/governance/plugins/test_messaging.py -xvs
```

## Additional Considerations
1. **Backward Compatibility**: Ensure existing code using Message class still works
2. **Serialization**: Verify JSON/pickle serialization still works with comparison methods
3. **Performance**: Consider caching comparison results for frequently compared messages
4. **Edge Cases**: Handle None values in timestamp or other fields

## Expected Outcome
- All tests in test_messaging.py pass
- No TypeError when messages with same priority are in queue
- Messages are properly ordered by priority, then timestamp, then ID
- Circuit breaker test passes with proper failure counting

Please implement Option 1 (total_ordering decorator) as it's cleaner and more maintainable.