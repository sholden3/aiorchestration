# Cascading Authentication Documentation
## Three-Level Fallback Strategy for Maximum Flexibility

## Overview
The AI orchestration system implements a **cascading authentication strategy** that provides maximum flexibility for different deployment scenarios while optimizing for performance when possible.

## Authentication Priority Order

### 1️⃣ **Environment Variable** (Highest Priority)
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```
- **Use Case**: Production deployments, CI/CD environments
- **Benefits**: Most secure (not in code), easiest to rotate
- **Performance**: Best (uses SDK directly)

### 2️⃣ **Configuration File** (Second Priority)
```python
# config.py or .env file
anthropic_api_key = "sk-ant-api03-..."
```
- **Use Case**: Development environments, testing
- **Benefits**: Persistent across sessions, team sharing
- **Performance**: Best (uses SDK directly)

### 3️⃣ **CLI Fallback** (Lowest Priority)
```bash
# No API key needed - uses Claude Code CLI
```
- **Use Case**: Individual developers, evaluation
- **Benefits**: No API key required, uses existing Claude Code
- **Performance**: Slower (subprocess overhead ~114ms)

## Implementation Details

### Detection Logic
```python
# Cascading check in ClaudeUnifiedIntegration
api_key = os.getenv('ANTHROPIC_API_KEY')  # Check env first
if not api_key and config:
    api_key = config.ai.anthropic_api_key  # Check config second
if not api_key:
    use_cli_fallback()  # Fall back to CLI
```

### Feature Comparison
| Method | Setup Complexity | API Key Required | Performance |
|--------|------------------|------------------|-------------|
| SDK (with API key) | 3 steps | Yes | Untested - may be faster |
| CLI (fallback) | 6 steps | No | Untested - baseline |

**Performance Impact**: Cannot be determined without testing both methods with actual API access

## Configuration Examples

### Example 1: Production Deployment
```bash
# Set environment variable in production
export ANTHROPIC_API_KEY="sk-ant-api03-production-key"
python main.py
# Uses SDK with environment variable
```

### Example 2: Development with Config
```python
# .env file
ANTHROPIC_API_KEY=sk-ant-api03-dev-key

# Or in config.py
class AIIntegrationConfig:
    anthropic_api_key = "sk-ant-api03-dev-key"
```

### Example 3: Individual Developer without API Key
```python
# No configuration needed
# System automatically falls back to Claude Code CLI
# Just ensure Claude Code is installed and authenticated
```

## Status Checking

The system provides real-time status of which authentication method is active:

```python
integration = ClaudeUnifiedIntegration(config)
status = integration.get_status()

print(f"Method: {status['method']}")  # 'sdk' or 'cli'
print(f"API Key Source: {status['api_key_source']}")  # 'environment', 'config', or 'none (using CLI)'
print(f"Recommendations: {status['recommendations']}")  # Actionable setup advice
```

## Migration Path

### For New Users
1. Start with CLI (no setup required)
2. Evaluate system capabilities
3. Upgrade to SDK when ready for production

### For Existing CLI Users
1. System continues to work unchanged
2. Add API key when performance matters
3. No code changes required

### For API Key Users
1. Immediate SDK benefits
2. Automatic fallback if key issues
3. Seamless transition

## Security Considerations

### API Key Security
- **Never commit API keys** to version control
- Use environment variables in production
- Rotate keys regularly
- Use different keys for dev/staging/production

### Fallback Security
- CLI fallback uses user's Claude Code authentication
- No API key exposure risk in CLI mode
- Separate authentication domains

## Troubleshooting

### Issue: "Anthropic SDK not installed"
```bash
pip install anthropic
```

### Issue: "API key not found"
Check priority order:
1. `echo $ANTHROPIC_API_KEY`
2. Check config file
3. Verify Claude Code is installed

### Issue: "CLI command not found"
```bash
# Verify Claude Code installation
claude --version
# Or update PATH in config
```

## Testing the Cascade

Run the included test to verify cascade behavior:
```bash
python test_cascading_auth.py
```

Expected output:
```
1. Testing environment variable priority... [OK]
2. Testing config file fallback... [OK]
3. Testing CLI fallback... [OK]
```

## Benefits of This Approach

1. **Zero Breaking Changes**: Existing CLI users continue working
2. **Progressive Enhancement**: Add API key when ready
3. **Flexible Deployment**: Different auth for different environments
4. **Automatic Optimization**: Uses best available method
5. **Graceful Degradation**: Falls back if primary method fails

## Recommendations by Use Case

| Use Case | Recommended Method | Why |
|----------|-------------------|-----|
| Production | Environment Variable + SDK | Security & Performance |
| Development | Config File + SDK | Convenience & Speed |
| Testing/CI | Environment Variable + SDK | Isolation & Control |
| Evaluation | CLI Fallback | No commitment required |
| Individual Dev | Any method | Based on preference |

## Future Enhancements

- Automatic SDK installation prompt
- Key rotation reminders
- Usage analytics per method
- Performance monitoring dashboard
- Multi-provider support (OpenAI, Cohere, etc.)

---

This cascading approach ensures the system works for everyone, from individual developers without API keys to production deployments requiring maximum performance.