from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class BackendDeveloperAgent(BaseAgent):
    agent_name: str = "Backend Developer"
    agent_role: str = "Backend Services & Business Logic Implementation"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Implement backend business logic using Python FastAPI and SQLAlchemy.\n"
            "2. Define database access models, services, and authentication handlers.\n"
            "3. Ensure clean architecture with proper error handling and status codes.\n"
            "Produce complete backend code files inside fenced code blocks with filename annotations (e.g. ````python filename=app/services/main_service.py````)."
        )
