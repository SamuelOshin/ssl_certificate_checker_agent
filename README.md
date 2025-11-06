# SSL Certificate Checker Agent 🔐🤖

An **AI-powered A2A-compliant agent** for checking SSL/TLS certificates via Telex integration. Built with FastAPI and Google Gemini, implementing JSON-RPC 2.0 + A2A protocol for intelligent agent-to-agent communication.

## Features

✅ **AI-Powered Analysis** - Natural language understanding with Google Gemini  
✅ **Certificate Validation** - Check if SSL certificates are valid  
📅 **Expiration Tracking** - Get expiration dates with countdown  
🏢 **Issuer Information** - Display certificate issuer details  
⚠️ **Expiry Warnings** - Alert when certificates expire within 30 days  
🔄 **Multi-Domain Support** - Check multiple domains simultaneously  
📊 **Detailed Reports** - Key size, algorithms, SANs, and more  
🤖 **Conversational Interface** - Ask questions in natural language  

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- Virtual environment (recommended)
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ssl_certificate_checker_agent.git
cd ssl_certificate_checker_agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Google Gemini Setup

1. **Get your Google Gemini API key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Copy the API key

2. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API key
   # GOOGLE_API_KEY=your-actual-api-key-here
   ```

3. **Update model configuration** (optional):
   ```env
   # Choose your preferred Gemini model
   LLM_MODEL=gemini-2.0-flash-lite  # Fast and efficient
   # LLM_MODEL=gemini-1.5-pro       # More capable but slower
   # LLM_MODEL=gemini-1.5-flash     # Balanced performance
   ```

### Running Locally

```bash
# Start the server
uvicorn app.main:app --reload --port 5001

# Server will be available at:
# http://localhost:5001
```

### API Endpoints

- **Root**: `GET /` - API information
- **Agent Card**: `GET /.well-known/agent.json` - A2A agent discovery
- **Health**: `GET /health` - Health check
- **A2A SSL Endpoint**: `POST /a2a/ssl` - AI-powered SSL certificate checking
- **API Docs**: `GET /docs` - Interactive API documentation

## Usage

### Via Telex (AI-Powered)

1. Register the agent in Telex using the agent card URL:
   ```
   https://your-domain.com/.well-known/agent.json
   ```

2. Chat with the AI agent in natural language:
   ```
   Check SSL for github.com
   Is google.com's certificate expiring soon?
   Check github.com, google.com, and stackoverflow.com certificates
   What happens if a certificate expires?
   Compare SSL certificates for these domains: api.example.com, www.example.com
   ```

### Via cURL (Testing)

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
          {
            "kind": "text",
            "text": "Check SSL for github.com"
          }
        ],
        "messageId": "msg-001"
      }
    }
  }'
```

## Architecture

### Repository Structure

```
ssl_certificate_checker_agent/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── simple_ai_agent.py  # Google Gemini AI agent with SSL tools
│   │   └── __init__.py
│   ├── models/                 # Data models
│   │   ├── a2a_models.py       # A2A protocol models
│   │   ├── ssl_models.py       # SSL certificate models
│   │   └── error_models.py     # Error handling models
│   ├── routes/                 # API routes
│   │   ├── a2a_routes.py       # A2A endpoint with AI integration
│   │   └── general_routes.py   # General endpoints
│   ├── services/               # Business logic
│   │   └── ssl_checker.py      # SSL checking service
│   └── utils/                  # Utilities
├── config/
│   └── agent.json              # Agent card configuration
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── AI_ENHANCEMENT.md           # AI agent implementation details
├── ARCHITECTURE.md             # Detailed architecture docs
└── get_started.md             # Implementation guide
```

### AI Agent Architecture

The application follows an **AI-first architecture** with layered design:

1. **AI Agent Layer** (`app/agents/`)
   - Google Gemini integration with function calling
   - Natural language processing and intent extraction
   - SSL certificate analysis tools

2. **Routes Layer** (`app/routes/`)
   - A2A protocol endpoint handling
   - JSON-RPC 2.0 request/response processing
   - Error handling and response formatting

3. **Service Layer** (`app/services/`)
   - Core SSL certificate checking logic
   - Synchronous certificate validation
   - Error handling and recovery

4. **Model Layer** (`app/models/`)
   - Pydantic data validation models
   - A2A protocol structures
   - SSL certificate data structures

See [AI_ENHANCEMENT.md](AI_ENHANCEMENT.md) for detailed AI agent implementation and [ARCHITECTURE.md](ARCHITECTURE.md) for system architecture.

