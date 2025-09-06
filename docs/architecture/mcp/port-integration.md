# Port Discovery & Integration Architecture

**Component:** `apps/api/mcp/port_integration.py`  
**Version:** 1.0.0  
**Phase:** MCP-001 PHOENIX_RISE_FOUNDATION  
**Status:** Operational  
**Authors:** Alex Novak & Dr. Sarah Chen  

## Overview

The Port Integration system provides dynamic port discovery and allocation for the MCP governance server and related services. This eliminates port conflicts, enables multiple service instances, and provides automatic fallback mechanisms when preferred ports are unavailable.

## Architecture Philosophy

### Design Principles
1. **Zero Configuration**: Works out of the box without manual port setup
2. **Conflict Resolution**: Automatically finds available ports
3. **Service Registry**: Tracks all allocated ports centrally
4. **Atomic Operations**: Thread-safe port allocation
5. **Graceful Degradation**: Falls back to defaults if discovery fails

### Problem Solved
Manual port configuration leads to conflicts, especially in development environments with multiple services. Dynamic discovery ensures services always start successfully.

## System Architecture

```
┌─────────────────────────────────────────────┐
│            Service Startup                  │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│         Check Preferred Port                │
│              (e.g., 8001)                   │
└──────────────────┬──────────────────────────┘
                   │
              ┌────┴────┐
              │Available│
              └────┬────┘
                Yes│ │No
                   │ ↓
                   │ ┌─────────────────────────┐
                   │ │   Scan Port Range       │
                   │ │    (8001-8100)          │
                   │ └───────────┬─────────────┘
                   │             │
                   ↓             ↓
┌─────────────────────────────────────────────┐
│           Register Allocation               │
│            (.ports.json)                    │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│          Return Allocated Port              │
└─────────────────────────────────────────────┘
```

## Core Components

### 1. Port Discovery Function
```python
async def discover_backend_port(
    service_name: str,
    fallback: int = 8001
) -> int:
    """
    Discover available port for backend service.
    
    Args:
        service_name: Unique identifier for service
        fallback: Default port if discovery fails
    
    Returns:
        Available port number
    """
```

### 2. Port Registry
```python
class PortRegistry:
    """Manages port allocations across services."""
    
    def __init__(self, registry_file=".ports.json"):
        self.registry_file = registry_file
        self.allocations = self._load_registry()
        self.lock = threading.Lock()
```

### 3. Port Scanner
```python
def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False
```

## Port Allocation Strategy

### Priority Order
1. **Preferred Port**: Try service's preferred port first
2. **Previously Allocated**: Check registry for last successful port
3. **Range Scan**: Scan configured range for available port
4. **Fallback**: Use hardcoded fallback as last resort

### Port Ranges by Service
| Service | Preferred | Range Start | Range End | Fallback |
|---------|-----------|-------------|-----------|----------|
| MCP Governance | 8001 | 8001 | 8100 | 8001 |
| MCP HTTP Bridge | 8002 | 8001 | 8100 | 8002 |
| Backend API | 8000 | 8000 | 8099 | 8000 |
| WebSocket | 8080 | 8080 | 8180 | 8080 |

### Allocation Algorithm
```python
async def allocate_port(service_name: str, config: dict) -> int:
    # 1. Try preferred port
    preferred = config.get('preferred')
    if preferred and is_port_available(preferred):
        return preferred
    
    # 2. Check registry for previous allocation
    previous = registry.get_allocation(service_name)
    if previous and is_port_available(previous):
        return previous
    
    # 3. Scan range
    for port in range(config['range_start'], config['range_end']):
        if is_port_available(port):
            return port
    
    # 4. Use fallback
    return config['fallback']
```

## Registry Management

### Registry File Format (`.ports.json`)
```json
{
    "allocations": {
        "mcp-governance": {
            "port": 8001,
            "pid": 12345,
            "started": "2025-01-06T14:00:00Z",
            "host": "127.0.0.1"
        },
        "mcp-http-bridge": {
            "port": 8002,
            "pid": 12346,
            "started": "2025-01-06T14:00:01Z",
            "host": "127.0.0.1"
        }
    },
    "version": "1.0.0",
    "updated": "2025-01-06T14:00:01Z"
}
```

### Registry Operations

#### Register Allocation
```python
def register_allocation(service_name: str, port: int, pid: int):
    with self.lock:
        self.allocations[service_name] = {
            "port": port,
            "pid": pid,
            "started": datetime.utcnow().isoformat(),
            "host": "127.0.0.1"
        }
        self._save_registry()
```

#### Release Allocation
```python
def release_allocation(service_name: str):
    with self.lock:
        if service_name in self.allocations:
            del self.allocations[service_name]
            self._save_registry()
```

#### Cleanup Stale Allocations
```python
def cleanup_stale_allocations():
    """Remove allocations for dead processes."""
    for service, info in list(self.allocations.items()):
        if not is_process_alive(info['pid']):
            self.release_allocation(service)
```

## Configuration

### Port Configuration (`mcp_config.yaml`)
```yaml
port:
  service_name: mcp-governance
  preferred: 8001
  range_start: 8001
  range_end: 8100
  fallback: 8001
  
  discovery:
    enabled: true
    registry_file: .ports.json
    cleanup_stale: true
    retry_attempts: 3
    retry_delay: 1  # seconds
```

### Environment Variables
```bash
# Override port discovery
export MCP_PORT_DISCOVERY_DISABLED=false
export MCP_PORT_PREFERRED=8001
export MCP_PORT_RANGE_START=8001
export MCP_PORT_RANGE_END=8100
export MCP_PORT_REGISTRY=.ports.json
```

## Error Handling

### Common Errors

