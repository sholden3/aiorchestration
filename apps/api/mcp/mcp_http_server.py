"""
MCP HTTP Server

Provides HTTP endpoints for the Claude Code hook bridge to call the MCP governance server.
This wraps the MCP server with FastAPI to enable HTTP-based communication.

Author: Dr. Sarah Chen
Phase: MCP-002 NEURAL_LINK_BRIDGE
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apps.api.mcp.governance_server import GovernanceMCPServer
from apps.api.mcp.config_loader import get_config

logger = logging.getLogger(__name__)


# Pydantic models for request/response
class ConsultationRequest(BaseModel):
    """Request model for governance consultation."""
    operation: str = Field(..., description="Operation type being consulted")
    context: Dict[str, Any] = Field(..., description="Context for the operation")
    correlation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class ConsultationResponse(BaseModel):
    """Response model for governance consultation."""
    approved: bool = Field(..., description="Whether operation is approved")
    confidence: float = Field(..., description="Confidence level of decision")
    recommendations: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)
    persona_guidance: Dict[str, Any] = Field(default_factory=dict)
    block_reason: Optional[str] = None
    remediation: Optional[str] = None
    correlation_id: str = Field(..., description="Correlation ID for tracing")


class AuditRequest(BaseModel):
    """Request model for audit logging."""
    operation: str = Field(..., description="Operation that was executed")
    context: Dict[str, Any] = Field(..., description="Execution context")
    correlation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class ContextRequest(BaseModel):
    """Request model for governance context."""
    operation: str = Field(..., description="Operation type")
    context: Dict[str, Any] = Field(..., description="Current context")
    correlation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


# Create FastAPI app
app = FastAPI(
    title="MCP Governance HTTP Server",
    description="HTTP interface for Claude Code hook bridge to MCP governance",
    version="1.0.0"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global MCP server instance
mcp_server: Optional[GovernanceMCPServer] = None


@app.on_event("startup")
async def startup_event():
    """Initialize MCP server on startup."""
    global mcp_server
    
    logger.info("Starting MCP HTTP server")
    
    # Create and initialize MCP server
    mcp_server = GovernanceMCPServer()
    await mcp_server.initialize()
    
    logger.info(f"MCP HTTP server ready on port {mcp_server.port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global mcp_server
    
    if mcp_server:
        await mcp_server.shutdown()
    
    logger.info("MCP HTTP server shutdown complete")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_available": mcp_server is not None
    }


@app.post("/consult_governance", response_model=ConsultationResponse)
async def consult_governance(request: ConsultationRequest):
    """
    Consult governance for an operation.
    
    This is the main endpoint called by the Claude Code hook bridge.
    """
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")
    
    try:
        # Use the MCP server's consultation logic
        result = await mcp_server.server.tool()._registry['consult_governance'](
            request.operation,
            request.context
        )
        
        # Parse the JSON response
        governance_result = json.loads(result) if isinstance(result, str) else result
        
        # Build response
        response = ConsultationResponse(
            approved=governance_result.get('approved', True),
            confidence=governance_result.get('confidence', 0.5),
            recommendations=governance_result.get('recommendations', []),
            warnings=governance_result.get('warnings', []),
            persona_guidance=governance_result.get('persona_guidance', {}),
            block_reason=governance_result.get('block_reason'),
            remediation=governance_result.get('remediation'),
            correlation_id=request.correlation_id
        )
        
        # Log consultation
        logger.info(
            f"Governance consultation: operation={request.operation}, "
            f"approved={response.approved}, correlation_id={request.correlation_id}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Governance consultation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit_execution")
async def audit_execution(request: AuditRequest):
    """
    Audit an executed operation.
    
    Called by PostToolUse hook for audit trail.
    """
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")
    
    try:
        # Log to audit system (would go to database in production)
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": request.operation,
            "context": request.context,
            "correlation_id": request.correlation_id
        }
        
        # In production, this would write to database
        logger.info(f"Audit entry: {json.dumps(audit_entry)}")
        
        # Update metrics
        if hasattr(mcp_server, 'metrics'):
            mcp_server.metrics['total_requests'] += 1
        
        return {
            "status": "recorded",
            "correlation_id": request.correlation_id
        }
        
    except Exception as e:
        logger.error(f"Audit recording error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_governance_context")
async def get_governance_context(request: ContextRequest):
    """
    Get governance context for prompt injection.
    
    Called by UserPromptSubmit hook.
    """
    if not mcp_server:
        raise HTTPException(status_code=503, detail="MCP server not initialized")
    
    try:
        # Get current governance configuration
        config = get_config()
        governance_config = config.get_governance_config()
        
        # Build context based on operation and current state
        context = {
            "active_policies": governance_config.get('mode', 'standard'),
            "compliance_level": f"{governance_config.get('complianceLevel', 0.95) * 100}%",
            "restrictions": [],
            "recommendations": []
        }
        
        # Add operation-specific context
        if 'file' in request.operation.lower():
            context['restrictions'].append('validate file paths')
            context['recommendations'].append('use defensive file operations')
        
        if 'command' in request.operation.lower() or 'bash' in request.operation.lower():
            context['restrictions'].append('sanitize command inputs')
            context['recommendations'].append('use timeouts for commands')
        
        if 'production' in str(request.context).lower():
            context['restrictions'].append('no direct production changes')
            context['recommendations'].append('use staging environment first')
        
        return context
        
    except Exception as e:
        logger.error(f"Context generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get server metrics."""
    if not mcp_server:
        return {"error": "MCP server not initialized"}
    
    metrics = {
        "server_metrics": mcp_server.metrics,
        "cache_hit_rate": mcp_server._calculate_cache_hit_rate(),
        "uptime_seconds": (datetime.utcnow() - mcp_server.start_time).total_seconds(),
        "available_personas": len(mcp_server.personas.personas) if mcp_server.personas else 0
    }
    
    return metrics


@app.get("/personas")
async def get_personas():
    """Get available personas."""
    if not mcp_server or not mcp_server.personas:
        return {"error": "Personas not initialized"}
    
    return mcp_server.personas.get_all_personas()


# Error handling middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    
    # Add to request state
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Add correlation ID to response
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


def run_server():
    """Run the HTTP server."""
    config = get_config()
    server_config = config.get_server_config()
    
    host = server_config.get('host', '127.0.0.1')
    port = server_config.get('port', {}).get('preferred', 8001)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, server_config.get('log_level', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting MCP HTTP server on {host}:{port}")
    
    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=server_config.get('reload', False),
        log_level=server_config.get('log_level', 'INFO').lower()
    )


if __name__ == "__main__":
    run_server()