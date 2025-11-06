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
