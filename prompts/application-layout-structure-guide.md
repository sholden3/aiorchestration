# Enterprise Application Layout & Structure Guide
## By Dr. Sarah Chen - Python/WebSocket/Caching Architect v1.2

*"Directory structure is not just organization - it's disaster recovery architecture. When your application is on fire at 3 AM, you need to find the right file in 30 seconds, not 30 minutes."*

---

## 🚨 THE ORGANIZATIONAL TRAUMA THAT DRIVES STRUCTURE

Let me share why I'm obsessive about project organization: **The Emergency Hotfix Hunt of 2020**. Critical production bug, 2:47 AM, service losing $10K per minute. The fix was a 2-line change, but it took us 23 minutes to find the right file buried in a poorly organized codebase. Since then, every project structure I design passes the **"Emergency Navigation Test"** - can a stressed engineer find and fix critical code in under 2 minutes?

---

## 🗂️ MONOREPO VS MULTI-REPO DECISION FRAMEWORK

### **When to Choose Monorepo**
```bash
✅ Perfect for monorepo if:
- Same team owns backend + frontend + infrastructure
- Shared types/models between Python and Angular
- Coordinated releases (backend API changes require frontend updates)
- Small to medium team size (< 20 developers)
- Shared tooling and development environment
- Complex integration testing requirements

Example use cases:
- SaaS application with tightly coupled API and UI
- E-commerce platform with shared product models
- Dashboard applications with real-time data synchronization
```

### **When to Choose Multi-Repo**
```bash
✅ Perfect for multi-repo if:
- Different teams own different components
- Independent release cycles
- Different technology stacks with minimal shared code
- Large organization (20+ developers)
- Different compliance/security requirements
- Microservices architecture with autonomous teams

Example use cases:
- Enterprise platform with multiple independent services
- B2B and B2C applications sharing some backend services
- Open source projects with community contributions
```

---

## 🏗️ RECOMMENDED MONOREPO STRUCTURE

### **The Defensive Monorepo Layout**