## Error Handling

The agent implements robust error handling with JSON-RPC 2.0 error codes:

### Standard Error Codes

- `-32700` - Parse error (invalid JSON)
- `-32600` - Invalid request
- `-32601` - Method not found
- `-32602` - Invalid parameters
- `-32603` - Internal error

### Custom Application Codes

- `-32001` - SSL connection error
- `-32002` - SSL certificate error
- `-32003` - Domain not found
- `-32004` - Timeout error
- `-32005` - Invalid domain

All errors are returned in JSON-RPC 2.0 compliant format with helpful messages.

## Configuration

### Agent Card

Update `config/agent.json` before deployment:

```json
{
  "url": "https://your-actual-domain.com/a2a",
  "provider": {
    "organization": "Your Organization",
    "url": "https://your-website.com"
  },
  "documentationUrl": "https://your-docs.com"
}
```

### Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
# Google Gemini API Configuration (Required)
GOOGLE_API_KEY=your-google-gemini-api-key-here

# AI Model Settings
LLM_MODEL=gemini-2.0-flash-lite
GEMINI_MODEL=google-gla:gemini-2.0-flash-lite
GEMINI_TEMPERATURE=0.3
GEMINI_MAX_TOKENS=2048
GEMINI_THINKING_BUDGET=0

# Server Configuration
HOST=0.0.0.0
PORT=5001

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO

# SSL Checker Configuration
SSL_TIMEOUT=10
WARNING_DAYS=30

# CORS Configuration
ALLOWED_ORIGINS=*

# A2A Server Settings
A2A_PATH_PREFIX=/a2a/ssl
ENABLE_STREAMING=true
```

**Required Environment Variables:**
- `GOOGLE_API_KEY`: Your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

**Optional Environment Variables:**
- `LLM_MODEL`: Choose your preferred Gemini model (`gemini-2.0-flash-lite`, `gemini-1.5-pro`, `gemini-1.5-flash`)
- `SSL_TIMEOUT`: Connection timeout in seconds (default: 10)
- `WARNING_DAYS`: Days before expiration to show warnings (default: 30)

## Deployment

### Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Deploy:
   ```bash
   railway up
   ```

4. Get your URL:
   ```bash
   railway domain
   ```

5. Update `config/agent.json` with your Railway URL

### Docker

```bash
# Build
docker build -t ssl-checker-agent .

# Run
docker run -p 5001:5001 ssl-checker-agent
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/
```

### Adding New Features

1. Update models in `app/models/`
2. Implement service logic in `app/services/`
3. Add routes in `app/routes/`
4. Update agent card skills in `config/agent.json`
5. Add tests in `tests/`

## AI Agent Skills

The AI agent provides intelligent SSL certificate analysis with natural language understanding:

### 🤖 Conversational SSL Analysis
Ask questions in natural language and get intelligent responses:

**Examples**:
- "Check SSL for github.com"
- "Is google.com's certificate expiring soon?"
- "What happens if a certificate expires?"
- "Compare SSL certificates for github.com and gitlab.com"
- "Check these domains: api.example.com, www.example.com, dev.example.com"

### 🔍 Single Domain Analysis
Get comprehensive SSL certificate information for one domain:
- Certificate validity status
- Expiration date and countdown
- Issuer information (Let's Encrypt, DigiCert, etc.)
- Security details (key size, algorithms, SANs)
- Chain validation status

### 📊 Multiple Domain Comparison
Check multiple domains simultaneously with comparative analysis:
- Summary table with status overview
- Individual certificate details
- Bulk expiry warnings
- Comparative security analysis

### ⚠️ Intelligent Expiry Monitoring
Smart expiration tracking with contextual warnings:
- Days remaining until expiration
- Priority alerts for certificates expiring soon
- Batch monitoring capabilities
- Proactive renewal recommendations

## Troubleshooting

### Common Issues

**Connection Timeout**
- Increase `SSL_TIMEOUT` in configuration
- Check firewall/network settings

**DNS Resolution Failed**
- Verify domain name is correct
- Check DNS server availability

**Certificate Parse Error**
- Domain may not have SSL/TLS enabled
- Certificate may be malformed

### Debug Mode

Run with debug logging:

```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload --port 5001
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Resources

- [A2A Protocol Specification](https://docs.telex.im/docs/telex-developers/building-agents/overview)
- [Telex Documentation](https://docs.telex.im/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

## Support

For issues and questions:
- Open an issue on GitHub
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
- Review [get_started.md](get_started.md) for implementation guide

---

**Built with ❤️ for HNGi13**
