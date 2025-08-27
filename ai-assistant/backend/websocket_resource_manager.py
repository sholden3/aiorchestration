"""
FIX H1: WebSocket Resource Management with Connection Limits and Cleanup
Architecture: Dr. Sarah Chen
Pattern: Resource-bounded connections with automatic cleanup
"""
import asyncio
import time
import logging
from typing import Dict, Set, Optional, Any
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import WebSocket

logger = logging.getLogger(__name__)

@dataclass
class WebSocketConnection:
    """Managed WebSocket connection with metadata"""
    connection_id: str
    user_id: str
    websocket: WebSocket
    created_at: float
    last_activity: float
    bytes_sent: int = 0
    bytes_received: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    def is_stale(self, timeout_seconds: int) -> bool:
        """Check if connection is stale"""
        return (time.time() - self.last_activity) > timeout_seconds

class WebSocketMetrics:
    """Metrics tracking for WebSocket connections"""
    
    def __init__(self):
        self.total_connections = 0
        self.active_connections = 0
        self.failed_connections = 0
        self.cleanup_cycles = 0
        self.connections_cleaned = 0
        self.bytes_sent_total = 0
        self.bytes_received_total = 0
        self.peak_connections = 0
        self.connection_errors = defaultdict(int)
        
    def record_connection_established(self, user_id: str):
        """Record new connection"""
        self.total_connections += 1
        self.active_connections += 1
        if self.active_connections > self.peak_connections:
            self.peak_connections = self.active_connections
            
    def record_connection_closed(self, user_id: str):
        """Record connection closure"""
        self.active_connections = max(0, self.active_connections - 1)
        
    def record_connection_error(self, user_id: str, error: str):
        """Record connection error"""
        self.failed_connections += 1
        self.connection_errors[error] += 1
        
    def record_cleanup_cycle(self, cleaned_count: int):
        """Record cleanup cycle"""
        self.cleanup_cycles += 1
        self.connections_cleaned += cleaned_count
        
    def record_data_transfer(self, bytes_sent: int, bytes_received: int):
        """Record data transfer metrics"""
        self.bytes_sent_total += bytes_sent
        self.bytes_received_total += bytes_received
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'total_connections': self.total_connections,
            'active_connections': self.active_connections,
            'failed_connections': self.failed_connections,
            'cleanup_cycles': self.cleanup_cycles,
            'connections_cleaned': self.connections_cleaned,
            'bytes_sent_total': self.bytes_sent_total,
            'bytes_received_total': self.bytes_received_total,
            'peak_connections': self.peak_connections,
            'top_errors': dict(sorted(
                self.connection_errors.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])
        }