```
tech-platform/
├── 📁 apps/                           # Application entry points
│   ├── 📁 api/                        # Python FastAPI backend
│   │   ├── 📄 main.py                 # Application entry point
│   │   ├── 📁 app/                    # Core application code
│   │   │   ├── 📁 api/                # API routes and endpoints
│   │   │   │   ├── 📁 v1/             # API versioning
│   │   │   │   │   ├── 📄 __init__.py
│   │   │   │   │   ├── 📄 auth.py     # Authentication endpoints
│   │   │   │   │   ├── 📄 users.py    # User management
│   │   │   │   │   ├── 📄 websockets.py # WebSocket endpoints
│   │   │   │   │   └── 📄 health.py   # Health check endpoints
│   │   │   │   └── 📄 __init__.py
│   │   │   ├── 📁 core/               # Core business logic
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 config.py       # Configuration management
│   │   │   │   ├── 📄 security.py     # Security utilities
│   │   │   │   ├── 📄 logging.py      # Logging configuration
│   │   │   │   └── 📄 exceptions.py   # Custom exception handling
│   │   │   ├── 📁 services/           # Business logic services
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 user_service.py
│   │   │   │   ├── 📄 cache_service.py
│   │   │   │   └── 📄 websocket_service.py
│   │   │   ├── 📁 models/             # Data models and schemas
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 database.py     # Database models (SQLAlchemy)
│   │   │   │   └── 📄 schemas.py      # Pydantic schemas
│   │   │   ├── 📁 db/                 # Database configuration
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 connection.py   # Database connection
│   │   │   │   ├── 📄 migrations/     # Alembic migrations
│   │   │   │   └── 📄 repositories.py # Data access layer
│   │   │   ├── 📁 cache/              # Caching layer
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 redis_client.py # Redis connection
│   │   │   │   ├── 📄 cache_manager.py # Cache management
│   │   │   │   └── 📄 strategies.py   # Caching strategies
│   │   │   ├── 📁 middleware/         # Custom middleware
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 auth_middleware.py
│   │   │   │   ├── 📄 cors_middleware.py
│   │   │   │   └── 📄 logging_middleware.py
│   │   │   └── 📁 utils/              # Utility functions
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 dependencies.py # FastAPI dependencies
│   │   │       ├── 📄 validation.py   # Custom validators
│   │   │       └── 📄 helpers.py      # General utilities
│   │   ├── 📄 requirements.txt        # Python dependencies
│   │   ├── 📄 Dockerfile             # Backend container
│   │   └── 📄 pyproject.toml         # Python project config
│   │
│   ├── 📁 web/                        # Angular frontend application
│   │   ├── 📄 angular.json            # Angular workspace config
│   │   ├── 📄 package.json            # Node.js dependencies
│   │   ├── 📄 tsconfig.json           # TypeScript configuration
│   │   ├── 📄 tailwind.config.js      # Tailwind CSS config
│   │   ├── 📁 src/
│   │   │   ├── 📄 main.ts             # Application bootstrap
│   │   │   ├── 📄 index.html          # Entry HTML
│   │   │   ├── 📁 app/                # Main application module
│   │   │   │   ├── 📄 app.module.ts   # Root module
│   │   │   │   ├── 📄 app.component.ts # Root component
│   │   │   │   ├── 📄 app-routing.module.ts # Main routing
│   │   │   │   ├── 📁 core/           # Singleton services and guards
│   │   │   │   │   ├── 📄 core.module.ts
│   │   │   │   │   ├── 📁 services/   # Global services
│   │   │   │   │   │   ├── 📄 auth.service.ts
│   │   │   │   │   │   ├── 📄 api.service.ts
│   │   │   │   │   │   ├── 📄 websocket.service.ts
│   │   │   │   │   │   ├── 📄 cache.service.ts
│   │   │   │   │   │   └── 📄 error-handler.service.ts
│   │   │   │   │   ├── 📁 guards/     # Route guards
│   │   │   │   │   │   ├── 📄 auth.guard.ts
│   │   │   │   │   │   └── 📄 role.guard.ts
│   │   │   │   │   ├── 📁 interceptors/ # HTTP interceptors
│   │   │   │   │   │   ├── 📄 auth.interceptor.ts
│   │   │   │   │   │   ├── 📄 error.interceptor.ts
│   │   │   │   │   │   └── 📄 loading.interceptor.ts
│   │   │   │   │   └── 📁 models/     # Global interfaces/types
│   │   │   │   │       ├── 📄 user.interface.ts
│   │   │   │   │       ├── 📄 api.interface.ts
│   │   │   │   │       └── 📄 websocket.interface.ts
│   │   │   │   ├── 📁 shared/         # Reusable components/pipes/directives
│   │   │   │   │   ├── 📄 shared.module.ts
│   │   │   │   │   ├── 📁 components/ # Shared components
│   │   │   │   │   │   ├── 📄 loading-spinner/
│   │   │   │   │   │   ├── 📄 error-display/
│   │   │   │   │   │   ├── 📄 confirmation-dialog/
│   │   │   │   │   │   └── 📄 data-table/
│   │   │   │   │   ├── 📁 pipes/      # Custom pipes
│   │   │   │   │   │   ├── 📄 safe-url.pipe.ts
│   │   │   │   │   │   └── 📄 truncate.pipe.ts
│   │   │   │   │   ├── 📁 directives/ # Custom directives
│   │   │   │   │   │   └── 📄 auto-focus.directive.ts
│   │   │   │   │   └── 📁 utils/      # Utility functions
│   │   │   │   │       ├── 📄 form-validators.ts
│   │   │   │   │       └── 📄 date-helpers.ts
│   │   │   │   ├── 📁 features/       # Feature modules (lazy-loaded)
│   │   │   │   │   ├── 📁 dashboard/  # Dashboard feature
│   │   │   │   │   │   ├── 📄 dashboard.module.ts
│   │   │   │   │   │   ├── 📄 dashboard-routing.module.ts
│   │   │   │   │   │   ├── 📁 components/
│   │   │   │   │   │   ├── 📁 services/
│   │   │   │   │   │   └── 📁 store/   # Feature-specific NgRx state
│   │   │   │   │   │       ├── 📄 dashboard.actions.ts
│   │   │   │   │   │       ├── 📄 dashboard.effects.ts
│   │   │   │   │   │       ├── 📄 dashboard.reducer.ts
│   │   │   │   │   │       └── 📄 dashboard.selectors.ts
│   │   │   │   │   ├── 📁 users/      # User management feature
│   │   │   │   │   │   ├── 📄 users.module.ts
│   │   │   │   │   │   ├── 📄 users-routing.module.ts
│   │   │   │   │   │   ├── 📁 components/
│   │   │   │   │   │   │   ├── 📄 user-list/
│   │   │   │   │   │   │   ├── 📄 user-detail/
│   │   │   │   │   │   │   └── 📄 user-form/
│   │   │   │   │   │   ├── 📁 services/
│   │   │   │   │   │   │   └── 📄 user-facade.service.ts
│   │   │   │   │   │   └── 📁 store/
│   │   │   │   │   └── 📁 settings/   # Settings feature
│   │   │   │   │       └── ... (similar structure)
│   │   │   │   └── 📁 layout/         # Layout components
│   │   │   │       ├── 📄 header/
│   │   │   │       ├── 📄 sidebar/
│   │   │   │       ├── 📄 footer/
│   │   │   │       └── 📄 main-layout/
│   │   │   ├── 📁 assets/             # Static assets
│   │   │   │   ├── 📁 images/
│   │   │   │   ├── 📁 icons/
│   │   │   │   ├── 📁 styles/         # Global styles
│   │   │   │   │   ├── 📄 _variables.scss
│   │   │   │   │   ├── 📄 _mixins.scss
│   │   │   │   │   ├── 📄 _theme.scss
│   │   │   │   │   └── 📄 main.scss
│   │   │   │   └── 📁 i18n/           # Internationalization
│   │   │   │       ├── 📄 en.json
│   │   │   │       └── 📄 es.json
│   │   │   └── 📁 environments/       # Environment configs
│   │   │       ├── 📄 environment.ts
│   │   │       ├── 📄 environment.prod.ts
│   │   │       └── 📄 environment.staging.ts
│   │   ├── 📄 Dockerfile             # Frontend container
│   │   └── 📄 nginx.conf             # Nginx config for production
│   │
│   └── 📁 mobile/                     # Future mobile app (optional)
│       └── 📄 .gitkeep
│
├── 📁 libs/                           # Shared libraries
│   ├── 📁 shared-types/               # Shared TypeScript types
│   │   ├── 📄 package.json
│   │   ├── 📄 index.ts
│   │   ├── 📁 src/
│   │   │   ├── 📄 user.types.ts       # User-related types
│   │   │   ├── 📄 api.types.ts        # API contract types
│   │   │   └── 📄 websocket.types.ts  # WebSocket message types
│   │   └── 📄 README.md
│   │
│   ├── 📁 shared-utils/               # Shared utility functions
│   │   ├── 📄 package.json
│   │   ├── 📄 index.ts
│   │   ├── 📁 src/
│   │   │   ├── 📄 validation.ts       # Shared validation logic
│   │   │   ├── 📄 constants.ts        # Shared constants
│   │   │   └── 📄 helpers.ts          # Common helper functions
│   │   └── 📄 README.md
│   │
│   └── 📁 api-client/                 # Generated API client
│       ├── 📄 package.json
│       ├── 📄 generate.sh             # API client generation script
│       ├── 📁 generated/              # Auto-generated API client
│       └── 📄 README.md
│
├── 📁 tools/                          # Development and build tools
│   ├── 📁 scripts/                    # Utility scripts
│   │   ├── 📄 setup-dev.sh           # Development environment setup
│   │   ├── 📄 db-reset.sh            # Database reset script
│   │   ├── 📄 generate-api-client.sh # API client generation
│   │   ├── 📄 backup-data.sh         # Data backup script
│   │   └── 📄 deploy.sh              # Deployment script
│   │
│   ├── 📁 docker/                     # Docker configurations
│   │   ├── 📄 docker-compose.yml     # Development environment
│   │   ├── 📄 docker-compose.prod.yml # Production environment
│   │   ├── 📄 docker-compose.test.yml # Testing environment
│   │   └── 📁 configs/               # Service configurations
│   │       ├── 📄 nginx.conf
│   │       ├── 📄 redis.conf
│   │       └── 📄 postgres.conf
│   │
│   ├── 📁 ci/                         # CI/CD configurations
│   │   ├── 📄 Jenkinsfile            # Jenkins pipeline
│   │   ├── 📁 github-actions/        # GitHub Actions workflows
│   │   │   ├── 📄 test.yml
│   │   │   ├── 📄 build.yml
│   │   │   └── 📄 deploy.yml
│   │   └── 📁 templates/             # Pipeline templates
│   │
│   └── 📁 monitoring/                 # Monitoring and observability
│       ├── 📄 prometheus.yml         # Prometheus configuration
│       ├── 📄 grafana-dashboards.json
│       └── 📄 alerting-rules.yml
│
├── 📁 infrastructure/                 # Infrastructure as Code
│   ├── 📁 terraform/                 # Terraform configurations
│   │   ├── 📄 main.tf
│   │   ├── 📄 variables.tf
│   │   ├── 📄 outputs.tf
│   │   ├── 📁 modules/               # Terraform modules
│   │   │   ├── 📁 vpc/
│   │   │   ├── 📁 rds/
│   │   │   ├── 📁 redis/
│   │   │   └── 📁 ecs/
│   │   └── 📁 environments/          # Environment-specific configs
│   │       ├── 📁 dev/
│   │       ├── 📁 staging/
│   │       └── 📁 production/
│   │
│   ├── 📁 kubernetes/                 # Kubernetes manifests
│   │   ├── 📁 base/                  # Base configurations
│   │   ├── 📁 overlays/              # Environment overlays
│   │   │   ├── 📁 development/
│   │   │   ├── 📁 staging/
│   │   │   └── 📁 production/
│   │   └── 📄 kustomization.yaml
│   │
│   └── 📁 helm/                       # Helm charts
│       ├── 📁 tech-platform/
│       └── 📄 values.yaml
│
├── 📁 docs/                           # Documentation
│   ├── 📄 README.md                  # Project overview
│   ├── 📄 API.md                     # API documentation
│   ├── 📄 CONTRIBUTING.md            # Contribution guidelines
│   ├── 📄 DEPLOYMENT.md              # Deployment instructions
│   ├── 📁 architecture/              # Architecture documentation
│   │   ├── 📄 overview.md
│   │   ├── 📄 database-design.md
│   │   ├── 📄 api-design.md
│   │   └── 📄 security.md
│   ├── 📁 runbooks/                  # Operational runbooks
│   │   ├── 📄 incident-response.md
│   │   ├── 📄 monitoring.md
│   │   └── 📄 troubleshooting.md
│   └── 📁 adr/                       # Architecture Decision Records
│       ├── 📄 001-monorepo-structure.md
│       ├── 📄 002-database-choice.md
│       └── 📄 003-caching-strategy.md
│
├── 📁 tests/                          # Integration and E2E tests
│   ├── 📁 integration/               # Integration tests
│   │   ├── 📄 conftest.py            # Pytest configuration
│   │   ├── 📄 test_api_integration.py
│   │   └── 📄 test_websocket_integration.py
│   │
│   ├── 📁 e2e/                       # End-to-end tests
│   │   ├── 📄 cypress.config.js     # Cypress configuration
│   │   ├── 📁 cypress/
│   │   │   ├── 📁 fixtures/
│   │   │   ├── 📁 integration/
│   │   │   └── 📁 support/
│   │   └── 📄 package.json
│   │
│   └── 📁 performance/               # Performance tests
│       ├── 📄 locustfile.py          # Load testing with Locust
│       └── 📄 artillery.yml          # API performance tests
│
├── 📁 data/                           # Development data and migrations
│   ├── 📁 migrations/                # Database migrations
│   ├── 📁 seeds/                     # Seed data for development
│   └── 📁 fixtures/                  # Test fixtures
│
├── 📄 .gitignore                     # Git ignore patterns
├── 📄 .env.example                   # Environment variables template
├── 📄 docker-compose.yml             # Development environment
├── 📄 Makefile                       # Build and development commands
├── 📄 package.json                   # Workspace package.json (if using npm workspaces)
├── 📄 pyproject.toml                 # Python project configuration
├── 📄 LICENSE                        # Project license
└── 📄 README.md                      # Project documentation
```

