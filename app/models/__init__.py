"""
Data models for SSL Certificate Checker Agent
Exports A2A protocol models, SSL models, and error handling models
"""
from app.models.a2a_models import (
    JSONRPCRequest,
    JSONRPCResponse,
    TaskResult,
    TaskStatus,
    A2AMessage,
    TextPart,
    DataPart,
    FilePart,
    Artifact
)
from app.models.ssl_models import (
    SSLCertificate,
    SSLCheckResult
)
from app.models.error_models import (
    A2AErrorCode,
    create_error_response,
    create_parse_error,
    create_invalid_request_error,
    create_method_not_found_error,
    create_invalid_params_error,
    create_internal_error
)

__all__ = [
    # A2A Models
    "JSONRPCRequest",
    "JSONRPCResponse",
    "TaskResult",
    "TaskStatus",
    "A2AMessage",
    "TextPart",
    "DataPart",
    "FilePart",
    "Artifact",
    # SSL Models
    "SSLCertificate",
    "SSLCheckResult",
    # Error Models
    "A2AErrorCode",
    "create_error_response",
    "create_parse_error",
    "create_invalid_request_error",
    "create_method_not_found_error",
    "create_invalid_params_error",
    "create_internal_error"
]