#### 1. No Available Ports
```python
class NoAvailablePortError(Exception):
    """Raised when no ports available in range."""
    
    def __init__(self, service_name, range_start, range_end):
        super().__init__(
            f"No available ports for {service_name} "
            f"in range {range_start}-{range_end}"
        )
```

#### 2. Registry Lock Timeout
```python
try:
    with timeout(5):
        with registry.lock:
            # Perform operation
except TimeoutError:
    logger.error("Registry lock timeout")
    # Use fallback port
```

#### 3. Permission Denied
```python
try:
    socket.bind((host, port))
except PermissionError:
    logger.error(f"Permission denied for port {port}")
    # Ports <1024 require root on Unix
```

### Recovery Strategies
1. **Retry with Delay**: Wait and retry for transient failures
2. **Expand Range**: Try wider port range if configured range full
3. **Clean Registry**: Remove stale entries and retry
4. **Use Fallback**: Always have working fallback port

## Platform Considerations

### Windows
```python
if platform.system() == 'Windows':
    # Windows-specific socket options
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

### Linux/macOS
```python
if platform.system() in ['Linux', 'Darwin']:
    # Unix-specific socket options
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
```

### Docker/Kubernetes
```yaml
# In containerized environments
port:
  discovery:
    enabled: false  # Use orchestrator's port management
  preferred: ${SERVICE_PORT}  # From environment
```

## Integration Points

### MCP Server Integration
```python
# In governance_server.py
async def initialize(self):
    # Use port discovery
    port_config = self.config.get_port_config()
    self.port = await discover_backend_port(
        service_name=port_config['service_name'],
        fallback=port_config['fallback']
    )
    logger.info(f"MCP server using port {self.port}")
```

### Service Discovery
```python
def get_service_port(service_name: str) -> int:
    """Get port for running service from registry."""
    registry = PortRegistry()
    allocation = registry.get_allocation(service_name)
    if allocation:
        return allocation['port']
    raise ServiceNotFoundError(service_name)
```

### Health Checks
```python
async def check_service_health(service_name: str) -> bool:
    """Check if service is healthy on allocated port."""
    port = get_service_port(service_name)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:{port}/health")
            return response.status_code == 200
    except:
        return False
```

## Testing

### Unit Tests
```python
def test_port_discovery():
    """Test port discovery logic."""
    port = discover_backend_port("test-service", fallback=9000)
    assert 8001 <= port <= 8100 or port == 9000

def test_registry_operations():
    """Test registry CRUD operations."""
    registry = PortRegistry(":memory:")
    registry.register_allocation("test", 8001, 12345)
    assert registry.get_allocation("test")["port"] == 8001
```

### Integration Tests
```python
async def test_concurrent_allocation():
    """Test multiple services allocating ports concurrently."""
    tasks = [
        discover_backend_port(f"service-{i}")
        for i in range(10)
    ]
    ports = await asyncio.gather(*tasks)
    assert len(set(ports)) == 10  # All unique
```

### Load Tests
```python
def test_port_allocation_performance():
    """Test port allocation under load."""
    start = time.time()
    for _ in range(100):
        discover_backend_port("test-service")
    elapsed = time.time() - start
    assert elapsed < 1.0  # 100 allocations in <1 second
```

## Monitoring

### Metrics
```python
port_metrics = {
    "allocations_total": 100,
    "allocation_failures": 2,
    "average_allocation_time_ms": 5,
    "ports_in_use": 3,
    "registry_cleanup_runs": 10,
    "stale_allocations_removed": 5
}
```

### Health Indicators
- Registry file accessible
- Preferred ports available
- No allocation failures
- Low allocation latency

### Alerting
- Port exhaustion (>90% of range used)
- Registry lock timeouts
- Repeated allocation failures
- Stale allocation accumulation

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8001  # Linux/macOS
netstat -ano | findstr :8001  # Windows

# Kill process if needed
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### Registry Corruption
```bash
# Backup corrupted registry
mv .ports.json .ports.json.backup

# Reset registry
echo '{"allocations": {}, "version": "1.0.0"}' > .ports.json

# Restart services
```

### Discovery Disabled
```bash
# Check if discovery is disabled
env | grep MCP_PORT_DISCOVERY_DISABLED

# Enable discovery
unset MCP_PORT_DISCOVERY_DISABLED
```

## Best Practices

### 1. Always Use Discovery
```python
# Good
port = await discover_backend_port("my-service")

# Bad
port = 8001  # Hardcoded
```

### 2. Clean Registry on Shutdown
```python
async def shutdown():
    release_allocation("my-service")
    await cleanup()
```

### 3. Monitor Port Usage
```python
if get_ports_in_use() > 0.9 * (range_end - range_start):
    logger.warning("Port range nearly exhausted")
```

### 4. Use Service Names Consistently
```python
SERVICE_NAME = "mcp-governance"  # Define once
port = await discover_backend_port(SERVICE_NAME)
```

## Future Enhancements

### Phase 3 Improvements
- Service mesh integration
- DNS-based service discovery
- Multi-host port coordination

### Phase 4 Improvements
- Kubernetes service integration
- Consul/etcd backend for registry
- Port prediction based on patterns

### Long-term Vision
- Zero-configuration networking
- Automatic service mesh enrollment
- Cross-cluster port management

## References

- [Socket Programming](https://docs.python.org/3/library/socket.html)
- [Service Discovery Patterns](https://microservices.io/patterns/service-discovery)
- [Port Registry Implementation](../../../apps/api/mcp/port_integration.py)

---

**Reviewed By:** Alex Novak, Dr. Sarah Chen  
**Last Updated:** 2025-01-06  
**Next Review:** Post Phase MCP-003 Implementation