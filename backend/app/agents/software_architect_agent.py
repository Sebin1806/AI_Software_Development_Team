from typing import Any, Dict
from app.agents.base_agent import BaseAgent


class SoftwareArchitectAgent(BaseAgent):
    agent_name: str = "Software Architect"
    agent_role: str = "System Architecture & Design Decisions"

    def get_task_instructions(self, user_prompt: str, project_context: Dict[str, Any], previous_outputs: Dict[str, Any]) -> str:
        return (
            "1. Design high-level system architecture and component interactions.\n"
            "2. Define frontend, backend, and database technology stack.\n"
            "3. Outline complete project directory/folder structure.\n"
            "4. Provide design patterns and architecture diagrams in Mermaid syntax.\n"
            "Produce the architecture specification in a markdown block ````markdown filename=architecture.md````."
        )
