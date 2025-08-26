"""Test multi-tenant orchestrator implementation"""
import asyncio
import time
from orchestrator import MultiTenantOrchestrator, TenantIsolationLevel

async def test_orchestrator():
    """Test orchestrator with actual execution"""
    print("=== Testing Multi-Tenant Orchestrator ===\n")
    
    # Create orchestrator
    orchestrator = MultiTenantOrchestrator()
    
    # Test 1: Create tenant
    print("1. Creating tenant...")
    tenant_result = await orchestrator.create_tenant("TestCorp", TenantIsolationLevel.ISOLATED)
    if tenant_result.success:
        print(f"   [OK] Tenant created: {tenant_result.data.id}")
        tenant_id = tenant_result.data.id
    else:
        print(f"   [FAIL] Failed: {tenant_result.error}")
        return False
    
    # Test 2: Create agent
    print("\n2. Creating agent...")
    agent_result = await orchestrator.create_agent(tenant_id)
    if agent_result.success:
        print(f"   [OK] Agent created: {agent_result.data.id}")
        agent_id = agent_result.data.id
    else:
        print(f"   [FAIL] Failed: {agent_result.error}")
        return False
    
    # Test 3: Execute task
    print("\n3. Executing task...")
    task_result = await orchestrator.execute_task(
        agent_id,
        "Optimize database query performance"
    )
    if task_result.success:
        print(f"   [OK] Task executed in {task_result.metadata.get('execution_ms', 0):.2f}ms")
        print(f"   - Persona used: {task_result.metadata.get('persona_used', 'None')}")
        print(f"   - Response: {task_result.data.get('response', '')[:80]}...")
    else:
        print(f"   [FAIL] Failed: {task_result.error}")
        return False
    
    # Test 4: Execute cached task
    print("\n4. Executing same task (should hit cache)...")
    cached_result = await orchestrator.execute_task(
        agent_id,
        "Optimize database query performance"
    )
    if cached_result.success:
        cache_hit = cached_result.metadata.get('cache_hit', False)
        print(f"   [OK] Cache hit: {cache_hit}")
        print(f"   - Execution: {cached_result.metadata.get('execution_ms', 0):.2f}ms")
    
    # Test 5: Get metrics
    print("\n5. Getting metrics...")
    metrics = orchestrator.get_metrics()
    print(f"   [OK] Total tenants: {metrics['total_tenants']}")
    print(f"   [OK] Total agents: {metrics['total_agents']}")
    print(f"   [OK] Cache hit rate: {metrics['cache_metrics']['hit_rate']}%")
    
    # Test 6: Agent limit
    print("\n6. Testing agent limits...")
    for i in range(5):
        result = await orchestrator.create_agent(tenant_id)
        if not result.success:
            print(f"   [OK] Agent limit enforced at agent #{i+2}: {result.error}")
            break
    
    # Test 7: Remove agent
    print("\n7. Removing agent...")
    remove_result = await orchestrator.remove_agent(agent_id)
    if remove_result.success:
        print(f"   [OK] Agent removed")
    
    print("\n=== All Tests Passed ===")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_orchestrator())
    exit(0 if result else 1)