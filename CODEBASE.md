# SSL Certificate Checker Agent - Codebase Reference

## Overview

This document provides a comprehensive reference for developers working on the SSL Certificate Checker Agent. It explains the purpose of each file, how components interact, and key implementation details.

## Core Architecture

The agent follows an **AI-first architecture** with clean separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   Routes        │    │   Services      │
│   (Gemini)      │◄──►│   (FastAPI)     │◄──►│   (Business     │
│                 │    │                 │    │    Logic)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Models        │    │   Configuration │    │   External      │
│   (Pydantic)    │    │   (.env, JSON)  │    │   APIs           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Directory Structure & Key Files

### `/app/` - Main Application Code

#### `main.py`
**Purpose**: FastAPI application entry point with minimal configuration
**Key Components**:
- FastAPI app initialization
- CORS middleware setup
- Router registration (A2A and general routes)
- Environment variable loading
- Server startup configuration

**Why Minimal?**: Follows clean architecture principles - main.py only orchestrates, doesn't contain business logic.

#### `/agents/simple_ai_agent.py`
**Purpose**: Google Gemini AI agent with SSL checking capabilities
**Key Components**:
- `SimpleAIAgent` class with Gemini integration
- Function calling tools for SSL operations
- Conversation history management
- Response formatting for A2A protocol

**Core Methods**:
- `process_message()`: Main entry point for AI processing
- `check_ssl_single()`: Tool for single domain checks
- `check_ssl_multiple()`: Tool for multiple domain checks

**AI Integration**:
```python
# Uses google-genai library directly (not Pydantic AI)
import google.genai as genai

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
model = client.models.generate_content(...)
```

#### `/routes/a2a_routes.py`
**Purpose**: A2A protocol endpoint handler for Telex integration
**Key Components**:
- `/a2a/ssl` POST endpoint
- JSON-RPC 2.0 request validation
- Telex message format parsing (`parts[0]` for interpreted text)
- AI agent integration
- TaskResult response formatting

**Request Flow**:
1. Validate JSON-RPC 2.0 format
2. Extract message from `params.message.parts[0].text`
3. Call AI agent with conversation context
4. Format response as `TaskResult` with artifacts

#### `/routes/general_routes.py`
**Purpose**: General API endpoints (health, agent card, root)
**Key Components**:
- `GET /` - API information
- `GET /health` - Health check endpoint
- `GET /.well-known/agent.json` - A2A agent discovery

#### `/services/ssl_checker.py`
**Purpose**: Core SSL certificate checking logic
**Key Components**:
- `SSLChecker` class with synchronous checking
- Certificate parsing using `cryptography` library
- Error handling for connection issues
- Domain validation and timeout management

**Core Method**:
```python
def check_certificate(self, domain: str) -> SSLCheckResult:
    # Synchronous SSL connection and certificate retrieval
    # Returns structured certificate data
```

**Important**: Uses synchronous operations to avoid event loop conflicts in FastAPI.

#### `/models/a2a_models.py`
**Purpose**: A2A protocol data models for Telex compatibility
**Key Components**:
- `JSONRPCRequest` - Incoming request structure
- `TaskResult` - A2A response format
- `A2AMessage` - Message wrapper with role/content
- `Artifact` - Structured data attachments
- `DataPart` - Flexible data container (dict/list)

**Telex Format Support**:
- `parts[0]`: Interpreted text (primary input)
- `parts[1]`: Conversation history (context)

#### `/models/ssl_models.py`
**Purpose**: SSL certificate data structures
**Key Components**:
- `SSLCertificate` - Certificate details
- `SSLCheckResult` - Check operation result
- `CertificateChain` - Certificate chain information

**Data Flow**:
```
cryptography.x509.Certificate → SSLCertificate → SSLCheckResult
```

#### `/models/error_models.py`
**Purpose**: Error handling and response models
**Key Components**:
- JSON-RPC 2.0 error codes
- Custom application error codes (-32001 to -32005)
- Error response builders

### `/config/` - Configuration Files

#### `agent.json`
**Purpose**: A2A agent card for Telex discovery
**Key Sections**:
- Agent metadata (name, description, version)
- Skills definition with examples
- Contact information
- API endpoint URLs

**Registration**: Used by Telex to discover and register the agent.

### Root Level Files

#### `.env` & `.env.example`
**Purpose**: Environment variable configuration
**Required Variables**:
- `GOOGLE_API_KEY` - Google Gemini API key
- `LLM_MODEL` - Model selection (gemini-2.0-flash-lite)

**Optional Variables**:
- Server configuration (HOST, PORT)
- SSL settings (SSL_TIMEOUT, WARNING_DAYS)
- AI model parameters (temperature, max_tokens)