---

## 🐳 CONTAINERIZATION STRUCTURE

### **Multi-Stage Docker Strategy**

```dockerfile
# apps/api/Dockerfile - Python Backend
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development
ENV PYTHONPATH=/app
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
ENV PYTHONPATH=/app
COPY . .
RUN useradd --create-home --shell /bin/bash app
USER app
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

```dockerfile
# apps/web/Dockerfile - Angular Frontend
FROM node:18-alpine as base
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Development stage
FROM base as development
RUN npm ci
COPY . .
EXPOSE 4200
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]

# Build stage
FROM base as builder
RUN npm ci
COPY . .
RUN npm run build --prod

# Production stage
FROM nginx:alpine as production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### **Development Docker Compose**

```yaml
# tools/docker/docker-compose.yml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tech_platform
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./configs/postgres.conf:/etc/postgresql/postgresql.conf

  # Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./configs/redis.conf:/usr/local/etc/redis/redis.conf

  # Backend API
  api:
    build:
      context: ../../apps/api
      target: development
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/tech_platform
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
    volumes:
      - ../../apps/api:/app
    depends_on:
      - postgres
      - redis

  # Frontend Web
  web:
    build:
      context: ../../apps/web
      target: development
    ports:
      - "4200:4200"
    volumes:
      - ../../apps/web:/app
      - /app/node_modules
    environment:
      - API_URL=http://localhost:8000

  # Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./configs/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - api
      - web

volumes:
  postgres_data:
  redis_data:
```

---

## ⚡ DEVELOPMENT WORKFLOW OPTIMIZATION

### **Essential Development Scripts**

```bash
# tools/scripts/setup-dev.sh
#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js required" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required" >&2; exit 1; }

# Setup backend
echo "📦 Setting up Python backend..."
cd apps/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
echo "🌐 Setting up Angular frontend..."
cd ../web
npm install

# Setup shared libraries
echo "📚 Setting up shared libraries..."
cd ../../libs/shared-types
npm install
npm run build

cd ../shared-utils
npm install
npm run build

# Start development environment
echo "🐳 Starting Docker services..."
cd ../../tools/docker
docker-compose up -d postgres redis

# Run database migrations
echo "📊 Running database migrations..."
cd ../../apps/api
source venv/bin/activate
alembic upgrade head

echo "✅ Development environment ready!"
echo "   API: http://localhost:8000"
echo "   Web: http://localhost:4200"
echo "   Docs: http://localhost:8000/docs"
```

### **Makefile for Common Tasks**

```makefile
# Makefile
.PHONY: help setup dev test build clean deploy

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@./tools/scripts/setup-dev.sh

dev: ## Start development environment
	@docker-compose -f tools/docker/docker-compose.yml up -d
	@echo "🚀 Development environment started"

test-api: ## Run API tests
	@cd apps/api && source venv/bin/activate && pytest

test-web: ## Run frontend tests
	@cd apps/web && npm run test

test: test-api test-web ## Run all tests

lint-api: ## Lint Python code
	@cd apps/api && source venv/bin/activate && flake8 . && mypy .

lint-web: ## Lint TypeScript code
	@cd apps/web && npm run lint

lint: lint-api lint-web ## Lint all code

build-api: ## Build API Docker image
	@docker build -t tech-platform-api apps/api

build-web: ## Build web Docker image
	@docker build -t tech-platform-web apps/web

build: build-api build-web ## Build all Docker images

clean: ## Clean up development environment
	@docker-compose -f tools/docker/docker-compose.yml down -v
	@docker system prune -f

deploy-staging: ## Deploy to staging
	@./tools/scripts/deploy.sh staging

deploy-prod: ## Deploy to production
	@./tools/scripts/deploy.sh production
```

