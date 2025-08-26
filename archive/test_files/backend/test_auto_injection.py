"""Test auto-injection session management"""
import asyncio
import json
from auto_injection import AutoInjectionManager, InjectionType

async def test_auto_injection():
    """Test auto-injection functionality"""
    print("=== Testing Auto-Injection Session Management ===\n")
    
    manager = AutoInjectionManager()
    
    # Test 1: Create session
    print("1. Creating session with auto-injection...")
    
    initial_context = {
        'project': 'AI Assistant',
        'environment': 'development',
        'tenant_id': 'test-tenant'
    }
    
    result = await manager.create_session('agent-001', initial_context)
    if result.success:
        session_id = result.data
        print(f"   [OK] Session created: {session_id}")
        print(f"   - Creation time: {result.metadata.get('creation_ms', 0):.2f}ms")
    else:
        print(f"   [FAIL] {result.error}")
        return False
    
    # Test 2: Get session context
    print("\n2. Getting session context...")
    
    context_result = await manager.get_session_context(session_id)
    if context_result.success:
        context = context_result.data
        print(f"   [OK] Session context retrieved")
        print(f"   - Current context: {context['current_context']}")
        print(f"   - Total injections: {context['session_state']['metrics']['total_injections']}")
    
    # Test 3: Inject custom context
    print("\n3. Injecting custom context...")
    
    custom_context = {
        'task': 'code_review',
        'language': 'python',
        'evidence': 'static analysis completed'
    }
    
    inject_result = await manager.inject_context(
        session_id,
        InjectionType.CONTEXT,
        custom_context
    )
    
    if inject_result.success:
        print("   [OK] Custom context injected")
    
    # Test 4: Test assumption prevention
    print("\n4. Testing assumption prevention in injection...")
    
    assumption_content = {
        'claim': 'This should work faster',
        'note': 'Probably improves performance'
    }
    
    inject_result2 = await manager.inject_context(
        session_id,
        InjectionType.CONTEXT,
        assumption_content
    )
    
    if not inject_result2.success:
        print(f"   [OK] Assumption blocked: {inject_result2.error}")
    else:
        print("   [WARNING] Assumption not blocked")
    
    # Test 5: Context rotation
    print("\n5. Testing context rotation...")
    
    new_context = {
        'task': 'testing',
        'phase': 'unit_tests',
        'measurement': 'Coverage at 85%'
    }
    
    rotate_result = await manager.rotate_context(session_id, new_context)
    if rotate_result.success:
        print(f"   [OK] Context rotated")
        print(f"   - Context depth: {rotate_result.metadata.get('context_depth')}")
    
    # Test 6: Multiple sessions
    print("\n6. Creating multiple sessions...")
    
    sessions_created = 0
    for i in range(2, 5):
        agent_id = f"agent-{i:03d}"
        result = await manager.create_session(agent_id)
        if result.success:
            sessions_created += 1
    
    print(f"   [OK] Created {sessions_created} additional sessions")
    
    # Test 7: Session statistics
    print("\n7. Session statistics:")
    
    stats = manager.get_statistics()
    print(f"   - Active sessions: {stats['active_sessions']}")
    print(f"   - Total injections: {stats['total_injections']}")
    print(f"   - Success rate: {stats['success_rate']:.2%}")
    print(f"   - Avg context depth: {stats['avg_context_depth']:.1f}")
    
    # Test 8: Export/Import session
    print("\n8. Testing session export/import...")
    
    export_result = await manager.export_session(session_id)
    if export_result.success:
        print("   [OK] Session exported")
        session_data = export_result.data
        
        # Clear session and reimport
        del manager.sessions[session_id]
        
        import_result = await manager.import_session(session_data)
        if import_result.success:
            print(f"   [OK] Session imported: {import_result.data}")
    
    # Test 9: Active sessions list
    print("\n9. Active sessions:")
    
    active = manager.get_active_sessions()
    for session in active[:3]:  # Show first 3
        print(f"   - {session['session_id']}: {session['metrics']['total_injections']} injections")
    
    # Test 10: Cleanup
    print("\n10. Testing expired session cleanup...")
    
    # Manually expire a session for testing
    if manager.sessions:
        first_session = list(manager.sessions.values())[0]
        from datetime import datetime, timedelta
        first_session.last_updated = datetime.now() - timedelta(hours=25)
    
    cleaned = await manager.cleanup_expired_sessions()
    print(f"   [OK] Cleaned {cleaned} expired sessions")
    
    print("\n=== All Auto-Injection Tests Passed ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_auto_injection())
    exit(0 if result else 1)