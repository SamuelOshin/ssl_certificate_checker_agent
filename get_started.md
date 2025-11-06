# SSL Certificate Checker Agent - Final Correct Implementation
SSL Certificate Checker Agent - Implementation Plan
📋 Project Overview
What This Agent Does
An AI agent that checks SSL/TLS certificates for any domain and provides:

✅ Certificate validity status
📅 Expiration date and countdown
🏢 Issuer information (Let's Encrypt, DigiCert, etc.)
🔐 Security grade (A+, A, B, etc.)
⚠️ Warnings for certificates expiring soon
🔄 Chain validation
📊 Certificate details (SANs, algorithms, key size)

Why This Is Valuable
For IT Teams:

Prevents production outages from expired certificates
Monitors multiple domains from one place
Proactive renewal reminders
Quick debugging of SSL issues

Business Impact:

Cost Savings: Prevents downtime ($5,000+ per hour for many businesses)
Security: Ensures proper SSL configuration
Compliance: Helps meet security requirements
Peace of Mind: Automated monitoring

Real-World Use Case
Before (Manual):
1. Developer remembers to check SSL → Maybe once a month
2. Opens browser → 30 seconds
3. Checks certificate details → 2 minutes
4. Records expiration date → 1 minute
5. Forgets to check again → Certificate expires
6. Production down → $$$$$
After (Automated Agent):
1. Scheduled check runs daily → Automatic
2. Agent checks all domains → 5 seconds each
3. Posts to Telex if expiring soon → Instant
4. Team gets 30-day warning → No outages
5. SSL renewed before expiration → Happy users

🎯 Project Goals
Primary Features (MVP)

✅ Check SSL certificate for any domain
✅ Show expiration date with countdown
✅ Display issuer and basic details
✅ Warn if expiring within 30 days
✅ Post results to Telex channel

Advanced Features (Phase 2)

🔄 Schedule automatic daily checks
📊 Track certificate history
🌍 Check from multiple locations
🔗 Validate certificate chain
📈 Security grade calculation
🚨 Alert escalation for critical issues

Success Metrics

Response Time: < 3 seconds per domain
Accuracy: 100% correct expiration dates
Uptime: 99.9% agent availability
Adoption: Team checks 10+ domains/week


🏗️ Architecture
High-Level Flow
┌─────────────────────┐
│  User in Telex      │
│  "Check SSL for     │
│   api.example.com"  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Telex (A2A Client)                 │
│  Sends JSON-RPC request to agent    │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  SSL Checker Agent (FastAPI)        │
│  ┌───────────────────────────────┐  │
│  │ 1. Parse domain from request  │  │
│  │ 2. Connect to domain via SSL  │  │
│  │ 3. Extract certificate data   │  │
│  │ 4. Analyze expiration/issuer  │  │
│  │ 5. Format results             │  │
│  │ 6. Return A2A response        │  │
│  └───────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Results posted to  │
│  Telex channel      │
│  with formatting    │
└─────────────────────┘
Component Breakdown
1. SSL Connection Handler

Connects to domain on port 443
Retrieves SSL certificate
Handles timeouts and errors
No external API needed!

2. Certificate Parser

Extracts certificate fields
Calculates expiration countdown
Validates certificate chain
Checks Subject Alternative Names (SANs)

3. Security Analyzer

Checks cipher suites
Validates key strength
Assesses protocol version
Assigns security grade

4. A2A Service

Receives requests from Telex
Coordinates SSL check
Formats response
Returns structured data
## Project Structure
/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration
│   │   └── logging.py               # Logging setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ssl.py                   # SSL certificate models
│   │   └── a2a.py                   # A2A protocol models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── request.py               # Request schemas
│   │   └── response.py              # Response schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ssl_checker.py           # Core SSL checking logic
│   │   ├── certificate_analyzer.py   # Certificate analysis
│   │   ├── security_grader.py       # Security grading
│   │   ├── a2a_service.py           # A2A protocol handler
│   │   └── scheduler_service.py     # Optional: automated checks
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── a2a.py                   # A2A endpoints
│   │   ├── jsonrpc.py               # JSON-RPC endpoint
│   │   └── health.py                # Health checks
│   │
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py            # Output formatting
│       ├── validators.py            # Domain validation
│       └── date_utils.py            # Date calculations
│
├── config/
│   ├── agent_card.json              # A2A Agent Card
│   └── monitored_domains.json      # Optional: domain list
│
├── tests/
│   ├── __init__.py
│   ├── test_ssl_checker.py
│   ├── test_certificate_analyzer.py
│   └── test_a2a_integration.py
│
├── scripts/
│   ├── test_ssl_check.py            # Manual testing script
│   └── add_domain.py                # Add domains to monitor
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
## 🎯 Correct Structure (JSON-RPC 2.0 + A2A Protocol)

Based on the blog post https://fynix.dev/blog/a2a-python-fastapi, Telex sends **JSON-RPC 2.0 requests** with A2A messages inside the `params`.

### Request Format (from Telex)
```json
{
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
      "messageId": "msg-001",
      "taskId": "task-001"
    },
    "configuration": {
      "blocking": true
    }
  }
}
```

### Response Format (to Telex)
```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "id": "task-001",
    "contextId": "context-id",
    "status": {
      "state": "input-required",
      "timestamp": "2025-01-30T10:30:00.000Z",
      "message": {
        "messageId": "msg-uuid",
        "role": "agent",
        "parts": [
          {
            "kind": "text",
            "text": "✅ SSL Certificate: github.com..."
          }
        ],
        "kind": "message",
        "taskId": "task-001"
      }
    },
    "artifacts": [
      {
        "artifactId": "artifact-uuid",
        "name": "ssl_certificate",
        "parts": [
          {
            "kind": "data",
            "data": { /* certificate data */ }
          }
        ]
      }
    ],
    "history": [],
    "kind": "task"
  }
}
```

---

## 🔧 Correct Implementation

### Step 1: Complete Models

Create `app/models/a2a_models.py`:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
from uuid import uuid4

# ============= Message Parts =============
class TextPart(BaseModel):
    """Text content part"""
    kind: Literal["text"] = "text"
    text: str

class DataPart(BaseModel):
    """Data content part - can contain conversation history"""
    kind: Literal["data"] = "data"
    data: Union[Dict[str, Any], List[Any]]  # Can be dict or array

class FilePart(BaseModel):
    """File content part"""
    kind: Literal["file"] = "file"
    file_url: str
    mime_type: Optional[str] = None

# Union type for all part types
MessagePartType = TextPart | DataPart | FilePart

# ============= Messages =============
class A2AMessage(BaseModel):
    """A2A Protocol Message"""
    kind: Literal["message"] = "message"
    role: Literal["user", "agent"]
    parts: List[MessagePartType]
    messageId: str = Field(default_factory=lambda: f"msg-{uuid4()}")
    taskId: Optional[str] = None  # Optional now, Telex may not always include it

class MessageConfiguration(BaseModel):
    """Message configuration"""
    blocking: bool = True

# ============= Request =============
class MessageParams(BaseModel):
    """JSON-RPC params for message/send"""
    message: A2AMessage
    configuration: Optional[MessageConfiguration] = None

class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    method: Literal["message/send"]
    params: MessageParams

# ============= Response =============
class Artifact(BaseModel):
    """Task artifact"""
    artifactId: str = Field(default_factory=lambda: f"artifact-{uuid4()}")
    name: str
    parts: List[MessagePartType]

class TaskStatus(BaseModel):
    """Task status"""
    state: Literal["input-required", "completed", "failed"] = "input-required"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: A2AMessage

class TaskResult(BaseModel):
    """Task execution result"""
    id: str  # taskId
    contextId: str
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: List[A2AMessage] = []
    kind: Literal["task"] = "task"

class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: Optional[TaskResult] = None
    error: Optional[Dict[str, Any]] = None

class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 Error"""
    code: int
    message: str
    data: Optional[Any] = None
```

### Step 2: SSL Models (Keep Same)

Create `app/models/ssl_models.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SSLCertificate(BaseModel):
    """SSL Certificate Information"""
    domain: str
    isValid: bool
    issuer: str
    subject: str
    notBefore: datetime
    notAfter: datetime
    daysUntilExpiry: int
    isExpired: bool
    isExpiringSoon: bool
    keySize: int
    signatureAlgorithm: str
    sanList: List[str] = []
    serialNumber: str

class SSLCheckResult(BaseModel):
    """SSL Check Result"""
    domain: str
    success: bool
    certificate: Optional[SSLCertificate] = None
    error: Optional[str] = None
    checkedAt: datetime = Field(default_factory=datetime.utcnow)
    warnings: List[str] = []
```

### Step 3: SSL Checker Service (Keep Same)

Create `app/services/ssl_checker.py`:

```python
import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from typing import Optional, List

from app.models.ssl_models import SSLCertificate, SSLCheckResult

class SSLCheckerService:
    """SSL Certificate Checking Service"""
    
    def __init__(self, timeout: int = 10, warning_days: int = 30):
        self.timeout = timeout
        self.warning_days = warning_days
    
    async def check_domain(self, domain: str, port: int = 443) -> SSLCheckResult:
        """Check SSL certificate for domain"""
        try:
            cert_der = self._get_certificate(domain, port)
            certificate = self._parse_certificate(cert_der, domain)
            warnings = self._generate_warnings(certificate)
            
            return SSLCheckResult(
                domain=domain,
                success=True,
                certificate=certificate,
                warnings=warnings
            )
        
        except socket.timeout:
            return SSLCheckResult(domain=domain, success=False, error="Connection timeout")
        except socket.gaierror:
            return SSLCheckResult(domain=domain, success=False, error="Domain not found (DNS error)")
        except ssl.SSLError as e:
            return SSLCheckResult(domain=domain, success=False, error=f"SSL error: {str(e)}")
        except Exception as e:
            return SSLCheckResult(domain=domain, success=False, error=f"Unexpected error: {str(e)}")
    
    def _get_certificate(self, domain: str, port: int) -> bytes:
        """Retrieve SSL certificate"""
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.getpeercert(binary_form=True)
    
    def _parse_certificate(self, cert_der: bytes, domain: str) -> SSLCertificate:
        """Parse certificate data"""
        cert = x509.load_der_x509_certificate(cert_der, default_backend())
        
        # Extract issuer CN
        issuer_cn = "Unknown"
        for attr in cert.issuer:
            if attr.oid._name == "commonName":
                issuer_cn = attr.value
                break
        
        # Extract subject CN
        subject_cn = domain
        for attr in cert.subject:
            if attr.oid._name == "commonName":
                subject_cn = attr.value
                break
        
        # Dates
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        now = datetime.now(not_after.tzinfo)
        
        days_until_expiry = (not_after - now).days
        is_expired = now > not_after
        is_expiring_soon = 0 < days_until_expiry <= self.warning_days
        
        # Key info
        public_key = cert.public_key()
        key_size = public_key.key_size
        
        # SANs
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            san_list = [dns.value for dns in san_ext.value if isinstance(dns, x509.DNSName)]
        except x509.ExtensionNotFound:
            pass
        
        return SSLCertificate(
            domain=domain,
            isValid=not is_expired,
            issuer=issuer_cn,
            subject=subject_cn,
            notBefore=not_before.replace(tzinfo=None),
            notAfter=not_after.replace(tzinfo=None),
            daysUntilExpiry=days_until_expiry,
            isExpired=is_expired,
            isExpiringSoon=is_expiring_soon,
            keySize=key_size,
            signatureAlgorithm=cert.signature_algorithm_oid._name,
            sanList=san_list,
            serialNumber=hex(cert.serial_number)[:16]
        )
    
    def _generate_warnings(self, cert: SSLCertificate) -> List[str]:
        """Generate warnings"""
        warnings = []
        
        if cert.isExpired:
            warnings.append(f"⚠️ Certificate EXPIRED {abs(cert.daysUntilExpiry)} days ago")
        elif cert.daysUntilExpiry <= 7:
            warnings.append(f"🚨 Certificate expires in {cert.daysUntilExpiry} days (CRITICAL)")
        elif cert.isExpiringSoon:
            warnings.append(f"⚠️ Certificate expires in {cert.daysUntilExpiry} days")
        
        if cert.keySize < 2048:
            warnings.append("⚠️ Weak key size (< 2048 bits)")
        
        return warnings
```

### Step 4: Response Formatter

Create `app/utils/formatters.py`:

```python
from app.models.ssl_models import SSLCheckResult
from typing import List

class SSLResponseFormatter:
    """Format SSL check results"""
    
    def format_single_result(self, result: SSLCheckResult) -> str:
        """Format single SSL check result"""
        if not result.success:
            return f"❌ **SSL Check Failed: {result.domain}**\n\nError: {result.error}"
        
        cert = result.certificate
        lines = []
        
        # Status emoji
        if cert.isExpired:
            emoji, status = "❌", "EXPIRED"
        elif cert.daysUntilExpiry <= 7:
            emoji, status = "🚨", "CRITICAL"
        elif cert.isExpiringSoon:
            emoji, status = "⚠️", "WARNING"
        else:
            emoji, status = "✅", "VALID"
        
        lines.append(f"{emoji} **SSL Certificate: {result.domain}**")
        lines.append(f"**Status**: {status}")
        lines.append("")
        
        # Expiration
        if cert.isExpired:
            lines.append(f"⚠️ **Expired**: {cert.notAfter.strftime('%Y-%m-%d')}")
            lines.append(f"**Days Ago**: {abs(cert.daysUntilExpiry)}")
        else:
            lines.append(f"📅 **Expires**: {cert.notAfter.strftime('%Y-%m-%d %H:%M')}")
            lines.append(f"⏰ **Days Left**: {cert.daysUntilExpiry}")
        
        lines.append("")
        
        # Details
        lines.append("### 🔐 Certificate Details")
        lines.append(f"- **Issuer**: {cert.issuer}")
        lines.append(f"- **Subject**: {cert.subject}")
        lines.append(f"- **Key Size**: {cert.keySize} bits")
        lines.append(f"- **Algorithm**: {cert.signatureAlgorithm}")
        lines.append("")
        
        # SANs
        if cert.sanList:
            lines.append(f"### 🌐 Covered Domains ({len(cert.sanList)})")
            for san in cert.sanList[:5]:
                lines.append(f"- `{san}`")
            if len(cert.sanList) > 5:
                lines.append(f"- _...and {len(cert.sanList) - 5} more_")
            lines.append("")
        
        # Warnings
        if result.warnings:
            lines.append("### ⚠️ Warnings")
            for warning in result.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        lines.append(f"_Checked at {result.checkedAt.strftime('%Y-%m-%d %H:%M:%S UTC')}_")
        
        return "\n".join(lines)
    
    def format_multiple_results(self, results: List[SSLCheckResult]) -> str:
        """Format multiple results"""
        lines = []
        
        lines.append(f"## 🔐 SSL Certificate Summary ({len(results)} domains)")
        lines.append("")
        
        # Stats
        valid = sum(1 for r in results if r.success and not r.certificate.isExpired and not r.certificate.isExpiringSoon)
        warnings = sum(1 for r in results if r.success and r.certificate.isExpiringSoon and not r.certificate.isExpired)
        expired = sum(1 for r in results if r.success and r.certificate.isExpired)
        errors = sum(1 for r in results if not r.success)
        
        lines.append(f"✅ Valid: {valid}")
        lines.append(f"⚠️ Expiring Soon: {warnings}")
        lines.append(f"❌ Expired: {expired}")
        lines.append(f"🚫 Errors: {errors}")
        lines.append("")
        
        # Details
        expired_list = [r for r in results if r.success and r.certificate.isExpired]
        warning_list = [r for r in results if r.success and r.certificate.isExpiringSoon and not r.certificate.isExpired]
        error_list = [r for r in results if not r.success]
        
        if expired_list:
            lines.append("### ❌ Expired Certificates")
            for r in expired_list:
                lines.append(f"- **{r.domain}**: Expired {abs(r.certificate.daysUntilExpiry)} days ago")
            lines.append("")
        
        if warning_list:
            lines.append("### ⚠️ Expiring Soon")
            for r in warning_list:
                lines.append(f"- **{r.domain}**: {r.certificate.daysUntilExpiry} days remaining")
            lines.append("")
        
        if error_list:
            lines.append("### 🚫 Check Errors")
            for r in error_list:
                lines.append(f"- **{r.domain}**: {r.error}")
            lines.append("")
        
        return "\n".join(lines)
```

### Step 5: Message Parser

Create `app/services/message_parser.py`:

```python
import re
from typing import Optional, List, Tuple

class MessageParser:
    """Parse user messages"""
    
    def parse_ssl_request(self, text: str) -> Optional[Tuple[str, List[str]]]:
        """
        Parse SSL check request
        Returns: (action, domains) or None
        """
        text = text.lower().strip()
        
        # Pattern 1: "check ssl for domain.com"
        match = re.search(r'check\s+ssl\s+for\s+([a-z0-9.-]+(?:\s*,\s*[a-z0-9.-]+)*)', text)
        if match:
            domains_str = match.group(1)
            domains = [d.strip() for d in domains_str.split(',')]
            return ("check_multiple" if len(domains) > 1 else "check_single", domains)
        
        # Pattern 2: "check domain.com"
        match = re.search(r'check\s+([a-z0-9.-]+(?:\s*,\s*[a-z0-9.-]+)*)', text)
        if match:
            domains_str = match.group(1)
            domains = [d.strip() for d in domains_str.split(',')]
            return ("check_multiple" if len(domains) > 1 else "check_single", domains)
        
        # Pattern 3: Just domain names
        domains = re.findall(r'[a-z0-9.-]+\.[a-z]{2,}', text)
        if domains:
            return ("check_multiple" if len(domains) > 1 else "check_single", domains)
        
        return None
```

### Step 6: A2A Handler

Create `app/services/a2a_handler.py`:

```python
from app.models.a2a_models import (
    JSONRPCRequest, JSONRPCResponse, JSONRPCError,
    TaskResult, TaskStatus, Artifact, A2AMessage,
    TextPart, DataPart
)
from app.services.ssl_checker import SSLCheckerService
from app.services.message_parser import MessageParser
from app.utils.formatters import SSLResponseFormatter
from uuid import uuid4
from typing import List, Optional, Dict, Any

class A2AHandler:
    """Handle A2A Protocol Requests"""
    
    def __init__(self):
        self.ssl_checker = SSLCheckerService()
        self.parser = MessageParser()
        self.formatter = SSLResponseFormatter()
    
    async def handle_jsonrpc_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle JSON-RPC request"""
        try:
            # Extract user message
            user_message = request.params.message
            
            # Extract the interpreted text and conversation history
            interpreted_text, conversation_history = self._extract_parts(user_message)
            
            if not interpreted_text:
                return self._error_response(
                    request.id,
                    -32602,
                    "Invalid params: no text in message"
                )
            
            # Use the interpreted text (Telex's interpretation at index 0)
            # You can also use conversation_history for context if needed
            
            # Parse intent from the interpreted text
            parsed = self.parser.parse_ssl_request(interpreted_text)
            if not parsed:
                # If parsing fails, try the conversation history
                if conversation_history:
                    parsed = self._parse_from_history(conversation_history)
                
                if not parsed:
                    return self._help_response(
                        request.id, 
                        user_message.taskId or f"task-{uuid4()}"
                    )
            
            action, domains = parsed
            task_id = user_message.taskId or f"task-{uuid4()}"
            
            # Perform checks
            if action == "check_single":
                return await self._handle_single_check(request.id, task_id, domains[0])
            else:
                return await self._handle_multiple_checks(request.id, task_id, domains)
        
        except Exception as e:
            return self._error_response(
                request.id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    def _extract_parts(self, message: A2AMessage) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """
        Extract parts from Telex message structure:
        - parts[0]: TextPart with interpreted text
        - parts[1]: DataPart with conversation history (optional)
        
        Returns: (interpreted_text, conversation_history)
        """
        interpreted_text = None
        conversation_history = []
        
        if len(message.parts) >= 1:
            # First part is the interpreted text
            first_part = message.parts[0]
            if isinstance(first_part, TextPart):
                interpreted_text = first_part.text
        
        if len(message.parts) >= 2:
            # Second part is conversation history
            second_part = message.parts[1]
            if isinstance(second_part, DataPart):
                if isinstance(second_part.data, list):
                    conversation_history = second_part.data
        
        return interpreted_text, conversation_history
    
    def _parse_from_history(self, history: List[Dict[str, Any]]) -> Optional[tuple[str, List[str]]]:
        """
        Try to parse SSL check request from conversation history
        Look through last messages for domain mentions
        """
        # Combine last few messages
        recent_text = ""
        for msg in history[-5:]:  # Last 5 messages
            if isinstance(msg, dict) and msg.get("kind") == "text":
                recent_text += " " + msg.get("text", "")
        
        if recent_text:
            return self.parser.parse_ssl_request(recent_text)
        
        return None
    
    async def _handle_single_check(self, request_id: str, task_id: str, domain: str) -> JSONRPCResponse:
        """Handle single domain check"""
        result = await self.ssl_checker.check_domain(domain)
        
        # Format response text
        response_text = self.formatter.format_single_result(result)
        
        # Create artifacts
        artifacts = []
        if result.success:
            artifacts.append(Artifact(
                name="ssl_certificate",
                parts=[
                    DataPart(data=result.certificate.dict())
                ]
            ))
        
        # Create task result
        task_result = TaskResult(
            id=task_id,
            contextId=f"ctx-{uuid4()}",
            status=TaskStatus(
                state="input-required",
                message=A2AMessage(
                    role="agent",
                    parts=[TextPart(text=response_text)],
                    taskId=task_id
                )
            ),
            artifacts=artifacts,
            history=[]
        )
        
        return JSONRPCResponse(
            id=request_id,
            result=task_result
        )
    
    async def _handle_multiple_checks(self, request_id: str, task_id: str, domains: List[str]) -> JSONRPCResponse:
        """Handle multiple domain checks"""
        results = []
        for domain in domains:
            result = await self.ssl_checker.check_domain(domain)
            results.append(result)
        
        # Format response text
        response_text = self.formatter.format_multiple_results(results)
        
        # Create artifacts
        artifacts = [
            Artifact(
                name="ssl_summary",
                parts=[
                    DataPart(data={
                        "results": [r.dict() for r in results],
                        "summary": {
                            "total": len(results),
                            "valid": sum(1 for r in results if r.success and not r.certificate.isExpired),
                            "expired": sum(1 for r in results if r.success and r.certificate.isExpired),
                            "errors": sum(1 for r in results if not r.success)
                        }
                    })
                ]
            )
        ]
        
        # Create task result
        task_result = TaskResult(
            id=task_id,
            contextId=f"ctx-{uuid4()}",
            status=TaskStatus(
                state="input-required",
                message=A2AMessage(
                    role="agent",
                    parts=[TextPart(text=response_text)],
                    taskId=task_id
                )
            ),
            artifacts=artifacts,
            history=[]
        )
        
        return JSONRPCResponse(
            id=request_id,
            result=task_result
        )
    
    def _help_response(self, request_id: str, task_id: str) -> JSONRPCResponse:
        """Return help message"""
        help_text = """I can help you check SSL certificates! 🔐

Try these commands:
- `Check SSL for github.com`
- `Check github.com, google.com`
- Just mention domain names

I'll check the certificate and let you know:
✅ If it's valid
📅 When it expires
⚠️ If there are any issues"""
        
        task_result = TaskResult(
            id=task_id,
            contextId=f"ctx-{uuid4()}",
            status=TaskStatus(
                state="input-required",
                message=A2AMessage(
                    role="agent",
                    parts=[TextPart(text=help_text)],
                    taskId=task_id
                )
            ),
            artifacts=[],
            history=[]
        )
        
        return JSONRPCResponse(
            id=request_id,
            result=task_result
        )
    
    def _error_response(self, request_id: str, code: int, message: str) -> JSONRPCResponse:
        """Return error response"""
        return JSONRPCResponse(
            id=request_id,
            error={
                "code": code,
                "message": message
            }
        )
```

### Step 7: FastAPI Application

Create `app/main.py`:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.models.a2a_models import JSONRPCRequest, JSONRPCResponse
from app.services.a2a_handler import A2AHandler

app = FastAPI(
    title="SSL Certificate Checker Agent",
    description="A2A-compliant SSL certificate monitoring agent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handler
a2a_handler = A2AHandler()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SSL Certificate Checker Agent",
        "version": "1.0.0",
        "description": "Check SSL certificates for any domain",
        "endpoint": "/a2a/ssl",
        "examples": [
            "Check SSL for github.com",
            "Check github.com, google.com"
        ]
    }

@app.post("/a2a/ssl")
async def a2a_endpoint(request: JSONRPCRequest) -> JSONRPCResponse:
    """
    A2A endpoint - receives JSON-RPC 2.0 requests from Telex
    
    This matches the structure from the blog post exactly:
    - JSON-RPC 2.0 wrapper
    - method: "message/send"
    - params with message and configuration
    """
    response = await a2a_handler.handle_jsonrpc_request(request)
    return response

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
```

### Step 8: Requirements

Create `requirements.txt`:

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.9.0
cryptography>=41.0.0
python-dotenv>=1.0.0
```

---

## 🧪 Testing

### Test with cURL (New Telex Format)

```bash
# Start server
uvicorn app.main:app --reload --port 5001

# Test with Telex's new format (interpreted text + conversation history)
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "df9f853c3d7542d3b1e01957c72db1d1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "github.com"
          },
          {
            "kind": "data",
            "data": [
              {
                "kind": "text",
                "text": "Check SSL for github.com"
              },
              {
                "kind": "text",
                "text": "I need to verify the certificate"
              }
            ]
          }
        ],
        "messageId": "ea6dc8031df74e0da50398e6a0828a4e"
      },
      "configuration": {
        "blocking": true
      }
    }
  }'

