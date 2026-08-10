from pydantic import BaseModel
from typing import List


class AgentExecutionRequest(BaseModel):
    completed_agents: List[str] = []


class AgentExecutionResponse(BaseModel):
    next_agent: str | None