# Performance Evidence Correction
## Retracting Unsubstantiated Claims

## ❌ RETRACTED CLAIM
"SDK is 17% faster than CLI approach"

## Why This Was Wrong
1. **No SDK installed** - Cannot measure SDK performance
2. **No API key** - Cannot test actual SDK response times
3. **Mixed measurements** - Compared subprocess overhead to HTTPS overhead incorrectly
4. **Assumed benefits** - Made assumptions without evidence

## What We Actually Know

### Measured Facts
| Metric | Value | Evidence Level |
|--------|-------|----------------|
| Subprocess creation | 41-114ms | ✅ Measured |
| HTTPS connection setup | 189ms | ✅ Measured |
| SDK total response time | Unknown | ❌ No API key |
| CLI total response time | Unknown | ❌ No Claude Code |
| Actual performance difference | Unknown | ❌ Cannot compare |

### What We Can Say (Evidence-Based)

#### Theoretical Advantages of SDK:
- **Connection pooling** - Might reuse connections (not verified)
- **No subprocess overhead** - Saves 41-114ms (measured)
- **Direct API calls** - Fewer layers (architectural fact)

#### Theoretical Advantages of CLI:
- **Persistent session** - Might keep connection alive (not verified)
- **Local caching** - Claude Code might cache responses (unknown)
- **Optimized binary** - Might be faster than Python (unknown)

## Corrected Documentation

### Before (Wrong):
"SDK is 17% faster than CLI"

### After (Correct):
"SDK *may* be faster than CLI due to avoiding subprocess overhead, but this cannot be verified without testing both approaches with actual API access"

## What Would Be Needed to Make Performance Claims

### Minimum Requirements:
1. Install Anthropic SDK
2. Obtain API key
3. Measure both approaches with identical prompts
4. Run multiple iterations for statistical significance
5. Test under various conditions (cold start, warm cache, etc.)

### Test Protocol:
```python
# Need actual implementation
async def measure_sdk_performance():
    # Requires: pip install anthropic
    # Requires: ANTHROPIC_API_KEY set
    times = []
    for i in range(10):
        start = time.perf_counter()
        response = await sdk_client.messages.create(...)
        times.append(time.perf_counter() - start)
    return statistics.mean(times)

async def measure_cli_performance():
    # Requires: Claude Code installed
    # Requires: Claude Code authenticated
    times = []
    for i in range(10):
        start = time.perf_counter()
        response = await cli_client.execute(...)
        times.append(time.perf_counter() - start)
    return statistics.mean(times)

# Only then can we claim:
sdk_time = await measure_sdk_performance()
cli_time = await measure_cli_performance()
improvement = ((cli_time - sdk_time) / cli_time) * 100
print(f"SDK is {improvement:.1f}% faster")  # IF positive
```

## Lessons Learned

### Governance Violations:
1. **Made performance claim without measurement** ❌
2. **Assumed SDK would be faster** ❌
3. **Used theoretical calculations as facts** ❌
4. **Did not acknowledge measurement limitations** ❌

### Correct Approach:
1. **State what is measurable** ✅
2. **Acknowledge what cannot be verified** ✅
3. **Separate facts from assumptions** ✅
4. **Require evidence before claims** ✅

## Revised Recommendation

### What We Can Say:
- Cascading authentication provides **flexibility** (verified)
- SDK approach requires **fewer setup steps** (3 vs 6, documented)
- SDK provides **better error messages** (typed exceptions, verified in docs)
- Performance comparison **requires testing** (cannot claim without evidence)

### What We Cannot Say (Without Testing):
- SDK is X% faster ❌
- CLI has Y ms overhead ❌
- SDK will improve response times ❌
- Either approach is definitively better for performance ❌

## Action Items
1. Remove all unsubstantiated performance claims from documentation
2. Add disclaimer that performance benefits require testing
3. Focus on verified benefits (flexibility, setup simplicity)
4. Plan actual performance testing when resources available