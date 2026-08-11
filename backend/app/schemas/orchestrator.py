from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel


class AgentExecutionRequest(BaseModel):
    completed_agents: List[str] = []


class AgentExecutionResponse(BaseModel):
    next_agent: Optional[str] = None


class StartTaskRequest(BaseModel):
    project_id: UUID
    user_prompt: str


class StartTaskResponse(BaseModel):
    task_id: UUID
    project_id: UUID
    status: str
    message: str


class AgentLogSchema(BaseModel):
    agent_name: str
    step_number: int
    status: str
    retry_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TaskExecutionStatusResponse(BaseModel):
    task_id: UUID
    project_id: UUID
    status: str
    current_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[AgentLogSchema] = []


class ArtifactSchema(BaseModel):
    id: UUID
    agent_name: str
    file_name: str
    file_type: str
    content: str
    created_at: Optional[datetime] = None


class TaskExecutionResultsResponse(BaseModel):
    task_id: UUID
    project_id: UUID
    status: str
    total_artifacts: int
    artifacts: List[ArtifactSchema] = []