"""Test base patterns implementation"""
import asyncio
from base_patterns import DatabaseOperation

class TestOp(DatabaseOperation):
    """Test subclass without implementation"""
    pass

async def test_not_implemented():
    try:
        op = TestOp(None)
        await op._perform_operation(None)
    except NotImplementedError as e:
        print(f"NotImplementedError raised: {e}")
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    return False

if __name__ == "__main__":
    result = asyncio.run(test_not_implemented())
    print(f"Test passed: {result}")