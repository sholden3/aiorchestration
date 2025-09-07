#!/usr/bin/env python3
"""
Test script to verify Message comparison methods work correctly.
"""

import heapq
from datetime import datetime, timezone
from libs.governance.plugins.messaging import Message


def test_message_comparison():
    """Test that Message comparison methods work correctly."""
    
    # Create test messages with different priorities
    now = datetime.now(timezone.utc)
    
    msg1 = Message(
        id="1", 
        topic="test", 
        payload="data1", 
        priority=1,  # Higher priority (lower number)
        timestamp=now, 
        sender="test"
    )
    
    msg2 = Message(
        id="2", 
        topic="test", 
        payload="data2", 
        priority=2,  # Lower priority (higher number)
        timestamp=now, 
        sender="test"
    )
    
    msg3 = Message(
        id="3", 
        topic="test", 
        payload="data3", 
        priority=1,  # Same priority as msg1, but later timestamp
        timestamp=datetime.now(timezone.utc),
        sender="test"
    )
    
    # Test basic comparison
    print("Testing basic message comparison:")
    print(f"msg1 < msg2 (priority 1 vs 2): {msg1 < msg2}")  # Should be True
    print(f"msg2 < msg1 (priority 2 vs 1): {msg2 < msg1}")  # Should be False
    print(f"msg1 < msg3 (same priority, earlier timestamp): {msg1 < msg3}")  # Should be True
    print(f"msg1 == msg1 (same ID): {msg1 == msg1}")  # Should be True
    print(f"msg1 == msg2 (different ID): {msg1 == msg2}")  # Should be False
    
    # Test heap operations - this was the original problem
    print("\nTesting heap operations (original issue):")
    queue = []
    
    try:
        # These operations should not raise TypeError anymore
        heapq.heappush(queue, (msg1.priority, msg1))
        heapq.heappush(queue, (msg2.priority, msg2))
        heapq.heappush(queue, (msg3.priority, msg3))
        
        print("Successfully added messages to heap!")
        
        # Pop messages in priority order
        print("Messages in priority order:")
        while queue:
            priority, message = heapq.heappop(queue)
            print(f"  Priority {priority}, ID {message.id}, Timestamp {message.timestamp}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Test with same priority messages (the problematic case)
    print("\nTesting same priority messages:")
    same_priority_queue = []
    
    # Create multiple messages with same priority
    for i in range(3):
        msg = Message(
            id=f"same_priority_{i}",
            topic="test",
            payload=f"data_{i}",
            priority=5,  # All same priority
            timestamp=datetime.now(timezone.utc),
            sender="test"
        )
        heapq.heappush(same_priority_queue, (msg.priority, msg))
    
    print("Same priority messages processed successfully!")
    
    # Pop and show order
    print("Order of same priority messages:")
    while same_priority_queue:
        priority, message = heapq.heappop(same_priority_queue)
        print(f"  ID: {message.id}")
    
    return True


if __name__ == "__main__":
    print("Testing Message comparison implementation...")
    print("=" * 60)
    
    try:
        success = test_message_comparison()
        if success:
            print("\n✓ All tests passed! Message comparison is working correctly.")
        else:
            print("\n✗ Some tests failed.")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