# Test with multiple domains (interpreted from conversation)
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-002",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "github.com, google.com, stackoverflow.com"
          },
          {
            "kind": "data",
            "data": [
              {
                "kind": "text",
                "text": "Can you check SSL certificates?"
              },
              {
                "kind": "text",
                "text": "Yes, check for github.com, google.com, and stackoverflow.com"
              }
            ]
          }
        ],
        "messageId": "msg-002"
      }
    }
  }'

# Test old format (backward compatibility - just text part)
curl -X POST http://localhost:5001/a2a/ssl \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-003",
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
        "messageId": "msg-003",
        "taskId": "task-003"
      },
      "configuration": {
        "blocking": true
      }
    }
  }'
```

### Expected Response

```json
{
  "jsonrpc": "2.0",
  "id": "test-001",
  "result": {
    "id": "task-001",
    "contextId": "ctx-12345",
    "status": {
      "state": "input-required",
      "timestamp": "2025-01-30T10:30:00.000Z",
      "message": {
        "messageId": "msg-uuid",
        "role": "agent",
        "parts": [
          {
            "kind": "text",
            "text": "✅ **SSL Certificate: github.com**\n**Status**: VALID\n\n📅 **Expires**: 2024-03-15 08:39\n⏰ **Days Left**: 45\n\n### 🔐 Certificate Details\n- **Issuer**: DigiCert Inc\n- **Subject**: github.com\n- **Key Size**: 2048 bits\n- **Algorithm**: sha256WithRSAEncryption\n\n_Checked at 2024-01-30 10:30:00 UTC_"
          }
        ],
        "kind": "message",
        "taskId": "task-001"
      }
    },
    "artifacts": [
      {
        "artifactId": "artifact-uuid",
        "name": "ssl_certificate",
        "parts": [
          {
            "kind": "data",
            "data": {
              "domain": "github.com",
              "isValid": true,
              "issuer": "DigiCert Inc",
              "daysUntilExpiry": 45,
              ...
            }
          }
        ]
      }
    ],
    "history": [],
    "kind": "task"
  }
}
```

---

## 📝 Understanding Telex's New Message Structure

### What Telex Sends Now:

```json
{
  "parts": [
    {
      "kind": "text",
      "text": "github.com"  // ← Telex's interpretation of what your agent needs
    },
    {
      "kind": "data",
      "data": [  // ← Last 20 messages from conversation
        {
          "kind": "text",
          "text": "Check SSL for github.com"
        },
        {
          "kind": "text",
          "text": "I need to verify the certificate"
        }
      ]
    }
  ]
}
```

### How Your Agent Uses This:

1. **Primary Source (parts[0])**: Use Telex's interpreted text
   - Telex has already extracted "github.com" from the conversation
   - This is what your agent should process first
   - More reliable than parsing raw user input

2. **Fallback (parts[1])**: Use conversation history if needed
   - If interpreted text is unclear, look at conversation history
   - Get additional context about user's intent
   - See what was discussed before

### Example Flow:

**User says:** "Can you check the certificate for GitHub's main site?"

**Telex interprets and sends:**
```json
{
  "parts": [
    {
      "kind": "text",
      "text": "github.com"  // ← Your agent gets this clean domain
    },
    {
      "kind": "data",
      "data": [
        {
          "kind": "text",
          "text": "Can you check the certificate for GitHub's main site?"
        }
      ]
    }
  ]
}
```

**Your agent:**
1. Reads `parts[0].text` → "github.com"
2. Parses it → Finds valid domain
3. Checks SSL certificate
4. Returns result

**If parts[0] is unclear**, your agent can look at `parts[1].data` for context.

---

## ✅ Key Updates Made

| Aspect | Before | After (Updated) |
|--------|--------|-----------------|
| **DataPart.data type** | `Dict[str, Any]` | `Union[Dict, List]` - can be array now |
| **taskId** | Required | Optional - Telex may not include it |
| **Message parsing** | Single text extraction | Two-step: interpreted text + history |
| **Fallback logic** | None | Checks conversation history if needed |
| **Backward compat** | No | Yes - works with old format too |

---

1. **Deploy to Railway**: `railway up`
2. **Get URL**: `https://ssl-checker.up.railway.app`
3. **Register in Telex**:
   - Endpoint: `https://ssl-checker.up.railway.app/a2a/ssl`
   - Method: POST
   - Protocol: JSON-RPC 2.0 + A2A

---

## ✅ Key Points

This implementation now:
- ✅ Uses **JSON-RPC 2.0 wrapper** (like the blog)
- ✅ Has `method: "message/send"` (required)
- ✅ Uses `kind: "message"` and `kind: "text"` (required)
- ✅ Returns proper `TaskResult` with `status`, `artifacts`, `history`
- ✅ Matches the blog post structure **exactly**
- ✅ Works with Telex out of the box

Ready to deploy! 🎉