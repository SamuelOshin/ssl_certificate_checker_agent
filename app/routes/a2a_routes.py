"""
A2A Protocol Routes for Telex Integration
Handles JSON-RPC 2.0 wrapped A2A requests for SSL certificate checking
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.simple_ai_agent import ssl_agent
from app.models.a2a_models import (
    JSONRPCRequest,
    JSONRPCResponse,
    TaskResult,
    TaskStatus,
    A2AMessage,
    TextPart,
    DataPart,
    Artifact
)

router = APIRouter(tags=["A2A Protocol"])


@router.post("/a2a/ssl")
async def handle_ssl_a2a_request(request: JSONRPCRequest) -> JSONRPCResponse:
    """
    Handle A2A protocol SSL certificate checking requests (Telex format)

    Accepts JSON-RPC 2.0 wrapped requests with message/send method
    Expects Telex format: parts[0] = interpreted text, parts[1] = conversation history
    Returns JSON-RPC 2.0 wrapped TaskResult
    """
    try:
        # Extract message from request params
        params = request.params
        message = params.message

        # Extract user input following Telex A2A format
        user_text = ""
        conversation_history = []

        # parts[0] is interpreted text (primary source)
        if message.parts and len(message.parts) > 0:
            part_0 = message.parts[0]
            if hasattr(part_0, 'text'):
                user_text = part_0.text
            elif hasattr(part_0, 'data') and isinstance(part_0.data, str):
                user_text = part_0.data

        # parts[1] is conversation history (DataPart with array)
        if message.parts and len(message.parts) > 1:
            part_1 = message.parts[1]
            if hasattr(part_1, 'data') and isinstance(part_1.data, list):
                conversation_history = part_1.data

        if not user_text:
            raise HTTPException(status_code=400, detail="No text found in message parts")

        # Generate context and task IDs
        context_id = f"ctx-{uuid.uuid4()}"
        task_id = request.id or f"task-{uuid.uuid4()}"

        # Process with AI agent
        result = await ssl_agent.process_message(user_text, conversation_history)

        # Create response message
        response_message = A2AMessage(
            role="agent",
            parts=[TextPart(text=result.get("response", "SSL check completed"))],
            taskId=task_id
        )

        # Create artifacts from SSL check results
        artifacts = []
        if "artifacts" in result and result["artifacts"]:
            for artifact_data in result["artifacts"]:
                artifact_name = artifact_data.get("name", "ssl_result")
                artifact_content = artifact_data.get("data", {})

                # Create markdown summary
                if artifact_name == "check_ssl_certificate":
                    cert_data = artifact_content.get("certificate", {})
                    summary_text = f"""# SSL Certificate Check

**Domain:** {artifact_content.get('domain', 'N/A')}
**Status:** {'✅ Valid' if artifact_content.get('success', False) else '❌ Invalid'}
**Valid Until:** {cert_data.get('valid_until', 'N/A')}
**Days Remaining:** {cert_data.get('days_until_expiry', 'N/A')}

## Certificate Details
- **Issuer:** {cert_data.get('issuer', 'N/A')}
- **Subject:** {cert_data.get('subject', 'N/A')}
- **Valid From:** {cert_data.get('valid_from', 'N/A')}
"""
                elif artifact_name == "check_multiple_domains":
                    summary_text = f"""# Multiple Domain SSL Check

**Total Domains:** {artifact_content.get('total_domains', 0)}

## Results
"""
                    for domain_result in artifact_content.get('results', []):
                        summary_text += f"- **{domain_result.get('domain', 'N/A')}**: {domain_result.get('status', 'N/A')}"
                        if 'days_remaining' in domain_result:
                            summary_text += f" ({domain_result['days_remaining']} days)"
                        summary_text += "\n"
                else:
                    summary_text = f"**{artifact_name}**: {artifact_content.get('message', 'Completed')}"

                artifacts.append(Artifact(
                    name=artifact_name,
                    parts=[
                        TextPart(kind="text", text=summary_text),
                        DataPart(kind="data", data=artifact_content)
                    ]
                ))

        # Create task status
        status = TaskStatus(
            state="completed" if result.get("success", False) else "failed",
            message=response_message
        )

        # Create task result
        task_result = TaskResult(
            id=task_id,
            contextId=context_id,
            status=status,
            artifacts=artifacts,
            history=[response_message]
        )

        # Return JSON-RPC 2.0 response
        return JSONRPCResponse(
            jsonrpc="2.0",
            id=request.id,
            result=task_result
        )

    except Exception as e:
        # Return JSON-RPC 2.0 error
        error_response = JSONRPCResponse(
            jsonrpc="2.0",
            id=request.id or "error",
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )
        return error_response


