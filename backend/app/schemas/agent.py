from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class AgentCreate(BaseModel):
    name: str
    role: str


class AgentResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    role: str
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }