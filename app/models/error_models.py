"""
Error models and utilities for A2A protocol
Implements JSON-RPC 2.0 error codes and A2A-specific error handling
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class A2AErrorCode(Enum):
    """JSON-RPC 2.0 standard error codes"""
    PARSE_ERROR = -32700       # Invalid JSON
    INVALID_REQUEST = -32600   # Invalid Request object
    METHOD_NOT_FOUND = -32601  # Method does not exist
    INVALID_PARAMS = -32602    # Invalid method parameters
    INTERNAL_ERROR = -32603    # Internal JSON-RPC error
    
    # Custom application errors (range: -32000 to -32099)
    SSL_CONNECTION_ERROR = -32001
    SSL_CERTIFICATE_ERROR = -32002
    DOMAIN_NOT_FOUND = -32003
    TIMEOUT_ERROR = -32004
    INVALID_DOMAIN = -32005


class JSONRPCErrorDetail(BaseModel):
    """JSON-RPC 2.0 Error object"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Complete JSON-RPC error response"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    error: JSONRPCErrorDetail


def create_error_response(
    request_id: Optional[str],
    code: A2AErrorCode,
    message: str,
    data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Create a JSON-RPC 2.0 compliant error response
    
    Args:
        request_id: The request ID from the original request (can be None for parse errors)
        code: The error code from A2AErrorCode enum
        message: Human-readable error message
        data: Optional additional error data
        
    Returns:
        Dictionary representing the error response
    """
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code.value,
            "message": message,
            "data": data or {}
        }
    }


def create_parse_error(request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a parse error response (invalid JSON)"""
    return create_error_response(
        request_id,
        A2AErrorCode.PARSE_ERROR,
        "Parse error: Invalid JSON was received"
    )


def create_invalid_request_error(request_id: Optional[str] = None, details: str = "") -> Dict[str, Any]:
    """Create an invalid request error response"""
    message = "Invalid Request: The JSON sent is not a valid Request object"
    if details:
        message += f" - {details}"
    return create_error_response(
        request_id,
        A2AErrorCode.INVALID_REQUEST,
        message
    )


def create_method_not_found_error(request_id: str, method: str) -> Dict[str, Any]:
    """Create a method not found error response"""
    return create_error_response(
        request_id,
        A2AErrorCode.METHOD_NOT_FOUND,
        f"Method not found: '{method}' is not a valid method",
        {"method": method}
    )


def create_invalid_params_error(request_id: str, details: str) -> Dict[str, Any]:
    """Create an invalid parameters error response"""
    return create_error_response(
        request_id,
        A2AErrorCode.INVALID_PARAMS,
        f"Invalid params: {details}"
    )


def create_internal_error(request_id: str, details: str = "") -> Dict[str, Any]:
    """Create an internal error response"""
    message = "Internal error"
    if details:
        message += f": {details}"
    return create_error_response(
        request_id,
        A2AErrorCode.INTERNAL_ERROR,
        message
    )


def create_ssl_connection_error(request_id: str, domain: str, details: str = "") -> Dict[str, Any]:
    """Create an SSL connection error response"""
    message = f"SSL connection error for domain '{domain}'"
    if details:
        message += f": {details}"
    return create_error_response(
        request_id,
        A2AErrorCode.SSL_CONNECTION_ERROR,
        message,
        {"domain": domain, "details": details}
    )


def create_domain_not_found_error(request_id: str, domain: str) -> Dict[str, Any]:
    """Create a domain not found error response"""
    return create_error_response(
        request_id,
        A2AErrorCode.DOMAIN_NOT_FOUND,
        f"Domain not found: '{domain}' could not be resolved (DNS error)",
        {"domain": domain}
    )


def create_timeout_error(request_id: str, domain: str, timeout_seconds: int = 10) -> Dict[str, Any]:
    """Create a timeout error response"""
    return create_error_response(
        request_id,
        A2AErrorCode.TIMEOUT_ERROR,
        f"Connection timeout: '{domain}' did not respond within {timeout_seconds} seconds",
        {"domain": domain, "timeout": timeout_seconds}
    )


def create_invalid_domain_error(request_id: str, domain: str, reason: str = "") -> Dict[str, Any]:
    """Create an invalid domain error response"""
    message = f"Invalid domain: '{domain}'"
    if reason:
        message += f" - {reason}"
    return create_error_response(
        request_id,
        A2AErrorCode.INVALID_DOMAIN,
        message,
        {"domain": domain, "reason": reason}
    )