#### `requirements.txt`
**Purpose**: Python dependencies
**Key Dependencies**:
- `fastapi` - Web framework
- `google-genai` - Google Gemini integration
- `cryptography` - Certificate parsing
- `pydantic` - Data validation
- `python-dotenv` - Environment loading

#### `test_a2a_request.json`
**Purpose**: Test payload for A2A endpoint validation
**Usage**: Used for manual testing and debugging

## Component Interactions

### Request Flow (A2A)

```
User Message → Telex → /a2a/ssl → a2a_routes.py → SimpleAIAgent → ssl_checker.py → Response
     ↓             ↓         ↓             ↓              ↓              ↓            ↓
  Natural      JSON-RPC   Validate     Extract        AI Process    SSL Check    TaskResult
  Language     2.0        Request      Message         & Tools       Certificate   + Artifacts
```

### AI Agent Workflow

1. **Message Reception**: Routes extract text from `parts[0]`
2. **AI Processing**: Gemini analyzes intent and calls appropriate tools
3. **Tool Execution**: SSL checker validates certificates synchronously
4. **Response Formatting**: Results formatted as A2A TaskResult with artifacts

### Error Handling Flow

```
Exception → Catch → Map to Error Code → JSON-RPC Error Response
     ↓         ↓         ↓                ↓
  Any Error  Routes/   -32001 to       {"jsonrpc": "2.0",
  (SSL, DNS,  Services  -32005         "error": {...}}
  Timeout, etc.)
```

## Key Design Decisions

### Synchronous SSL Checking
**Why?**: FastAPI runs on async event loop. SSL operations with timeouts work better synchronously to avoid complex async/await patterns.

### Direct Gemini Integration
**Why not Pydantic AI?**: Initial attempts with Pydantic AI had integration issues. Direct `google-genai` library provides more control and simpler implementation.

### Minimal main.py
**Why?**: Clean architecture principle. Main file should only orchestrate components, not contain business logic.

### A2A Protocol Compliance
**Why strict?**: Telex requires exact JSON-RPC 2.0 + A2A format. Deviations break integration.

## Development Workflow

### Adding New Features

1. **Models First**: Define data structures in `/models/`
2. **Service Logic**: Implement business logic in `/services/`
3. **AI Tools**: Add new tools to `SimpleAIAgent`
4. **Routes**: Expose via appropriate routes
5. **Configuration**: Update agent card skills
6. **Tests**: Add unit/integration tests

### Environment Setup

```bash
# 1. Clone and setup
git clone <repo>
cd ssl_certificate_checker_agent
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 3. Run locally
uvicorn app.main:app --reload --port 5001
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:5001/health

# Agent card
curl http://localhost:5001/.well-known/agent.json

# A2A SSL check (see test_a2a_request.json)
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d @test_a2a_request.json
```

## Common Issues & Solutions

### "Cannot run the event loop"
**Cause**: Async SSL operations conflicting with FastAPI's event loop
**Solution**: Use synchronous SSL checking in `ssl_checker.py`

### "TaskManager initialization error"
**Cause**: Pydantic AI integration issues
**Solution**: Use direct `google-genai` library instead

### A2A Protocol Format Errors
**Cause**: Incorrect TaskResult or artifact structure
**Solution**: Strictly follow Telex A2A specification in `a2a_models.py`

### Gemini API Errors
**Cause**: Invalid API key or model configuration
**Solution**: Verify `GOOGLE_API_KEY` and model name in `.env`

## File Dependencies

```
main.py
├── routes/
│   ├── a2a_routes.py
│   │   ├── agents/simple_ai_agent.py
│   │   │   ├── services/ssl_checker.py
│   │   │   └── models/ssl_models.py
│   │   └── models/a2a_models.py
│   └── general_routes.py
└── config/agent.json

Environment: .env → python-dotenv → os.getenv()
External APIs: google-genai → Gemini API
SSL: cryptography → Domain certificates
```

## Performance Considerations

- **SSL Timeouts**: 10-second default prevents hanging connections
- **Gemini Token Limits**: 2048 max tokens configured
- **Synchronous Operations**: SSL checking doesn't block event loop
- **Connection Pooling**: Not implemented (single checks are fast)

## Security Notes

- API keys stored in environment variables (not committed)
- SSL certificate validation uses system trust stores
- No sensitive data logging in production
- CORS configured for Telex domains

## Future Enhancements

- **Caching**: Certificate results caching to reduce API calls
- **Batch Processing**: Optimize multiple domain checks
- **Webhooks**: Certificate expiry notifications
- **Database**: Persistent certificate history
- **Metrics**: Monitoring and analytics

---

**For detailed implementation guides, see:**
- [AI_ENHANCEMENT.md](AI_ENHANCEMENT.md) - AI agent implementation details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture documentation
- [get_started.md](get_started.md) - Development setup guide