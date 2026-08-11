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
    current_step: int = 0
    total_steps: int = 12
    percentage_completed: int = 0
    current_agent: Optional[str] = None
    agents_completed: int = 0
    agents_failed: int = 0
    artifacts_generated: int = 0
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[AgentLogSchema] = []


class ArtifactSchema(BaseModel):
    id: UUID
    task_id: UUID
    project_id: UUID
    agent_name: str
    file_name: str
    relative_path: Optional[str] = None
    category: str
    file_type: str
    content: str
    version: int = 1
    content_hash: Optional[str] = None
    created_at: Optional[datetime] = None


class WorkflowSummarySchema(BaseModel):
    total_agents: int = 12
    agents_completed: int = 0
    total_artifacts: int = 0
    code_review_findings: List[str] = []
    security_findings: List[str] = []
    generated_tests: List[str] = []
    deployment_configuration: List[str] = []
    overall_status: str


class TaskExecutionResultsResponse(BaseModel):
    task_id: UUID
    project_id: UUID
    status: str
    workflow_summary: WorkflowSummarySchema
    agent_outputs: Dict[str, Any] = {}
    total_artifacts: int
    artifacts: List[ArtifactSchema] = []