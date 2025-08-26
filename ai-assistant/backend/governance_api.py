#!/usr/bin/env python
"""
Governance API for UI Integration
Provides REST endpoints for managing data-driven governance from the UI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
from pathlib import Path

from data_driven_governance import (
    DataDrivenGovernanceOrchestrator,
    ExecutionMode,
    GovernanceResult
)

app = FastAPI(title="Governance API", version="5.0")

# Enable CORS for UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = DataDrivenGovernanceOrchestrator()

# Pydantic models for API

class ExecutionRequest(BaseModel):
    """Request to execute governance"""
    prompt: str
    mode: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    agents: Optional[List[str]] = None
    personas: Optional[List[str]] = None
    override_config: Optional[Dict[str, Any]] = None

class ConfigUpdateRequest(BaseModel):
    """Request to update configuration"""
    updates: Dict[str, Any]
    source: str = "ui"
    validate_before_apply: bool = True

class AgentConfig(BaseModel):
    """Agent configuration model"""
    id: str
    name: str
    enabled: bool = True
    personas_enabled: List[str] = Field(default_factory=list)
    execution_order: int = 0
    can_parallelize: bool = True
    intercepts: bool = False
    runs_after: List[str] = Field(default_factory=list)
    mandatory: bool = False

class PersonaConfig(BaseModel):
    """Persona configuration model"""
    id: str
    name: str
    role: str
    enabled: bool = True
    weight: float = 1.0
    keywords: List[str] = Field(default_factory=list)
    validations: Dict[str, bool] = Field(default_factory=dict)
    rules: Dict[str, Any] = Field(default_factory=dict)

class ValidationRuleConfig(BaseModel):
    """Validation rule configuration model"""
    name: str
    enabled: bool = True
    severity: str = "warning"
    patterns: List[str] = Field(default_factory=list)
    exceptions: List[str] = Field(default_factory=list)
    auto_fix: bool = False

class PromptInterceptionConfig(BaseModel):
    """Prompt interception configuration"""
    enabled: bool = True
    enhance_clarity: bool = True
    add_context: bool = True
    technical_precision: bool = True
    best_practices: bool = True
    distribution_mode: str = "all"  # all, selected, none

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Governance API",
        "version": "5.0",
        "status": "active",
        "endpoints": {
            "config": "/api/governance/config",
            "execute": "/api/governance/execute",
            "status": "/api/governance/status"
        }
    }

@app.get("/api/governance/config")
async def get_config():
    """Get current governance configuration"""
    return {
        "config": orchestrator.config,
        "status": orchestrator.get_status(),
        "validation": orchestrator.validate_config()
    }

@app.post("/api/governance/config/update")
async def update_config(request: ConfigUpdateRequest):
    """Update governance configuration"""
    # Validate if requested
    if request.validate_before_apply:
        # Create temp config for validation
        temp_config = orchestrator.config.copy()
        orchestrator._merge_config(temp_config, request.updates)
        
        valid, errors = orchestrator.validate_config(temp_config)
        if not valid:
            raise HTTPException(status_code=400, detail={
                "error": "Invalid configuration",
                "validation_errors": errors
            })
    
    # Apply updates
    success = orchestrator.update_config(request.updates, request.source)
    
    return {
        "success": success,
        "config": orchestrator.config,
        "status": orchestrator.get_status()
    }

@app.post("/api/governance/config/reset")
async def reset_config(to_defaults: bool = False):
    """Reset configuration to defaults or previous state"""
    success = orchestrator.reset_config(to_defaults)
    
    return {
        "success": success,
        "config": orchestrator.config,
        "status": orchestrator.get_status()
    }

@app.get("/api/governance/config/export")
async def export_config(format: str = "json"):
    """Export configuration in specified format"""
    if format not in ["json", "yaml", "python"]:
        raise HTTPException(status_code=400, detail="Invalid format. Use json, yaml, or python")
    
    exported = orchestrator.export_config(format)
    
    return {
        "format": format,
        "data": exported,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/governance/config/import")
async def import_config(config: Dict[str, Any]):
    """Import configuration"""
    valid, errors = orchestrator.validate_config(config)
    
    if not valid:
        raise HTTPException(status_code=400, detail={
            "error": "Invalid configuration",
            "validation_errors": errors
        })
    
    orchestrator.config = config
    orchestrator.save_config()
    
    return {
        "success": True,
        "config": orchestrator.config,
        "status": orchestrator.get_status()
    }

@app.get("/api/governance/agents")
async def get_agents():
    """Get all configured agents"""
    return {
        "agents": {
            agent_id: {
                "id": agent.id,
                "name": agent.name,
                "enabled": agent.enabled,
                "personas": agent.personas,
                "execution_order": agent.execution_order,
                "can_parallelize": agent.can_parallelize,
                "intercepts": agent.intercepts,
                "runs_after": agent.runs_after,
                "mandatory": agent.mandatory
            }
            for agent_id, agent in orchestrator.agents.items()
        }
    }

@app.post("/api/governance/agents/add")
async def add_agent(agent: AgentConfig):
    """Add a new agent"""
    # Add to config
    orchestrator.config['agents'][agent.id] = agent.dict()
    
    # Re-parse agents
    orchestrator.agents = orchestrator._parse_agents()
    
    # Save config
    orchestrator.save_config()
    
    return {
        "success": True,
        "agent": agent.dict(),
        "total_agents": len(orchestrator.agents)
    }

@app.delete("/api/governance/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in orchestrator.config['agents']:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Check if mandatory
    if orchestrator.agents[agent_id].mandatory:
        raise HTTPException(status_code=400, detail=f"Cannot delete mandatory agent {agent_id}")
    
    del orchestrator.config['agents'][agent_id]
    orchestrator.agents = orchestrator._parse_agents()
    orchestrator.save_config()
    
    return {
        "success": True,
        "deleted": agent_id,
        "remaining_agents": list(orchestrator.agents.keys())
    }

@app.get("/api/governance/personas")
async def get_personas():
    """Get all configured personas"""
    return {
        "personas": {
            persona_id: {
                "id": persona.id,
                "name": persona.name,
                "role": persona.role,
                "enabled": persona.enabled,
                "weight": persona.weight,
                "keywords": persona.keywords,
                "validations": persona.validations,
                "rules": persona.rules
            }
            for persona_id, persona in orchestrator.personas.items()
        }
    }

@app.post("/api/governance/personas/add")
async def add_persona(persona: PersonaConfig):
    """Add a new persona"""
    orchestrator.config['personas'][persona.id] = persona.dict()
    orchestrator.personas = orchestrator._parse_personas()
    orchestrator.save_config()
    
    return {
        "success": True,
        "persona": persona.dict(),
        "total_personas": len(orchestrator.personas)
    }

@app.patch("/api/governance/personas/{persona_id}/toggle")
async def toggle_persona(persona_id: str):
    """Enable/disable a persona"""
    if persona_id not in orchestrator.personas:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    
    current_state = orchestrator.personas[persona_id].enabled
    orchestrator.config['personas'][persona_id]['enabled'] = not current_state
    orchestrator.personas = orchestrator._parse_personas()
    orchestrator.save_config()
    
    return {
        "success": True,
        "persona": persona_id,
        "enabled": not current_state
    }

@app.get("/api/governance/rules")
async def get_validation_rules():
    """Get all validation rules"""
    return {
        "rules": {
            rule_name: {
                "name": rule.name,
                "enabled": rule.enabled,
                "severity": rule.severity,
                "patterns": rule.patterns,
                "exceptions": rule.exceptions,
                "auto_fix": rule.auto_fix
            }
            for rule_name, rule in orchestrator.validation_rules.items()
        }
    }

@app.post("/api/governance/rules/add")
async def add_validation_rule(rule: ValidationRuleConfig):
    """Add a new validation rule"""
    if 'validation_rules' not in orchestrator.config:
        orchestrator.config['validation_rules'] = {'global': {}}
    
    orchestrator.config['validation_rules']['global'][rule.name] = rule.dict()
    orchestrator.validation_rules = orchestrator._parse_validation_rules()
    orchestrator.save_config()
    
    return {
        "success": True,
        "rule": rule.dict(),
        "total_rules": len(orchestrator.validation_rules)
    }

@app.post("/api/governance/execute")
async def execute_governance(request: ExecutionRequest):
    """Execute governance with specified configuration"""
    # Apply temporary overrides if provided
    original_config = None
    if request.override_config:
        original_config = orchestrator.config.copy()
        orchestrator.update_config(request.override_config, "api")
    
    try:
        # Execute governance
        result = await orchestrator.execute(
            prompt=request.prompt,
            mode=request.mode,
            context=request.context
        )
        
        return {
            "success": result.success,
            "mode": result.mode,
            "agents_executed": result.agents_executed,
            "personas_executed": result.personas_executed,
            "violations": result.violations,
            "audit_results": result.audit_results,
            "prompt_transformations": result.prompt_transformations,
            "execution_time_ms": result.execution_time_ms,
            "metadata": result.metadata
        }
    
    finally:
        # Restore original config if overridden
        if original_config:
            orchestrator.config = original_config
            orchestrator.agents = orchestrator._parse_agents()
            orchestrator.personas = orchestrator._parse_personas()
            orchestrator.validation_rules = orchestrator._parse_validation_rules()

@app.get("/api/governance/status")
async def get_status():
    """Get current governance system status"""
    return orchestrator.get_status()

@app.post("/api/governance/prompt/intercept")
async def intercept_prompt(prompt: str, context: Optional[Dict[str, Any]] = None):
    """Test prompt interception and rewriting"""
    result = await orchestrator.prompt_interceptor.intercept_and_rewrite(prompt, context)
    
    return {
        "original": result['original'],
        "rewritten": result['rewritten'],
        "transformations": result['transformations'],
        "timestamp": result['timestamp']
    }

@app.get("/api/governance/modes")
async def get_execution_modes():
    """Get available execution modes"""
    return {
        "modes": [
            {
                "id": mode.value,
                "name": mode.name,
                "description": f"Execute with {mode.value.replace('_', ' ')}"
            }
            for mode in ExecutionMode
        ],
        "current_defaults": orchestrator.config.get('defaults', {})
    }

@app.post("/api/governance/test")
async def test_configuration(test_prompt: str = "Test governance system"):
    """Test current configuration with a sample prompt"""
    results = {}
    
    for mode in ExecutionMode:
        try:
            result = await orchestrator.execute(test_prompt, mode=mode.value)
            results[mode.value] = {
                "success": result.success,
                "agents": result.agents_executed,
                "personas": result.personas_executed,
                "violations": len(result.violations),
                "time_ms": result.execution_time_ms
            }
        except Exception as e:
            results[mode.value] = {
                "success": False,
                "error": str(e)
            }
    
    return {
        "test_prompt": test_prompt,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/governance/monitor")
async def monitor_governance(websocket):
    """WebSocket endpoint for real-time governance monitoring"""
    await websocket.accept()
    
    try:
        while True:
            # Send status updates every second
            status = orchestrator.get_status()
            await websocket.send_json({
                "type": "status",
                "data": status,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(1)
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    
    finally:
        await websocket.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "governance-api",
        "version": "5.0",
        "timestamp": datetime.now().isoformat()
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize governance system on startup"""
    print("Governance API v5.0 starting...")
    
    # Validate configuration
    valid, errors = orchestrator.validate_config()
    if not valid:
        print(f"Configuration validation errors: {errors}")
    
    print(f"Loaded {len(orchestrator.agents)} agents")
    print(f"Loaded {len(orchestrator.personas)} personas")
    print(f"Loaded {len(orchestrator.validation_rules)} validation rules")
    print("Governance API ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Saving governance configuration...")
    orchestrator.save_config()
    print("Governance API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)