from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    owner_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True
    }