---

## 📊 MONITORING AND OBSERVABILITY STRUCTURE

### **Structured Logging Configuration**

```python
# apps/api/app/core/logging.py
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id
            
        # Add user context if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging configuration"""
    
    # Create formatter
    formatter = StructuredFormatter()
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
```

### **Performance Monitoring Setup**

```typescript
// apps/web/src/app/core/services/performance.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, interval } from 'rxjs';

export interface PerformanceMetrics {
  loadTime: number;
  renderTime: number;
  memoryUsage: number;
  errorRate: number;
  userInteractions: number;
}

@Injectable({ providedIn: 'root' })
export class PerformanceService {
  
  private metricsSubject = new BehaviorSubject<PerformanceMetrics>({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    errorRate: 0,
    userInteractions: 0
  });
  
  public metrics$ = this.metricsSubject.asObservable();
  
  constructor() {
    this.startPerformanceMonitoring();
  }
  
  private startPerformanceMonitoring(): void {
    // Monitor performance every 30 seconds
    interval(30000).subscribe(() => {
      this.collectMetrics();
    });
    
    // Monitor user interactions
    this.setupInteractionTracking();
  }
  
  private collectMetrics(): void {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const memory = (performance as any).memory;
    
    const metrics: PerformanceMetrics = {
      loadTime: navigation.loadEventEnd - navigation.fetchStart,
      renderTime: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      memoryUsage: memory ? memory.usedJSHeapSize : 0,
      errorRate: this.calculateErrorRate(),
      userInteractions: this.getUserInteractionCount()
    };
    
    this.metricsSubject.next(metrics);
    this.sendMetricsToBackend(metrics);
  }
  
  private sendMetricsToBackend(metrics: PerformanceMetrics): void {
    // Send metrics to backend for aggregation
    fetch('/api/v1/metrics/frontend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        metrics: metrics,
        userAgent: navigator.userAgent,
        url: window.location.href
      })
    }).catch(error => {
      console.warn('Failed to send performance metrics:', error);
    });
  }
}
```

