# SSL Certificate Checker Agent - Architecture & Error Handling

## Repository Structure

```
ssl_certificate_checker_agent/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application with middleware
│   ├── models/
│   │   ├── __init__.py            # Model exports
│   │   ├── a2a_models.py          # JSON-RPC 2.0 + A2A protocol models
│   │   ├── ssl_models.py          # SSL certificate data structures
│   │   └── error_models.py        # Error codes and response builders
│   ├── routes/
│   │   ├── __init__.py            # Router exports
│   │   ├── a2a_routes.py          # A2A SSL endpoint with error handling
│   │   └── general_routes.py     # Root, health, agent card endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── a2a_handler.py         # Request orchestration with error handling
│   │   ├── message_parser.py      # Natural language intent parsing
│   │   └── ssl_checker.py         # Core SSL verification logic
│   └── utils/
│       ├── __init__.py
│       └── formatters.py          # Response formatting for Telex
├── config/
│   └── agent.json                 # A2A Agent Card (well-known URL)
├── scripts/                       # Utility scripts (future)
├── tests/                         # Unit and integration tests
├── requirements.txt               # Python dependencies
├── ARCHITECTURE.md                # This file
└── get_started.md                # Implementation guide
```

## Design Pattern: Repository Pattern

### Layered Architecture

1. **Routes Layer** (`app/routes/`)
   - HTTP request/response handling
   - JSON-RPC 2.0 protocol validation
   - Error response formatting
   - Routing to appropriate handlers

2. **Service Layer** (`app/services/`)
   - Business logic orchestration
   - Domain-specific operations
   - Error handling and recovery
   - Data transformation

3. **Model Layer** (`app/models/`)
   - Data structures and validation
   - Protocol definitions
   - Error code definitions

4. **Utility Layer** (`app/utils/`)
   - Cross-cutting concerns
   - Formatting and presentation
   - Helper functions

### Benefits

- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Layers can be tested independently
- **Maintainability**: Changes are localized to specific layers
- **Scalability**: Easy to add new features or modify existing ones

## Error Handling Strategy

### JSON-RPC 2.0 Error Codes

The application implements standard JSON-RPC 2.0 error codes plus custom application-specific codes:

#### Standard Codes (JSON-RPC 2.0)

| Code | Name | Description |
|------|------|-------------|
| -32700 | `PARSE_ERROR` | Invalid JSON received |
| -32600 | `INVALID_REQUEST` | Invalid Request object |
| -32601 | `METHOD_NOT_FOUND` | Method does not exist |
| -32602 | `INVALID_PARAMS` | Invalid method parameters |
| -32603 | `INTERNAL_ERROR` | Internal JSON-RPC error |

#### Custom Application Codes (-32000 to -32099)

| Code | Name | Description |
|------|------|-------------|
| -32001 | `SSL_CONNECTION_ERROR` | Failed to connect to domain |
| -32002 | `SSL_CERTIFICATE_ERROR` | Certificate parsing error |
| -32003 | `DOMAIN_NOT_FOUND` | DNS resolution failed |
| -32004 | `TIMEOUT_ERROR` | Connection timeout |
| -32005 | `INVALID_DOMAIN` | Invalid domain format |

### Error Response Format

All errors follow JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "error": {
    "code": -32003,
    "message": "Domain not found: 'invalid-domain.xyz' could not be resolved (DNS error)",
    "data": {
      "domain": "invalid-domain.xyz"
    }
  }
}
```

### Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Request                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Routes Layer (a2a_routes.py)                    │
│  • Parse raw JSON                                            │
│  • Validate JSON-RPC structure                               │
│  • Check method                                              │
│  • Route to handler                                          │
│  • Catch all exceptions                                      │
│  • Return JSON-RPC compliant response                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│            Service Layer (a2a_handler.py)                    │
│  • Extract message parts                                     │
│  • Parse domain intent                                       │
│  • Orchestrate SSL checks                                    │
│  • Handle business logic errors                              │
│  • Format task results                                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│          SSL Checker Service (ssl_checker.py)                │
│  • Validate domain format                                    │
│  • Connect to domain:443                                     │
│  • Retrieve certificate                                      │
│  • Parse certificate data                                    │
│  • Handle connection/timeout errors                          │
│  • Return SSLCheckResult                                     │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Layer Error Handling

#### Layer 1: Route Level (`a2a_routes.py`)

Handles protocol-level errors:
- JSON parsing errors
- Request validation errors
- Method validation errors
- Global exception catching

```python
@router.post("/ssl")
async def a2a_ssl_endpoint(request: Request) -> JSONResponse:
    try:
        # Parse JSON
        body = await request.body()
        json_data = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(content=create_parse_error())
    
    try:
        # Validate request structure
        jsonrpc_request = JSONRPCRequest(**json_data)
    except ValidationError as e:
        return JSONResponse(content=create_invalid_request_error())
    
    # ... rest of handling
```

#### Layer 2: Handler Level (`a2a_handler.py`)

Handles business logic errors:
- Message parsing errors
- Domain validation errors
- SSL check orchestration errors

```python
async def handle_jsonrpc_request(self, request: JSONRPCRequest):
    try:
        # Extract and parse
        interpreted_text = self._extract_parts(message)
        
        if not interpreted_text:
            return JSONRPCResponse(
                error=create_invalid_params_error(...)
            )
    except ValueError as e:
        return JSONRPCResponse(
            error=create_error_response(
                A2AErrorCode.INVALID_PARAMS, str(e)
            )
        )
