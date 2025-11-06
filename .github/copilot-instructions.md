# SSL Certificate Checker Agent - AI Coding Guidelines

## Project Overview
An **AI-powered A2A-compliant agent** for checking SSL/TLS certificates via Telex integration. Built with FastAPI and Google Gemini, implementing JSON-RPC 2.0 + A2A protocol for intelligent agent-to-agent communication.

## Architecture

### Core Components
```
app/
├── agents/
│   └── simple_ai_agent.py    # Google Gemini AI agent with SSL tools
├── models/
│   ├── a2a_models.py         # JSON-RPC 2.0 + A2A protocol models
│   └── ssl_models.py         # SSL certificate data structures
├── routes/
│   ├── a2a_routes.py         # A2A endpoint with AI integration
│   └── general_routes.py     # Health, agent card endpoints
├── services/
│   └── ssl_checker.py        # Synchronous SSL verification logic
└── main.py                   # FastAPI app with router registration
```

### Data Flow
1. Telex sends JSON-RPC 2.0 request to `/a2a/ssl`
2. `a2a_routes.py` extracts interpreted text (parts[0]) + conversation history (parts[1])
3. `SimpleAIAgent` processes message with Google Gemini and calls SSL tools
4. `ssl_checker.py` performs synchronous certificate validation
5. Response formatted as `TaskResult` with `artifacts` containing certificate data

## Protocol Implementation

### Telex Message Structure
Telex sends two-part messages:
- **parts[0]**: Interpreted text (primary source) - what Telex extracted for the agent
- **parts[1]**: Conversation history as DataPart with array - context/fallback

**Critical**: Always use `parts[0].text` as primary input. Only parse `parts[1].data` array if parts[0] is unclear.

### A2A Response Pattern
```python
TaskResult(
    id=taskId,                    # From request or generated
    contextId=f"ctx-{uuid4()}",   # New per request
    status=TaskStatus(
        state="completed",        # Or "input-required"/"failed"
        message=A2AMessage(       # Agent's response
            role="agent",
            parts=[TextPart(text=ai_formatted_result)]
        )
    ),
    artifacts=[                   # Structured data
        Artifact(name="ssl_certificate", parts=[DataPart(data=cert_dict)])
    ]
)
```

## Key Conventions

### AI Agent Implementation
- **Direct Gemini Integration**: Uses `google-genai` library, not Pydantic AI
- **Function Calling**: AI agent calls `check_ssl_single` and `check_ssl_multiple` tools
- **Conversation Context**: Maintains history for context-aware responses
- **Synchronous Operations**: SSL checking is synchronous to avoid event loop conflicts

### SSL Certificate Checking
- **Timeout**: 10 seconds default for socket connections
- **Warning threshold**: 30 days before expiration
- **Port**: 443 (configurable but not exposed in MVP)
- Use `ssl.create_default_context()` + `socket.create_connection()`
- Parse with `cryptography.x509.load_der_x509_certificate()`

### AI Message Processing
Support multiple natural language formats:
1. "Check SSL for domain.com"
2. "Check domain.com, domain2.com" (multiple)
3. "Is google.com's certificate expiring soon?"
4. "Compare SSL certificates for github.com and gitlab.com"

**Implementation**: Google Gemini handles intent extraction and tool calling automatically

### Response Formatting
- Use emoji markers: ✅ (valid), ❌ (expired), ⚠️ (expiring soon)
- Include countdown: "Days Left: X"
- Multi-domain: Show summary table with status column
- Always timestamp: "_Checked at {datetime.utcnow()}_"
- AI provides contextual explanations and insights

## Development Workflows

### Running Locally
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows

# Start the server
uvicorn app.main:app --reload --port 5001
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Google API key
GOOGLE_API_KEY=your-api-key-here
LLM_MODEL=gemini-2.0-flash-lite
```

### Testing A2A Endpoint
Use curl with full JSON-RPC structure:

```bash
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {"kind": "text", "text": "Check SSL for github.com"}
        ],
        "messageId": "msg-001"
      }
    }
  }'
```

### Dependencies
- `fastapi>=0.120.4` - Web framework
- `google-genai>=1.47.0` - Direct Google Gemini integration
- `cryptography>=46.0.3` - Certificate parsing
- `pydantic>=2.12.3` - Data validation
- `uvicorn>=0.38.0` - ASGI server

## Common Pitfalls

### AI Integration Issues
**WRONG**: Using Pydantic AI framework (causes integration issues)
**RIGHT**: Direct `google-genai` library integration

### Event Loop Conflicts
**WRONG**: Async SSL operations in FastAPI
**RIGHT**: Synchronous SSL checking to avoid event loop issues

### DataPart Type Handling
**WRONG**: `DataPart.data: Dict[str, Any]`
**RIGHT**: `DataPart.data: Union[Dict[str, Any], List[Any]]`

Telex sends conversation history as array in parts[1].

### Optional taskId
Don't require `taskId` in incoming messages - Telex may omit it. Generate with `f"task-{uuid4()}"` if missing.

### Certificate Expiry Calculation
```python
days_until_expiry = (cert.not_valid_after - datetime.utcnow()).days
is_expiring_soon = 0 < days_until_expiry <= 30  # Not if already expired
```

## Project-Specific Patterns

### AI Agent Architecture
- **SimpleAIAgent Class**: Main AI processing with Gemini client
- **Function Tools**: `check_ssl_single` and `check_ssl_multiple` for tool calling
- **Conversation History**: Context preservation across interactions
- **Error Handling**: Graceful degradation with informative messages

### Error Handling Strategy
Return structured errors in A2A format, never raise unhandled exceptions from endpoint:
- Socket timeout → `SSLCheckResult(success=False, error="Connection timeout")`
- DNS failure → `error="Domain not found (DNS error)"`
- Gemini API error → `error="AI processing failed"`
- Always wrap in `JSONRPCResponse` with proper `id` matching

### Artifacts vs Message Content
- **Message parts**: AI-formatted human-readable results with insights
- **Artifacts**: Structured data for programmatic use
- Single domain → 1 artifact with certificate dict
- Multiple domains → 1 artifact with summary + all results array

## Integration Notes

### Telex Registration
- Endpoint: `https://{your-domain}/a2a/ssl`
- Method: POST
- Protocol: JSON-RPC 2.0 + A2A
- Agent Card: `/.well-known/agent.json`
- No authentication in MVP (add Bearer token in production)

### Deployment (Railway)
```bash
railway init
railway up
railway domain
```

Update `config/agent.json` with your Railway URL before deployment.

## Reference Files
- **Architecture**: `ARCHITECTURE.md` - System design and patterns
- **AI Implementation**: `AI_ENHANCEMENT.md` - AI agent details and testing
- **Codebase Guide**: `CODEBASE.md` - Developer reference for all files
- **Setup Guide**: `get_started.md` - Development and deployment instructions
- **API Docs**: `README.md` - Complete usage and configuration guide

## Current Implementation Status
✅ **AI-Powered**: Direct Google Gemini integration with function calling
✅ **A2A Compliant**: Full JSON-RPC 2.0 + Telex protocol support
✅ **Production Ready**: Tested, deployed, and validated
✅ **Clean Architecture**: Modular design with clear separation of concerns
✅ **Well Documented**: Comprehensive guides for development and deployment
