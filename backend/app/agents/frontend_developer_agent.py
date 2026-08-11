from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class FrontendDeveloperAgent(BaseAgent):
    agent_name: str = "Frontend Developer"
    agent_role: str = "Frontend Application & UI Implementation"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Generate frontend React/TypeScript pages and UI components based on the UI/UX design.\n"
            "2. Implement state management, API integration services, and routing.\n"
            "3. Include proper styles, responsive layout, and error boundaries.\n"
            "Produce complete, production-ready frontend code files with specified filename annotations (e.g. ````tsx filename=src/App.tsx````)."
        )
