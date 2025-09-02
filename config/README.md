# Configuration System

## Overview
Centralized configuration system for the AI Development Assistant, supporting both frontend (Angular/Electron) and backend (Python/FastAPI) components.

## Configuration Files

### Base Configuration
- `app.config.json` - Main configuration file with all default values

### Environment-Specific Configurations
- `app.config.development.json` - Development environment overrides
- `app.config.production.json` - Production environment overrides
- `app.config.test.json` - Test environment overrides (optional)

## Configuration Structure

```json
{
  "app": {
    "name": "Application name",
    "version": "Semantic version",
    "environment": "development|production|test"
  },
  "backend": {
    "host": "Backend host",
    "port": 8000,
    "protocol": "http|https",
    "api_prefix": "/api",
    "database": { ... },
    "cache": { ... },
    "websocket": { ... }
  },
  "frontend": {
    "electron": { ... },
    "api": { ... }
  },
  "features": {
    "ai_integration": { ... },
    "governance": { ... },
    "templates": { ... },
    "practices": { ... }
  }
}
```

## Usage

### Backend (Python)
```python
from core.config import get_config

config = get_config()
print(f"Running on port: {config.backend.port}")
print(f"Environment: {config.environment}")
```

### Frontend (Angular)
```typescript
import { AppConfigService } from './services/app-config.service';

constructor(private appConfig: AppConfigService) {}

ngOnInit() {
  const apiUrl = this.appConfig.getApiUrl();
  const isProduction = this.appConfig.isProduction();
}
```

### Electron Main Process
```javascript
const appConfig = loadAppConfig();
console.log(`Backend port: ${appConfig.backend.port}`);
```

## Environment Variables

Production configuration supports environment variable substitution using `${VAR_NAME}` syntax:

- `DATABASE_URL` - Database connection string
- `JWT_SECRET` - JWT signing secret
- `AI_PROVIDER` - AI service provider (openai, anthropic, etc.)
- `AI_API_KEY` - API key for AI service

## Configuration Loading Order

1. Load base `app.config.json`
2. Load environment-specific config (e.g., `app.config.development.json`)
3. Merge environment config over base config
4. Substitute environment variables
5. Apply command-line overrides (if any)

## Validation

Run the configuration validator:
```bash
node validate-config.js
```

This will check:
- Required fields are present
- Values are within valid ranges
- Environment variables are set (warnings only)
- JSON syntax is correct

## Best Practices

1. **Never commit secrets** - Use environment variables for sensitive data
2. **Use environment-specific files** - Don't modify base config for deployments
3. **Validate before deployment** - Run validator in CI/CD pipeline
4. **Document changes** - Update this README when adding new config options
5. **Version control** - Track all config changes in git (except secrets)

## Adding New Configuration

1. Add to `app.config.json` with sensible defaults
2. Add environment-specific overrides if needed
3. Update validation rules in `validate-config.js`
4. Update TypeScript/Python models
5. Document the new configuration option

## Troubleshooting

### Config not loading
- Check file paths and permissions
- Validate JSON syntax
- Check console/logs for errors

### Wrong values being used
- Check environment detection
- Verify merge order
- Check for typos in field names

### Environment variables not working
- Ensure using `${VAR_NAME}` syntax
- Check variable is exported in environment
- Verify substitution is happening (check logs)