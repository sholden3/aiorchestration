# API Contracts

**Last Updated:** 2025-09-03  
**API Version:** 2.0  
**Reviewed By:** Alex Novak & Dr. Sarah Chen  
**Next Review:** 2025-10-01  

## Overview
The AI Orchestration Platform follows RESTful design principles with additional WebSocket support for real-time communication. Our API contracts emphasize consistency, predictability, and developer experience while maintaining strict governance and security standards.

## API Design Standards
### Design Principles
- **Principle 1:** RESTful design with resource-based URLs
- **Principle 2:** Consistent JSON request/response format
- **Principle 3:** Comprehensive error handling with actionable messages

### Naming Conventions
- **Resource Naming:** Plural nouns (e.g., `/users`, `/messages`)
- **Endpoint Naming:** Lowercase with hyphens (e.g., `/api/chat-messages`)
- **Parameter Naming:** snake_case for consistency with Python backend
- **Header Naming:** Title-Case-With-Hyphens (e.g., `X-Request-ID`)

### HTTP Standards
- **Methods:** GET (read), POST (create), PUT (update), DELETE (remove), PATCH (partial update)
- **Status Codes:** 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Server Error)
- **Headers:** Content-Type, Authorization, X-Request-ID, X-Rate-Limit
- **Content Types:** application/json (primary), multipart/form-data (file uploads)

## Versioning Strategy
### Version Management
- **Versioning Approach:** URL path versioning (e.g., `/api/v2/`)
- **Version Format:** Major.Minor (e.g., v2.0)
- **Deprecation Policy:** 6-month notice for major versions
- **Migration Strategy:** Parallel operation during transition period

### Backward Compatibility
- **Breaking Changes:** New major version required
- **Non-breaking Changes:** Added fields, new endpoints
- **Client Migration:** SDK auto-update for minor versions
- **Sunset Timeline:** 6 months after new major version

## Authentication & Authorization
### Authentication Methods
- **Primary:** JWT Bearer tokens
- **Secondary:** API keys for service-to-service
- **Token Format:** JWT with RS256 signature
- **Expiration:** 1 hour access, 7 days refresh

### Authorization Model
- **Access Control:** Role-Based Access Control (RBAC)
- **Scopes:** read, write, admin, governance
- **Permissions:** Granular per-resource permissions
- **Rate Limiting:** 1000 requests/hour standard, 5000 premium

## Request/Response Format
### Request Structure
```json
{
  "data": {
    "type": "resource-type",
    "attributes": {
      "field1": "value1",
      "field2": "value2"
    }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
```

### Response Structure
```json
{
  "data": {
    "id": "resource-id",
    "type": "resource-type",
    "attributes": {},
    "relationships": {}
  },
  "meta": {
    "request_id": "uuid",
    "response_time_ms": 123,
    "version": "2.0"
  }
}
```

### Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "field_name",
      "reason": "validation_error"
    }
  },
  "meta": {
    "request_id": "uuid",
    "documentation_url": "https://docs.api.com/errors/ERROR_CODE"
  }
}
```

## Core API Endpoints
### Authentication Endpoints
- **POST /api/v2/auth/login** - User authentication
- **POST /api/v2/auth/refresh** - Token refresh
- **POST /api/v2/auth/logout** - Session termination

### Chat & AI Endpoints
- **POST /api/v2/chat** - Process chat messages
- **GET /api/v2/chat/history** - Retrieve chat history
- **DELETE /api/v2/chat/{id}** - Delete chat message
- **WebSocket /ws/chat** - Real-time chat stream

### Validation & Governance
- **POST /api/v2/validate/code** - Validate code against governance
- **POST /api/v2/validate/documentation** - Validate documentation
- **GET /api/v2/governance/rules** - Retrieve governance rules
- **GET /api/v2/governance/compliance** - Check compliance status

### System Management
- **GET /api/v2/status** - System health check
- **GET /api/v2/metrics** - Performance metrics
- **GET /api/v2/audit** - Audit log access
- **POST /api/v2/circuit-breaker/reset** - Reset circuit breaker

## Data Models
### Core Models
```json
{
  "User": {
    "id": "uuid",
    "email": "string",
    "name": "string",
    "role": "enum",
    "created_at": "datetime",
    "updated_at": "datetime"
  },
  "ChatMessage": {
    "id": "uuid",
    "user_id": "uuid",
    "content": "string",
    "type": "enum",
    "metadata": "object",
    "timestamp": "datetime"
  },
  "ValidationResult": {
    "id": "uuid",
    "file_path": "string",
    "is_valid": "boolean",
    "score": "float",
    "violations": "array",
    "timestamp": "datetime"
  }
}
```

### Validation Rules
- **Field Validation:** Type checking, format validation, required fields
- **Business Rules:** Governance compliance, rate limits, permissions
- **Cross-field Validation:** Dependency checks, consistency rules
- **Custom Validators:** Language-specific code validation, documentation standards

## Error Handling
### Error Categories
- **Client Errors (4xx):** Invalid requests, authentication failures, not found
- **Server Errors (5xx):** Internal errors, service unavailable, timeout
- **Validation Errors:** Field validation, business rule violations
- **Authentication Errors:** Invalid token, expired session, insufficient permissions

### Error Response Standards
- **Error Codes:** UPPERCASE_SNAKE_CASE (e.g., INVALID_TOKEN)
- **Error Messages:** Human-readable, actionable guidance
- **Error Details:** Field-specific errors, validation details
- **Localization:** English primary, i18n support planned

## Rate Limiting & Throttling
### Rate Limit Strategy
- **Global Limits:** 10,000 requests/hour per IP
- **Per-User Limits:** 1,000 requests/hour standard
- **Per-Endpoint Limits:** Varies by resource intensity
- **Burst Limits:** 100 requests/minute burst allowance

### Headers & Responses
- **Limit Headers:** X-RateLimit-Limit
- **Remaining Headers:** X-RateLimit-Remaining
- **Reset Headers:** X-RateLimit-Reset
- **Exceeded Response:** 429 Too Many Requests

## Pagination & Filtering
### Pagination Standards
- **Method:** Cursor-based pagination
- **Parameters:** limit (default: 20, max: 100), cursor
- **Response Format:** data array with meta.pagination object
- **Metadata:** total_count, has_next, next_cursor

### Filtering & Sorting
- **Filter Parameters:** filter[field]=value
- **Sort Parameters:** sort=field,-field2 (- for descending)
- **Search Parameters:** q=search_term
- **Advanced Queries:** filter[created_at][gte]=2025-01-01

## Caching Strategy
### Cache Headers
- **Cache-Control:** max-age=300, private
- **ETag:** Entity version hashing
- **Last-Modified:** Resource modification timestamp
- **Expires:** Explicit expiration time

### Caching Policies
- **Static Resources:** 1 year cache, immutable
- **Dynamic Data:** 5 minutes cache, must-revalidate
- **User-specific Data:** No cache, private
- **Invalidation Strategy:** Tag-based invalidation, cascade clearing

## Documentation & Testing
### API Documentation
- **Documentation Tool:** OpenAPI 3.0 / Swagger
- **Schema Definition:** JSON Schema validation
- **Example Requests:** Provided for all endpoints
- **SDK Generation:** Auto-generated from OpenAPI spec

### Testing Strategy
- **Contract Testing:** Pact consumer-driven contracts
- **Integration Testing:** Postman collections
- **Load Testing:** K6 performance tests
- **Security Testing:** OWASP ZAP automated scans

## Monitoring & Analytics
### API Metrics
- **Performance Metrics:** Response time P50/P95/P99, throughput
- **Usage Metrics:** Request count, unique users, endpoint usage
- **Error Metrics:** Error rate, error types, error trends
- **Business Metrics:** Feature adoption, user engagement

### Logging Standards
- **Request Logging:** Method, path, headers, user
- **Response Logging:** Status, duration, size
- **Error Logging:** Full stack trace, context, request details
- **Audit Logging:** All state changes, compliance events

## Client Integration
### SDK Support
- **Supported Languages:** Python, TypeScript, JavaScript
- **SDK Features:** Auto-retry, circuit breaker, caching
- **Documentation:** Language-specific guides
- **Examples:** Sample applications for each SDK

### Integration Guidelines
- **Best Practices:** Use SDK, implement retry logic, handle errors
- **Error Handling:** Exponential backoff, circuit breaker pattern
- **Retry Logic:** 3 retries with exponential backoff
- **Timeout Configuration:** 30s default, configurable per endpoint

## Deprecation & Migration
### Deprecation Process
- **Notice Period:** 6 months for major changes
- **Communication:** Email, dashboard notices, API warnings
- **Migration Path:** Detailed migration guides, tools
- **Support Timeline:** 6 months overlap support

### Breaking Changes
- **Change Categories:** Removal, rename, behavior change
- **Impact Assessment:** Automated impact analysis
- **Migration Tools:** Auto-migration scripts where possible
- **Rollback Plan:** Version pinning, gradual rollout

---

## Change Log
| Date | Change | Author | Impact |
|------|--------|--------|--------|
| 2025-09-03 | Initial API v2.0 specification | Both Architects | Major |
| 2025-09-01 | Added WebSocket endpoints | Alex Novak | Minor |
| 2025-08-30 | Defined core endpoints | Dr. Sarah Chen | Major |

## References
- [OpenAPI Specification](https://swagger.io/specification/)
- [REST API Best Practices](https://restfulapi.net/)
- [JWT Standards](https://jwt.io/)
- [Internal Governance Rules](../../libs/governance/config.yaml)