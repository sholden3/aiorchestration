"""
Minimal version of main.py that works with basic dependencies
Use this if you have issues with the full version
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import json

# Try imports with fallbacks
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    print("FastAPI not installed. Please run: pip install fastapi")
    sys.exit(1)

try:
    import uvicorn
except ImportError:
    print("Uvicorn not installed. Please run: pip install uvicorn")
    sys.exit(1)

# Optional imports - use dict if pydantic fails
try:
    from pydantic import BaseModel
    USE_PYDANTIC = True
except ImportError:
    print("Warning: Pydantic not available, using dictionaries")
    USE_PYDANTIC = False
    BaseModel = dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple request/response models
if USE_PYDANTIC:
    class AITask(BaseModel):
        prompt: str
        persona: Optional[str] = None
        context: Optional[Dict[str, Any]] = {}
        use_cache: bool = True
    
    class TaskResponse(BaseModel):
        success: bool
        response: Optional[str] = None
        error: Optional[str] = None
        cached: bool = False
        tokens_saved: int = 0
        persona_used: Optional[str] = None
        execution_time_ms: int = 0
else:
    # Use regular functions if pydantic not available
    def AITask(**kwargs):
        return {
            'prompt': kwargs.get('prompt', ''),
            'persona': kwargs.get('persona'),
            'context': kwargs.get('context', {}),
            'use_cache': kwargs.get('use_cache', True)
        }
    
    def TaskResponse(**kwargs):
        return kwargs

class MinimalBackendService:
    """
    Minimal backend service with mock responses
    """
    
    def __init__(self, port: int = 8001):
        self.app = FastAPI(title="AI Assistant Backend (Minimal)")
        self.port = port
        self.cache = {}  # Simple in-memory cache
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Configure CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Define minimal API endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "cache_enabled": True,
                "personas_available": 3,
                "mode": "minimal"
            }
        
        @self.app.post("/ai/execute")
        async def execute_ai_task(request_data: dict):
            """Execute AI task with mock response"""
            prompt = request_data.get('prompt', '')
            use_cache = request_data.get('use_cache', True)
            
            # Check cache
            cache_key = f"cache_{prompt}"
            if use_cache and cache_key in self.cache:
                logger.info(f"Cache hit for: {prompt[:30]}...")
                return {
                    "success": True,
                    "response": self.cache[cache_key],
                    "cached": True,
                    "tokens_saved": 100,
                    "persona_used": "ai_integration",
                    "execution_time_ms": 1
                }
            
            # Generate mock response
            await asyncio.sleep(0.5)  # Simulate processing
            
            response = f"""Mock response for: {prompt[:50]}...
            
This is a mock response from the minimal backend.
The full system would provide:
- Three-persona governance validation
- Intelligent caching
- Real Claude integration

For now, this demonstrates the system is working."""
            
            # Store in cache
            if use_cache:
                self.cache[cache_key] = response
            
            return {
                "success": True,
                "response": response,
                "cached": False,
                "tokens_saved": 0,
                "persona_used": "ai_integration",
                "execution_time_ms": 500
            }
        
        @self.app.post("/ai/orchestrated")
        async def execute_orchestrated(request_data: dict):
            """Orchestrated execution with mock governance"""
            prompt = request_data.get('prompt', '')
            
            await asyncio.sleep(0.2)  # Simulate governance
            
            logger.info("Mock governance: 3 personas analyzing...")
            logger.info("Mock: Sarah validates AI approach")
            logger.info("Mock: Marcus checks performance")
            logger.info("Mock: Emily reviews UX impact")
            logger.info("Mock: Consensus reached - UNANIMOUS")
            
            return {
                "success": True,
                "response": "Governance validated response",
                "cached": False,
                "tokens_saved": 0,
                "persona_used": "orchestrated_consensus",
                "execution_time_ms": 200
            }
        
        @self.app.get("/orchestration/status")
        async def get_orchestration_status():
            """Return mock orchestration status"""
            return {
                "is_running": True,
                "agents": {
                    "total": 3,
                    "active": 1,
                    "idle": 2,
                    "busy": 0
                },
                "tasks": {
                    "queued": 0,
                    "active": 1,
                    "completed": 5,
                    "failed": 0
                },
                "performance": {
                    "total_tokens_used": 1500,
                    "average_response_time": 450,
                    "overall_success_rate": 0.95
                },
                "governance_active": True,
                "persona_orchestration_active": True
            }
        
        @self.app.get("/metrics/cache")
        async def get_cache_metrics():
            """Return cache metrics"""
            total_requests = len(self.cache) * 2  # Assume each cached item was requested twice
            cache_hits = len(self.cache)
            
            return {
                "hit_rate": cache_hits / max(total_requests, 1),
                "tokens_saved": cache_hits * 100,
                "hot_cache_size_mb": 0.1,
                "warm_cache_files": len(self.cache),
                "total_requests": total_requests,
                "cache_hits": cache_hits,
                "cache_misses": cache_hits
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            logger.info("WebSocket client connected")
            
            try:
                # Send initial message
                await websocket.send_json({
                    "type": "connection",
                    "status": "connected",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep connection alive
                while True:
                    # Wait for client messages
                    data = await websocket.receive_json()
                    
                    # Echo back or handle commands
                    if data.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    else:
                        await websocket.send_json({
                            "type": "echo",
                            "data": data
                        })
                        
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
        
        @self.app.get("/ws/status")
        async def websocket_status():
            """WebSocket status endpoint"""
            return {
                "active_connections": 0,
                "connections": []
            }
        
        @self.app.post("/cache/clear")
        async def clear_cache():
            """Clear the cache"""
            self.cache.clear()
            return {"message": "Cache cleared successfully"}
    
    def run(self):
        """Start the minimal backend service"""
        logger.info(f"Starting Minimal AI Backend on port {self.port}")
        logger.info("This is a minimal version with mock responses")
        logger.info("Full features available with complete installation")
        
        uvicorn.run(
            self.app,
            host="127.0.0.1",
            port=self.port,
            log_level="info"
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Minimal AI Backend')
    parser.add_argument('--port', type=int, default=8001, help='Port to run on')
    args = parser.parse_args()
    
    service = MinimalBackendService(port=args.port)
    service.run()

if __name__ == "__main__":
    main()