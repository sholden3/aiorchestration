"""Test specialized databases with mock data"""
import asyncio
from specialized_databases import SpecializedDatabases, DatabaseType
from test_fixtures import mock_database_manager

async def test_specialized_databases():
    """Test specialized database operations"""
    print("=== Testing Specialized Databases ===\n")
    
    # Create instance
    db = SpecializedDatabases()
    
    # Mock the database manager for testing
    db.db_manager = await create_mock_manager()
    db.initialized = True  # Bypass initialization for testing
    
    # Test 1: Record learning pattern
    print("1. Recording learning pattern...")
    learning_result = await db.record_learning(
        pattern="User prefers concise responses",
        context={"session": "test123", "persona": "marcus"},
        outcome="Positive feedback received",
        confidence=0.85
    )
    if learning_result.success:
        print(f"   [OK] Learning recorded: {learning_result.data.id}")
        print(f"   - Confidence: {learning_result.data.confidence}")
    else:
        print(f"   [FAIL] {learning_result.error}")
    
    # Test 2: Report bug
    print("\n2. Reporting bug...")
    bug_result = await db.report_bug(
        description="Cache hit rate calculation incorrect",
        stack_trace="File cache.py line 145",
        severity="high"
    )
    if bug_result.success:
        print(f"   [OK] Bug reported: {bug_result.data.id}")
        print(f"   - Severity: {bug_result.data.severity}")
        print(f"   - Status: {bug_result.data.status}")
    else:
        print(f"   [FAIL] {bug_result.error}")
    
    # Test 3: Add assumption
    print("\n3. Adding business assumption...")
    assumption_result = await db.add_assumption(
        assumption="Users want fast response times",
        rationale="Based on user feedback and industry standards"
    )
    if assumption_result.success:
        print(f"   [OK] Assumption added: {assumption_result.data.id}")
        print(f"   - Validated: {assumption_result.data.validated}")
    else:
        print(f"   [FAIL] {assumption_result.error}")
    
    # Test 4: Validate assumption
    print("\n4. Validating assumption...")
    if assumption_result.success:
        validation_result = await db.validate_assumption(
            assumption_result.data.id,
            "User survey confirmed preference for <500ms response"
        )
        if validation_result.success:
            print(f"   [OK] Assumption validated")
        else:
            print(f"   [FAIL] {validation_result.error}")
    
    # Test 5: Add rule
    print("\n5. Adding business rule...")
    rule_result = await db.add_rule(
        rule_name="Max agents per tenant",
        condition="tenant.agent_count >= tenant.max_agents",
        action="reject_agent_creation",
        priority=100
    )
    if rule_result.success:
        print(f"   [OK] Rule added: {rule_result.data.rule_name}")
        print(f"   - Priority: {rule_result.data.priority}")
        print(f"   - Active: {rule_result.data.active}")
    else:
        print(f"   [FAIL] {rule_result.error}")
    
    # Test 6: Get statistics
    print("\n6. Database statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n=== All Tests Complete ===")
    return True

async def create_mock_manager():
    """Create mock database manager for testing"""
    from unittest.mock import AsyncMock, MagicMock
    
    manager = MagicMock()
    pool = AsyncMock()
    
    # Mock connection
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value="UPDATE 1")
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(return_value=None)
    
    # Mock acquire context
    class MockAcquire:
        async def __aenter__(self):
            return conn
        async def __aexit__(self, *args):
            pass
    
    pool.acquire = lambda: MockAcquire()
    manager.pool = pool
    
    return manager

if __name__ == "__main__":
    result = asyncio.run(test_specialized_databases())
    exit(0 if result else 1)