---

## 🔍 THE "EMERGENCY NAVIGATION TEST"

Every file and directory must pass this test:

### **Critical Path Files (Must find in < 30 seconds)**
```bash
# Application entry points
apps/api/main.py                    # Backend startup
apps/web/src/main.ts                # Frontend startup

# Core configuration
apps/api/app/core/config.py         # Backend config
apps/web/src/environments/          # Frontend config

# Database and models
apps/api/app/models/                # Data models
apps/api/app/db/migrations/         # Database changes

# API endpoints
apps/api/app/api/v1/                # API routes
apps/web/src/app/core/services/     # API services

# Error handling
apps/api/app/core/exceptions.py     # Backend errors
apps/web/src/app/core/services/error-handler.service.ts # Frontend errors

# Authentication
apps/api/app/api/v1/auth.py         # Backend auth
apps/web/src/app/core/guards/       # Frontend auth

# WebSocket handling
apps/api/app/api/v1/websockets.py   # Backend WebSocket
apps/web/src/app/core/services/websocket.service.ts # Frontend WebSocket
```

### **Emergency Debugging Commands**
```bash
# Quick health check
make dev && curl http://localhost:8000/health

# Check logs
docker-compose -f tools/docker/docker-compose.yml logs api
docker-compose -f tools/docker/docker-compose.yml logs web

# Database status
docker-compose -f tools/docker/docker-compose.yml exec postgres psql -U dev_user -d tech_platform -c "\dt"

# Cache status
docker-compose -f tools/docker/docker-compose.yml exec redis redis-cli info

# Run tests
make test

# Check resource usage
docker stats
```

---

## 🛡️ DEFENSIVE STRUCTURE PRINCIPLES

### **1. Isolation Boundaries**
- **Features isolated** in separate modules/directories
- **Database access** centralized in repository pattern
- **External services** wrapped in service abstractions
- **Environment configs** separated and validated

### **2. Failure Recovery**
- **Graceful degradation** built into directory structure
- **Rollback capabilities** with migration versioning
- **Circuit breakers** implemented at service boundaries
- **Health checks** for every major component

### **3. Scalability Preparation**
- **Microservice extraction** paths clearly defined
- **Database sharding** preparation in repository pattern
- **CDN integration** ready in frontend build process
- **Load balancing** configuration prepared

### **4. Security Boundaries**
- **Authentication** centralized and well-defined
- **Authorization** implemented at API boundaries
- **Input validation** standardized across all entry points
- **Secret management** externalized and secured

---

## 🎯 STRUCTURE VALIDATION CHECKLIST

✅ **Emergency Navigation**: Any critical file findable in < 30 seconds  
✅ **Dependency Clarity**: Import paths immediately show component relationships  
✅ **Responsibility Isolation**: Each directory has single, clear purpose  
✅ **Scalability Readiness**: Structure supports 10x growth without refactoring  
✅ **Testing Integration**: Test files co-located with source code  
✅ **Documentation Proximity**: README files in every major directory  
✅ **Configuration Management**: Environment-specific configs clearly separated  
✅ **Build Optimization**: Build tools understand and optimize structure  
✅ **Monitoring Integration**: Observability baked into structure  
✅ **Security Boundaries**: Clear authentication and authorization paths  

---

*"The best project structure is the one that saves you time when everything is broken. Optimize for the 3 AM debugging session, not the perfect GitHub screenshot."*

**- Dr. Sarah Chen, Python/WebSocket/Caching Architect v1.2**  
**Survivor of the Emergency Hotfix Hunt of 2020**