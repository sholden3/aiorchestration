# Anthropic SDK Migration Plan

## Current State
- Using CLI subprocess calls (claude_integration.py)
- 114ms overhead per call
- No token counting or retry logic
- Complex 6-step setup process

## Target State
- Direct SDK integration
- <10ms overhead (HTTPS only)
- Built-in token counting and retries
- Simple 3-step setup

## Implementation Steps

### 1. Add SDK Dependency
```bash
pip install anthropic
```

Add to requirements.txt:
```
anthropic==0.18.1  # Or latest version
```

### 2. Create New SDK Integration Module
```python
# claude_sdk_integration.py
import os
from anthropic import AsyncAnthropic
from typing import Dict, Any, Optional

class ClaudeSDKIntegration:
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncAnthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def call_claude(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "success": True,
                "response": response.content[0].text,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### 3. Update Configuration
```python
# config.py additions
class AIIntegrationConfig(BaseSettings):
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    use_sdk: bool = Field(True, description="Use SDK instead of CLI")
```

### 4. Migration Strategy
- Keep both implementations temporarily
- Add feature flag to switch between CLI and SDK
- Test SDK with subset of requests
- Monitor performance and errors
- Gradual rollout

### 5. Testing Plan
```python
# test_claude_sdk.py
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_sdk_integration():
    # Mock SDK client
    mock_client = AsyncMock()
    # Test token counting
    # Test error handling
    # Test retry logic
```

## Benefits Quantified
- Performance: 114ms saved per call
- Setup: 3 steps vs 6 steps (50% reduction)
- Token tracking: 0 → Full visibility
- Error handling: Generic → Specific exceptions

## Migration Timeline
1. Day 1: Add SDK, create integration module
2. Day 2: Add configuration and feature flag
3. Day 3: Testing and validation
4. Day 4: Documentation update
5. Day 5: Gradual rollout

## Rollback Plan
- Feature flag allows instant rollback to CLI
- Both implementations coexist during transition
- No breaking changes to external interfaces