#!/usr/bin/env python3
"""
Governance Configuration Management API

FastAPI endpoints for managing documentation standards and governance
configuration through the UI.

Author: Dr. Sarah Chen & Alex Novak
Created: 2025-09-03
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import yaml
import json
import sys

# Add governance modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "governance"))

from governance.core.template_renderer import DocumentTemplateRenderer
from governance.core.exemption_manager import DocumentationExemptionManager


# Pydantic models for API
class DocumentSection(BaseModel):
    """Document section configuration"""
    section: str
    level: int = 2
    required: bool = True
    weight: int = 10
    description: str = ""
    template: str = ""
    validation: Dict[str, Any] = {}


class DocumentTypeConfig(BaseModel):
    """Document type configuration"""
    description: str
    file_pattern: str
    priority: int = 1
    required_sections: List[DocumentSection]


class ExemptionRequest(BaseModel):
    """Request to add/modify exemption"""
    path: str
    exemption_type: str = Field(default="full", description="full or section")
    pattern_type: str = Field(default="exact", description="exact, glob, or regex")
    reason: str = "Manual exemption via UI"
    expires: Optional[str] = None
    exempt_sections: Optional[List[str]] = None


class ValidationRequest(BaseModel):
    """Request to validate documentation"""
    file_path: str
    content: Optional[str] = None


# Create router
router = APIRouter(prefix="/api/governance/documentation", tags=["governance"])

# Global instances
template_renderer: Optional[DocumentTemplateRenderer] = None
exemption_manager: Optional[DocumentationExemptionManager] = None


def initialize_managers():
    """Initialize the governance managers"""
    global template_renderer, exemption_manager
    
    config_path = Path(__file__).parent.parent.parent.parent / "governance" / "documentation_standards.yaml"
    
    template_renderer = DocumentTemplateRenderer(config_path)
    exemption_manager = DocumentationExemptionManager(config_path)


@router.on_event("startup")
async def startup_event():
    """Initialize managers on startup"""
    initialize_managers()


@router.get("/standards")
async def get_documentation_standards():
    """
    Get current documentation standards configuration.
    
    Returns:
        Complete documentation standards configuration
    """
    try:
        if not template_renderer:
            initialize_managers()
        
        return JSONResponse(
            content=template_renderer.get_api_response(),
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/standards")
async def update_documentation_standards(config: Dict[str, Any] = Body(...)):
    """
    Update documentation standards configuration.
    
    Args:
        config: New configuration to save
        
    Returns:
        Success status
    """
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "governance" / "documentation_standards.yaml"
        
        # Validate configuration structure
        required_keys = ['version', 'document_types', 'validation_rules', 'exemptions']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Add metadata
        config['metadata'] = config.get('metadata', {})
        config['metadata']['last_updated'] = datetime.now().isoformat()
        config['metadata']['updated_via'] = 'UI API'
        
        # Save configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        
        # Reload managers
        initialize_managers()
        
        return JSONResponse(
            content={"status": "success", "message": "Configuration updated successfully"},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate")
async def validate_document(request: ValidationRequest):
    """
    Validate a document against standards.
    
    Args:
        request: Validation request with file path and optional content
        
    Returns:
        Validation result
    """
    try:
        if not template_renderer:
            initialize_managers()
        
        file_path = Path(request.file_path)
        
        # Determine document type
        doc_type = None
        for dtype, config in template_renderer.config.get('document_types', {}).items():
            if config.get('file_pattern') == file_path.name:
                doc_type = dtype
                break
        
        if not doc_type:
            return JSONResponse(
                content={
                    "valid": False,
                    "error": f"Unknown document type for {file_path.name}"
                },
                status_code=400
            )
        
        # Validate document
        if request.content:
            # Validate provided content
            result = template_renderer.validate_document(doc_type, request.content)
        else:
            # Read and validate file
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")
            
            content = file_path.read_text(encoding='utf-8')
            result = template_renderer.validate_document(doc_type, content)
        
        return JSONResponse(content=result, status_code=200)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/exemptions")
async def get_exemptions():
    """
    Get all active exemptions.
    
    Returns:
        List of all exemptions
    """
    try:
        if not exemption_manager:
            initialize_managers()
        
        return JSONResponse(
            content=exemption_manager.get_api_response(),
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exemptions")
async def add_exemption(exemption: ExemptionRequest):
    """
    Add a new exemption.
    
    Args:
        exemption: Exemption details
        
    Returns:
        Success status
    """
    try:
        if not exemption_manager:
            initialize_managers()
        
        success = exemption_manager.add_exemption(
            path=exemption.path,
            exemption_type=exemption.exemption_type,
            pattern_type=exemption.pattern_type,
            reason=exemption.reason,
            expires=exemption.expires,
            exempt_sections=exemption.exempt_sections
        )
        
        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Exemption added for {exemption.path}"
                },
                status_code=201
            )
        else:
            raise ValueError("Failed to add exemption")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/exemptions/{path:path}")
async def remove_exemption(path: str, exemption_type: str = "full"):
    """
    Remove an exemption.
    
    Args:
        path: Path to remove exemption for
        exemption_type: Type of exemption to remove
        
    Returns:
        Success status
    """
    try:
        if not exemption_manager:
            initialize_managers()
        
        success = exemption_manager.remove_exemption(path, exemption_type)
        
        if success:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": f"Exemption removed for {path}"
                },
                status_code=200
            )
        else:
            raise ValueError("Failed to remove exemption")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/{document_type}")
async def get_document_template(document_type: str, variables: Optional[Dict[str, Any]] = None):
    """
    Get a rendered document template.
    
    Args:
        document_type: Type of document template
        variables: Optional variables for rendering
        
    Returns:
        Rendered template
    """
    try:
        if not template_renderer:
            initialize_managers()
        
        if document_type not in template_renderer.list_document_types():
            raise ValueError(f"Unknown document type: {document_type}")
        
        template = template_renderer.render_document(document_type, variables or {})
        
        return JSONResponse(
            content={
                "document_type": document_type,
                "template": template,
                "structure": template_renderer.get_document_structure(document_type)
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/document-types")
async def list_document_types():
    """
    List all available document types.
    
    Returns:
        List of document types with their configurations
    """
    try:
        if not template_renderer:
            initialize_managers()
        
        types = {}
        for doc_type in template_renderer.list_document_types():
            types[doc_type] = template_renderer.get_document_structure(doc_type)
        
        return JSONResponse(content=types, status_code=200)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document-types/{document_type}")
async def add_document_type(document_type: str, config: DocumentTypeConfig):
    """
    Add a new document type.
    
    Args:
        document_type: Name of the new document type
        config: Configuration for the document type
        
    Returns:
        Success status
    """
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "governance" / "documentation_standards.yaml"
        
        # Load current config
        with open(config_path, 'r', encoding='utf-8') as f:
            current_config = yaml.safe_load(f)
        
        # Add new document type
        current_config['document_types'][document_type] = config.dict()
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(current_config, f, default_flow_style=False, sort_keys=False)
        
        # Reload managers
        initialize_managers()
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Document type '{document_type}' added successfully"
            },
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/document-types/{document_type}")
async def remove_document_type(document_type: str):
    """
    Remove a document type.
    
    Args:
        document_type: Name of the document type to remove
        
    Returns:
        Success status
    """
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "governance" / "documentation_standards.yaml"
        
        # Load current config
        with open(config_path, 'r', encoding='utf-8') as f:
            current_config = yaml.safe_load(f)
        
        # Remove document type
        if document_type in current_config['document_types']:
            del current_config['document_types'][document_type]
        else:
            raise ValueError(f"Document type '{document_type}' not found")
        
        # Save updated config
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(current_config, f, default_flow_style=False, sort_keys=False)
        
        # Reload managers
        initialize_managers()
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Document type '{document_type}' removed successfully"
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Export router for inclusion in main app
__all__ = ['router']