```

#### Layer 3: Service Level (`ssl_checker.py`)

Handles domain-specific errors:
- Connection timeouts
- DNS failures
- Certificate parsing errors

```python
async def check_domain(self, domain: str) -> SSLCheckResult:
    try:
        # Connect and retrieve certificate
        cert = self._get_certificate(domain)
        return SSLCheckResult(success=True, certificate=cert)
    except socket.timeout:
        return SSLCheckResult(
            success=False,
            error="Connection timeout"
        )
```

## Error Helper Functions

The `error_models.py` provides convenient helper functions:

```python
# Parse error (invalid JSON)
create_parse_error(request_id)

# Invalid request structure
create_invalid_request_error(request_id, details="Missing 'method' field")

# Method not found
create_method_not_found_error(request_id, method="unknown/method")

# Invalid parameters
create_invalid_params_error(request_id, details="No domain specified")

# Internal error
create_internal_error(request_id, details="Unexpected exception")

# SSL-specific errors
create_ssl_connection_error(request_id, domain, details)
create_domain_not_found_error(request_id, domain)
create_timeout_error(request_id, domain, timeout_seconds=10)
create_invalid_domain_error(request_id, domain, reason)
```

## Logging Strategy

Comprehensive logging at each layer:

```python
import logging

logger = logging.getLogger(__name__)

# Info: Normal operations
logger.info(f"Processing SSL check for {domain}")

# Warning: Recoverable issues
logger.warning(f"Domain parsing failed, trying fallback")

# Error: Expected errors
logger.error(f"SSL connection failed: {e}")

# Exception: Unexpected errors (includes stack trace)
logger.exception(f"Unexpected error: {e}")
```

## HTTP Status Codes

**Important**: JSON-RPC 2.0 always returns HTTP 200, even for errors!

- `200 OK`: All JSON-RPC responses (success or error)
- `500 Internal Server Error`: Only for catastrophic failures outside JSON-RPC

Actual errors are indicated in the JSON-RPC response body via the `error` field.

## Testing Error Handling

### Test Parse Error

```bash
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

### Test Invalid Request

```bash
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "123"}'
```

### Test Method Not Found

```bash
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "123",
    "method": "invalid/method"
  }'
```

## Best Practices

1. **Always use error helper functions** instead of manually creating error objects
2. **Log errors at the appropriate level** (info/warning/error/exception)
3. **Include context in error messages** (domain, action, etc.)
4. **Return structured errors** with `data` field for programmatic handling
5. **Use appropriate error codes** - standard for protocol, custom for domain logic
6. **Keep HTTP 200** for JSON-RPC responses
7. **Catch exceptions at the right layer** - don't let them bubble to FastAPI
8. **Provide helpful error messages** for end users via Telex

## Future Enhancements

- [ ] Error metrics and monitoring
- [ ] Rate limiting with custom error codes
- [ ] Retry logic for transient errors
- [ ] Error aggregation for batch operations
- [ ] Detailed error documentation endpoint
- [ ] Error code to HTTP status mapping for non-JSON-RPC clients

## Agent Card (A2A Discovery)

The agent card is a JSON specification that describes the agent's capabilities and metadata. It's served at the well-known URL `/.well-known/agent.json` following the A2A protocol standard.

### Agent Card Structure

```json
{
  "name": "SSL Certificate Checker",
  "description": "An AI agent that checks SSL/TLS certificates...",
  "url": "https://your-agent-domain.com/a2a",
  "version": "1.0.0",
  "provider": {
    "organization": "HNGi13",
    "url": "https://github.com/..."
  },
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {
      "id": "ssl_single_check",
      "name": "Single Domain SSL Check",
      "description": "Check SSL certificate for a single domain",
      "examples": [...]
    },
    {
      "id": "ssl_multiple_check",
      "name": "Multiple Domain SSL Check",
      "description": "Check SSL certificates for multiple domains",
      "examples": [...]
    }
  ]
}
```

### Agent Discovery Flow

1. **Telex discovers agent**: Requests `https://your-agent-domain.com/.well-known/agent.json`
2. **Agent returns card**: Describes capabilities, skills, and endpoints
3. **Telex registers agent**: Adds agent to available integrations
4. **User invokes agent**: Telex sends requests to `url` from agent card
5. **Agent responds**: Returns structured A2A responses

### Skills Definition

Each skill represents a specific capability:

- **ssl_single_check**: Check one domain's SSL certificate
- **ssl_multiple_check**: Check multiple domains simultaneously  
- **ssl_expiry_check**: Focus on expiration warnings

Skills include:
- Input/output modes (text/plain, application/json)
- Example inputs and outputs
- Descriptions for Telex UI

### Updating the Agent Card

When deploying, update these fields in `config/agent.json`:

```json
{
  "url": "https://your-actual-domain.com/a2a",
  "provider": {
    "organization": "Your Org Name",
    "url": "https://your-website.com"
  },
  "documentationUrl": "https://your-docs.com"
}
```

The agent card is automatically served by the `/well-known/agent.json` endpoint in `general_routes.py`.
