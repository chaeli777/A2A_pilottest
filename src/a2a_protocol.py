"""
A2A Protocol Standard Message Formats
Based on: https://a2a-protocol.org/
"""
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ============================================
# JSON-RPC 2.0 Base
# ============================================

class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 Request"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class JsonRpcResponse(BaseModel):
    """JSON-RPC 2.0 Response"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


# ============================================
# A2A Agent Card
# ============================================

class AgentProvider(BaseModel):
    name: str
    contactEmail: Optional[str] = None


class AgentCapabilities(BaseModel):
    streaming: bool = False
    push: bool = False


class AgentSkill(BaseModel):
    name: str
    description: str
    inputSchema: Optional[Dict[str, Any]] = None
    outputSchema: Optional[Dict[str, Any]] = None


class AgentCard(BaseModel):
    """A2A Standard Agent Card"""
    protocolVersion: str = "1.0"
    name: str
    description: str
    url: str
    provider: AgentProvider
    iconUrl: Optional[str] = None
    version: str = "1.0"
    documentationUrl: Optional[str] = None
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    securitySchemes: Dict[str, Any] = Field(default_factory=dict)
    defaultInputModes: List[str] = Field(default_factory=lambda: ["text"])
    defaultOutputModes: List[str] = Field(default_factory=lambda: ["text"])
    skills: List[AgentSkill] = Field(default_factory=list)
    supportsAuthenticatedExtendedCard: bool = False


# ============================================
# A2A Task & Message
# ============================================

TaskStatus = Literal["submitted", "working", "input-needed", "completed", "failed"]


class TaskInput(BaseModel):
    """Task 입력"""
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class TaskOutput(BaseModel):
    """Task 출력"""
    text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """A2A Task"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = "submitted"
    input: TaskInput
    output: Optional[TaskOutput] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    """A2A Message (대화형 요청/응답)"""
    role: Literal["user", "agent", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Artifact(BaseModel):
    """A2A Artifact (작업 결과물)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "text", "json", "image", etc.
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================
# A2A API Requests/Responses
# ============================================

class CreateTaskRequest(BaseModel):
    """Task 생성 요청"""
    input: TaskInput
    metadata: Optional[Dict[str, Any]] = None


class CreateTaskResponse(BaseModel):
    """Task 생성 응답"""
    taskId: str
    status: TaskStatus


class GetTaskStatusResponse(BaseModel):
    """Task 상태 조회 응답"""
    task: Task


class SubmitMessageRequest(BaseModel):
    """Message 제출 요청"""
    taskId: str
    message: Message


class StreamEvent(BaseModel):
    """스트리밍 이벤트"""
    type: Literal["message", "artifact", "status", "error"]
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)

