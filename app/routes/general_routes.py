"""
General API routes (root, health, etc.)
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
from typing import Dict, Any
import os

router = APIRouter(tags=["General"])

# Path to agent card
AGENT_CARD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "agent.json"
)


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint - provides API information
    
    Returns:
        API metadata and usage examples
    """
    return {
        "name": "SSL Certificate Checker Agent",
        "version": "1.0.0",
        "description": "A2A-compliant SSL certificate monitoring agent",
        "protocol": "JSON-RPC 2.0 + A2A",
        "agentCard": "/.well-known/agent.json",
        "endpoints": {
            "a2a": "/a2a/ssl",
            "health": "/health",
            "docs": "/docs",
            "agentCard": "/.well-known/agent.json"
        },
        "examples": [
            "Check SSL for github.com",
            "Check github.com, google.com",
            "Check SSL certificate for example.com"
        ],
        "supported_methods": [
            "message/send"
        ],
        "skills": [
            "Single domain SSL check",
            "Multiple domain SSL check",
            "SSL expiry warnings"
        ]
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Global health check endpoint
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "ssl-certificate-checker-agent"
    }


@router.get("/.well-known/agent.json")
async def get_agent_card():
    """
    Agent Card endpoint - A2A protocol well-known URL
    
    Returns the agent card JSON file that describes the agent's
    capabilities, skills, and metadata for Telex integration.
    
    This follows the A2A protocol standard for agent discovery.
    """
    return FileResponse(
        AGENT_CARD_PATH,
        media_type="application/json",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600"
        }
    )

