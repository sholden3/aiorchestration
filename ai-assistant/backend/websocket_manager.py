"""
Real-time WebSocket manager for live monitoring
Broadcasts system events, metrics, and orchestration updates
"""

import asyncio
import json
from typing import Set, Dict, Any, List
from datetime import datetime
import logging
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """WebSocket event types"""
    ORCHESTRATION_STATUS = "orchestration_status"
    CACHE_METRICS = "cache_metrics"
    TASK_UPDATE = "task_update"
    PERSONA_DECISION = "persona_decision"
    SYSTEM_ALERT = "system_alert"
    PERFORMANCE_METRIC = "performance_metric"
    ASSUMPTION_VALIDATION = "assumption_validation"

class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts real-time updates
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.broadcast_queue: asyncio.Queue = asyncio.Queue()
        self.is_broadcasting = False
        
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'client_id': client_id or f"client_{len(self.active_connections)}",
            'connected_at': datetime.now().isoformat(),
            'subscriptions': set(EventType)  # Subscribe to all events by default
        }
        
        # Send welcome message
        await self.send_personal_message(websocket, {
            'type': 'connection',
            'status': 'connected',
            'client_id': self.connection_metadata[websocket]['client_id'],
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"WebSocket client {client_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.discard(websocket)
            client_id = self.connection_metadata.get(websocket, {}).get('client_id', 'unknown')
            del self.connection_metadata[websocket]
            logger.info(f"WebSocket client {client_id} disconnected. Remaining connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], event_type: EventType = None):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        # Add event type
        if event_type:
            message['event_type'] = event_type.value
            
        disconnected = []
        
        for connection in self.active_connections:
            try:
                # Check if client is subscribed to this event type
                metadata = self.connection_metadata.get(connection, {})
                subscriptions = metadata.get('subscriptions', set())
                
                if not event_type or event_type in subscriptions:
                    await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_orchestration_status(self, status: Dict[str, Any]):
        """Broadcast orchestration status update"""
        await self.broadcast({
            'type': 'orchestration_status',
            'data': status
        }, EventType.ORCHESTRATION_STATUS)
    
    async def broadcast_cache_metrics(self, metrics: Dict[str, Any]):
        """Broadcast cache metrics update"""
        await self.broadcast({
            'type': 'cache_metrics',
            'data': metrics
        }, EventType.CACHE_METRICS)
    
    async def broadcast_task_update(self, task_id: str, status: str, details: Dict[str, Any] = None):
        """Broadcast task status update"""
        await self.broadcast({
            'type': 'task_update',
            'task_id': task_id,
            'status': status,
            'details': details or {}
        }, EventType.TASK_UPDATE)
    
    async def broadcast_persona_decision(self, persona: str, decision: str, confidence: float):
        """Broadcast persona decision"""
        await self.broadcast({
            'type': 'persona_decision',
            'persona': persona,
            'decision': decision,
            'confidence': confidence
        }, EventType.PERSONA_DECISION)
    
    async def broadcast_assumption_validation(self, assumption: str, validated: bool, challenger: str = None):
        """Broadcast assumption validation event"""
        await self.broadcast({
            'type': 'assumption_validation',
            'assumption': assumption,
            'validated': validated,
            'challenger': challenger
        }, EventType.ASSUMPTION_VALIDATION)
    
    async def broadcast_system_alert(self, severity: str, message: str):
        """Broadcast system alert"""
        await self.broadcast({
            'type': 'system_alert',
            'severity': severity,
            'message': message
        }, EventType.SYSTEM_ALERT)
    
    async def handle_client_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Handle incoming message from client"""
        msg_type = message.get('type')
        
        if msg_type == 'subscribe':
            # Update client subscriptions
            events = message.get('events', [])
            if websocket in self.connection_metadata:
                subscriptions = set()
                for event in events:
                    try:
                        subscriptions.add(EventType(event))
                    except ValueError:
                        logger.warning(f"Invalid event type: {event}")
                self.connection_metadata[websocket]['subscriptions'] = subscriptions
                
                await self.send_personal_message(websocket, {
                    'type': 'subscription_update',
                    'subscribed_to': [e.value for e in subscriptions]
                })
                
        elif msg_type == 'ping':
            # Respond to ping
            await self.send_personal_message(websocket, {
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        
        elif msg_type == 'request_status':
            # Client requesting current status
            await self.send_personal_message(websocket, {
                'type': 'status_response',
                'connections': len(self.active_connections),
                'timestamp': datetime.now().isoformat()
            })
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about all connections"""
        return [
            {
                'client_id': metadata.get('client_id'),
                'connected_at': metadata.get('connected_at'),
                'subscriptions': [e.value for e in metadata.get('subscriptions', [])]
            }
            for metadata in self.connection_metadata.values()
        ]

# Global WebSocket manager instance
ws_manager = WebSocketManager()