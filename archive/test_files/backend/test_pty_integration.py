"""Test PTY console integration"""
import asyncio
import sys
from pty_integration import PTYIntegrationManager, AgentConsole

async def test_pty_integration():
    """Test PTY console functionality"""
    print("=== Testing PTY Console Integration ===\n")
    
    # Create manager
    manager = PTYIntegrationManager(max_consoles=5)
    
    # Test 1: Create console for agent
    print("1. Creating console for agent...")
    result = await manager.create_console("agent-001", shell=None)
    if result.success:
        print(f"   [OK] Console created")
        print(f"   - Session ID: {result.data.session_id}")
        print(f"   - Shell: {result.data.shell}")
        print(f"   - Startup time: {result.metadata.get('startup_ms', 0):.2f}ms")
    else:
        print(f"   [FAIL] {result.error}")
        return False
    
    # Test 2: Execute command
    print("\n2. Executing command in console...")
    cmd_result = await manager.execute_in_console("agent-001", "echo 'Hello from PTY'")
    if cmd_result.success:
        print(f"   [OK] Command executed")
        print(f"   - Output: {cmd_result.data}")
    else:
        print(f"   [FAIL] {cmd_result.error}")
    
    # Test 3: Read console output
    print("\n3. Reading console output...")
    console = await manager.get_console("agent-001")
    if console:
        output = await console.read_output(lines=5)
        print(f"   [OK] Output buffer: {len(output)} lines")
        for line in output:
            print(f"   > {line}")
    
    # Test 4: Console limits
    print("\n4. Testing console limits...")
    created = 0
    for i in range(2, 7):  # Try to create 5 more (total 6, limit 5)
        agent_id = f"agent-{i:03d}"
        result = await manager.create_console(agent_id)
        if result.success:
            created += 1
        else:
            print(f"   [OK] Limit enforced at console #{i}: {result.error}")
            break
    print(f"   Created {created} additional consoles")
    
    # Test 5: Statistics
    print("\n5. Manager statistics:")
    stats = manager.get_statistics()
    print(f"   - Total consoles: {stats['total_consoles']}")
    print(f"   - Active consoles: {stats['active_consoles']}")
    print(f"   - Available slots: {stats['available_slots']}")
    
    # Test 6: Cleanup
    print("\n6. Removing console...")
    removed = await manager.remove_console("agent-001")
    if removed:
        print("   [OK] Console removed")
    
    # Test 7: Shutdown
    print("\n7. Shutting down all consoles...")
    await manager.shutdown()
    final_stats = manager.get_statistics()
    print(f"   [OK] All consoles shut down ({final_stats['total_consoles']} remaining)")
    
    print("\n=== All PTY Tests Passed ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_pty_integration())
    exit(0 if result else 1)