class WebSocketResourceManager:
    """
    FIX H1: Production WebSocket management with resource limits
    Sarah's defensive patterns: Connection limits, cleanup timeouts, resource monitoring
    """
    
    def __init__(self, 
                 max_connections: int = 1000,
                 max_connections_per_user: int = 5,
                 connection_timeout: int = 300,  # 5 minutes
                 cleanup_interval: int = 60,     # 1 minute
                 heartbeat_interval: int = 30):  # 30 seconds
        """
        Initialize resource manager with limits
        
        Args:
            max_connections: Maximum total connections
            max_connections_per_user: Maximum connections per user
            connection_timeout: Seconds before connection considered stale
            cleanup_interval: Seconds between cleanup cycles
            heartbeat_interval: Seconds between heartbeat checks
        """
        # Connection storage
        self._connections: Dict[str, WebSocketConnection] = {}
        self._user_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # Resource limits
        self.max_connections = max_connections
        self.max_connections_per_user = max_connections_per_user
        self.connection_timeout = connection_timeout
        self.cleanup_interval = cleanup_interval
        self.heartbeat_interval = heartbeat_interval
        
        # Connection semaphore for limiting
        self._connection_semaphore = asyncio.Semaphore(max_connections)
        
        # Metrics and monitoring
        self._metrics = WebSocketMetrics()
        
        # Background tasks
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(f"WebSocket Resource Manager initialized: "
                   f"max_connections={max_connections}, "
                   f"timeout={connection_timeout}s")
    
    async def start_background_tasks(self):
        """Start background monitoring tasks"""
        if self._running:
            return
            
        self._running = True
        self._health_monitor_task = asyncio.create_task(self._connection_health_monitor())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("WebSocket background tasks started")
    
    async def stop_background_tasks(self):
        """Stop background monitoring tasks"""
        self._running = False
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
                
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
                
        logger.info("WebSocket background tasks stopped")
    
    async def _connection_health_monitor(self):
        """
        Monitor connection health and cleanup stale connections
        Sarah's proactive pattern: Regular cleanup prevents resource exhaustion
        """
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                current_time = time.time()
                cleanup_count = 0
                stale_connections = []
                
                # Identify stale connections
                for conn_id, connection in list(self._connections.items()):
                    if connection.is_stale(self.connection_timeout):
                        stale_connections.append(conn_id)
                        logger.warning(f"Stale connection detected: {conn_id} "
                                     f"(idle for {current_time - connection.last_activity:.1f}s)")
                
                # Clean up stale connections
                for conn_id in stale_connections:
                    await self._force_connection_cleanup(conn_id, reason="timeout")
                    cleanup_count += 1
                
                # Log cleanup metrics
                if cleanup_count > 0:
                    self._metrics.record_cleanup_cycle(cleanup_count)
                    logger.info(f"Cleanup cycle: removed {cleanup_count} stale connections")
                
                # Log resource usage
                total_connections = len(self._connections)
                memory_estimate = self._estimate_memory_usage()
                
                if total_connections > 0:
                    logger.debug(f"Resource status: {total_connections} connections, "
                               f"~{memory_estimate:.2f}MB memory")
                
                # Alert on high resource usage
                usage_percent = (total_connections / self.max_connections) * 100
                if usage_percent > 85:
                    logger.warning(f"High connection usage: {usage_percent:.1f}% "
                                 f"({total_connections}/{self.max_connections})")
                
            except Exception as e:
                logger.error(f"Connection health monitor error: {e}", exc_info=True)
    
    async def _heartbeat_monitor(self):
        """Send periodic heartbeats to detect dead connections"""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                dead_connections = []
                for conn_id, connection in list(self._connections.items()):
                    try:
                        # Send ping to check if connection is alive
                        await connection.websocket.send_json({
                            'type': 'ping',
                            'timestamp': time.time()
                        })
                        connection.messages_sent += 1
                    except Exception:
                        dead_connections.append(conn_id)
                
                # Clean up dead connections
                for conn_id in dead_connections:
                    await self._force_connection_cleanup(conn_id, reason="heartbeat_failed")
                    
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}", exc_info=True)
    
    def can_accept_connection(self, user_id: str) -> tuple[bool, str]:
        """
        Check if a new connection can be accepted
        
        Returns:
            (can_accept, reason_if_rejected)
        """
        # Check total connection limit
        if len(self._connections) >= self.max_connections:
            return False, f"Maximum connections reached ({self.max_connections})"
        
        # Check per-user limit
        user_conn_count = len(self._user_connections.get(user_id, set()))
        if user_conn_count >= self.max_connections_per_user:
            return False, f"User connection limit reached ({self.max_connections_per_user})"
        
        return True, ""
    
    @asynccontextmanager
    async def managed_connection(self, websocket: WebSocket, user_id: str):
        """
        Context manager for WebSocket connections with guaranteed cleanup
        Sarah's pattern: RAII for connection lifecycle management
        """
        connection_id = f"{user_id}_{int(time.time() * 1000)}"
        connection = None
        
        try:
            # Check if we can accept the connection
            can_accept, reason = self.can_accept_connection(user_id)
            if not can_accept:
                logger.warning(f"Connection rejected for {user_id}: {reason}")
                await websocket.close(code=1008, reason=reason)
                raise ConnectionRefusedError(reason)
            
            # Acquire connection slot
            async with self._connection_semaphore:
                # Create and register connection
                connection = WebSocketConnection(
                    connection_id=connection_id,
                    user_id=user_id,
                    websocket=websocket,
                    created_at=time.time(),
                    last_activity=time.time()
                )
                
                self._connections[connection_id] = connection
                self._user_connections[user_id].add(connection_id)
                self._metrics.record_connection_established(user_id)
                
                logger.info(f"Connection established: {connection_id} for user {user_id} "
                          f"(total: {len(self._connections)})")
                
                yield connection
                
        except Exception as e:
            self._metrics.record_connection_error(user_id, str(type(e).__name__))
            logger.error(f"Connection error for {user_id}: {e}")
            raise
            
        finally:
            # Guaranteed cleanup
            if connection:
                await self._force_connection_cleanup(connection_id, reason="connection_closed")
    
    async def _force_connection_cleanup(self, connection_id: str, reason: str = "unknown"):
        """
        Force cleanup of a connection
        Ensures all resources are properly released
        """
        if connection_id not in self._connections:
            return
            
        try:
            connection = self._connections[connection_id]
            
            # Close WebSocket if still open
            try:
                await connection.websocket.close(code=1001, reason=reason)
            except Exception:
                pass  # WebSocket might already be closed
            
            # Remove from tracking
            del self._connections[connection_id]
            self._user_connections[connection.user_id].discard(connection_id)
            
            # Clean up empty user entries
            if not self._user_connections[connection.user_id]:
                del self._user_connections[connection.user_id]
            
            # Update metrics
            self._metrics.record_connection_closed(connection.user_id)
            self._metrics.record_data_transfer(
                connection.bytes_sent, 
                connection.bytes_received
            )
            
            logger.info(f"Connection cleaned up: {connection_id} (reason: {reason})")
            
        except Exception as e:
            logger.error(f"Error during connection cleanup: {e}", exc_info=True)
    
    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection by ID"""
        return self._connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> Set[str]:
        """Get all connection IDs for a user"""
        return self._user_connections.get(user_id, set()).copy()
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections of a user"""
        connection_ids = self.get_user_connections(user_id)
        
        for conn_id in connection_ids:
            connection = self.get_connection(conn_id)
            if connection:
                try:
                    await connection.websocket.send_json(message)
                    connection.messages_sent += 1
                    connection.bytes_sent += len(json.dumps(message))
                    connection.update_activity()
                except Exception as e:
                    logger.error(f"Error broadcasting to {conn_id}: {e}")
                    await self._force_connection_cleanup(conn_id, reason="broadcast_failed")
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        # Rough estimation: 5KB base + 1KB per connection
        base_memory = 5.0  # MB
        per_connection = 0.001  # MB
        return base_memory + (len(self._connections) * per_connection)
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource manager status"""
        return {
            'active_connections': len(self._connections),
            'max_connections': self.max_connections,
            'usage_percent': (len(self._connections) / self.max_connections * 100),
            'unique_users': len(self._user_connections),
            'memory_estimate_mb': self._estimate_memory_usage(),
            'metrics': self._metrics.get_metrics(),
            'limits': {
                'max_total': self.max_connections,
                'max_per_user': self.max_connections_per_user,
                'timeout_seconds': self.connection_timeout,
                'cleanup_interval': self.cleanup_interval
            }
        }