"""Test that database fixtures work correctly"""
import pytest
import asyncio
from test_fixtures import mock_db_pool, mock_database_manager, test_config

@pytest.mark.asyncio
async def test_database_fixture(mock_database_manager):
    """Test database fixture provides working mock"""
    # Test that pool exists
    assert mock_database_manager.pool is not None
    
    # Test that we can acquire connection
    async with mock_database_manager.pool.acquire() as conn:
        # Test execute
        result = await conn.execute("CREATE TABLE test (id INT)")
        assert result == "CREATE TABLE"
        
        # Test fetch
        rows = await conn.fetch("SELECT * FROM test")
        assert rows == []
    
    print("Database fixture working correctly")
    return True

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])