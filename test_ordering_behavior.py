#!/usr/bin/env python3
"""
Additional test to verify exact ordering behavior.
"""

import heapq
from datetime import datetime, timezone, timedelta
from libs.governance.plugins.messaging import Message


def test_exact_ordering():
    """Test the exact ordering behavior: priority -> timestamp -> ID."""
    
    base_time = datetime.now(timezone.utc)
    
    # Create messages to test all three comparison levels
    messages = [
        # Different priorities - should sort by priority first
        Message("msg_p3", "test", "data", 3, base_time, "sender"),
        Message("msg_p1", "test", "data", 1, base_time, "sender"), 
        Message("msg_p2", "test", "data", 2, base_time, "sender"),
        
        # Same priority, different timestamps - should sort by timestamp
        Message("msg_t2", "test", "data", 1, base_time + timedelta(seconds=2), "sender"),
        Message("msg_t1", "test", "data", 1, base_time + timedelta(seconds=1), "sender"),
        
        # Same priority and timestamp, different IDs - should sort by ID
        Message("msg_id_c", "test", "data", 1, base_time, "sender"),
        Message("msg_id_a", "test", "data", 1, base_time, "sender"),
        Message("msg_id_b", "test", "data", 1, base_time, "sender"),
    ]
    
    # Add all messages to heap
    heap = []
    for msg in messages:
        heapq.heappush(heap, (msg.priority, msg))
    
    # Expected order based on our comparison logic:
    # 1. Priority 1 messages first (lower number = higher priority)
    # 2. Within same priority, earlier timestamps first
    # 3. Within same priority and timestamp, lexicographic ID order
    
    print("Messages in priority queue order:")
    results = []
    while heap:
        priority, msg = heapq.heappop(heap)
        results.append(msg)
        print(f"  ID: {msg.id:<12} Priority: {msg.priority} Timestamp: {msg.timestamp}")
    
    # Verify the ordering is correct
    print("\nVerification:")
    
    # Should have all priority 1 messages first
    priority_1_msgs = [msg for msg in results if msg.priority == 1]
    priority_2_msgs = [msg for msg in results if msg.priority == 2] 
    priority_3_msgs = [msg for msg in results if msg.priority == 3]
    
    expected_priority_1_order = [
        "msg_id_a",  # Same priority/timestamp, sorted by ID
        "msg_id_b",
        "msg_id_c", 
        "msg_p1",    # Same priority/timestamp, sorted by ID
        "msg_t1",    # Same priority, earlier timestamp
        "msg_t2",    # Same priority, later timestamp
    ]
    
    actual_priority_1_order = [msg.id for msg in priority_1_msgs]
    
    print(f"Expected priority 1 order: {expected_priority_1_order}")
    print(f"Actual priority 1 order:   {actual_priority_1_order}")
    
    if actual_priority_1_order == expected_priority_1_order:
        print("✓ Priority 1 messages ordered correctly")
    else:
        print("✗ Priority 1 messages NOT ordered correctly")
    
    # Check that priorities are in correct order overall
    all_priorities = [msg.priority for msg in results]
    print(f"All message priorities in order: {all_priorities}")
    
    if all_priorities == sorted(all_priorities):
        print("✓ Overall priority ordering is correct")
    else:
        print("✗ Overall priority ordering is incorrect")


if __name__ == "__main__":
    print("Testing exact Message ordering behavior...")
    print("=" * 60)
    test_exact_ordering()
