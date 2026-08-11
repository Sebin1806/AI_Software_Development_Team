from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class APIDeveloperAgent(BaseAgent):
    agent_name: str = "API Developer"
    agent_role: str = "REST API Specification & Endpoint Implementation"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Design RESTful API routes, Pydantic request/response models, and status codes.\n"
            "2. Produce complete FastAPI router files inside python code blocks ````python filename=app/api/v1_router.py````.\n"
            "3. Produce OpenAPI / Swagger documentation specification in YAML block ````yaml filename=openapi.yaml````."
        )
